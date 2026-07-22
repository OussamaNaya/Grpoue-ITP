# Explication de la Phase 1 - Projet Fournitex (Jalon 1)

Ce document explique en détail le **Jalon 1 (Phase 1)** du cahier des charges du projet Fournitex, qui constitue le socle de l'automatisation n8n.

## 1. Explication de la règle clé

> [!NOTE]
> *"① des relances systématiques, datées et JUSTES — jamais sur une facture soldée ou en litige ;"*

* **Relances systématiques et datées** : L'automatisation doit envoyer des rappels (relances) de manière automatique, sans oublier personne, en respectant un calendrier strict (J+15, J+30, J+45, etc.). Chaque rappel doit être précisément daté.
* **JUSTES** : Le montant réclamé au client doit être 100% correct (calculé au centime près). Si le client a payé une partie (paiement partiel), le système ne doit réclamer que le reste (le solde exact).
* **Jamais sur une facture soldée ou en litige** : 
   * **Soldée** : L'application ne doit **jamais** envoyer de relance si la facture a déjà été totalement payée (Solde = 0). 
   * **En litige** : Si un client a un problème ou une réclamation en cours sur une facture (litige OUVERT d'après la règle **R3**), le système doit bloquer toutes les relances sur cette facture jusqu'à ce que le problème soit réglé (litige CLOS).

---

## 2. Les Étapes de la Phase 1 (Jalon 1)

Pour réussir cette première phase, voici les étapes exactes à configurer :

### Étape 1 : Ingestion des données (Récupération de la data)
* Importer et lier les données provenant des fichiers ou de la base de données fournie (`clients.csv`, `factures.csv`, `paiements.csv`, `litiges.csv`).
* L'objectif est d'avoir une vue globale pour chaque facture : le client associé, les paiements reçus, et le statut d'éventuels litiges.

### Étape 2 : Calcul des échéances manquantes (Règle R4)
* Vérifier la date d'échéance de chaque facture. Si elle est manquante, le système doit la calculer automatiquement à partir des conditions de paiement du client.
* *Exemple* : Si le client a "30J", l'échéance est la date d'émission de la facture + 30 jours. Si c'est "60J_FIN_DE_MOIS", c'est la date d'émission + 60 jours, prolongé jusqu'au dernier jour du mois en question.

### Étape 3 : Calcul des soldes justes (Règle R1)
> [!IMPORTANT]
> C'est l'étape la plus critique du Jalon 1. Si les soldes sont faux, tout le reste le sera.

* Pour chaque facture, calculer le reste à payer (le solde).
* **Formule** : `Solde = Montant TTC de la facture - (Somme de tous les paiements liés à cette facture)`.
* *Attention* : Gérer correctement les paiements multiples et partiels.

### Étape 4 : Détection et séparation des anomalies (Règle R7)
> [!WARNING]
> Les données fournies contiennent des anomalies volontaires. Elles doivent être détectées.

* Créer des filtres pour détecter les factures avec des données incohérentes et les envoyer vers une "File Anomalies" (sans relance).
* *Exemples d'anomalies à bloquer* : 
  * Facture en double
  * Montant TTC différent de HT + TVA
  * Date d'échéance antérieure à la date d'émission
  * Paiement non lié (orphelin) ou trop-perçu

### Étape 5 : Bloquer les factures soldées ou en litige (Règle R3)
* Une fois les soldes calculés, écarter toutes les factures dont le `Solde est <= 0` (factures soldées).
* Croiser les données avec le fichier `litiges.csv` : si la facture a un litige avec le statut **OUVERT**, bloquer la facture pour éviter toute relance automatique.

---
*Ces étapes permettent de préparer une base de données saine et juste, prête pour la **Phase 2** (le moteur de relances basé sur les retards).*
