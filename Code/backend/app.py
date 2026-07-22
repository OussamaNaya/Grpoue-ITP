from flask import Flask, jsonify
from flask_cors import CORS
import pandas as pd
import os
import math

app = Flask(__name__)
CORS(app)

# Les CSV sont dans le dossier 'output/' a côté de ce fichier app.py
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, 'output')

def clean_nan(val):
    try:
        if val is None:
            return None
        if isinstance(val, float) and math.isnan(val):
            return None
        if pd.isna(val):
            return None
    except (TypeError, ValueError):
        pass
    return val

@app.route('/api/dashboard-stats', methods=['GET'])
def get_stats():
    try:
        factures_path = os.path.join(OUTPUT_DIR, 'factures_valides.csv')
        anomalies_path = os.path.join(OUTPUT_DIR, 'anomalies.csv')
        relances_path  = os.path.join(OUTPUT_DIR, 'relances_a_envoyer.csv')

        factures_df  = pd.read_csv(factures_path, sep=';') if os.path.exists(factures_path) else pd.DataFrame()
        anomalies_df = pd.read_csv(anomalies_path, sep=';') if os.path.exists(anomalies_path) else pd.DataFrame()
        relances_df  = pd.read_csv(relances_path,  sep=';') if os.path.exists(relances_path)  else pd.DataFrame()

        # Total à recouvrer = somme des soldes depuis les factures valides
        total_recouvrer = 0.0
        if not factures_df.empty and 'solde' in factures_df.columns:
            total_recouvrer = factures_df['solde'].sum()

        stats = {
            'factures_en_retard':   len(relances_df),
            'montant_a_recouvrer':  f"{total_recouvrer:,.2f} \u20ac".replace(',', ' '),
            'anomalies_bloquees':   len(anomalies_df),
            'relances_a_envoyer':   len(relances_df),
            'repartition': {}
        }

        if not relances_df.empty and 'code_modele' in relances_df.columns:
            stats['repartition'] = relances_df['code_modele'].value_counts().to_dict()

        return jsonify(stats)
    except Exception as e:
        import traceback
        return jsonify({'error': str(e), 'trace': traceback.format_exc()}), 500


@app.route('/api/anomalies', methods=['GET'])
def get_anomalies():
    try:
        anomalies_path = os.path.join(OUTPUT_DIR, 'anomalies.csv')
        if not os.path.exists(anomalies_path):
            return jsonify([])

        df = pd.read_csv(anomalies_path, sep=';')

        def get_style(type_ano):
            if type_ano == 'Facture en double':
                return {'color': 'bg-red-50 border-red-500 text-red-700', 'icon': 'warning'}
            elif 'calcul' in str(type_ano).lower() or 'ttc' in str(type_ano).lower():
                return {'color': 'bg-orange-50 border-orange-500 text-orange-700', 'icon': 'calculate'}
            elif 'négatif' in str(type_ano).lower() or 'trop' in str(type_ano).lower():
                return {'color': 'bg-blue-50 border-blue-500 text-blue-700', 'icon': 'account_balance_wallet'}
            else:
                return {'color': 'bg-yellow-50 border-yellow-500 text-yellow-700', 'icon': 'info'}

        result = []
        for _, row in df.iterrows():
            style = get_style(row.get('type_anomalie', ''))
            result.append({
                'type':       clean_nan(row.get('type_anomalie')),
                'facture_id': clean_nan(row.get('facture_id')),
                'color':      style['color'],
                'icon':       style['icon']
            })

        return jsonify(result)
    except Exception as e:
        import traceback
        return jsonify({'error': str(e), 'trace': traceback.format_exc()}), 500


@app.route('/api/outbox', methods=['GET'])
def get_outbox():
    try:
        relances_path = os.path.join(OUTPUT_DIR, 'relances_a_envoyer.csv')
        if not os.path.exists(relances_path):
            return jsonify([])

        df = pd.read_csv(relances_path, sep=';')

        def get_badge(code):
            if code == 'RELANCE_1':              return 'bg-yellow-100 text-yellow-800'
            if code == 'RELANCE_2':              return 'bg-orange-100 text-orange-800'
            if code == 'RELANCE_3':              return 'bg-red-100 text-red-800'
            if code == 'ALERTE_VALIDATION':      return 'bg-purple-100 text-purple-800'
            if code == 'TRANSFERT_RECOUVREMENT': return 'bg-gray-200 text-gray-900'
            return 'bg-gray-100 text-gray-800'

        # Croiser avec factures_valides pour avoir le solde
        factures_path = os.path.join(OUTPUT_DIR, 'factures_valides.csv')
        if os.path.exists(factures_path):
            factures_df = pd.read_csv(factures_path, sep=';')
            if not factures_df.empty:
                df = df.merge(factures_df[['facture_id', 'solde']], on='facture_id', how='left')

        result = []
        for _, row in df.iterrows():
            solde = row.get('solde')
            montant_str = f"{solde:.2f} \u20ac" if pd.notnull(solde) else "N/A"
            result.append({
                'client':     clean_nan(row.get('raison_sociale')),
                'id':         clean_nan(row.get('facture_id')),
                'retard':     f"{clean_nan(row.get('jours_retard'))} jours",
                'niveau':     clean_nan(row.get('code_modele')),
                'montant':    montant_str,
                'badgeColor': get_badge(row.get('code_modele')),
                'objet':      clean_nan(row.get('objet_email')),
                'message':    clean_nan(row.get('corps_email'))
            })

        return jsonify(result)
    except Exception as e:
        import traceback
        return jsonify({'error': str(e), 'trace': traceback.format_exc()}), 500


@app.route('/')
def index():
    return "<h2>Fournitex ADV - Backend API</h2><p>Routes: /api/dashboard-stats, /api/anomalies, /api/outbox</p>"


if __name__ == '__main__':
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    app.run(port=5000, debug=True)
