@echo off
echo ========================================
echo Initialisation des bases de donnees
echo ========================================
echo.

echo [1/3] PostgreSQL Source...
docker exec -i postgres-source psql -U sourceuser -d source_db < scripts\init_postgres_source.sql
if errorlevel 1 (
    echo [ERREUR] Echec PostgreSQL Source
) else (
    echo [OK] PostgreSQL Source initialise
)

echo.
echo [2/3] MySQL Source...
docker exec -i mysql-source mysql -u mysqluser -pmysqlpass source_db < scripts\init_mysql_source.sql
if errorlevel 1 (
    echo [ERREUR] Echec MySQL Source
) else (
    echo [OK] MySQL Source initialise
)

echo.
echo [3/3] PostgreSQL Target...
docker exec -i postgres-target psql -U targetuser -d target_db < scripts\init_postgres_target.sql
if errorlevel 1 (
    echo [ERREUR] Echec PostgreSQL Target
) else (
    echo [OK] PostgreSQL Target initialise
)

echo.
echo ========================================
echo Initialisation terminee!
echo ========================================
echo.
echo Verification des donnees:
echo.
echo PostgreSQL Source:
docker exec postgres-source psql -U sourceuser -d source_db -c "SELECT COUNT(*) as total FROM employees_source;"
echo.
echo MySQL Source:
docker exec mysql-source mysql -u mysqluser -pmysqlpass source_db -se "SELECT COUNT(*) as total FROM employees_mysql;"
echo.
echo PostgreSQL Target (devrait etre vide):
docker exec postgres-target psql -U targetuser -d target_db -c "SELECT COUNT(*) as total FROM employees_unified;"
echo.
pause