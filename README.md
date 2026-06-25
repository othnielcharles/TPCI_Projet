# IT Parc - Gestion de Parc Informatique

Ce module Odoo 18 a été conçu pour TECHPARK CI afin de répondre aux 5 objectifs principaux :
- Centralisation
- Traçabilité
- Anticipation
- Reporting
- Pilotage

## Fonctionnalités

1. **Gestion des équipements** : Enregistrement de chaque équipement avec ses caractéristiques, un workflow à quatre étapes (Brouillon → Affecté → En maintenance → Retiré).
2. **Affectation aux employés** : Historique des affectations, wizard de réaffectation avec saisie de motif.
3. **Suivi des interventions** : Enregistrement de chaque maintenance (corrective ou préventive), calcul des durées et coûts, vue calendrier.
4. **Gestion des contrats** : Suivi des contrats fournisseurs, calcul automatique des jours restants avant expiration, wizard de renouvellement.
5. **Alertes automatiques** : Déclenchement automatique d'alertes via tâche planifiée (cron) pour les fins de garantie et de contrats.
6. **Import en masse** : Wizard d'importation CSV avec détection des doublons par numéro de série.
7. **Rapports PDF** : Fiche individuelle, inventaire complet, historique des maintenances par période.
8. **Exports Excel** : Téléchargement natif de 3 fichiers `.xlsx` avec `xlsxwriter` (couleurs conditionnelles, synthèses des coûts).
9. **Dashboard Dynamique OWL** : Tableau de bord natif intégré via le composant OWL 2, avec graphique Chart.js interactif et KPIs dynamiques récupérés par RPC.

## Installation

1. S'assurer que les modules natifs `hr, stock, purchase, account, maintenance, mail, contacts, web` sont disponibles.
2. Installer `xlsxwriter` dans votre environnement Python (`pip install xlsxwriter`).
3. Placer le dossier `it_parc` dans le dossier des addons.
4. Lancer Odoo avec l'option `-u it_parc` ou l'installer via l'interface "Applications".

## Sécurité
Deux groupes de sécurité sont implémentés :
- **IT Technicien** : Peut voir les équipements et créer des interventions.
- **IT Manager** : Accès complet à toutes les fonctionnalités et paramètres du module. Les administrateurs (root/admin) héritent automatiquement de ce groupe.

## Technologies Utilisées
- Odoo 18 Enterprise
- Python 3.11+
- OWL 2 (Odoo Web Library)
- Chart.js
- xlsxwriter pour l'export Excel natif.
