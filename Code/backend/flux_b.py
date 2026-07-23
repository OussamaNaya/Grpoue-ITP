"""
flux_b.py — Flux B : Génération automatisée de devis
Fournitex ADV — Cahier des charges exercice youmanIT

Étapes :
  B1 — Lecture des demandes en texte libre + extraction lignes (produit + quantité)
  B2 — Matching catalogue (référence exacte → libellé approché → à clarifier)  [R8]
  B3 — Calcul remise (R9), TVA, totaux HT/TVA/TTC
  B4 — Contrôles : R10 (remise hors grille), R12 (IBAN, manipulation, client inconnu)
  B5 — Génération devis numéroté DEV-Fxxxx, validité 30 jours, FR/EN             [R11]
  B6 — Journal complet + routage messages mixtes                                   [R12]

Idempotence : si un devis_id est déjà dans journal_devis.csv, la demande est ignorée.
"""

import pandas as pd
import re
import os
import sys
from datetime import datetime, timedelta
from difflib import SequenceMatcher

# Assurer l'encodage UTF-8 en sortie console (Windows)
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# ─── Paths ────────────────────────────────────────────────────────────────────
BASE_DIR   = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR   = os.path.join(BASE_DIR, 'Cahier des charges')
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output')
OUTBOX_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'outbox_simule', 'devis')

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(OUTBOX_DIR, exist_ok=True)

# ─── Constantes ───────────────────────────────────────────────────────────────
REMISE_PLAFOND = 18.0          # R9 : plafond absolu
SEUIL_AMBIGUITE = 0.55         # seuil similarité libellé (difflib)
DATE_REFERENCE  = datetime(2026, 7, 27)
VALIDITE_JOURS  = 30

# Regex détection IBAN / RIB (R12)
IBAN_PATTERN = re.compile(
    r'\b[A-Z]{2}\d{2}[\s\-]?(?:\d{4}[\s\-]?){4,6}\d{1,4}\b', re.IGNORECASE
)
# Regex détection tentative de manipulation tarifaire (R12)
MANIPULATION_PATTERNS = [
    re.compile(r'ignor[e|ez|ons]\s+(la\s+)?grille', re.IGNORECASE),
    re.compile(r'remise\s+(de\s+)?\d{2,3}\s*%\s*(valid[eé]e?\s+par|autoris[eé]e?)', re.IGNORECASE),
    re.compile(r'appliqu[e|ez|ons]\s+(une\s+)?remise\s+except', re.IGNORECASE),
    re.compile(r'génère\s+(le\s+)?devis\s+directement', re.IGNORECASE),
    re.compile(r'prix\s+spécial\s+valid[eé]', re.IGNORECASE),
]
# Regex détection réclamation dans message mixte (R12)
RECLAMATION_PATTERNS = [
    re.compile(r'\b(facture|relance)\s+[A-Z]{3}-\d{4}-\d{4}\b', re.IGNORECASE),
    re.compile(r'\b(contestons?|contestez?|erreur|payée?|vérifi[e|ez])\b', re.IGNORECASE),
    re.compile(r'\bne\s+(la\s+)?(trouve|trouvons)\s+pas\b', re.IGNORECASE),
]

# ─── Chargement des données ───────────────────────────────────────────────────
print("B1 — Chargement des données...")
clients_df  = pd.read_csv(os.path.join(DATA_DIR, 'clients.csv'),            sep=';')
catalogue   = pd.read_csv(os.path.join(DATA_DIR, 'catalogue.csv'),          sep=';')
grille_rem  = pd.read_csv(os.path.join(DATA_DIR, 'grille_remises_volume.csv'), sep=';')
demandes_df = pd.read_csv(os.path.join(DATA_DIR, 'demandes_devis.csv'),     sep=';')
modeles_df  = pd.read_csv(os.path.join(DATA_DIR, 'modeles_courriers.csv'),  sep=';')

modeles = modeles_df.set_index('code_modele').to_dict('index')
clients_dict = clients_df.set_index('client_id').to_dict('index')

# Grille remises volume — triée desc pour matching palier
grille_rem = grille_rem.sort_values('qte_min', ascending=False)

# ─── Idempotence : devis déjà générés ────────────────────────────────────────
journal_path = os.path.join(OUTPUT_DIR, 'journal_devis.csv')
deja_traites = set()
if os.path.exists(journal_path):
    existing_journal = pd.read_csv(journal_path, sep=';')
    if 'demande_id' in existing_journal.columns:
        deja_traites = set(existing_journal['demande_id'].dropna().unique())

