@echo off
chcp 65001 >nul
cls

echo.
echo  ╔════════════════════════════════════════════════════════════════════════╗
echo  ║              VÉRIFICATION DE L'ENVIRONNEMENT ETL                       ║
echo  ╚════════════════════════════════════════════════════════════════════════╝
echo.

echo  [1/9] Vérification des services Docker...
echo  ════════════════════════════════════════════════════════════════════════
docker-compose ps
echo.

echo  [2/9] Health check - Application Flask...
echo  ════════════════════════════════════════════════════════════════════════
curl -s http://localhost:5000/health
echo.
echo.

echo  [3/9] Health check - Prometheus...
echo  ════════════════════════════════════════════════════════════════════════
curl -s http://localhost:9090/-/healthy
echo.
echo.

echo  [4/9] Connexions Airflow...
echo  ════════════════════════════════════════════════════════════════════════
docker exec airflow-webserver airflow connections list 2>nul | findstr "mysql_source_conn postgres_source_conn postgres_target_conn"
echo.

echo  [5/9] Données PostgreSQL Source...
echo  ════════════════════════════════════════════════════════════════════════
docker exec postgres-source psql -U sourceuser -d source_db -tc "SELECT COUNT(*) FROM employes_source;" 2>nul
echo  employés dans PostgreSQL Source
echo.

echo  [6/9] Données MySQL Source...
echo  ════════════════════════════════════════════════════════════════════════
docker exec mysql-source mysql -u mysqluser -pmysqlpass source_db -se "SELECT COUNT(*) FROM employes_mysql;" 2>nul
echo  employés dans MySQL Source
echo.

echo  [7/9] Données PostgreSQL Target (base unifiée)...
echo  ════════════════════════════════════════════════════════════════════════
docker exec postgres-target psql -U targetuser -d target_db -tc "SELECT COUNT(*) FROM employes_unified;" 2>nul
echo  employés dans la base unifiée
echo.

echo  [8/9] Répartition par source...
echo  ════════════════════════════════════════════════════════════════════════
docker exec postgres-target psql -U targetuser -d target_db -c "SELECT source, COUNT(*) as count FROM employes_unified GROUP BY source ORDER BY source;" 2>nul
echo.

echo  [9/9] Test API Flask - Statistiques...
echo  ════════════════════════════════════════════════════════════════════════
curl -s http://localhost:5000/api/stats
echo.
echo.

echo  ╔════════════════════════════════════════════════════════════════════════╗
echo  ║                    VÉRIFICATION TERMINÉE                               ║
echo  ╚════════════════════════════════════════════════════════════════════════╝
echo.
echo  Accès aux interfaces :
echo  ─────────────────────────────────────────────────────────────────────────
echo   • Airflow    : http://localhost:8080 (admin/admin)
echo   • Flask App  : http://localhost:5000
echo   • Grafana    : http://localhost:3000 (admin/admin)
echo   • Prometheus : http://localhost:9090
echo.
pause