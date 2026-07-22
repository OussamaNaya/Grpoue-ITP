# 📊 Métriques du Tableau de Bord — Fournitex ADV

> Ces 4 indicateurs clés (KPI) résument en un coup d'œil l'état du portefeuille client et des actions de recouvrement à mener.

---

## 1. 🔴 Factures en retard — `27`

**Question à laquelle répond cette métrique :**
> Combien de factures nécessitent une action de recouvrement aujourd'hui ?

### Origine de la donnée
Ce chiffre correspond exactement au **nombre de lignes dans `relances_a_envoyer.csv`**, généré par `phase2.py`.

### Conditions pour qu'une facture soit comptée ici
Pour apparaître dans ce compteur, une facture doit avoir passé **tous les filtres** de `phase1.py` :

| Condition | Détail |
|---|---|
| ✅ Non soldée | `solde > 0` (le client n'a pas encore tout payé) |
| ✅ Sans litige | Non présente dans `litiges.csv` avec un litige actif |
| ✅ Sans anomalie | Non bloquée par une erreur détectée dans les données |
| ✅ Échéance dépassée | La date d'échéance est antérieure à la date d'analyse |

---

## 2. 💙 Montant à recouvrer — `104 020 €`

**Question à laquelle répond cette métrique :**
> Quel est le total d'argent que Fournitex n'a pas encore reçu ?

### Origine de la donnée
C'est la **somme de tous les champs `solde`** de `factures_valides.csv`, calculée par `phase1.py`.

### Formule de calcul
```
solde (par facture) = montant_TTC - somme des paiements reçus
```

**Exemple concret :**
- Facture à **5 000 €** TTC
- Paiements reçus : **2 000 €**
- Contribution au total : **3 000 €**

Ce montant représente l'**exposition financière réelle** de Fournitex, c'est-à-dire l'argent qui lui est dû mais pas encore encaissé.

---

## 3. 🔴 Anomalies bloquées — `7` (badge CRITICAL)

**Question à laquelle répond cette métrique :**
> Combien de factures ont été mises en quarantaine car elles contiennent des erreurs ?

### Origine de la donnée
Ces 7 factures ont été détectées par `phase1.py` et exportées dans `anomalies.csv`. Elles sont **exclues** du processus de relance automatique.

### Types d'anomalies possibles

| Type | Description |
|---|---|
| 📄 Facture en double | Même montant + même client + même date détectés deux fois |
| ➗ Erreur de calcul TTC | `HT × (1 + TVA)` ne correspond pas au `montant_TTC` du fichier source |
| 💸 Solde négatif | Le client a trop payé (trop-perçu — remboursement à prévoir) |

> ⚠️ **Ces 7 factures nécessitent une intervention manuelle** via la page **"Anomalies Center"** avant de pouvoir être intégrées au flux de recouvrement.

---

## 4. 🕐 Relances à envoyer — `27` (Aujourd'hui)

**Question à laquelle répond cette métrique :**
> Combien d'emails de relance sont prêts à être expédiés ?

### Origine de la donnée
C'est le nombre d'emails générés par `phase2.py` dans `relances_a_envoyer.csv`. Pour chaque relance, le fichier contient :

| Champ | Contenu |
|---|---|
| `raison_sociale` | Nom du client |
| `contact_email` | Adresse email du destinataire |
| `code_modele` | Niveau de relance (RELANCE_1, RELANCE_2, RELANCE_3…) |
| `objet_email` | Sujet de l'email prêt à envoyer |
| `corps_email` | Texte complet personnalisé de l'email |

Ces 27 emails sont **validables et consultables** dans la page **Outbox** avant expédition.

---

## 🔗 Relation entre les métriques

```
Fichiers sources : clients.csv, factures.csv, paiements.csv, litiges.csv
                              ↓
                          phase1.py
              ┌───────────────────────────────────┐
              │ factures_valides.csv  → 65 lignes  │ ← Montant total = somme des soldes
              │ anomalies.csv         →  7 lignes  │ ← Anomalies bloquées = 7
              └───────────────────────────────────┘
                              ↓
                          phase2.py (filtre les échues + calcule le niveau)
              ┌───────────────────────────────────┐
              │ relances_a_envoyer.csv → 27 lignes │ ← Factures en retard = 27
              └───────────────────────────────────┘  ← Relances à envoyer = 27
```

> **Pourquoi "Factures en retard" et "Relances à envoyer" affichent-elles toutes les deux `27` ?**
> Car le système génère **exactement une relance par facture en retard**. Il n'y a pas de factures retardées sans email associé, et vice versa.