# ─── Compteur devis (pour numérotation) ──────────────────────────────────────
devis_counter_path = os.path.join(OUTPUT_DIR, 'devis_counter.txt')
if os.path.exists(devis_counter_path):
    with open(devis_counter_path, 'r') as f:
        devis_counter = int(f.read().strip())
else:
    devis_counter = 0

# ─── Helpers ──────────────────────────────────────────────────────────────────

def masquer_iban(texte: str) -> str:
    """R12 : masque tout IBAN/RIB en clair."""
    return IBAN_PATTERN.sub('[IBAN_MASQUÉ]', texte)

def detecter_manipulation(texte: str) -> bool:
    """R12 : True si instruction de manipulation tarifaire détectée."""
    return any(p.search(texte) for p in MANIPULATION_PATTERNS)

def detecter_reclamation(texte: str) -> bool:
    """R12 : True si message contient une réclamation."""
    return any(p.search(texte) for p in RECLAMATION_PATTERNS)

def similarite(a: str, b: str) -> float:
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def matcher_produit(libelle_demande: str) -> dict | None:
    """
    B2 / R8 : Retourne le produit du catalogue le plus proche,
    ou None si introuvable / ambigu.
    """
    libelle_low = libelle_demande.lower().strip()

    # 1. Référence exacte
    match_ref = catalogue[catalogue['reference'].str.lower() == libelle_low]
    if not match_ref.empty:
        return match_ref.iloc[0].to_dict()

    # 2. Libellé exact (insensible à la casse)
    match_lib = catalogue[catalogue['libelle'].str.lower() == libelle_low]
    if not match_lib.empty:
        return match_lib.iloc[0].to_dict()

    # 3. Similarité sur libellé
    scores = catalogue['libelle'].apply(lambda l: similarite(libelle_low, l))
    best_score = scores.max()
    best_matches = catalogue[scores >= SEUIL_AMBIGUITE]

    if best_matches.empty:
        return None  # introuvable

    if len(best_matches) == 1:
        return best_matches.iloc[0].to_dict()  # unique → chiffré

    # Plusieurs → ambigu si les 2 meilleurs sont proches
    top2 = scores.nlargest(2).values
    if top2[0] - top2[1] < 0.15:
        return None  # ambigu
    return catalogue.loc[scores.idxmax()].to_dict()

def remise_volume(qte: float) -> float:
    """R9 : remise volume selon palier."""
    for _, row in grille_rem.iterrows():
        if qte >= row['qte_min']:
            return float(row['remise_pct'])
    return 0.0

def calculer_remise(qte: float, remise_contractuelle_pct: float) -> tuple[float, str]:
    """
    R9 : Meilleure remise entre contractuelle et volume. Plafond 18%.
    Retourne (remise_pct, justification).
    """
    rem_vol  = remise_volume(qte)
    rem_cont = float(remise_contractuelle_pct)
    remise   = max(rem_vol, rem_cont)
    remise   = min(remise, REMISE_PLAFOND)

    if rem_vol > rem_cont:
        justif = f"remise volume (≥{int(qte)} unités) : {rem_vol}%"
    elif rem_cont > 0:
        justif = f"remise contractuelle client : {rem_cont}%"
    else:
        justif = "aucune remise applicable"
    return remise, justif

# ─── B1 : Extraction des lignes produit + quantité depuis texte libre ─────────

# ─── B1 : Extraction des lignes produit + quantité depuis texte libre ─────────

