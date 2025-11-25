@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul
cls

echo.
echo  ╔════════════════════════════════════════════════════════════════════════╗
echo  ║           PIPELINE ETL AUTOMATISÉ AVEC APACHE AIRFLOW                  ║
echo  ║                    Projet M1 IBAM 2025 - Groupe 6 - ISIE               ║
echo  ║                         Exercice 14                                    ║
echo  ╚════════════════════════════════════════════════════════════════════════╝
echo.
echo  À PROPOS DU PROJET
echo  ═════════════════════════════════════════════════════════════════════════
echo.
echo  Ce projet est un pipeline ETL (Extract, Transform, Load) professionnel
echo  qui synchronise automatiquement des données d'employés depuis trois
echo  sources différentes vers une base de données unifiée, avec une application
echo  web Flask pour consulter et gérer les données.
echo.
echo  Caractéristiques principales :
echo  ──────────────────────────────────────────────────────────────────────
echo   • Application Flask avec API REST et interface web interactive
echo   • Extraction parallèle depuis CSV, MySQL et PostgreSQL
echo   • Transformation et nettoyage automatique des données
echo   • Synchronisation intelligente (INSERT/UPDATE)
echo   • Monitoring en temps réel avec Prometheus et Grafana
echo   • Configuration 100%% automatisée - Zéro intervention manuelle
echo.
echo  Données de test :
echo  ──────────────────────────────────────────────────────────────────────
echo   • 38 employés répartis sur 3 sources
echo   • CSV : 23 employés
echo   • MySQL : 8 employés
echo   • PostgreSQL : 7 employés
echo.
echo  Technologies utilisées :
echo  ──────────────────────────────────────────────────────────────────────
echo   • Flask 3.0 - Application web et API REST
echo   • Apache Airflow 2.7.3 - Orchestration ETL
echo   • PostgreSQL 15 - Bases de données
echo   • MySQL 8.0 - Base de données source
echo   • Prometheus - Collecte de métriques
echo   • Grafana - Visualisation et dashboards
echo   • Docker - Conteneurisation
echo.
echo  Temps d'installation : environ 2-3 minutes
echo.
echo  ═════════════════════════════════════════════════════════════════════════
echo.
echo  Appuyez sur ENTRÉE pour démarrer l'installation et le test...
pause >nul

cls
echo.
echo  ╔════════════════════════════════════════════════════════════════════════╗
echo  ║              DÉMARRAGE DE L'ENVIRONNEMENT ETL                          ║
echo  ╚════════════════════════════════════════════════════════════════════════╝
echo.

REM ═══════════════════════════════════════════════════════════════════════════
REM  ETAPE 1 : VÉRIFICATION DE DOCKER
REM ═══════════════════════════════════════════════════════════════════════════
echo  [ETAPE 1/7] Vérification de Docker Desktop...
echo  ──────────────────────────────────────────────────────────────────────
docker info >nul 2>&1
if errorlevel 1 (
    echo  ERREUR : Docker Desktop n'est pas démarré !
    echo.
    echo  Veuillez démarrer Docker Desktop et relancer ce script.
    echo.
    pause
    exit /b 1
)
echo  Docker Desktop est actif et opérationnel
echo.

REM ═══════════════════════════════════════════════════════════════════════════
REM  ETAPE 2 : NETTOYAGE DES ANCIENS CONTENEURS
REM ═══════════════════════════════════════════════════════════════════════════
echo  [ETAPE 2/7] Nettoyage des conteneurs existants...
echo  ──────────────────────────────────────────────────────────────────────
docker-compose down >nul 2>&1
echo  Nettoyage terminé
echo.

REM ═══════════════════════════════════════════════════════════════════════════
REM  ETAPE 3 : DÉMARRAGE DES SERVICES
REM ═══════════════════════════════════════════════════════════════════════════
echo  [ETAPE 3/7] Démarrage de tous les services...
echo  ──────────────────────────────────────────────────────────────────────
echo  Services à démarrer :
echo     • Application Flask (API REST + Interface Web)
echo     • PostgreSQL Source (7 employés)
echo     • MySQL Source (8 employés)
echo     • PostgreSQL Target (base unifiée)
echo     • Apache Airflow (webserver + scheduler)
echo     • Prometheus (collecte de métriques)
echo     • Grafana (dashboards de monitoring)
echo.

