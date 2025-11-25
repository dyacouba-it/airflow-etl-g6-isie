#!/bin/bash

clear
echo ""
echo "  ╔════════════════════════════════════════════════════════════════════════╗"
echo "  ║                 NETTOYAGE COMPLET DE L'ENVIRONNEMENT                   ║"
echo "  ╚════════════════════════════════════════════════════════════════════════╝"
echo ""
echo "  ATTENTION : Cette opération va supprimer toutes les données !"
echo ""
echo "  Cela inclut :"
echo "   - Tous les conteneurs"
echo "   - Tous les volumes (bases de données)"
echo "   - Tous les réseaux"
echo "   - Les logs Airflow"
echo ""
read -p "  Tapez OUI (en majuscules) pour confirmer : " confirmation

if [ "$confirmation" != "OUI" ]; then
    echo ""
    echo "  Annulation du nettoyage."
    echo ""
    exit 0
fi

echo ""
echo "  [1/4] Arrêt et suppression des conteneurs et volumes..."
docker-compose down -v

echo ""
echo "  [2/4] Suppression des volumes orphelins..."
docker volume prune -f

echo ""
echo "  [3/4] Suppression des logs Airflow..."
if [ -d "logs" ]; then
    rm -rf logs
    echo "  Logs supprimés"
else
    echo "  Pas de logs à supprimer"
fi

echo ""
echo "  [4/4] Nettoyage terminé"
echo ""
echo "  ╔════════════════════════════════════════════════════════════════════════╗"
echo "  ║                    NETTOYAGE TERMINÉ AVEC SUCCÈS                       ║"
echo "  ╚════════════════════════════════════════════════════════════════════════╝"
echo ""
echo "  Pour redémarrer avec un environnement propre, exécutez :"
echo "  ./start.sh"
echo ""