# Table de synonymes catalogue → mots-clés de recherche dans les messages
# Chaque entrée : (reference_catalogue, [liste de mots-clés])
CATALOGUE_KEYWORDS = [
    ('PAP-A4-500',   ['ramette', 'ramettes', 'papier a4', 'feuille', 'a4 80']),
    ('PAP-CAH-96',   ['cahier', 'cahiers', 'grands carreaux']),
    ('PAP-STY-BL',   ['stylo', 'stylos', 'bille bleu', 'bille bleue']),
    ('PAP-MARK-4',   ['marqueur', 'marqueurs', 'effacable', 'effaçable']),
    ('PAP-ENV-DL',   ['enveloppe', 'enveloppes', 'enveloppes dl', 'dl autocollante']),
    ('PAP-CLAS-8',   ['classeur', 'classeurs', 'dos 8', 'dos 8cm', 'classeurs a4']),
    ('MOB-CHA-ERG',  ['chaise', 'chaises', 'ergonomique', 'ergonomiques', 'ergonomic chair', 'ergonomic chairs', 'fauteuil']),
    ('MOB-BUR-140',  ['bureau', 'bureaux', 'plateau 140', '140x70', 'desk']),
    ('MOB-CAI-3T',   ['caisson', 'caissons', 'tiroir', 'tiroirs', 'roulettes']),
    ('MOB-ARM-HT',   ['armoire', 'armoires', 'armoire haute', 'rideau', 'rideaux']),
    ('MOB-LAMP-LED', ['lampe', 'lampes', 'lampe led', 'lampes led', 'led lamp', 'led desk lamp', 'bureau led']),
    ('INF-ECR-24',   ['ecran', 'ecrans', 'écran', 'écrans', 'screen', 'screens', 'moniteur', 'full hd', '24 pouces', '24pouces']),
    ('INF-CLA-SF',   ['clavier', 'claviers', 'keyboard', 'sans fil azerty', 'azerty']),
    ('INF-SOU-ERG',  ['souris', 'mouse', 'ergonomic mouse', 'verticale']),
    ('INF-DOCK-USB', ["station d'accueil", 'stations accueil', 'station accueil', 'dock', 'docking', 'usb-c', 'usbc', "stations d'accueil"]),
    ('INF-CAS-BT',   ['casque', 'casques', 'headset', 'headsets', 'bluetooth headset', 'casque bluetooth', 'casques bluetooth', 'audio bluetooth']),
    ('INF-WEB-HD',   ['webcam', 'webcams', 'full hd webcam', 'full hd webcams', 'camera', 'camara']),
    ('HYG-GEL-5L',   ['gel', 'hydroalcoolique', 'gel hydroalcoolique', 'bidon', 'bidons']),
    ('HYG-PAP-12',   ['papier toilette', 'wc']),
    ('HYG-ESS-6',    ['essuie-mains', 'essuie mains', 'essuie', 'bobine', 'bobines', 'essuie-main']),
    ('HYG-SAV-CR',   ['savon', 'recharge savon', 'recharges savon', 'savon creme', 'savon crème']),
    ('CAF-CAP-100',  ['capsule', 'capsules', 'cafe', 'café', 'capsules cafe', 'capsules café', 'nespresso']),
    ('CAF-GOB-1000', ['gobelet', 'gobelets', 'gobelets carton', 'cup', 'cups']),
    ('CAF-THE-100',  ['the', 'thé', 'sachets the', 'sachets thé', 'sachet the', 'sachet thé', 'assortiment']),
    ('CAF-SUC-1000', ['sucre', 'buchette', 'bûchette', 'buchettes', 'bûchettes']),
    ('SEC-EXT-6KG',  ['extincteur', 'extincteurs', 'poudre 6', '6 kg', '6kg']),
    ('SEC-TRO-PH',   ['trousse', 'trousses', 'premiers secours', 'first aid', 'pharmacie']),
    ('SEC-GIL-JN',   ['gilet', 'gilets', 'haute visibilite', 'haute visibilité', 'visibility', 'high vis', 'jaune']),
]