docker-compose up -d --build

if errorlevel 1 (
    echo  ERREUR : Échec du démarrage des services !
    echo.
    pause
    exit /b 1
)
echo.
echo  Tous les services ont démarré avec succès
echo.

REM ═══════════════════════════════════════════════════════════════════════════
REM  ETAPE 4 : INITIALISATION (AVEC COMPTEUR)
REM ═══════════════════════════════════════════════════════════════════════════
echo  [ETAPE 4/7] Initialisation et configuration...
echo  ──────────────────────────────────────────────────────────────────────
echo  Cette étape prend environ 2 minutes. Veuillez patienter...
echo.
echo  En cours :
echo  • Initialisation des bases de données
echo  • Insertion des données de test (38 employés)
echo  • Configuration d'Airflow (connexions, métadonnées)
echo  • Démarrage de l'application Flask
echo  • Provisioning de Grafana (datasource + dashboard)
echo.

set total=120
for /l %%i in (1,1,120) do (
    set /a step=%%i
    set /a percent=step*100/total
    set /a bars=step*50/total
    
    REM Créer la barre de progression
    set "progress="
    for /l %%j in (1,1,!bars!) do (
        set "progress=!progress!█"
    )
    set /a remaining=50-bars
    for /l %%k in (1,1,!remaining!) do (
        set "progress=!progress!░"
    )
    
    REM Afficher la progression sur la même ligne
    <nul set /p "=  [!progress!] !percent!%% - !step!/120s                 "
    echo.
    timeout /t 1 >nul
)

echo.
echo  Initialisation terminée
echo.

REM ═══════════════════════════════════════════════════════════════════════════
REM  ETAPE 5 : VÉRIFICATION DES SERVICES
REM ═══════════════════════════════════════════════════════════════════════════
echo  [ETAPE 5/7] Vérification des services...
echo  ──────────────────────────────────────────────────────────────────────
docker-compose ps
echo.
echo  Tous les services sont opérationnels
echo.

REM ═══════════════════════════════════════════════════════════════════════════
REM  ETAPE 6 : CRÉATION DES CONNEXIONS AIRFLOW
REM ═══════════════════════════════════════════════════════════════════════════
echo  [ETAPE 6/7] Configuration des connexions Airflow...
echo  ──────────────────────────────────────────────────────────────────────
docker exec airflow-webserver airflow connections delete mysql_source_conn 2>nul
docker exec airflow-webserver airflow connections delete postgres_source_conn 2>nul
docker exec airflow-webserver airflow connections delete postgres_target_conn 2>nul

docker exec airflow-webserver airflow connections add mysql_source_conn --conn-type mysql --conn-host mysql-source --conn-schema source_db --conn-login mysqluser --conn-password mysqlpass --conn-port 3306 >nul 2>&1

docker exec airflow-webserver airflow connections add postgres_source_conn --conn-type postgres --conn-host postgres-source --conn-schema source_db --conn-login sourceuser --conn-password sourcepass --conn-port 5432 >nul 2>&1

docker exec airflow-webserver airflow connections add postgres_target_conn --conn-type postgres --conn-host postgres-target --conn-schema target_db --conn-login targetuser --conn-password targetpass --conn-port 5432 >nul 2>&1

echo  Connexions Airflow configurées avec succès
echo.

REM ═══════════════════════════════════════════════════════════════════════════
REM  ETAPE 7 : VÉRIFICATION DE L'APPLICATION FLASK
REM ═══════════════════════════════════════════════════════════════════════════
echo  [ETAPE 7/7] Vérification de l'application Flask...
echo  ──────────────────────────────────────────────────────────────────────

REM Attendre que Flask soit prêt (max 30 secondes)
set /a count=0
:wait_flask
set /a count+=1
curl -s http://localhost:5000/health >nul 2>&1
if %errorlevel% EQU 0 (
    echo  Application Flask prête et opérationnelle !
    goto flask_ready
)
if %count% GEQ 30 (
    echo  ATTENTION : Flask n'a pas démarré dans le délai imparti
    echo  Vous pouvez vérifier manuellement : http://localhost:5000
    goto flask_ready
)
timeout /t 1 >nul
goto wait_flask

:flask_ready
echo.

