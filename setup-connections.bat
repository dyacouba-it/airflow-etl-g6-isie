@echo off
echo ================================================
echo   CREATION DES CONNEXIONS AIRFLOW
echo ================================================
echo.

echo Suppression des connexions existantes...
docker exec airflow-webserver airflow connections delete mysql_source_conn 2>nul
docker exec airflow-webserver airflow connections delete postgres_source_conn 2>nul
docker exec airflow-webserver airflow connections delete postgres_target_conn 2>nul
echo.

echo Creation des nouvelles connexions...
echo.

echo [1/3] MySQL Source...
docker exec airflow-webserver airflow connections add mysql_source_conn ^
    --conn-type mysql ^
    --conn-host mysql-source ^
    --conn-schema source_db ^
    --conn-login mysqluser ^
    --conn-password mysqlpass ^
    --conn-port 3306
echo.

echo [2/3] PostgreSQL Source...
docker exec airflow-webserver airflow connections add postgres_source_conn ^
    --conn-type postgres ^
    --conn-host postgres-source ^
    --conn-schema source_db ^
    --conn-login sourceuser ^
    --conn-password sourcepass ^
    --conn-port 5432
echo.

echo [3/3] PostgreSQL Target...
docker exec airflow-webserver airflow connections add postgres_target_conn ^
    --conn-type postgres ^
    --conn-host postgres-target ^
    --conn-schema target_db ^
    --conn-login targetuser ^
    --conn-password targetpass ^
    --conn-port 5432
echo.

echo ================================================
echo   CONNEXIONS CREEES AVEC SUCCES !
echo ================================================
echo.

echo Verification :
docker exec airflow-webserver airflow connections list
echo.
pause