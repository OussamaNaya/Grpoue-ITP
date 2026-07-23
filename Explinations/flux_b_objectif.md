# 🎯 Objectif du Flux B — Devis

> Extrait du cahier des charges : `cdc_exercice_fournitex.docx`

---

## Description générale

Le **Flux B** est dédié à la **génération automatisée de devis** à partir de demandes formulées en texte libre.

---

## Étapes du traitement

| Étape | Description |
|-------|-------------|
| **B1** | **Lecture des demandes en texte libre** — extraction des lignes : produit demandé + quantité. |
| **B2** | **Matching des produits au catalogue** — référence exacte ou libellé. Si introuvable/ambigu → ligne « à clarifier » (R8). |
| **B3** | **Calcul des remises et de la TVA** — application de la remise (R9), calcul des totaux HT / TVA / TTC. |
| **B4** | **Génération du devis numéroté** — document produit en FR/EN (mode simulé). |
| **B5** | **Alertes de validation humaine** — si remise hors grille → alerte déclenchée (R10). |
| **B6** | **Journal** — traçabilité de toutes les décisions prises. |

---

## ⚡ Déclencheur

- **En production** : à la réception de chaque demande de devis.
- **Pour l'épreuve** : le fichier `demandes_devis.csv` fait foi et peut être traité en **une seule passe**.

---

## ✅ Ce que le Flux B fait

- Lire et interpréter des demandes en texte libre
- Matcher les produits au catalogue
- Appliquer remises et TVA
- Générer un devis numéroté (simulé)
- Signaler les lignes à clarifier
- Alerter en cas de remise hors grille
- Alimenter le journal et le tableau de bord

---

## ❌ Ce que le Flux B ne fait PAS (hors périmètre)

- Modification des tarifs du catalogue
- Négociation commerciale
- Validation finale des devis hors grille *(décision humaine)*
- Signature de quoi que ce soit
- Envoi réel d'emails

---

*Source : Cahier des charges Fournitex — Section 2 & 4*
