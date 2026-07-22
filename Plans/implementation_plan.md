# Plan d'Implémentation Technique - Projet Fournitex

Ce document détaille l'architecture technique proposée pour réaliser le projet Fournitex (Backend, Frontend, Services AI et Orchestration), en respectant les contraintes du cahier des charges.

## User Review Required

> [!CAUTION]
> Le cahier des charges impose la règle suivante (R12) : **"pas d'envoi en clair vers un service d'IA public non maîtrisé (anonymisation ou traitement local requis)"**. 
> Nous devons décider ensemble si nous utilisons une IA locale (ex: Ollama, 100% sécurisé mais demande des ressources PC) ou une IA publique (ex: OpenAI) avec un script de masquage des données très strict avant l'envoi.

## Open Questions

> [!IMPORTANT]
> 1. **Base de données (Backend)** : Le projet fournit un dump `fournitex_adv.sql`. Es-tu d'accord pour utiliser **MySQL** comme base de données principale ?
> 2. **Frontend (Tableau de bord)** : Le choix est libre. Préfères-tu qu'on utilise **Streamlit** (très rapide à faire en Python), **Metabase** (outil de reporting sans code), ou un framework classique (React/Vue.js) ?
> 3. **Environnement** : As-tu **Docker** installé sur ta machine ? Ça nous faciliterait énormément la vie pour lancer n8n, MySQL, et potentiellement l'IA locale tous ensemble.

## Proposed Changes

### 1. Orchestration & Logique Centrale (n8n)
**n8n** sera le chef d'orchestre (obligatoire selon le CDC).
- **Workflows** : Création des workflows pour lire la BDD, filtrer les anomalies, et générer les relances (J1/J2) ainsi que traiter les devis (J3).
- **Noeuds Code** : Utilisation de Javascript/Python dans n8n pour les règles métiers complexes (calcul des soldes exacts R1, calcul des échéances R4).

### 2. Backend (Base de données & Traitements)
- **Stockage principal** : Restauration du fichier `fournitex_adv.sql` dans MySQL.
- **Journalisation (Logs)** : Création de nouvelles tables pour journaliser chaque décision (facture relancée, écartée, anomalies, litiges) afin de respecter l'exigence de traçabilité.
- **Scripts Externes** : Si une logique est trop complexe pour n8n, nous créerons un petit script Python qui sera appelé par n8n.

### 3. Services AI (NLP & Sécurité)
L'IA intervient dans la partie Devis (R8) et Traduction (R11).
- **Solution Technique Proposée** : Utilisation de modèles de langage (LLM).
- **Tâches confiées à l'IA** :
  1. *Extraction* : Lire le texte libre du client et extraire (Produit + Quantité).
  2. *Matching / Clarification* : Si le produit n'est pas dans le catalogue, l'IA identifie la ligne comme "à clarifier".
  3. *Traduction* : Génération du devis en anglais si demandé.
  4. *Sécurité (R12)* : Détection des IBAN/RIB et des tentatives de modification de prix (Prompt Injection) pour les bloquer et alerter un humain.

### 4. Frontend (Tableau de Bord / Dashboard)
Pour afficher les KPI demandés (encours par stade, DSO simulé, devis générés/en attente) :
- **Outil proposé : Streamlit (Python)**.
- **Avantage** : Il permet de créer une interface web interactive en quelques lignes de code, connectée directement à notre base MySQL, ce qui est parfait pour un projet de 3 jours.

## Verification Plan

### Automated Tests
- **Test d'Idempotence** : Lancer le workflow n8n deux fois de suite. Vérifier dans la base de données qu'aucune relance ou devis n'a été créé en double.
- **Test des Soldes** : Script de vérification pour s'assurer que pour chaque facture, `Solde = Montant TTC - Somme(Paiements)`.

### Manual Verification
- Simulation d'un email client contenant un IBAN pour vérifier que notre filtre (ou l'IA) masque bien la donnée bancaire avant tout traitement.
- Vérification visuelle du Tableau de bord (Frontend) pour valider l'affichage des graphiques.