def extraire_lignes(message: str) -> list[dict]:
    """
    B1 : Extraction robuste par scan catalogue-first.
    Pour chaque produit du catalogue, on cherche ses mots-clés dans le message.
    Si trouvé, on extrait la quantité la plus proche (avant ou après le mot-clé).
    Retourne une liste de dict {libelle_demande, qte_brute}.
    """
    if not isinstance(message, str) or not message.strip():
        return []

    msg_low = message.lower().strip()
    msg_clean = re.sub(r'\bbonjour\b|\bmerci\b|\bcordialement\b|\bsvp\b|\bs\.v\.p\b', '', msg_low, flags=re.IGNORECASE)

    lignes = []
    refs_deja_trouvees = set()

    for ref_cat, keywords in CATALOGUE_KEYWORDS:
        if ref_cat in refs_deja_trouvees:
            continue

        found_kw = None
        found_pos = -1

        for kw in sorted(keywords, key=len, reverse=True):
            idx = msg_clean.find(kw)
            if idx != -1:
                found_kw = kw
                found_pos = idx
                break

        if found_kw is None:
            continue

        # Extraction de la quantité autour du mot clé trouvé
        zone_start = max(0, found_pos - 60)
        zone_end   = min(len(msg_clean), found_pos + len(found_kw) + 60)
        zone = msg_clean[zone_start:zone_end]

        nombres = [(m.start() + zone_start, float(m.group(1).replace(' ', '').replace(',', '.')))
                   for m in re.finditer(r'\b(\d+(?:\.\d+)?)\b', zone)
                   if float(m.group(1).replace(' ', '').replace(',', '.')) > 0
                   and float(m.group(1).replace(' ', '').replace(',', '.')) < 100000]

        if not nombres:
            qte = 1.0
        else:
            kw_pos_in_msg = found_pos
            qte = min(nombres, key=lambda x: abs(x[0] - kw_pos_in_msg))[1]

        zone_num_ctx = msg_clean[max(0, found_pos-80):found_pos+80]
        if re.search(r'\b' + str(int(qte)) + r'\s*(semaines?|jours?|mois|ans?|heures?|minutes?|%)\b', zone_num_ctx):
            qte = 1.0

        prod_row = catalogue[catalogue['reference'] == ref_cat]
        if prod_row.empty:
            continue
        libelle_catalogue = prod_row.iloc[0]['libelle']

        lignes.append({
            'libelle_demande'    : libelle_catalogue,
            'qte_brute'         : float(qte),
        })
        refs_deja_trouvees.add(ref_cat)

    # Fallback : chercher références exactes
    for _, cat_row in catalogue.iterrows():
        ref = cat_row['reference']
        if ref in refs_deja_trouvees:
            continue
        if ref.lower() in message.lower():
            qte_match = re.search(r'\b(\d+)\b', message[max(0, message.lower().find(ref.lower())-30):])
            qte = float(qte_match.group(1)) if qte_match else 1.0
            lignes.append({
                'libelle_demande'    : cat_row['libelle'],
                'qte_brute'         : qte,
            })
            refs_deja_trouvees.add(ref)

    # Gestion du cas DEV-0007 (KLX-200 inconnu)
    # Chercher un motif du type "réf. KLX-200" ou "ref KLX-200"
    m_ref_inconnue = re.search(r'r[eé]f(?:érence|\.)?\s*([A-Z0-9\-]+)', message, re.IGNORECASE)
    if m_ref_inconnue:
        ref_inc = m_ref_inconnue.group(1).upper()
        if ref_inc not in catalogue['reference'].values:
            # Chercher une quantité autour
            qte_match = re.search(r'\b(\d+)\b', message)
            qte = float(qte_match.group(1)) if qte_match else 1.0
            lignes.append({
                'libelle_demande': ref_inc,
                'qte_brute': qte
            })

    return lignes


# ─── Collecte des résultats ───────────────────────────────────────────────────
devis_records       = []  # devis chiffrés
lignes_clarifier    = []  # lignes à clarifier
alertes_validation  = []  # alertes humaines
journal_entries     = []  # journal complet
timestamp_str       = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

print(f"B1 — {len(demandes_df)} demandes à traiter...")

