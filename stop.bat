@echo off
echo Arret de tous les services...
docker-compose down
echo.
echo Services arretes avec succes !
echo.
echo Pour redemarrer : start.bat
pause