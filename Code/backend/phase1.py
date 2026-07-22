import pandas as pd
import numpy as np
from datetime import datetime
import os

# Paths
# backend/phase1.py est dans : Groupe ITP Projet/Code/backend/
# On remonte 3 niveaux pour atteindre : Groupe ITP Projet/
BASE_DIR   = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR   = os.path.join(BASE_DIR, 'Cahier des charges')
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output')

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

# Load data
print("Chargement des données...")
clients_df = pd.read_csv(os.path.join(DATA_DIR, 'clients.csv'), sep=';')
factures_df = pd.read_csv(os.path.join(DATA_DIR, 'factures.csv'), sep=';')
paiements_df = pd.read_csv(os.path.join(DATA_DIR, 'paiements.csv'), sep=';')
litiges_df = pd.read_csv(os.path.join(DATA_DIR, 'litiges.csv'), sep=';')

# Convert dates
factures_df['date_emission'] = pd.to_datetime(factures_df['date_emission'], format='%d/%m/%Y', errors='coerce')
factures_df['date_echeance'] = pd.to_datetime(factures_df['date_echeance'], format='%d/%m/%Y', errors='coerce')
paiements_df['date_paiement'] = pd.to_datetime(paiements_df['date_paiement'], format='%Y-%m-%d', errors='coerce')
litiges_df['date_ouverture'] = pd.to_datetime(litiges_df['date_ouverture'], format='%Y-%m-%d', errors='coerce')

# Merge factures with clients to get conditions_paiement
factures_df = factures_df.merge(clients_df[['client_id', 'conditions_paiement']], on='client_id', how='left')

# Calculate missing due dates (date_echeance)
print("Calcul des échéances manquantes...")
def calculate_echeance(row):
    if pd.notnull(row['date_echeance']):
        return row['date_echeance']
    
    date_emission = row['date_emission']
    condition = row['conditions_paiement']
    
    if pd.isnull(date_emission) or pd.isnull(condition):
        return pd.NaT
        
    if condition == '30J':
        return date_emission + pd.Timedelta(days=30)
    elif condition == '45J':
        return date_emission + pd.Timedelta(days=45)
    elif condition == '60J':
        return date_emission + pd.Timedelta(days=60)
    elif condition == '60J_FIN_DE_MOIS':
        temp_date = date_emission + pd.Timedelta(days=60)
        # End of that month
        if temp_date.month == 12:
            next_month = temp_date.replace(year=temp_date.year + 1, month=1, day=1)
        else:
            next_month = temp_date.replace(month=temp_date.month + 1, day=1)
        return next_month - pd.Timedelta(days=1)
    return pd.NaT

factures_df['date_echeance_calculee'] = factures_df.apply(calculate_echeance, axis=1)
factures_df['date_echeance'] = factures_df['date_echeance'].fillna(factures_df['date_echeance_calculee'])

# Aggregate payments
print("Calcul des soldes...")
somme_paiements = paiements_df.groupby('facture_id')['montant'].sum().reset_index()
somme_paiements.rename(columns={'montant': 'somme_paiements'}, inplace=True)

# Merge payments into factures
factures_df = factures_df.merge(somme_paiements, on='facture_id', how='left')
factures_df['somme_paiements'] = factures_df['somme_paiements'].fillna(0)

# Calculate balance
factures_df['solde'] = factures_df['montant_ttc'] - factures_df['somme_paiements']

# Identify Anomalies
print("Détection des anomalies...")
anomalies = []

# 1. Duplicates
duplicates = factures_df[factures_df.duplicated('facture_id', keep=False)].copy()
if not duplicates.empty:
    duplicates['type_anomalie'] = 'Facture en double'
    anomalies.append(duplicates)

# 2. Math errors (TTC != HT + TVA)
factures_df['ttc_calcule'] = round(factures_df['montant_ht'] * (1 + factures_df['tva_pct'] / 100), 2)
math_errors = factures_df[abs(factures_df['montant_ttc'] - factures_df['ttc_calcule']) > 0.05].copy()
if not math_errors.empty:
    math_errors['type_anomalie'] = 'Erreur calcul TTC'
    anomalies.append(math_errors)

# 3. Date inconsistencies (Due < Emission)
date_errors = factures_df[factures_df['date_echeance'] < factures_df['date_emission']].copy()
if not date_errors.empty:
    date_errors['type_anomalie'] = 'Echeance < Emission'
    anomalies.append(date_errors)

# 4. Overpayments
overpayments = factures_df[factures_df['solde'] < -0.01].copy()
if not overpayments.empty:
    overpayments['type_anomalie'] = 'Trop-perçu (Solde négatif)'
    anomalies.append(overpayments)

# 5. Orphan payments
orphan_payments = paiements_df[~paiements_df['facture_id'].isin(factures_df['facture_id'])].copy()
if not orphan_payments.empty:
    orphan_df = pd.DataFrame({'facture_id': orphan_payments['facture_id'], 'type_anomalie': 'Paiement orphelin'})
    anomalies.append(orphan_df)

if anomalies:
    anomalies_df = pd.concat(anomalies, ignore_index=True)
else:
    anomalies_df = pd.DataFrame()

# Exclude anomalies from valid invoices
if not anomalies_df.empty:
    anomalous_factures = anomalies_df['facture_id'].unique()
    factures_valides = factures_df[~factures_df['facture_id'].isin(anomalous_factures)].copy()
else:
    factures_valides = factures_df.copy()

# Filtrage (Règle R3)
print("Filtrage des factures soldées et litiges ouverts...")
# 1. Factures soldées
factures_valides = factures_valides[factures_valides['solde'] > 0]

# 2. Litiges ouverts
litiges_ouverts = litiges_df[litiges_df['statut'] == 'OUVERT']['facture_id'].unique()
factures_valides = factures_valides[~factures_valides['facture_id'].isin(litiges_ouverts)]

# Formatting and export
print("Exportation des résultats...")
for col in ['date_emission', 'date_echeance']:
    if col in factures_valides.columns:
        factures_valides[col] = factures_valides[col].dt.strftime('%d/%m/%Y')
    if col in anomalies_df.columns and pd.api.types.is_datetime64_any_dtype(anomalies_df[col]):
        anomalies_df[col] = anomalies_df[col].dt.strftime('%d/%m/%Y')

cols_to_export = [
    'facture_id', 'client_id', 'date_emission', 'date_echeance', 
    'montant_ht', 'tva_pct', 'montant_ttc', 'somme_paiements', 'solde', 'conditions_paiement'
]
factures_valides[cols_to_export].to_csv(os.path.join(OUTPUT_DIR, 'factures_valides.csv'), sep=';', index=False)

if not anomalies_df.empty:
    anomalies_df.to_csv(os.path.join(OUTPUT_DIR, 'anomalies.csv'), sep=';', index=False)

print(f"Traitement terminé avec succès !")
print(f"- {len(factures_valides)} factures prêtes à être relancées.")
print(f"- {len(anomalies_df)} anomalies détectées.")
print(f"Les fichiers générés se trouvent dans le dossier '{OUTPUT_DIR}'.")