for _, demande in demandes_df.iterrows():
    demande_id = str(demande['demande_id'])
    client_id  = str(demande['client_id'])
    langue     = str(demande.get('langue', 'FR')).strip().upper()
    message_brut = str(demande.get('message', '')) if pd.notna(demande.get('message')) else ''
    date_reception = str(demande.get('date_reception', ''))

    # ── Idempotence ──────────────────────────────────────────────────────────
    if demande_id in deja_traites:
        print(f"  [{demande_id}] Déjà traité — ignoré (idempotence)")
        journal_entries.append({
            'horodatage': timestamp_str, 'demande_id': demande_id,
            'client_id': client_id, 'action': 'IGNORE_IDEMPOTENCE',
            'detail': 'Demande déjà traitée lors d\'une exécution précédente'
        })
        continue

    # ── R12 : Masquage IBAN ───────────────────────────────────────────────────
    iban_detecte = bool(IBAN_PATTERN.search(message_brut))
    message_safe = masquer_iban(message_brut)   # on travaille sur la version masquée

    if iban_detecte:
        alertes_validation.append({
            'horodatage': timestamp_str, 'demande_id': demande_id,
            'client_id': client_id, 'type_alerte': 'SECURITE_IBAN',
            'detail': 'IBAN/RIB détecté dans le message — masqué dans tous les journaux et sorties. Vérification humaine requise.'
        })
        journal_entries.append({
            'horodatage': timestamp_str, 'demande_id': demande_id,
            'client_id': client_id, 'action': 'ALERTE_SECURITE',
            'detail': 'IBAN détecté et masqué (R12)'
        })

    # ── R12 : Détection manipulation tarifaire ────────────────────────────────
    if detecter_manipulation(message_brut):
        alertes_validation.append({
            'horodatage': timestamp_str, 'demande_id': demande_id,
            'client_id': client_id, 'type_alerte': 'SECURITE_MANIPULATION',
            'detail': f'Instruction de manipulation tarifaire détectée et ignorée (R12). Message original conservé dans le journal interne.'
        })
        journal_entries.append({
            'horodatage': timestamp_str, 'demande_id': demande_id,
            'client_id': client_id, 'action': 'MANIPULATION_IGNOREE',
            'detail': 'Tentative de manipulation tarifaire détectée et ignorée (R12)'
        })
        # On continue malgré tout pour chiffrer les vraies lignes produit

    # ── R12 : Message vide ────────────────────────────────────────────────────
    if not message_safe.strip():
        journal_entries.append({
            'horodatage': timestamp_str, 'demande_id': demande_id,
            'client_id': client_id, 'action': 'MESSAGE_VIDE',
            'detail': 'Message vide — demande de précisions envoyée'
        })
        # Courrier demande de précisions
        _outbox_path = os.path.join(OUTBOX_DIR, f'PRECISION_{demande_id}.txt')
        with open(_outbox_path, 'w', encoding='utf-8') as f:
            f.write(f"DESTINATAIRE : {demande.get('email_expediteur', 'inconnu')}\n")
            f.write(f"OBJET : Précision nécessaire — votre demande {demande_id}\n")
            f.write("---\n\nBonjour,\n\nNous avons bien reçu votre demande mais le message est vide ou illisible.\n")
            f.write("Pourriez-vous nous préciser les produits et quantités souhaités ?\n\nCordialement,\nService commercial Fournitex\n")
        continue

    # ── Client connu ? ────────────────────────────────────────────────────────
    client_info = clients_dict.get(client_id)
    client_inconnu = (client_info is None)
    if client_inconnu:
        alertes_validation.append({
            'horodatage': timestamp_str, 'demande_id': demande_id,
            'client_id': client_id, 'type_alerte': 'CLIENT_INCONNU',
            'detail': f'Client {client_id} absent du référentiel — prospect à qualifier. Devis généré sans remise contractuelle.'
        })
        journal_entries.append({
            'horodatage': timestamp_str, 'demande_id': demande_id,
            'client_id': client_id, 'action': 'CLIENT_INCONNU',
            'detail': 'Prospect non référencé — traitement sans remise contractuelle'
        })
        remise_contractuelle = 0.0
        contact_nom   = 'Client'
        raison_sociale = client_id
        segment        = 'STANDARD'
    else:
        remise_contractuelle = float(client_info.get('remise_contractuelle_pct', 0) or 0)
        contact_nom   = client_info.get('contact_nom', 'Client')
        raison_sociale = client_info.get('raison_sociale', client_id)
        segment        = client_info.get('segment', 'STANDARD')

    # ── R12 : Message mixte (devis + réclamation) ─────────────────────────────
    reclamation_detectee = detecter_reclamation(message_safe)
    if reclamation_detectee:
        alertes_validation.append({
            'horodatage': timestamp_str, 'demande_id': demande_id,
            'client_id': client_id, 'type_alerte': 'MESSAGE_MIXTE_RECLAMATION',
            'detail': f'Message mixte détecté pour {raison_sociale} ({demande_id}) : la partie réclamation est routée vers l\'humain. La partie devis est traitée normalement.'
        })
        journal_entries.append({
            'horodatage': timestamp_str, 'demande_id': demande_id,
            'client_id': client_id, 'action': 'RECLAMATION_ROUTEE_HUMAIN',
            'detail': 'Partie réclamation routée à l\'humain (R12), partie devis traitée'
        })

    # ── B1 : Extraction des lignes ────────────────────────────────────────────
    lignes_extraites = extraire_lignes(message_safe)

    if not lignes_extraites:
        journal_entries.append({
            'horodatage': timestamp_str, 'demande_id': demande_id,
            'client_id': client_id, 'action': 'AUCUNE_LIGNE_EXTRAITE',
            'detail': 'Aucune ligne produit identifiable dans le message'
        })
        # Courrier de clarification
        _outbox_path = os.path.join(OUTBOX_DIR, f'CLARIFICATION_{demande_id}.txt')
        with open(_outbox_path, 'w', encoding='utf-8') as f:
            f.write(f"DESTINATAIRE : {demande.get('email_expediteur', 'inconnu')}\n")
            f.write(f"OBJET : Précision nécessaire — votre demande {demande_id}\n")
            f.write("---\n\n")
            f.write(f"Bonjour {contact_nom},\n\n")
            f.write("Afin de finaliser votre devis, pourriez-vous préciser les produits et quantités souhaités ?\n\n")
            f.write("Service commercial Fournitex\n")
        continue

    # ── B2 : Matching catalogue ───────────────────────────────────────────────
    lignes_devis  = []   # lignes chiffrées
    lignes_nc     = []   # lignes à clarifier (non chiffrées)

    for ligne in lignes_extraites:
        lib_dem = ligne['libelle_demande']
        qte     = ligne['qte_brute']
        produit = matcher_produit(lib_dem)

        if produit is None:
            lignes_nc.append({'libelle_demande': lib_dem, 'qte': qte})
        else:
            # B3 : Calcul remise + TVA
            remise_pct, justif_remise = calculer_remise(qte, remise_contractuelle)
            prix_ht    = float(produit['prix_unitaire_ht'])
            tva_pct    = float(produit['tva_pct'])
            total_ht   = round(prix_ht * qte * (1 - remise_pct / 100), 2)
            total_tva  = round(total_ht * tva_pct / 100, 2)
            total_ttc  = round(total_ht + total_tva, 2)

            lignes_devis.append({
                'reference'     : produit['reference'],
                'libelle'       : produit['libelle'],
                'libelle_demande': lib_dem,
                'qte'           : qte,
                'prix_ht_unit'  : prix_ht,
                'remise_pct'    : remise_pct,
                'justif_remise' : justif_remise,
                'total_ht'      : total_ht,
                'tva_pct'       : tva_pct,
                'total_tva'     : total_tva,
                'total_ttc'     : total_ttc,
            })

    # ── Tracer les lignes à clarifier ─────────────────────────────────────────
    for lnc in lignes_nc:
        lignes_clarifier.append({
            'horodatage'     : timestamp_str,
            'demande_id'     : demande_id,
            'client_id'      : client_id,
            'raison_sociale' : raison_sociale,
            'libelle_demande': lnc['libelle_demande'],
            'qte'            : lnc['qte'],
            'motif'          : 'Produit introuvable ou ambigu dans le catalogue'
        })

    # ── B4 : Contrôle remise hors grille (R10) ────────────────────────────────
    remise_max_demande = max((l['remise_pct'] for l in lignes_devis), default=0)
    hors_grille = remise_max_demande > REMISE_PLAFOND  # ne devrait plus arriver (plafonnée en amont)

    # Détecter si une remise > plafond a été demandée explicitement dans le texte
    remise_demandee_match = re.search(r'remise\s+(?:de\s+)?(\d{1,3})\s*%', message_brut, re.IGNORECASE)
    if remise_demandee_match:
        remise_demandee_val = float(remise_demandee_match.group(1))
        if remise_demandee_val > REMISE_PLAFOND:
            alertes_validation.append({
                'horodatage': timestamp_str, 'demande_id': demande_id,
                'client_id': client_id, 'type_alerte': 'REMISE_HORS_GRILLE',
                'detail': (
                    f'Remise demandée {remise_demandee_val}% > plafond {REMISE_PLAFOND}% (R10). '
                    f'Devis généré avec la remise maximale autorisée ({REMISE_PLAFOND}%). '
                    f'Validation humaine requise si accord exceptionnel souhaité.'
                )
            })
            journal_entries.append({
                'horodatage': timestamp_str, 'demande_id': demande_id,
                'client_id': client_id, 'action': 'ALERTE_REMISE_HORS_GRILLE',
                'detail': f'Remise demandée {remise_demandee_val}% plafonnée à {REMISE_PLAFOND}% (R10)'
            })

    # ── Totaux globaux ────────────────────────────────────────────────────────
    grand_total_ht  = round(sum(l['total_ht']  for l in lignes_devis), 2)
    grand_total_tva = round(sum(l['total_tva'] for l in lignes_devis), 2)
    grand_total_ttc = round(sum(l['total_ttc'] for l in lignes_devis), 2)

    # ── B5 : Génération du devis numéroté ─────────────────────────────────────
    if lignes_devis:
        devis_counter += 1
        devis_id       = f"DEV-F{devis_counter:04d}"
        date_devis     = DATE_REFERENCE.strftime('%d/%m/%Y')
        date_validite  = (DATE_REFERENCE + timedelta(days=VALIDITE_JOURS)).strftime('%d/%m/%Y')

        # Choisir le modèle selon la langue (R11)
        modele_code = 'DEVIS_EN' if langue == 'EN' else 'DEVIS'
        modele = modeles.get(modele_code, modeles.get('DEVIS', {}))

        # Corps du devis
        corps = str(modele.get('corps_modele', '')).replace('\\n', '\n')
        corps = corps.replace('{devis_id}', devis_id)
        corps = corps.replace('{contact_nom}', contact_nom)
        corps = corps.replace('{total_ht}', f"{grand_total_ht:.2f}")
        corps = corps.replace('{total_ttc}', f"{grand_total_ttc:.2f}")

        objet = str(modele.get('objet_modele', '')).replace('{devis_id}', devis_id)

        # Contenu détaillé du devis (lignes)
        if langue == 'EN':
            entete_lignes = "Ref.          | Description                         |  Qty | Unit HT€ | Disc% | Total HT€  | VAT%  | Total TTC€"
        else:
            entete_lignes = "Réf.          | Désignation                         |  Qté | PU HT €  | Rem%  | Total HT € | TVA%  | Total TTC€"

        separateur = "-" * len(entete_lignes)
        lignes_txt = [entete_lignes, separateur]
        for l in lignes_devis:
            lignes_txt.append(
                f"{l['reference']:<14}| {l['libelle']:<35} | {int(l['qte']):>4} | {l['prix_ht_unit']:>8.2f} | {l['remise_pct']:>5.1f} | {l['total_ht']:>10.2f} | {l['tva_pct']:>5.0f} | {l['total_ttc']:>10.2f}"
            )
        lignes_txt.append(separateur)
        if langue == 'EN':
            lignes_txt.append(f"{'TOTAL':<60} | {grand_total_ht:>10.2f} |       | {grand_total_ttc:>10.2f}")
            validite_label = f"Valid until: {date_validite}"
        else:
            lignes_txt.append(f"{'TOTAL':<60} | {grand_total_ht:>10.2f} |       | {grand_total_ttc:>10.2f}")
            validite_label = f"Validité : jusqu'au {date_validite}"

        # Lignes à clarifier
        nc_txt = ""
        if lignes_nc:
            nc_txt = "\n\n--- LIGNES À CLARIFIER ---\n"
            for lnc in lignes_nc:
                nc_txt += f"  • {lnc['libelle_demande']} (qté: {lnc['qte']}) — référence introuvable ou ambiguë\n"

        # Écriture outbox
        outbox_filename = f"{devis_id}_{client_id}.txt"
        outbox_path = os.path.join(OUTBOX_DIR, outbox_filename)
        with open(outbox_path, 'w', encoding='utf-8') as f:
            f.write(f"DESTINATAIRE : {demande.get('email_expediteur', 'inconnu')}\n")
            f.write(f"OBJET : {objet}\n")
            f.write("=" * 60 + "\n\n")
            f.write(corps + "\n\n")
            f.write("\n".join(lignes_txt) + "\n")
            f.write(f"\n{validite_label}\n")
            if nc_txt:
                f.write(nc_txt)

        # Record pour CSV
        devis_records.append({
            'horodatage'        : timestamp_str,
            'devis_id'          : devis_id,
            'demande_id'        : demande_id,
            'client_id'         : client_id,
            'raison_sociale'    : raison_sociale,
            'langue'            : langue,
            'date_devis'        : date_devis,
            'date_validite'     : date_validite,
            'nb_lignes_chiffrees': len(lignes_devis),
            'nb_lignes_clarifier': len(lignes_nc),
            'grand_total_ht'    : grand_total_ht,
            'grand_total_tva'   : grand_total_tva,
            'grand_total_ttc'   : grand_total_ttc,
            'remise_max_appliquee': remise_max_demande,
            'fichier_outbox'    : outbox_filename,
            'detail_lignes'     : str([{k: v for k, v in l.items()} for l in lignes_devis]),
        })

        journal_entries.append({
            'horodatage': timestamp_str, 'demande_id': demande_id,
            'client_id': client_id, 'action': 'DEVIS_GENERE',
            'detail': f'{devis_id} — {len(lignes_devis)} lignes chiffrées, {len(lignes_nc)} à clarifier — TTC: {grand_total_ttc:.2f}€'
        })
        print(f"  [{demande_id}] OK {devis_id} genere - {len(lignes_devis)} lignes - {grand_total_ttc:.2f}EUR TTC")
    else:
        # Aucune ligne chiffrable → tout est à clarifier
        journal_entries.append({
            'horodatage': timestamp_str, 'demande_id': demande_id,
            'client_id': client_id, 'action': 'DEVIS_NON_GENERE',
            'detail': 'Aucune ligne chiffrable — toutes les lignes sont à clarifier'
        })
        # Courrier de clarification globale
        _outbox_path = os.path.join(OUTBOX_DIR, f'CLARIFICATION_{demande_id}.txt')
        tpl = modeles.get('LIGNE_A_CLARIFIER', {})
        objet_cl = str(tpl.get('objet_modele', '')).replace('{demande_id}', demande_id)
        corps_cl = str(tpl.get('corps_modele', '')).replace('\\n', '\n')
        corps_cl = corps_cl.replace('{contact_nom}', contact_nom)
        corps_cl = corps_cl.replace('{demande_id}', demande_id)
        corps_cl = corps_cl.replace('{libelle_demande}', ', '.join(l['libelle_demande'] for l in lignes_nc) or 'non identifié')
        with open(_outbox_path, 'w', encoding='utf-8') as f:
            f.write(f"DESTINATAIRE : {demande.get('email_expediteur', 'inconnu')}\n")
            f.write(f"OBJET : {objet_cl}\n")
            f.write("---\n\n" + corps_cl + "\n")
        print(f"  [{demande_id}] CLARIF : Aucune ligne chiffrable - clarification envoyee")

    # ── Courrier séparé pour les lignes à clarifier ───────────────────────────
    if lignes_nc and lignes_devis:
        tpl = modeles.get('LIGNE_A_CLARIFIER', {})
        objet_cl = str(tpl.get('objet_modele', '')).replace('{demande_id}', demande_id)
        corps_cl = str(tpl.get('corps_modele', '')).replace('\\n', '\n')
        corps_cl = corps_cl.replace('{contact_nom}', contact_nom)
        corps_cl = corps_cl.replace('{demande_id}', demande_id)
        ncs_list = ', '.join(f'« {l["libelle_demande"]} »' for l in lignes_nc)
        corps_cl = corps_cl.replace('{libelle_demande}', ncs_list)
        _outbox_path = os.path.join(OUTBOX_DIR, f'CLARIFICATION_{demande_id}.txt')
        with open(_outbox_path, 'w', encoding='utf-8') as f:
            f.write(f"DESTINATAIRE : {demande.get('email_expediteur', 'inconnu')}\n")
            f.write(f"OBJET : {objet_cl}\n")
            f.write("---\n\n" + corps_cl + "\n")

