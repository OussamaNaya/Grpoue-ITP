import pandas as pd
import numpy as np
from datetime import datetime
import os

BASE_DIR   = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR   = os.path.join(BASE_DIR, 'Cahier des charges')
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output')

# Load data
print("Chargement des données pour la Phase 2...")
factures_df = pd.read_csv(os.path.join(OUTPUT_DIR, 'factures_valides.csv'), sep=';')
clients_df = pd.read_csv(os.path.join(DATA_DIR, 'clients.csv'), sep=';')
modeles_df = pd.read_csv(os.path.join(DATA_DIR, 'modeles_courriers.csv'), sep=';')

# Convert dates
reference_date = pd.to_datetime('2026-07-27')
factures_df['date_echeance_dt'] = pd.to_datetime(factures_df['date_echeance'], format='%d/%m/%Y')

# Merge factures with clients to get contact info and segment
factures_df = factures_df.merge(clients_df[['client_id', 'raison_sociale', 'contact_nom', 'contact_email', 'segment']], on='client_id', how='left')

# Calculate delays
print("Calcul des retards...")
factures_df['jours_retard'] = (reference_date - factures_df['date_echeance_dt']).dt.days

# Determine action
def determine_relance(row):
    retard = row['jours_retard']
    segment = row['segment']
    
    if retard < 15:
        return 'AUCUNE'
    elif 15 <= retard < 30:
        return 'RELANCE_1'
    elif 30 <= retard < 45:
        return 'RELANCE_2'
    elif 45 <= retard < 60:
        if segment == 'GRAND_COMPTE':
            return 'ALERTE_VALIDATION'
        else:
            return 'RELANCE_3'
    else:
        return 'TRANSFERT_RECOUVREMENT'

print("Application des règles métier...")
factures_df['code_modele'] = factures_df.apply(determine_relance, axis=1)

# Filter out AUCUNE
relances_df = factures_df[factures_df['code_modele'] != 'AUCUNE'].copy()

# Generate messages
print("Génération des contenus d'emails/courriers...")
modeles_dict = modeles_df.set_index('code_modele').to_dict('index')

def format_message(row, col):
    code = row['code_modele']
    if code not in modeles_dict:
        return ""
    
    text = str(modeles_dict[code][col])
    
    # Replace variables
    text = text.replace('{facture_id}', str(row['facture_id']))
    text = text.replace('{contact_nom}', str(row['contact_nom']))
    text = text.replace('{solde}', f"{row['solde']:.2f}")
    text = text.replace('{date_echeance}', str(row['date_echeance']))
    text = text.replace('{raison_sociale}', str(row['raison_sociale']))
    
    if code == 'ALERTE_VALIDATION':
        text = text.replace('{objet}', f"Facture {row['facture_id']}")
        text = text.replace('{motif}', f"Relance 3 (45j+) sur client GRAND COMPTE")
        text = text.replace('{reference}', str(row['facture_id']))
        
    # Replace literal \n with actual newlines
    text = text.replace('\\n', '\n')
    
    return text

relances_df['objet_email'] = relances_df.apply(lambda row: format_message(row, 'objet_modele'), axis=1)
relances_df['corps_email'] = relances_df.apply(lambda row: format_message(row, 'corps_modele'), axis=1)

# Export
cols_to_export = [
    'facture_id', 'client_id', 'raison_sociale', 'contact_email', 
    'jours_retard', 'code_modele', 'objet_email', 'corps_email'
]

output_path = os.path.join(OUTPUT_DIR, 'relances_a_envoyer.csv')
relances_df[cols_to_export].to_csv(output_path, sep=';', index=False)

print(f"\nPhase 2 terminée avec succès !")
print(f"Total de {len(relances_df)} actions de relance générées.")
print(f"Fichier sauvegardé dans {output_path}")

counts = relances_df['code_modele'].value_counts()
print("\nDétail des actions :")
for code, count in counts.items():
    print(f"- {code}: {count}")
