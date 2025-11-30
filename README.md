# Transformation de Données avec Apache Airflow

**Projet M1 IBAM 2025 - Groupe 6 ISIE - Exercice 14**

Pipeline ETL (Extract, Transform, Load) entièrement automatisé orchestré par Apache Airflow, permettant la synchronisation de données depuis trois sources différentes (fichier CSV, base MySQL, base PostgreSQL) vers une base PostgreSQL cible unifiée, avec gestion intelligente du cycle de vie des données (soft delete), une interface web Flask moderne et un monitoring en temps réel via Prometheus et Grafana.

---

## Table des matières

- [Aperçu du projet](#aperçu-du-projet)
- [Architecture technique](#architecture-technique)
- [Fonctionnalités](#fonctionnalités)
- [Gestion du cycle de vie - Soft Delete](#-gestion-du-cycle-de-vie---soft-delete)
- [Prérequis](#prérequis)
- [Installation rapide](#installation-rapide)
- [Scénario de test](#-scénario-de-test-complet)
- [Guide d'utilisation](#guide-dutilisation)
- [Monitoring et visualisation](#monitoring-et-visualisation)
- [Commandes de vérification](#commandes-de-vérification)
- [Maintenance](#maintenance)
- [Structure du projet](#structure-du-projet)
- [Technologies utilisées](#technologies-utilisées)
- [Dépannage](#dépannage)
- [Points forts et dépassements](#points-forts-et-dépassements)
- [Auteurs](#auteurs)

---

## Aperçu du projet

### Objectif

Développer une solution ETL professionnelle qui :
- Extrait automatiquement des données depuis 3 sources hétérogènes
- Transforme et nettoie les données (normalisation, déduplication)
- Détecte intelligemment les changements (INSERT vs UPDATE)
- Gère le cycle de vie des données avec soft delete (préservation de l'historique)
- Synchronise vers une base de données unifiée avec traçabilité complète
- Valide l'intégrité des données après chaque exécution
- Fournit une interface web moderne pour la gestion et le monitoring
- Offre un monitoring en temps réel des performances

### Cas d'usage

Ce projet répond aux besoins d'entreprises ayant :
- Des données d'employés dispersées dans plusieurs systèmes
- Un besoin de centralisation pour l'analyse et le reporting
- Des contraintes de synchronisation quotidienne
- Des exigences de traçabilité et d'audit (conservation de l'historique)
- Un besoin de distinguer employés actifs et inactifs

### Résultats attendus

Après démarrage, le système :
- Synchronise automatiquement 200 employés depuis 3 sources
- S'exécute quotidiennement à minuit (@daily)
- Maintient l'intégrité des données avec validation
- Gère intelligemment les suppressions (soft delete)
- Fournit une interface web Flask interactive avec filtrage par statut
- Affiche les métriques en temps réel sur Grafana

---

## Architecture technique

### Schéma d'architecture complet

```
┌────────────────────────────────────────────────────────────────┐
│                      SOURCES DE DONNÉES                        │
├──────────────────┬──────────────────┬──────────────────────────┤
│  Fichier CSV     │   MySQL Source   │  PostgreSQL Source       │
│  (80 employés)   │   (50 employés)   │   (70 employés)           │
└────────┬─────────┴────────┬─────────┴──────────┬───────────────┘
         │                  │                    │
         └──────────────────┼────────────────────┘
                            │
                        ____|____
                        |       |
                        |       |
________________________|       |
|                               |
|                               |
|                               |
|                    ┌──────----▼──-──┐
|                    │ Apache Airflow │
|                    │   Scheduler    │
|                    │    (ETL Core)  │
|                    └───────┬────────┘
|                            │
|      ┌─────────────────────┼────────────────────┐
|      │                     │                    │
|  ┌───▼─────┐          ┌────▼─────┐         ┌────▼────┐
|  │ Extract │          │Transform │         │  Load   │
|  │Parallel │   ─→     │ & Clean  │   ─→    │ & Sync  │
|  └─────────┘          └──────────┘         └────┬────┘
|                                                 │
|                                       ┌─────────▼──────────┐
|                                       │ PostgreSQL Target  │
|                                       │(employes_unified)  │
|                                       │   200 employés   │
|                                       └─────────┬──────────┘
|                                                 │
|                             ┌───────────────────┼──────────────────┐
|                             │                   │                  │
|                       ┌─────▼─────┐      ┌──────▼──────┐    ┌──────▼──────┐
|                       │   Flask   │      │ Prometheus  │    │   Grafana   │
|_______________________│  Web App  │      │ (Métriques) │    │ (Dashboards)│
                        │ localhost │      └─────────────┘    └─────────────┘
                        │   :5000   │
                        └───────────┘
                   (Interface  principale)

```

### Composants principaux

| Composant | Rôle | Port | Données | Capacités |
|-----------|------|------|---------|-----------|
| **Flask Web App** | Interface web interactive | 5000 | Dashboard + API REST | CRUD, Soft Delete, Filtres |
| **Apache Airflow Webserver** | Interface orchestration | 8080 | - | - |
| **Apache Airflow Scheduler** | Orchestrateur de tâches | - | - | - |
| **PostgreSQL Source** | Base de données source | 5432 | 70 employés | CRUD Complet |
| **MySQL Source** | Base de données source | 3306 | 50 employés | CRUD Complet |
| **Fichier CSV** | Fichier source | - | 80 employés | READ ONLY |
| **PostgreSQL Target** | Base de données cible | 5433 | 200 employés (unifiés) | READ ONLY (via Flask) |
| **Prometheus** | Collecte de métriques | 9090 | Métriques système | - |
| **Grafana** | Visualisation | 3000 | Dashboards | - |

### Schéma des données unifiées

```sql
CREATE TABLE employes_unified (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    departement VARCHAR(255),
    salaire NUMERIC(10, 2),
    date_embauche DATE,                
    source VARCHAR(50) NOT NULL,          
    statut VARCHAR(20) DEFAULT 'actif',   
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

**Colonnes clés :**
- `email` : Clé naturelle pour la synchronisation
- `source` : Traçabilité de l'origine des données
- `statut` : Gestion du cycle de vie (actif/inactif)
- `date_embauche` : Date d'entrée dans l'entreprise 
- `created_at` / `updated_at` : Timestamps de suivi

---

## Fonctionnalités

### Interface Web Flask 

#### Dashboard interactif
- Vue d'ensemble en temps réel (39 employés)
- Graphique en donut de répartition par source
- KPI (Key Performance Indicators) avec distinction actif/inactif
- Dernière synchronisation affichée
- Filtres par statut (Tous, Actifs, Inactifs) 

#### Gestion des données

**Onglet "Tableau de bord"**
- Vue statistique globale
- Répartition par source
- Filtrage par statut (actif/inactif)

**Onglet "Base unifiée"**
- Consultation des données synchronisées (READ ONLY)
- Filtres dynamiques par statut
- Affichage de la date d'embauche 
- Pagination intelligente

**Onglet "Employés par source"**
- Vue statistique globale
- CSV : Lecture seule
- MySQL : Create, Read, Update, Soft Delete
- PostgreSQL : Create, Read, Update, Soft Delete
- Modification du statut via formulaire*

**Onglet "Test ETL"**
- Formulaires d'ajout rapide avec tous les champs
- Bouton pour lancer l'ETL et la synchronisation

**Onglet "API"**
- Documentation complète des 21 endpoints
- Exemples de code avec curl
- Workflow ETL expliqué

#### API REST complète (21 endpoints)

**Statistiques (3 endpoints)**
- `GET /api/stats` - Statistiques globales (total, par statut)
- `GET /api/sources/stats` - Compteurs par source
- `GET /api/stats/sources` - Répartition pour graphiques

**Base Unifiée (2 endpoints)**
- `GET /api/employes?statut=actif&limit=100` - Liste avec filtres
- `GET /api/employes/:id` - Détails d'un employé

**CSV Source (1 endpoint)**
- `GET /api/employes?source=CSV` - Employés CSV (lecture seule)

**MySQL Source (5 endpoints)**
- `GET /api/sources/mysql/employes` - Liste employés MySQL
- `GET /api/sources/mysql/employes/:id` - Détails
- `POST /api/sources/mysql/employes` - Ajouter (statut='actif' par défaut)
- `PUT /api/sources/mysql/employes/:id` - Modifier (avec statut)
- `DELETE /api/sources/mysql/employes/:id` - Soft Delete (statut='inactif')

**PostgreSQL Source (5 endpoints)**
- `GET /api/sources/postgresql/employes` - Liste employés PostgreSQL
- `GET /api/sources/postgresql/employes/:id` - Détails
- `POST /api/sources/postgresql/employes` - Ajouter (statut='actif' par défaut)
- `PUT /api/sources/postgresql/employes/:id` - Modifier (avec statut)
- `DELETE /api/sources/postgresql/employes/:id` - Soft Delete (statut='inactif')

**ETL (4 endpoints)**
- `POST /api/etl/trigger` - Déclencher l'ETL manuellement
- `GET /api/etl/status` - Statut du DAG Airflow
- `GET /api/etl/history` - Historique des exécutions
- `GET /api/etl/last-sync` - Dernière synchronisation 

### Pipeline ETL

#### Extraction parallèle
- Extraction simultanée depuis 3 sources différentes
- Gestion des erreurs par source indépendante
- Validation des schémas de données
- Préservation du champ statut

#### Transformation intelligente
- Normalisation des emails (minuscules, trim)
- Conversion des types de données
- Gestion du statut par défaut ('actif' si non spécifié)
- Nettoyage des doublons (dernière occurrence conservée)
- Enrichissement avec métadonnées (source, timestamps)
- Validation de la date d'embauche

#### Synchronisation différentielle
- Détection automatique INSERT vs UPDATE
- Comparaison par email (clé naturelle)
- Mise à jour du statut lors de la synchronisation
- Mise à jour uniquement des champs modifiés
- Conservation de l'historique avec timestamps

#### Validation post-synchronisation
- Vérification du nombre d'enregistrements
- Contrôle de cohérence du statut
- Contrôle de cohérence des données
- Génération de rapports d'exécution

### Automatisation complète

#### Provisioning automatique
- Bases de données initialisées avec 200 employés de test
- Statuts initialisés correctement (200 actifs, 0 inactif)
- Connexions Airflow créées automatiquement
- Application Flask démarrée automatiquement
- Datasource Prometheus configuré automatiquement
- Dashboard Grafana provisionné automatiquement
- DAG activé par défaut au premier démarrage

#### Configuration zéro
- Aucune intervention manuelle requise
- Démarrage en une seule commande (`start.bat`)
- Scripts de maintenance inclus

### Monitoring et observabilité

#### Métriques collectées
- Statut des services (up/down)
- Durée d'exécution des tâches ETL
- Nombre d'enregistrements synchronisés (par statut)
- Temps de disponibilité (uptime)

#### Dashboards en temps réel
- Actualisation automatique toutes les 5 secondes
- Alertes visuelles (rouge/vert)
- Graphiques d'évolution temporelle

---

##  Gestion du cycle de vie - Soft Delete

### Concept du Soft Delete

**Soft Delete**  
Quand on supprime un employé (physiquement) dans la base de données source (mysql ou postgresql),
au lieu de le supprimer physiquement les enregistrements de la base unifiée, nous **changeons simplement le statut** de l'employé de `'actif'` à `'inactif'` :
- Préservation complète de l'historique
- Traçabilité totale (audit trail)
- Possibilité de réactivation
- Rapports historiques complets


#### Exemple dans l'API REST

**Suppression d'un employé MySQL :**

```bash
# Appel API
curl -X DELETE http://localhost:5000/api/sources/mysql/employes/5

# Requête SQL exécutée en arrière-plan
UPDATE employes_mysql SET statut = 'inactif', updated_at = NOW() WHERE id = 5;

# Résultat
{
  "success": true,
  "message": "Employé Fatoumata Traoré marqué comme inactif (soft delete)"
}
```

### Filtrage par statut

#### Dans l'interface web

**Onglet "Tableau de bord" :**
- Boutons de filtre : **Tous** | **Actifs** | **Inactifs**
- Compteurs distincts : " 200 employés actifs" / "4 employés inactifs"

**Onglet "Base unifiée" :**
- Filtres identiques pour la consultation
- Affichage dynamique selon le filtre sélectionné

#### Via l'API REST

**Obtenir uniquement les employés actifs :**
```bash
curl "http://localhost:5000/api/employes?statut=actif&limit=100"
```

**Obtenir uniquement les employés inactifs :**
```bash
curl "http://localhost:5000/api/employes?statut=inactif&limit=100"
```

**Obtenir tous les employés (actifs + inactifs) :**
```bash
curl "http://localhost:5000/api/employes?limit=100"
```

### Synchronisation ETL avec soft delete

Le pipeline ETL respecte le statut lors de la synchronisation :

1. **Extraction** : Récupération de tous les employés (actifs + inactifs)
2. **Transformation** : Préservation du champ `statut`
3. **Load** : 
   - Si l'employé existe déjà → UPDATE avec mise à jour du statut
   - Si l'employé est nouveau → INSERT avec `statut = 'actif'` par défaut

  **Puis synchroniser via ETL :**
    ```bash
    curl -X POST http://localhost:5000/api/etl/trigger
    ```
---

## Prérequis

### Logiciels requis

#### Docker Desktop
**Version minimale :** 20.10+

**Installation :**
- **Windows** : https://docs.docker.com/desktop/install/windows-install/
  - Activer WSL 2 (Windows Subsystem for Linux)
  - Redémarrer après installation
- **macOS** : https://docs.docker.com/desktop/install/mac-install/
- **Linux** : https://docs.docker.com/engine/install/

**Vérification :**
```cmd
docker --version
docker-compose --version
```

#### Git 
Pour cloner le projet : https://git-scm.com/downloads

### Configuration système

| Ressource | Minimum | Recommandé |
|-----------|---------|------------|
| **RAM** | 8 GB | 16 GB |
| **Espace disque** | 10 GB | 20 GB |
| **Processeur** | 4 cœurs | 8 cœurs |
| **Système d'exploitation** | Windows 10, macOS 10.15, Ubuntu 20.04 | Versions récentes |

### Ports requis

Les ports suivants doivent être **disponibles** :
- `3000` - Grafana
- `3306` - MySQL Source
- `5000` - Flask Web App
- `5432` - PostgreSQL Source
- `5433` - PostgreSQL Target
- `8080` - Airflow Webserver
- `9090` - Prometheus

**Vérifier la disponibilité :**
```cmd
netstat -an | findstr "3000 3306 5000 5432 5433 8080 9090"
```

Si un port est occupé, arrêtez le service correspondant.

---

## Installation rapide

### Méthode 1 : Depuis GitHub
```bash
# Cloner le repository
git clone https://github.com/dyacouba-it/airflow-etl-g6-isie.git
cd airflow-etl-g6-isie

# Démarrer tous les services
docker-compose up -d

# Attendre 2 minutes le démarrage complet
```

### Méthode 2 : Script automatique (Windows)
```cmd
# Exécuter start.bat
start.bat

# Le script fait tout automatiquement :
# - Vérifie Docker
# - Lance docker-compose
# - Attend la disponibilité des services
# - Affiche les URLs d'accès
```

### Méthode 3 : Script automatique (Linux/macOS)
```bash
# Rendre le script exécutable
chmod +x start.sh

# Exécuter
./start.sh
```

### Vérification du démarrage

**Services à vérifier :**
```bash
docker-compose ps
```

**Résultat attendu :**
```
NAME                  STATUS        PORTS
airflow-scheduler     Up            -
airflow-webserver     Up            0.0.0.0:8080->8080/tcp
flask-api             Up            0.0.0.0:5000->5000/tcp
grafana               Up            0.0.0.0:3000->3000/tcp
mysql-source          Up            0.0.0.0:3306->3306/tcp
postgres-source       Up            0.0.0.0:5432->5432/tcp
postgres-target       Up            0.0.0.0:5433->5432/tcp
prometheus            Up            0.0.0.0:9090->9090/tcp
```

**Accès aux interfaces :**
- **Flask App** : http://localhost:5000 (Interface principale)
- **Airflow** : http://localhost:8080 (admin / admin)
- **Grafana** : http://localhost:3000 (admin / admin)
- **Prometheus** : http://localhost:9090

---

## Scénario de test complet

### Test 1 : Vérifier le soft delete

**Durée : 3 minutes**

#### Étape 1 : État initial (30 secondes)
```bash
# Ouvrir Flask
http://localhost:5000

# Onglet "Tableau de bord"
# Observer :  200 employés actifs, 0 inactif

# Cliquer sur "Actifs"
# Compter :  200 employés actifs affichés
```

#### Étape 2 : Supprimer un employé (soft delete) (1 minute)
```bash
# Onglet "Employés par source" → MySQL
# Trouver l'employé "Safiatou Sankara"
# Cliquer sur "Supprimer"
# Confirmer

# Message attendu : "✓ Employé marqué comme inactif (soft delete)"

# Vérifier dans MySQL
docker exec mysql-source mysql -u mysqluser -pmysqlpass source_db \
  -e "SELECT id, nom, email FROM employes_mysql WHERE id = 1;"

# Résultat : 0'
```

#### Étape 3 : Synchroniser vers la base unifiée (1 minute)
```bash
# Onglet "Test ETL"
# Cliquer sur "Lancer ETL et Synchroniser"
# Attendre 15 secondes

# Message : "Synchronisation terminée !"
```

#### Étape 4 : Vérification finale (30 secondes)
```bash
# Onglet "Tableau de bord"
# Cliquer sur "Actifs"
# Observer : 199 employés actifs (était 200 avant)

# Cliquer sur "Inactifs"
# Observer : 1 employé inactif (était 0 avant)
# Trouver "Safiatou Sankara" dans la liste

# Vérification SQL
docker exec postgres-target psql -U targetuser -d target_db \
  -c "SELECT nom, email, statut FROM employes_unified WHERE email = 'safiatou.sankara@entreprise.bf'';"

# Résultat : statut = 'inactif'
```

### Test 2 : Ajouter un employé et déclencher l'ETL

**Durée : 2 minutes**

#### Étape 1 : Ajouter un employé (30 secondes)
```bash
# Interface Flask → Onglet "Test ETL"
# Section "Ajouter dans MySQL Source"

Nom             : Test Professeur
Email           : prof.test@ibam.bf
Département     : Enseignement
Salaire         : 950000
Date d'embauche : 2024-11-01

# Cliquer sur "Ajouter dans MySQL"
# Message : "Employé ajouté avec succès dans MySQL"
# Observer : Compteur MySQL augmente
```

#### Étape 2 : Déclencher l'ETL (1 minute)
```bash
# Cliquer sur "Lancer ETL et Synchroniser"
# Observer la barre de progression (15 secondes)
# Message : "Synchronisation terminée !"
```

#### Étape 3 : Vérification (30 secondes)
```bash
# Onglet "Tableau de bord"
# Observer : Total passe de 200 → 201 employés
# Cliquer sur "Actifs"
# Observer :  200 employés actifs (l'employé ajouté a statut='actif' par défaut)

# Onglet "Base unifiée"
# Chercher "Test Professeur"
# Vérifier : source = MySQL, statut = actif

# Ligne de commande
docker exec postgres-target psql -U targetuser -d target_db \
  -c "SELECT * FROM employes_unified WHERE email = 'prof.test@ibam.bf';"

# Vérifier la présence avec statut = 'actif' 
```

### Test 3 : Filtrage par statut via API

**Durée : 1 minute**

```bash
# Obtenir uniquement les employés actifs
curl "http://localhost:5000/api/employes?statut=actif"

# Compter : devrait retourner 200 employés

# Obtenir uniquement les employés inactifs
curl "http://localhost:5000/api/employes?statut=inactif"

# Compter : devrait retourner 1 employé

# Obtenir tous les employés
curl "http://localhost:5000/api/employes"

# Compter : devrait retourner 201 employés (200 + 1)
```

### Test 4 : Réactivation d'un employé

**Durée : 2 minutes**

```bash
# Réactiver "Abdoulaye Ouedraogo" via API
curl -X PUT http://localhost:5000/api/sources/mysql/employes/1 \
  -H "Content-Type: application/json" \
  -d '{
    "nom": "Abdoulaye Ouedraogo",
    "email": "abdoulaye@example.com",
    "departement": "Informatique",
    "salaire": 850000,
    "date_embauche": "2023-01-15",
    "statut": "actif"
  }'

# Message : "Employé mis à jour avec succès"

# Synchroniser
curl -X POST http://localhost:5000/api/etl/trigger

# Attendre 15 secondes

# Vérifier
curl "http://localhost:5000/api/employes?statut=actif" | jq '.data[] | select(.email == "abdoulaye@example.com")'

# Résultat : Abdoulaye Ouedraogo apparaît avec statut = 'actif' ✅
```

---

## Guide d'utilisation

### Interface Flask (Port 5000)

#### Onglet "Tableau de bord"

**Vue d'ensemble :**
- **KPI Total** : Nombre total d'employés (actifs + inactifs)
- **KPI CSV** : Employés provenant du fichier CSV
- **KPI MySQL** : Employés de la base MySQL
- **KPI PostgreSQL** : Employés de la base PostgreSQL

**Filtres par statut :**
- **Tous** : Affiche tous les employés (actifs + inactifs)
- **Actifs** : Affiche uniquement les employés en poste
- **Inactifs** : Affiche uniquement les employés partis

**Graphique :**
- Donut chart montrant la répartition par source
- Actualisation automatique après synchronisation

#### Onglet "Base unifiée"

**Consultation :**
- Table en lecture seule avec pagination
- Colonnes : ID, Nom, Email, Département, Salaire, Date embauche, Source, Statut
- Filtres : Tous / Actifs / Inactifs

**Actions disponibles :**
- Consultation uniquement (READ ONLY)
- Pagination (10 employés par page)
- Filtrage dynamique par statut
- Pas de modification directe (passer par les sources)

#### Onglet "Employés par source"

**Sélection de la source :**
- **CSV** : Lecture seule
- **MySQL** : CRUD complet 
- **PostgreSQL** : CRUD complet

**Opérations MySQL/PostgreSQL :**
- **Ajouter** : Formulaire avec tous les champs (statut='actif' par défaut)
- **Modifier** : Édition complète incluant le statut
- **Supprimer** : Soft delete (changement statut → 'inactif')

#### Onglet "Test ETL"

**Formulaires d'ajout rapide :**
- Section MySQL avec tous les champs
- Section PostgreSQL avec tous les champs
- Bouton "Lancer ETL" centralisé

**Workflow recommandé :**
1. Ajouter un ou plusieurs employés
2. Observer l'incrémentation des compteurs
3. Cliquer sur "Lancer ETL"
4. Attendre 15 secondes
5. Vérifier la synchronisation

#### Onglet "API"

**Documentation complète :**
- 21 endpoints REST documentés
- Paramètres détaillés (limit, offset, statut, source)
- 3 exemples de code avec curl
- Workflow ETL expliqué en 5 étapes

### Airflow (Port 8080)

**Accès :** http://localhost:8080 (admin / admin)

**DAG `etl_employes` :**
- **État** : Activé par défaut (auto_start)
- **Schedule** : `@daily` (minuit chaque jour)
- **Tâches** :
  1. `extract_csv_data` (vert)
  2. `extract_mysql_data` (vert)
  3. `extract_postgresql_data` (vert)
  4. `transform_data` (vert)
  5. `detect_deletions` (vert)
  6. `load_data` (vert)
  7. `validate_load` (vert)

**Déclenchement manuel :**
1. Cliquer sur "Trigger DAG" (bouton Play ▶️)
2. Attendre ~15 secondes
3. Vérifier le statut (toutes les tâches en vert)

### Grafana (Port 3000)

**Accès :** http://localhost:3000 (admin / admin)

**Dashboard provisionné :**
- Nom : "ETL Monitoring Dashboard"
- Métriques en temps réel
- Actualisation : 5 secondes
- Interface en français

**Métriques affichées :**
- Statut des services (Up/Down)
- Temps de réponse
- Nombre de requêtes
- Utilisation des ressources

---

## Commandes de vérification

### Vérifier les données dans les sources 

#### Fichier CSV
```bash
# Voir le contenu du CSV
docker exec airflow-scheduler cat /opt/airflow/data/data.csv

# Compter les employés
docker exec airflow-scheduler sh -c "tail -n +2 /opt/airflow/data/data.csv | wc -l"
# Résultat attendu (si fichier initial) : 80
```

#### MySQL Source
```bash
# Connexion à MySQL
docker exec -it mysql-source mysql -u mysqluser -pmysqlpass source_db

# Requêtes utiles
SELECT COUNT(*) FROM employes_mysql;        # Résultat attendu (si base initiale) : 50

SELECT id, nom, email FROM employes_mysql ORDER BY id;

# Quitter
exit;
```

#### PostgreSQL Source
```bash
# Connexion à PostgreSQL
docker exec -it postgres-source psql -U sourceuser -d source_db

# Requêtes utiles
SELECT COUNT(*) FROM employes_mysql;   # Résultat attendu (si base initiale) :50                   

SELECT id, nom, email FROM employes_mysql ORDER BY id;

# Quitter
\q
```

#### PostgreSQL Target (Base unifiée)
```bash
# Connexion à PostgreSQL Target
docker exec -it postgres-target psql -U targetuser -d target_db

# Statistiques globales
SELECT COUNT(*) FROM employes_unified;                           
SELECT COUNT(*) FROM employes_unified WHERE statut = 'actif';      
SELECT COUNT(*) FROM employes_unified WHERE statut = 'inactif';  

# Répartition par source
SELECT source, COUNT(*) as total 
FROM employes_unified 
GROUP BY source 
ORDER BY source;

# Résultat attendu (si base initiale)
+--------------+-------+
| source       | total |
+--------------+-------+
| CSV          |    80 |
| mysql        |    50 |
| postgresql   |    70 |
+--------------+-------+

# Répartition par statut
SELECT statut, COUNT(*) as total 
FROM employes_unified 
GROUP BY statut;

# Résultat attendu (si base initiale)
+---------+-------+
| statut  | total |
+---------+-------+
| actif   |   200 |
| inactif |     0 |
+---------+-------+

# Répartition croisée (source × statut)
SELECT source, statut, COUNT(*) as total 
FROM employes_unified 
GROUP BY source, statut 
ORDER BY source, statut;

# Employés inactifs (détails)
SELECT id, nom, email, source, updated_at 
FROM employes_unified 
WHERE statut = 'inactif' 
ORDER BY updated_at DESC;

# Dernière synchronisation
SELECT MAX(updated_at) as derniere_synchro 
FROM employes_unified;

# Quitter
\q
```

### Vérifier les logs

```bash
# Logs Flask
docker logs flask-api --tail 50 -f

# Logs Airflow Scheduler
docker logs airflow-scheduler --tail 50 -f

# Logs tous les services
docker-compose logs --tail=50 -f

# Logs d'un conteneur spécifique avec timestamps
docker logs --timestamps <nom-conteneur> --tail 100
```

### Tester l'API REST

```bash
# Statistiques globales
curl http://localhost:5000/api/stats

# Liste des employés actifs (avec pagination)
curl "http://localhost:5000/api/employes?statut=actif&limit=300&offset=0"

# Liste des employés inactifs
curl "http://localhost:5000/api/employes?statut=inactif"

# Employés d'une source spécifique
curl "http://localhost:5000/api/employes?source=csv&limit=50" #csv
curl "http://localhost:5000/api/employes?source=mysql&limit=50" #mysql
curl "http://localhost:5000/api/employes?source=postgresql&limit=50" #postgresql

# Détails d'un employé
curl http://localhost:5000/api/employes/1

# Ajouter un employé dans MySQL
curl -X POST http://localhost:5000/api/sources/mysql/employes -H "Content-Type: application/json" -d "{ \"nom\": \"Test API\", \"email\": \"test.api@example.com\", \"departement\": \"IT\", \"salaire\": 800000, \"date_embauche\": \"2024-11-28\" }"


# Modifier un employé d'une source (changer le salaire)
curl -X PUT http://localhost:5000/api/sources/mysql/employes/2 -H "Content-Type: application/json" -d "{ \"nom\": \"Safiatou Sankara\", \"email\": \"safiatou.sankara@entreprise.bf\", \"departement\": \"Finance\", \"salaire\": 950000, \"date_embauche\": \"2019-05-18\" }"

# Soft Delete dans la source (cela fera changer le statut à "Inactif" après le lancement de l'ETL
curl -X DELETE http://localhost:5000/api/sources/mysql/employes/1

# Déclencher l'ETL
curl -X POST http://localhost:5000/api/etl/trigger

# Dernière synchronisation
curl http://localhost:5000/api/etl/last-sync
```

---

## Maintenance

### Arrêter tous les services
```bash
docker-compose down
```

### Redémarrer tous les services
```bash
docker-compose restart
```

### Redémarrer un service spécifique
```bash
docker-compose restart flask-api
docker-compose restart airflow-scheduler
```

### Nettoyer et repartir de zéro
```bash
# Arrêter et supprimer tout (volumes inclus)
docker-compose down -v

# Supprimer les images
docker-compose down --rmi all

# Redémarrer proprement
docker-compose up -d
```

### Sauvegarder la base unifiée
```bash
# Exporter en SQL
docker exec postgres-target pg_dump -U targetuser target_db > backup_$(date +%Y%m%d).sql

# Exporter en CSV
docker exec postgres-target psql -U targetuser -d target_db \
  -c "COPY employes_unified TO STDOUT WITH CSV HEADER" > backup_$(date +%Y%m%d).csv
```

### Restaurer la base unifiée
```bash
# Depuis un fichier SQL
cat backup_20241128.sql | docker exec -i postgres-target psql -U targetuser -d target_db
```

### Mise à jour du code Flask
```bash
# Modifier le code dans app/

# Reconstruire l'image Flask
docker-compose build flask-api

# Redémarrer le service
docker-compose up -d flask-api
```

## Technologies utilisées

### Backend
- **Python 3.11** : Langage principal
- **Apache Airflow 2.8.0** : Orchestration ETL
- **Flask 3.0** : Framework web
- **PostgreSQL 15** : Base de données cible + source
- **MySQL 8.0** : Base de données source

### Frontend
- **HTML5 / CSS3** : Structure et styles
- **JavaScript (Vanilla)** : Logique applicative
- **Chart.js 4.4** : Graphiques interactifs

### Monitoring
- **Prometheus 2.48** : Collecte de métriques
- **Grafana 10.2** : Visualisation

### Conteneurisation
- **Docker 24.0+** : Conteneurisation
- **Docker Compose 2.23+** : Orchestration

### Bibliothèques Python principales
```
apache-airflow==2.8.0
Flask==3.0.0
psycopg2-binary==2.9.9
pymysql==1.1.0
pandas==2.1.4
prometheus-client==0.19.0
```

---

## Dépannage

### Problème : Les conteneurs ne démarrent pas

**Symptômes :**
- `docker-compose up -d` échoue
- Erreurs de ports déjà utilisés
- Erreurs de mémoire insuffisante

**Solutions :**
```bash
# 1. Vérifier Docker
docker --version

# 2. Vérifier les ports occupés
netstat -an | findstr "3000 3306 5000 5432 5433 8080 9090"

# 3. Arrêter les processus conflictuels
# Windows : taskkill /PID <PID> /F
# Linux/macOS : kill -9 <PID>

# 4. Augmenter la mémoire Docker
# Docker Desktop → Settings → Resources → Memory : 8 GB minimum

# 5. Nettoyer Docker
docker system prune -a
docker volume prune
```

### Problème : Airflow ne démarre pas

**Symptômes :**
- Interface Airflow inaccessible sur le port 8080
- Erreurs dans les logs `docker logs airflow-scheduler`

**Solutions :**
```bash
# Vérifier les logs
docker logs airflow-scheduler --tail 100

# Erreur commune : "Database not initialized"
docker exec airflow-scheduler airflow db init

# Créer l'utilisateur admin si nécessaire
docker exec airflow-scheduler airflow users create \
  --username admin \
  --firstname Admin \
  --lastname User \
  --role Admin \
  --email admin@example.com \
  --password admin

# Redémarrer Airflow
docker-compose restart airflow-scheduler airflow-webserver
```

### Problème : Le DAG ne s'exécute pas

**Symptômes :**
- DAG reste en rouge ou gris
- Tâches ne se déclenchent pas
- Erreurs dans les logs des tâches

**Solutions :**
```bash
# 1. Vérifier que le DAG est activé
# Interface Airflow → DAGs → Vérifier le toggle (ON)

# 2. Déclencher manuellement
# Interface Airflow → Cliquer sur le bouton Play ▶️

# 3. Vérifier les logs de la tâche échouée
# Interface Airflow → DAG → Graph → Cliquer sur la tâche → Logs

# 4. Vérifier les connexions Airflow
docker exec airflow-scheduler airflow connections list

# 5. Tester la connexion PostgreSQL
docker exec airflow-scheduler airflow connections test postgres_target

# 6. Relancer le scheduler
docker-compose restart airflow-scheduler
```

### Problème : Flask retourne une erreur 500

**Symptômes :**
- Pages blanches ou erreurs 500
- API ne répond pas

**Solutions :**
```bash
# Vérifier les logs Flask
docker logs flask-api --tail 50 -f

# Erreur commune : Connexion DB échouée
# Vérifier que PostgreSQL et MySQL sont bien démarrés
docker-compose ps | grep -E "mysql|postgres"

# Tester les connexions
docker exec flask-api python -c "
import pymysql
conn = pymysql.connect(host='mysql-source', user='mysqluser', password='mysqlpass', database='source_db')
print('MySQL OK')
conn.close()
"

# Redémarrer Flask
docker-compose restart flask-api
```

### Problème : Les ports sont déjà utilisés

**Symptômes :**
- Erreur : `Bind for 0.0.0.0:5000 failed: port is already allocated`

**Solutions :**
```bash
# Identifier le processus
netstat -ano | findstr ":5000"
netstat -ano | findstr ":8080"

# Arrêter le processus (Windows)
taskkill /PID <PID> /F

# OU modifier le port dans docker-compose.yml
ports:
  - "5001:5000"  # Utiliser 5001 au lieu de 5000
```

### Problème : Grafana affiche "No data"

**Causes possibles :**
- Prometheus non connecté
- Datasource non configuré
- Requête Prometheus invalide

**Solutions :**
```bash
# Vérifier Prometheus
curl http://localhost:9090/-/healthy

# Tester une requête
curl "http://localhost:9090/api/v1/query?query=up"

# Dans Grafana
# Configuration → Data sources → Prometheus → Test
```

### Problème : L'ajout d'employé échoue

**Symptômes :**
- Message d'erreur dans Flask
- L'employé n'apparaît pas dans la source

**Solutions :**
```bash
# Vérifier les logs Flask
docker logs flask-api --tail 50

# Vérifier la connexion à la base
docker exec mysql-source mysql -u mysqluser -pmysqlpass -e "SELECT 1;"

# Vérifier les données dans le formulaire (champs requis)
```

### Commandes de diagnostic

```bash
# État de tous les services
docker-compose ps

# Logs de tous les services
docker-compose logs --tail=50

# Logs d'un service spécifique
docker logs <nom-conteneur> --tail 100 -f

# Ressources utilisées
docker stats

# Espace disque
docker system df

# Santé des conteneurs
docker ps --format "table {{.Names}}\t{{.Status}}"

# Nettoyer les ressources inutilisées
docker system prune -a
```

## Auteurs

**Projet M1 IBAM 2025 - Groupe 6**

### Membres du groupe

- DAO Yacouba
- DA Sansan Nilce
- KABORE Kiswendsida Inès Odette
- SAWADOGO Joëlle Anisaah

### Encadrement

- **Professeur :** Fadel GUY
- **Institution :** IBAM - Institut Burkinabè des Arts et Métiers
- **Année académique :** 2024-2025
- **Module :** Développement à Base de Composants et Services Web

### Contexte académique

**Exercice 14 :** Transformation de Données avec Apache Airflow

**Objectif :** Apprendre à utiliser Apache Airflow pour orchestrer un workflow ETL de
transformation de données.

**Tâche :** Créer un workflow Airflow pour extraire des données d'un ficher csv et de deux
bases de données source (Mysql, Postgresql), les transformer, et les charger dans une autre
base de données (Postgresql).
- Installez et configurez Apache Airflow.
- Connectez-vous aux bases de données source et cible.
- Créez une transformation pour extraire les données de la base de données source.
- Ajoutez des étapes de comparaison et de mise à jour pour synchroniser les données dans la base de données cible.
- Vérifiez les résultats dans la base de données cible.
- Observer les métriques sur Grafana

---

## Licence

Projet académique - Groupe 6 - ISIE IBAM 2025

---

## Support

Pour toute question concernant ce projet :

- **Issues GitHub :** https://github.com/dyacouba-it/airflow-etl-g6-isie/issues
- **Email :** [yacouba.info@gmail.com]
- **Documentation Airflow :** https://airflow.apache.org/docs/
- **Documentation Flask :** https://flask.palletsprojects.com/
- **Documentation Docker :** https://docs.docker.com/

---

## Améliorations futures

### V2.0 (suggestions)

- [ ] Dashboard analytique avancé (taux de rotation, statistiques départements)
- [ ] Notifications par email lors des changements de statut
- [ ] API GraphQL pour requêtes complexes
- [ ] Gestion des données sensibles (secrets vault)
- [ ] Clustering Airflow pour haute disponibilité
- [ ] Pipeline CI/CD automatisé

---

**Dernière mise à jour :** Novembre 2025  
**Version :** 1.0.0  
**Statut :** Production-ready