# ─── Sauvegarde compteur ──────────────────────────────────────────────────────
with open(devis_counter_path, 'w') as f:
    f.write(str(devis_counter))

# ─── B6 : Export CSV ──────────────────────────────────────────────────────────
print("\nB6 — Export des résultats...")

# Devis générés
if devis_records:
    devis_df = pd.DataFrame(devis_records)
    devis_path = os.path.join(OUTPUT_DIR, 'devis_generes.csv')
    devis_df.to_csv(devis_path, sep=';', index=False, encoding='utf-8-sig')
    print(f"  OK {len(devis_records)} devis exportes -> {devis_path}")

# Lignes à clarifier
if lignes_clarifier:
    clar_df = pd.DataFrame(lignes_clarifier)
    clar_path = os.path.join(OUTPUT_DIR, 'lignes_a_clarifier.csv')
    clar_df.to_csv(clar_path, sep=';', index=False, encoding='utf-8-sig')
    print(f"  WARN {len(lignes_clarifier)} lignes a clarifier -> {clar_path}")

# Alertes validation humaine
if alertes_validation:
    alertes_df = pd.DataFrame(alertes_validation)
    alertes_path = os.path.join(OUTPUT_DIR, 'alertes_validation.csv')
    alertes_df.to_csv(alertes_path, sep=';', index=False, encoding='utf-8-sig')
    print(f"  ALERTE {len(alertes_validation)} alertes -> {alertes_path}")

# Journal
if journal_entries:
    journal_df = pd.DataFrame(journal_entries)
    if os.path.exists(journal_path):
        journal_df.to_csv(journal_path, sep=';', mode='a', header=False, index=False, encoding='utf-8-sig')
    else:
        journal_df.to_csv(journal_path, sep=';', index=False, encoding='utf-8-sig')
    print(f"  JOURNAL mis a jour -> {journal_path}")

# ─── Résumé final ─────────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("FLUX B — Résumé d'exécution")
print("=" * 60)
print(f"  Demandes traitées   : {len(demandes_df) - len(deja_traites)}")
print(f"  Devis générés       : {len(devis_records)}")
print(f"  Lignes à clarifier  : {len(lignes_clarifier)}")
print(f"  Alertes humaines    : {len(alertes_validation)}")
print(f"  Outbox devis        : {OUTBOX_DIR}")
print("=" * 60)
