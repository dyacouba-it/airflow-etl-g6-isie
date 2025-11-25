# Transformation de Données avec Apache Airflow

**Projet M1 IBAM 2025 - Groupe 6 - Exercice 14**

Pipeline ETL (Extract, Transform, Load) entièrement automatisé orchestré par Apache Airflow, permettant la synchronisation de données depuis trois sources différentes (fichier CSV, base MySQL, base PostgreSQL) vers une base PostgreSQL cible unifiée, avec une interface web Flask moderne et un monitoring en temps réel via Prometheus et Grafana.

---

## Table des matières

- [Aperçu du projet](#aperçu-du-projet)
- [Architecture technique](#architecture-technique)
- [Fonctionnalités](#fonctionnalités)
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
- [Points forts et dépassements](#Points-forts-et-dépassements)
- [Auteurs](#auteurs)

---

## Aperçu du projet

### Objectif

Développer une solution ETL professionnelle qui :
- Extrait automatiquement des données depuis 3 sources hétérogènes
- Transforme et nettoie les données (normalisation, déduplication)
- Détecte intelligemment les changements (INSERT vs UPDATE)
- Synchronise vers une base de données unifiée
- Valide l'intégrité des données après chaque exécution
- Fournit une interface web moderne pour la gestion et le monitoring
- Offre un monitoring en temps réel des performances

### Cas d'usage

Ce projet répond aux besoins d'entreprises ayant :
- Des données d'employés dispersées dans plusieurs systèmes
- Un besoin de centralisation pour l'analyse et le reporting
- Des contraintes de synchronisation quotidienne
- Des exigences de traçabilité et d'audit

### Résultats attendus

Après démarrage, le système :
- Synchronise automatiquement **37 employés burkinabè** depuis 3 sources
- S'exécute quotidiennement à minuit (@daily)
- Maintient l'intégrité des données avec validation
- Fournit une interface web Flask interactive
- Affiche les métriques en temps réel sur Grafana

---

## Architecture technique

```
┌────────────────────────────────────────────────────────────────┐
│                      SOURCES DE DONNÉES                        │
├──────────────────┬──────────────────┬──────────────────────────┤
│  Fichier CSV     │   MySQL Source   │  PostgreSQL Source       │
│  (22 employés)   │   (8 employés)   │   (7 employés)           │
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
|                                       │   37→38 employés   │
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
                     (Interface principale)
```

### Composants principaux

| Composant | Rôle | Port | Données |
|-----------|------|------|---------|
| **Flask Web App** | Interface web interactive | 5000 | Dashboard + API REST |
| **Apache Airflow Webserver** | Interface orchestration | 8080 | - |
| **Apache Airflow Scheduler** | Orchestrateur de tâches | - | - |
| **PostgreSQL Source** | Base de données source | 5432 | 7 employés |
| **MySQL Source** | Base de données source | 3306 | 8 employés |
| **Fichier CSV** | Fichier source | - | 22 employés |
| **PostgreSQL Target** | Base de données cible | 5433 | 37 employés (unifiés) |
| **Prometheus** | Collecte de métriques | 9090 | Métriques système |
| **Grafana** | Visualisation | 3000 | Dashboards |

---

## Fonctionnalités

### Interface Web Flask (Nouvelle fonctionnalité)

#### Dashboard interactif
- Vue d'ensemble en temps réel (37 employés)
- Graphique en donut de répartition par source
- KPI (Key Performance Indicators)
- Dernière synchronisation affichée

#### Gestion des données
- **Onglet "Base unifiée"** : Consultation des données synchronisées
- **Onglet "Employés par source"** : Gestion CRUD par source
  - CSV : Lecture seule
  - MySQL : Create, Read, Update, Delete
  - PostgreSQL : Create, Read, Update, Delete
- **Onglet "Test ETL"** : Formulaires d'ajout rapide
- **Onglet "API"** : Documentation des endpoints REST

#### API REST complète
- `GET /api/stats` - Statistiques globales
- `GET /api/employes` - Liste employés unifiés
- `GET /api/sources/{source}/employes` - Employés par source
- `POST /api/sources/{source}/employes` - Ajouter
- `PUT /api/sources/{source}/employes/{id}` - Modifier
- `DELETE /api/sources/{source}/employes/{id}` - Supprimer
- `POST /api/etl/trigger` - Déclencher l'ETL
- `GET /api/etl/status` - Statut ETL

### Pipeline ETL

#### Extraction parallèle
- Extraction simultanée depuis 3 sources différentes
- Gestion des erreurs par source indépendante
- Validation des schémas de données

#### Transformation intelligente
- Normalisation des emails (minuscules, trim)
- Conversion des types de données
- Nettoyage des doublons (dernière occurrence conservée)
- Enrichissement avec métadonnées (source, timestamps)

#### Synchronisation différentielle
- Détection automatique INSERT vs UPDATE
- Comparaison par email (clé naturelle)
- Mise à jour uniquement des champs modifiés
- Conservation de l'historique avec timestamps

#### Validation post-synchronisation
- Vérification du nombre d'enregistrements
- Contrôle de cohérence des données
- Génération de rapports d'exécution

### Automatisation complète

#### Provisioning automatique
- Bases de données initialisées avec 37 employés de test
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
- Nombre d'enregistrements synchronisés
- Temps de disponibilité (uptime)

#### Dashboards en temps réel
- Actualisation automatique toutes les 5 secondes
- Alertes visuelles (rouge/vert)
- Graphiques d'évolution temporelle
- Interface en français

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

# Lancer l'environnement
start.bat  # Windows
# OU
./start.sh  # Linux/macOS
```

### Méthode 2 : Depuis une archive
```bash
# Extraire l'archive
unzip airflow-etl-g6-isie.zip
cd airflow-etl-g6-isie

# Lancer l'environnement
start.bat  # Windows
```

### Processus de démarrage

Le script `start.bat` effectue automatiquement :

1. **Vérification de Docker** (5 secondes)
2. **Nettoyage des conteneurs existants** (10 secondes)
3. **Démarrage des conteneurs** (30 secondes)
   - Application Flask
   - 3 bases de données (MySQL, 2x PostgreSQL)
   - Apache Airflow (webserver + scheduler)
   - Prometheus + Grafana
4. **Initialisation** (120 secondes avec barre de progression)
   - Création des tables
   - Insertion des 37 employés de test
   - Configuration d'Airflow
   - Configuration de Grafana
5. **Configuration des connexions Airflow** (10 secondes)
6. **Vérification de Flask** (10 secondes)

**Durée totale : environ 2 minutes**

### Sortie attendue

```
════════════════════════════════════════════════════════════════════════
                        INSTALLATION TERMINÉE                            
════════════════════════════════════════════════════════════════════════

 ACCÈS AUX INTERFACES
 ────────────────────────────────────────────────────────────────────

  Interface Web
  http://localhost:5000
  → Dashboard interactif avec déclenchement ETL

  Apache Airflow
  http://localhost:8080
  Identifiants : admin / admin
  → Pipeline ETL (DAG "etl_employe_sync" déjà activé)

  Prometheus (Métriques)
  http://localhost:9090
  → Collecte de métriques système

  Grafana (Monitoring)
  http://localhost:3000
  Identifiants : admin / admin
  → Dashboards de visualisation

 DONNÉES DE TEST : 38 employés (23 CSV + 8 MySQL + 7 PostgreSQL)

 Le projet est prêt. Bon test !
```

---


## SCÉNARIO DE TEST COMPLET

> **Cette section décrit le scénario de test recommandé pour démontrer le fonctionnement complet du pipeline ETL.**

### Vue d'ensemble

Le scénario se déroule en **4 étapes** :

1. **Vérifier l'état initial** (38 employés répartis)
2. **Ajouter/Modifier un employé** (démonstration du CRUD)
3. **Lancer l'ETL** (synchronisation)
4. **Vérifier la synchronisation** (38 employés synchronisés)

**Durée totale : 5 minutes**

---

### ÉTAPE 1 : Vérifier l'état initial

#### Via l'interface Flask

```
1. Ouvrir http://localhost:5000
2. Observer le dashboard :
   • Total : 38 employés
   • Répartition : 23 CSV + 8 MySQL + 7 PostgreSQL
   • Graphique en donut montrant la distribution
```

#### Via la ligne de commande

```bash
# Vérifier via l'API
curl http://localhost:5000/api/stats

# Vérifier la source CSV
type data\data.csv

# Vérifier la source MySQL
docker exec mysql-source mysql -u mysqluser -pmysqlpass source_db \
  -e "SELECT COUNT(*) AS total FROM employes_mysql;"
# Résultat attendu : 8

# Vérifier la source PostgreSQL
docker exec postgres-source psql -U sourceuser -d source_db \
  -c "SELECT COUNT(*) AS total FROM employes_source;"
# Résultat attendu : 7

# Vérifier la base unifiée
docker exec postgres-target psql -U targetuser -d target_db \
  -c "SELECT COUNT(*) AS total FROM employes_unified;"
# Résultat attendu : 37
```

**État initial confirmé : 38 employés (23 + 8 + 7)**

---

### ÉTAPE 2 : Ajouter ou modifier un employé

#### Option A : Via l'interface Flask

```
1. Aller sur l'onglet "Test ETL"
2. Remplir le formulaire MySQL ou PostgreSQL :
   • Nom : Test Professeur
   • Email : prof@test.bf
   • Département : Évaluation
   • Salaire : 950000
   • Date d'embauche : 25-11-2025
3. Cliquer sur "Ajouter dans MySQL"
4. Observer le message de succès
5. Observer : Le compteur MySQL augmente immédiatement (8 → 9)
```

#### Option B : Via la ligne de commande

```bash
# Ajouter un employé dans MySQL
docker exec mysql-source mysql -u mysqluser -pmysqlpass source_db -e \
  "INSERT INTO employes_mysql (nom, email, departement, salaire, date_embauche) \
   VALUES ('Test Professeur', 'prof@test.bf', 'Évaluation', 950000, '2025-11-25');"

# Vérifier l'ajout
docker exec mysql-source mysql -u mysqluser -pmysqlpass source_db \
  -e "SELECT COUNT(*) FROM employes_mysql;"
# Résultat attendu : 9 (était 8)
```

#### Option C : Modifier un employé existant

```
1. Aller sur l'onglet "Employés par source"
2. Sélectionner "MySQL" ou "PostgreSQL"
3. Cliquer sur "Modifier" pour un employé
4. Changer le salaire (ex: +100000 FCFA)
5. Enregistrer
6. Observer la modification immédiate dans la source
```

**Vérification importante :**

```bash
# La base unifiée N'A PAS encore changé
docker exec postgres-target psql -U targetuser -d target_db \
  -c "SELECT COUNT(*) FROM employes_unified;"
# Résultat : 38 (inchangé)

# Cela prouve que la synchronisation n'est PAS automatique
```

---

### ÉTAPE 3 : Lancer l'ETL

#### Via l'interface Flask

```
1. Cliquer sur "Lancer ETL" (bouton principal en haut)
2. Observer le message : "ETL déclenché avec succès"
3. Observer : Barre de progression ou message "Synchronisation en cours..."
4. Attendre 15 secondes
5. Observer le message : "Synchronisation terminée !"
6. Observer : Les compteurs se mettent à jour automatiquement
   • Total : 38 → 39
   • MySQL : 8 → 9
   • Le graphique se met à jour 
```

#### Alternative : Via Apache Airflow

```
1. Ouvrir http://localhost:8080
2. Se connecter : admin / admin
3. Trouver le DAG "etl_employe_sync"
4. Cliquer sur le bouton ▶ (Trigger DAG)
5. Aller dans "Graph View"
6. Observer l'exécution en temps réel
   • extract_csv → vert
   • extract_mysql → vert
   • extract_postgresql → vert
   • transform_clean → vert
   • load_to_target → vert
   • validate_sync → vert
7. Toutes les tâches deviennent vertes = succès
```

**Durée : 15 secondes**

---

### ÉTAPE 4 : Vérifier la synchronisation

#### Via l'interface Flask

```
1. Retourner sur l'onglet "Tableau de bord"
2. Observer :
   • Total = 39 employés (38 + 1) 
   • MySQL = 9 employés (8 + 1) 
   • Graphique mis à jour 
3. Aller sur l'onglet "Base unifiée"
4. Observer : Le nouvel employé "Test Professeur" apparaît dans la liste 
```

#### Via la ligne de commande

```bash
# Compteur total
docker exec postgres-target psql -U targetuser -d target_db \
  -c "SELECT COUNT(*) FROM employes_unified;"
# Résultat : 39 (était 38) 

# Trouver le nouvel employé
docker exec postgres-target psql -U targetuser -d target_db \
  -c "SELECT id, nom, email, source FROM employes_unified WHERE nom LIKE '%Professeur%';"
# Résultat attendu :
#  id |       nom       |      email      | source
# ----+-----------------+-----------------+--------
#  38 | Test Professeur | prof@test.bf    | MySQL

# Vérifier la répartition par source
docker exec postgres-target psql -U targetuser -d target_db \
  -c "SELECT source, COUNT(*) FROM employes_unified GROUP BY source ORDER BY source;"
# Résultat attendu :
#    source    | count
# -------------+-------
#  CSV         |    23
#  MySQL       |     9    ← était 8
#  PostgreSQL  |     7
```

**SYNCHRONISATION RÉUSSIE !**

---

### Résumé du scénario

  Étape               | État MySQL     | État Base Unifiée      | Action    |
|-------|-------------|----------------|------------------------------------|
| **1. État initial** | 8 employés     | 38 employés            | Vérifier  |
| **2. Ajout**        | 9 employés (+1)| 38 employés (inchangé) |  Ajouter  |
| **3. ETL**          | 9 employés     | En synchronisation...  | Lancer    |
| **4. Après ETL**    | 9 employés     | 39 employés (+1)       | Vérifier  |

### Ce que prouve ce scénario

1. Les sources sont **indépendantes** (MySQL, PostgreSQL)
2. On peut **ajouter/modifier** des données dans les sources
3. L'ETL **détecte les changements**
4. La synchronisation **fonctionne correctement**
5. La **traçabilité** est assurée (colonne `source`)
6. Le système est **complet et opérationnel**

---


## Guide d'utilisation

### Démarrage rapide (2 minutes)

```bash
# Windows
start.bat

# Linux/macOS
./start.sh
```

### Interface Flask (RECOMMANDÉE)

#### Premier accès

```
1. Ouvrir http://localhost:5000
2. Explorer le dashboard :
   • KPI avec 37 employés
   • Graphique de répartition
   • Dernière synchronisation
```

#### Déclencher l'ETL

```
1. Cliquer sur le bouton "Lancer ETL" (en haut)
2. Attendre 15 secondes
3. Observer les compteurs se mettre à jour
4. Message de succès : "Synchronisation terminée !"
```

#### Ajouter un employé

```
1. Aller sur l'onglet "Test ETL"
2. Choisir MySQL ou PostgreSQL
3. Remplir le formulaire
4. Cliquer sur "Ajouter"
5. Lancer l'ETL pour synchroniser
```

#### Modifier/Supprimer un employé

```
1. Aller sur l'onglet "Employés par source"
2. Sélectionner MySQL ou PostgreSQL
3. Cliquer sur "Modifier" ou "Supprimer"
4. Lancer l'ETL pour synchroniser
```

### Interface Airflow (Alternative)

#### Premier accès

```
1. Ouvrir http://localhost:8080
2. Se connecter : admin / admin
3. Le DAG "etl_employe_sync" est déjà ACTIVÉ (toggle bleu)
```

#### Déclencher manuellement

```
1. Cliquer sur le bouton ▶ (Trigger DAG)
2. Aller dans "Graph View"
3. Observer l'exécution (toutes les tâches deviennent vertes)
4. Durée : ~15 secondes
```

#### Comprendre le Graph View

```
extract_csv          ──┐
extract_mysql        ──┼──→ transform_clean ──→ load_to_target ──→ validate_sync
extract_postgresql   ──┘

• Vert = Succès
• Rouge = Échec
• Orange = En cours
• Bleu foncé = Pas encore exécuté
```

---

## Monitoring et visualisation

### Grafana

#### Accès

```
URL : http://localhost:3000
Identifiants : admin / admin
```

#### Dashboard pré-configuré

Le dashboard "Monitoring ETL Airflow" affiche :
- **Service Status** : État de Prometheus (Up/Down)
- **Scrape Duration** : Temps de collecte des métriques
- **Samples Scraped** : Nombre d'échantillons par seconde
- **Uptime** : Durée de fonctionnement

Actualisation : Automatique toutes les 5 secondes

### Prometheus

#### Accès

```
URL : http://localhost:9090
```

#### Métriques disponibles

- `up` : État des services (1 = up, 0 = down)
- `prometheus_target_scrapes_total` : Nombre total de collectes
- `prometheus_target_scrape_duration_seconds` : Durée des collectes

---

## Commandes de vérification

### Via l'API Flask

```bash
# Statistiques globales
curl http://localhost:5000/api/stats

# Liste des employés unifiés
curl http://localhost:5000/api/employes

# Employés d'une source
curl http://localhost:5000/api/sources/mysql/employes

# Déclencher l'ETL
curl -X POST http://localhost:5000/api/etl/trigger
```

### Via les bases de données

#### Source CSV

```bash
# Windows
type data\data.csv

# Linux/macOS
cat data/data.csv
```

#### Source MySQL

```bash
# Compter les employés
docker exec mysql-source mysql -u mysqluser -pmysqlpass source_db \
  -e "SELECT COUNT(*) AS total FROM employes_mysql;"

# Afficher les employés
docker exec mysql-source mysql -u mysqluser -pmysqlpass source_db \
  -e "SELECT * FROM employes_mysql;"
```

#### Source PostgreSQL

```bash
# Compter les employés
docker exec postgres-source psql -U sourceuser -d source_db \
  -c "SELECT COUNT(*) AS total FROM employes_source;"

# Afficher les employés
docker exec postgres-source psql -U sourceuser -d source_db \
  -c "SELECT * FROM employes_source;"
```

#### Base unifiée (Target)

```bash
# Compter les employés
docker exec postgres-target psql -U targetuser -d target_db \
  -c "SELECT COUNT(*) AS total FROM employes_unified;"

# Répartition par source
docker exec postgres-target psql -U targetuser -d target_db \
  -c "SELECT source, COUNT(*) FROM employes_unified GROUP BY source ORDER BY source;"

# Afficher tous les employés avec leur source
docker exec postgres-target psql -U targetuser -d target_db \
  -c "SELECT id, nom, email, source FROM employes_unified ORDER BY source, nom;"

# Chercher un employé spécifique
docker exec postgres-target psql -U targetuser -d target_db \
  -c "SELECT * FROM employes_unified WHERE nom LIKE '%Ouedraogo%';"
```

### Vérifier les services Docker

```bash
# État de tous les conteneurs
docker-compose ps

# Logs de Flask
docker logs flask-app --tail 50

# Logs d'Airflow
docker logs airflow-scheduler --tail 50

# Ressources utilisées
docker stats

# Santé des conteneurs
docker ps --format "table {{.Names}}\t{{.Status}}"
```

---

## Maintenance

### Scripts disponibles

#### start.bat
Démarre tout l'environnement (première installation ou redémarrage)
```cmd
start.bat
```

#### stop.bat
Arrête tous les conteneurs proprement
```cmd
stop.bat
```

#### clean.bat
Supprime tous les conteneurs, volumes et images
```cmd
clean.bat
```

#### verify.bat
Vérifie que les données sont correctement synchronisées
```cmd
verify.bat
```

### Commandes utiles

```bash
# Redémarrer un service spécifique
docker-compose restart flask-app

# Voir les logs en temps réel
docker-compose logs -f flask-app

# Reconstruire un conteneur
docker-compose up -d --build flask-app

# Nettoyer les ressources Docker inutilisées
docker system prune -a

# Sauvegarder les données
docker exec postgres-target pg_dump -U targetuser target_db > backup.sql

# Restaurer les données
cat backup.sql | docker exec -i postgres-target psql -U targetuser -d target_db
```

---

## Structure du projet

```
airflow-etl-g6-isie/
│
├── dags/                          # DAGs Apache Airflow
│   └── etl_sync_dag.py           # Pipeline ETL principal
│
├── backend/                       # Application Flask
│   ├── app.py                    # Point d'entrée Flask
│   ├── routes/                   # Endpoints API
│   │   ├── stats.py             # Statistiques
│   │   ├── employes.py          # Employés unifiés
│   │   ├── sources.py           # Sources de données
│   │   └── etl.py               # Déclenchement ETL
│   ├── services/                # Logique métier
│   │   ├── database.py          # Connexions DB
│   │   └── airflow.py           # Client Airflow
│   └── requirements.txt         # Dépendances Python
│
├── frontend/                      # Interface web
│   ├── static/
│   │   ├── css/                 # Styles
│   │   │   ├── variables.css    # Variables CSS
│   │   │   ├── base.css        # Styles de base
│   │   │   ├── layout.css      # Mise en page
│   │   │   ├── components.css  # Composants
│   │   │   └── responsive.css  # Responsive
│   │   └── js/                  # Scripts
│   │       ├── config.js        # Configuration
│   │       ├── api.js          # Client API
│   │       ├── ui.js           # Gestion UI
│   │       ├── charts.js       # Graphiques
│   │       ├── employees.js    # Gestion employés
│   │       ├── etl.js          # Gestion ETL
│   │       └── main.js         # Point d'entrée
│   └── templates/
│       └── index.html           # Page principale
│
├── data/                          # Données sources
│   └── data.csv                  # 22 employés CSV
│
├── init-scripts/                  # Scripts d'initialisation
│   ├── init-mysql.sql            # Init MySQL (8 employés)
│   └── init-postgres-source.sql  # Init PostgreSQL (7 employés)
│
├── prometheus/                    # Configuration Prometheus
│   └── prometheus.yml
│
├── grafana/                       # Configuration Grafana
│   ├── provisioning/
│   │   ├── datasources/
│   │   │   └── prometheus.yml
│   │   └── dashboards/
│   │       ├── dashboard.yml
│   │       └── monitoring-etl.json
│
├── docker-compose.yml            # Orchestration Docker
├── Dockerfile.flask              # Image Flask
├── start.bat                     # Script de démarrage Windows
├── start.sh                      # Script de démarrage Linux/macOS
├── stop.bat (stop.sh)            # Script d'arrêt
├── clean.bat (clean.sh)          # Script de nettoyage
├── verify.bat (verify.sh)        # Script de vérification
└── README.md                     # Cette documentation
```

---

## Technologies utilisées

### Backend
- **Python 3.11** - Langage principal
- **Apache Airflow 2.7.3** - Orchestration ETL
- **Flask 3.0** - Application web et API REST
- **Pandas 2.0** - Manipulation de données
- **SQLAlchemy 2.0** - ORM

### Bases de données
- **PostgreSQL 15** - Base source et cible
- **MySQL 8.0** - Base source

### Frontend
- **HTML5 / CSS3** - Structure et styles
- **JavaScript (Vanilla)** - Interactivité
- **Chart.js** - Visualisations

### Monitoring
- **Prometheus** - Collecte de métriques
- **Grafana** - Dashboards

### Infrastructure
- **Docker** - Conteneurisation
- **Docker Compose** - Orchestration

### Dépendances Python

```python
apache-airflow==2.7.3       # Orchestration
flask==3.0.0                # Framework web
pandas>=2.0.0               # Manipulation de données
sqlalchemy>=2.0.0           # ORM
pymysql>=1.1.0              # MySQL
psycopg2-binary>=2.9.0      # PostgreSQL
prometheus-client>=0.19.0   # Export métriques
requests>=2.31.0            # Client HTTP
python-dotenv>=1.0.0        # Variables d'environnement
```

---

## Dépannage

### Problèmes courants

#### Flask n'est pas accessible

**Symptômes :**
- http://localhost:5000 ne répond pas
- Message "This site can't be reached"

**Solutions :**
```bash
# Vérifier si Flask est démarré
docker ps | findstr flask

# Voir les logs Flask
docker logs flask-app

# Redémarrer Flask
docker-compose restart flask-app

# Vérifier le port
netstat -an | findstr ":5000"
```

#### Le DAG n'apparaît pas dans Airflow

**Causes possibles :**
- Le scheduler n'a pas encore scanné le dossier `dags/`
- Erreur de syntaxe dans le fichier Python

**Solutions :**
```bash
# Vérifier les logs du scheduler
docker logs airflow-scheduler --tail 50

# Redémarrer le scheduler
docker-compose restart airflow-scheduler

# Attendre 30 secondes puis rafraîchir Airflow
```

#### Les données ne se synchronisent pas

**Vérifications :**
1. Le DAG est-il activé ? (toggle bleu dans Airflow)
2. Le DAG s'est-il exécuté ? (vérifier dans Grid view)
3. Toutes les tâches sont-elles vertes ?
4. Y a-t-il des erreurs dans les logs ?

**Solutions :**
```bash
# Vérifier les logs de la tâche load_to_target
# Dans Airflow : DAG → Tâche → Log

# Vérifier les connexions
docker exec airflow-webserver airflow connections list

# Vérifier les données dans les sources
docker exec mysql-source mysql -u mysqluser -pmysqlpass source_db \
  -e "SELECT COUNT(*) FROM employes_mysql;"
```

#### Erreur "port already in use"

**Cause :** Un autre service utilise le port.

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

#### Grafana affiche "No data"

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

#### L'ajout d'employé échoue

**Symptômes :**
- Message d'erreur dans Flask
- L'employé n'apparaît pas dans la source

**Solutions :**
```bash
# Vérifier les logs Flask
docker logs flask-app --tail 50

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

---

## Points forts et dépassements

### Points forts du projet

**Automatisation totale (100%)**
- Zéro configuration manuelle requise
- Provisioning automatique de tous les composants
- DAG activé par défaut au démarrage
- Scripts de maintenance complets

**Interface web moderne**
- Application Flask avec dashboard interactif
- API REST complète (10+ endpoints)
- CRUD complet sur MySQL et PostgreSQL
- Design professionnel et responsive

**Architecture professionnelle**
- 9 conteneurs Docker orchestrés
- Séparation claire des environnements (source/target)
- Frontend modulaire (8 fichiers JS)
- Backend structuré (routes + services)

**Pipeline ETL robuste**
- Extraction parallèle depuis 3 sources hétérogènes
- Transformation avec nettoyage et validation
- Synchronisation différentielle (INSERT/UPDATE)
- Gestion d'erreurs par source
- 37 employés burkinabè synchronisés

**Observabilité complète**
- Métriques Prometheus en temps réel
- Dashboards Grafana en français
- Logs détaillés pour chaque tâche
- Validation automatique post-exécution

**Documentation exhaustive**
- README de 1000+ lignes
- Scénario de test détaillé en 4 étapes
- Guide d'utilisation complet
- Commandes de vérification pour toutes les sources

**Reproductibilité garantie**
- Fonctionne sur Windows, macOS, Linux
- Environnement isolé dans Docker
- Versions fixes des dépendances
- Temps de démarrage prévisible (~2 min)

### Dépassement des attentes

Le projet va au-delà de l'exercice 14 en intégrant :
- Interface web Flask moderne (non demandée)
- API REST complète (10+ endpoints)
- CRUD complet sur les sources
- Provisioning automatique (Grafana, Prometheus)
- Dashboard personnalisé
- Validation post-ETL
- Scripts de maintenance
- Documentation niveau production

### Démonstration recommandée

**Durée totale : 5 minutes**

#### 1. Démarrage (30 secondes)
```
• Exécuter start.bat
• Montrer la barre de progression
• Attendre le message "Installation terminée"
```

#### 2. Interface Flask (2 minutes)
```
• Ouvrir http://localhost:5000
• Montrer le dashboard avec 37 employés
• Aller sur "Test ETL"
• Ajouter un employé (Test Professeur)
• Observer : Compteur MySQL passe de 8 → 9
• Cliquer sur "Lancer ETL"
• Attendre 15 secondes
• Observer : Total passe de 37 → 38
• Aller sur "Base unifiée"
• Montrer "Test Professeur" synchronisé
```

#### 3. Vérification ligne de commande (1 minute)
```bash
# Montrer la répartition
docker exec postgres-target psql -U targetuser -d target_db \
  -c "SELECT source, COUNT(*) FROM employes_unified GROUP BY source;"

# CSV: 22, MySQL: 9 (était 8), PostgreSQL: 7
```

#### 4. Airflow (1 minute)
```
• Ouvrir http://localhost:8080 (admin/admin)
• Montrer le DAG déjà activé
• Montrer le Graph View avec toutes les tâches vertes
• Expliquer le pipeline Extract → Transform → Load
```

#### 5. Monitoring (30 secondes)
```
• Ouvrir Grafana http://localhost:3000 (admin/admin)
• Montrer le dashboard en français
• Expliquer les métriques Prometheus
```

**Points à souligner :**
- 0 configuration manuelle
- Interface web moderne
- CRUD complet
- Synchronisation automatique
- Traçabilité (colonne `source`)
- Documentation complète

---

## 👥 Auteurs

**Projet M1 IBAM 2025 - Groupe 6**

### Membres du groupe

- [DAO Yacouba]
- [DA Sansan Nilce]
- [KABORE Kiswendsida Inès Odette]
- [SAWADOGO Joëlle Anisaah]


### Encadrement

- **Professeur :** [Fadel GUY]
- **Institution :** IBAM - Institut Burkinabè des Arts et Métiers
- **Année académique :** 2024-2025
- **Module :** Développement à Base de Composants et Services Web

### Contexte académique

**Exercice 14 :** Transformation de Données avec Apache Airflow

**Objectif :** Apprendre à utiliser Apache Airflow pour orchestrer un workflow ETL de
transformation de données.

**Tâche :** Créer un workflow Airflow pour extraire des données d’un ficher csv et de deux
bases de données source (Mysql, Postgresql), les transformer, et les charger dans une autre
base de données (Postgresql).
- Installez et configurez Apache Airflow.
- Connectez-vous aux bases de données source et cible.
- Créez une transformation pour extraire les données de la base de données
source.
- Ajoutez des étapes de comparaison et de mise à jour pour synchroniser les
données dans la base de données cible.
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

- [ ] Support de sources supplémentaires (API REST)
- [ ] Gestion des données sensibles (secrets vault)
- [ ] Clustering Airflow pour haute disponibilité
- [ ] Authentification utilisateurs

---

**Dernière mise à jour :** Novembre 2025  
**Version :** 1.0.0  
**Statut :** Production-ready
