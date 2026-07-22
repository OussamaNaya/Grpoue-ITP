from flask import Flask, jsonify
from flask_cors import CORS
import pandas as pd
import os
import math

app = Flask(__name__)
CORS(app)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(BASE_DIR, 'output')

def clean_nan(val):
    if pd.isna(val) or (isinstance(val, float) and math.isnan(val)):
        return None
    return val

@app.route('/api/dashboard-stats', methods=['GET'])
def get_stats():
    try:
        factures_path = os.path.join(OUTPUT_DIR, 'factures_valides.csv')
        anomalies_path = os.path.join(OUTPUT_DIR, 'anomalies.csv')
        relances_path = os.path.join(OUTPUT_DIR, 'relances_a_envoyer.csv')

        factures_df = pd.read_csv(factures_path, sep=';') if os.path.exists(factures_path) else pd.DataFrame()
        anomalies_df = pd.read_csv(anomalies_path, sep=';') if os.path.exists(anomalies_path) else pd.DataFrame()
        relances_df = pd.read_csv(relances_path, sep=';') if os.path.exists(relances_path) else pd.DataFrame()

        nb_retards = len(factures_df[factures_df['date_echeance'].notnull()]) # Approximation pour démo
        
        # Calculate total a recouvrer from relances
        total_recouvrer = relances_df['solde'].sum() if 'solde' in relances_df.columns else factures_df['solde'].sum() if not factures_df.empty else 0
        
        stats = {
            'factures_en_retard': len(relances_df),
            'montant_a_recouvrer': f"{total_recouvrer:,.2f} €".replace(',', ' '),
            'anomalies_bloquees': len(anomalies_df),
            'relances_a_envoyer': len(relances_df),
            'repartition': {}
        }
        
        if not relances_df.empty and 'code_modele' in relances_df.columns:
            counts = relances_df['code_modele'].value_counts().to_dict()
            stats['repartition'] = counts

        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/anomalies', methods=['GET'])
def get_anomalies():
    try:
        anomalies_path = os.path.join(OUTPUT_DIR, 'anomalies.csv')
        if not os.path.exists(anomalies_path):
            return jsonify([])
            
        df = pd.read_csv(anomalies_path, sep=';')
        
        # Determine icon and color based on anomaly type
        def get_style(type_ano):
            if type_ano == 'Facture en double':
                return {'color': 'bg-red-50 border-red-500 text-red-700', 'icon': 'warning'}
            elif type_ano == 'Erreur calcul TTC':
                return {'color': 'bg-orange-50 border-orange-500 text-orange-700', 'icon': 'calculate'}
            elif type_ano == 'Trop-perçu (Solde négatif)':
                return {'color': 'bg-blue-50 border-blue-500 text-blue-700', 'icon': 'account_balance_wallet'}
            else:
                return {'color': 'bg-yellow-50 border-yellow-500 text-yellow-700', 'icon': 'info'}

        result = []
        for _, row in df.iterrows():
            style = get_style(row.get('type_anomalie', ''))
            result.append({
                'type': clean_nan(row.get('type_anomalie')),
                'facture_id': clean_nan(row.get('facture_id')),
                'color': style['color'],
                'icon': style['icon']
            })
            
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/outbox', methods=['GET'])
def get_outbox():
    try:
        relances_path = os.path.join(OUTPUT_DIR, 'relances_a_envoyer.csv')
        if not os.path.exists(relances_path):
            return jsonify([])
            
        df = pd.read_csv(relances_path, sep=';')
        
        def get_badge(code):
            if code == 'RELANCE_1': return 'bg-yellow-100 text-yellow-800'
            if code == 'RELANCE_2': return 'bg-orange-100 text-orange-800'
            if code == 'RELANCE_3': return 'bg-red-100 text-red-800'
            return 'bg-gray-100 text-gray-800'

        # We need to fetch amounts from factures_valides.csv since it's not exported in phase2 directly
        factures_path = os.path.join(OUTPUT_DIR, 'factures_valides.csv')
        factures_df = pd.read_csv(factures_path, sep=';')
        
        if not factures_df.empty:
            df = df.merge(factures_df[['facture_id', 'solde']], on='facture_id', how='left')

        result = []
        for _, row in df.iterrows():
            result.append({
                'client': clean_nan(row.get('raison_sociale')),
                'id': clean_nan(row.get('facture_id')),
                'retard': f"{clean_nan(row.get('jours_retard'))} jours",
                'niveau': clean_nan(row.get('code_modele')),
                'montant': f"{clean_nan(row.get('solde', 0)):.2f} €" if pd.notnull(row.get('solde')) else "N/A",
                'badgeColor': get_badge(row.get('code_modele')),
                'objet': clean_nan(row.get('objet_email')),
                'message': clean_nan(row.get('corps_email'))
            })
            
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route("/")
def hello_world():
    return "<p>Fournitex Backend !</p>"


if __name__ == '__main__':
    # Ensure output directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    app.run(port=5000, debug=True)
