@echo off
echo ========================================
echo Statut de l'environnement
echo ========================================
echo.
echo Conteneurs en cours d'execution:
docker-compose ps
echo.
echo ========================================
echo Logs recents Airflow:
echo ========================================
docker logs --tail 20 airflow-scheduler
echo.
pause