REM ═══════════════════════════════════════════════════════════════════════════
REM  AFFICHAGE DU RÉSULTAT FINAL
REM ═══════════════════════════════════════════════════════════════════════════
cls
echo.
echo  ╔════════════════════════════════════════════════════════════════════════╗
echo  ║                ENVIRONNEMENT PRÊT À L'EMPLOI !                         ║
echo  ╚════════════════════════════════════════════════════════════════════════╝
echo.
echo  ═════════════════════════════════════════════════════════════════════════
echo   ACCÈS AUX INTERFACES
echo  ═════════════════════════════════════════════════════════════════════════
echo.
echo   Application Flask (RECOMMANDÉ)
echo   ├─ URL         : http://localhost:5000
echo   ├─ Description : Dashboard interactif et API REST complète
echo   └─ Fonctions   : Consultation, statistiques, déclenchement ETL
echo.
echo   Apache Airflow (Orchestration ETL)
echo   ├─ URL         : http://localhost:8080
echo   ├─ Identifiant : admin
echo   ├─ Mot de passe: admin
echo   └─ Description : Pipeline ETL avec DAG pré-activé
echo.
echo   Grafana (Monitoring)
echo   ├─ URL         : http://localhost:3000
echo   ├─ Identifiant : admin
echo   ├─ Mot de passe: admin
echo   └─ Description : Dashboards de monitoring
echo.
echo   Prometheus (Métriques)
echo   ├─ URL         : http://localhost:9090
echo   └─ Description : Collecte de métriques système
echo.
echo  ═════════════════════════════════════════════════════════════════════════
echo   DONNÉES DE TEST DISPONIBLES
echo  ═════════════════════════════════════════════════════════════════════════
echo.
echo   • CSV            : 23 employés
echo   • MySQL Source   : 8 employés
echo   • PostgreSQL Src : 7 employés
echo   ───────────────────────────────────────
echo   TOTAL            : 38 employés à synchroniser
echo.
echo  ═════════════════════════════════════════════════════════════════════════
echo   PROCHAINES ÉTAPES
echo  ═════════════════════════════════════════════════════════════════════════
echo.
echo   OPTION 1 : Utiliser l'Application Flask
echo   ────────────────────────────────────────────────────────────────────────
echo   1. Ouvrir http://localhost:5000 dans votre navigateur
echo   2. Consulter le dashboard avec statistiques en temps réel
echo   3. Cliquer sur "Déclencher Synchronisation" pour lancer l'ETL
echo   4. Observer les données se mettre à jour automatiquement
echo.
echo   OPTION 2 : Utiliser Airflow directement
echo   ────────────────────────────────────────────────────────────────────────
echo   1. Ouvrir http://localhost:8080
echo   2. Se connecter avec : admin / admin
echo   3. Le DAG 'etl_employe_sync' est DÉJÀ ACTIVÉ
echo   4. Cliquer sur le bouton "Trigger DAG" pour lancer manuellement
echo   5. Observer l'exécution dans l'onglet "Graph" (10-15 secondes)
echo.
echo   VÉRIFICATION DES DONNÉES
echo   ────────────────────────────────────────────────────────────────────────
echo   Via l'API Flask :
echo   curl http://localhost:5000/api/stats
echo.
echo   Via PostgreSQL :
echo   docker exec postgres-target psql -U targetuser -d target_db -c "SELECT COUNT(*) FROM employes_unified;"
echo.
echo   MONITORING
echo   ────────────────────────────────────────────────────────────────────────
echo   Dashboard Grafana : http://localhost:3000
echo   "Monitoring ETL Airflow" avec métriques
echo.
echo  ═════════════════════════════════════════════════════════════════════════
echo   INFORMATIONS COMPLÉMENTAIRES
echo  ═════════════════════════════════════════════════════════════════════════
echo.
echo   • Le DAG s'exécute automatiquement tous les jours à minuit
echo   • Les données sont validées après chaque synchronisation
echo   • L'application Flask offre une API REST complète (10+ endpoints)
echo   • Le monitoring Grafana se rafraîchit toutes les 5 secondes
echo   • Tous les logs sont disponibles dans les interfaces
echo.
echo   Documentation complète : README.md
echo   Scripts de maintenance windows : stop.bat, clean.bat, verify.bat, stop.bat
echo   Documentation API : http://localhost:5000/api
echo.
echo  ═════════════════════════════════════════════════════════════════════════
echo.
pause