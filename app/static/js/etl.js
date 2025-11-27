/* ============================================
   ETL - Gestion du processus ETL
   ============================================ */

/**
 * Classe pour gérer le processus ETL
 */
class ETLManager {
    /**
     * Charge les informations de dernière synchronisation
     */
    async loadLastSync() {
        try {
            const response = await api.getLastSync();
            
            if (response.success && response.data && response.data.derniere_maj) {
                const date = new Date(response.data.derniere_maj);
                const formatted = date.toLocaleString('fr-FR');
                ui.updateElement('last-sync-text', `Dernière synchronisation : ${formatted}`);
                ui.toggleDisplay('last-sync-info', true);
            }
        } catch (error) {
            console.error('Erreur chargement dernière synchro:', error);
        }
    }

    /**
     * Charge les statistiques globales DEPUIS LA BASE UNIFIÉE
     */
    async loadStats() {
        try {
            // Charger depuis la BASE UNIFIÉE (après ETL)
            const [stats, sourcesStats, sourcesData] = await Promise.all([
                api.getStats(),           // Total unifié
                api.getSourcesStats(),    // Comptes par source {csv: 23, mysql: 8, postgresql: 8}
                api.getStatsPerSource()   // Détails pour le graphique (array)
            ]);
            
            // Mettre à jour le total unifié
            if (stats.success) {
                ui.updateElement('total-employes', stats.data.total_employes || 0);
            }
            
            // Mettre à jour les KPI par source (format direct)
            if (sourcesStats.success && sourcesStats.data) {
                ui.updateElement('count-csv', sourcesStats.data.csv || 0);
                ui.updateElement('count-mysql', sourcesStats.data.mysql || 0);
                ui.updateElement('count-postgresql', sourcesStats.data.postgresql || 0);
            }
            
            // Mettre à jour les graphiques (format array)
            if (sourcesData.success) {
                chartsManager.createSourceChart(sourcesData.data);
            }
        } catch (error) {
            console.error('Erreur chargement statistiques:', error);
        }
    }

    /**
     * Déclenche le processus ETL
     */
    async triggerETL(buttonElement) {
        const btn = buttonElement || event.target.closest('.btn');
        const originalContent = btn.innerHTML;
        
        ui.setButtonLoading(btn, true, originalContent, 'ETL en cours...');
        
        const resultDiv = document.getElementById('etl-result');
        if (resultDiv) {
            resultDiv.innerHTML = ui.createMessage(
                'info',
                'Synchronisation en cours... Veuillez patienter 15 secondes',
                'fa-hourglass-half'
            );
        }
        
        try {
            const response = await api.triggerETL();
            
            if (response.success) {
                if (resultDiv) {
                    resultDiv.innerHTML = ui.createMessage(
                        'success',
                        'ETL déclenché avec succès ! Actualisation des données...'
                    );
                }
                
                // Attendre 15 secondes puis actualiser
                setTimeout(async () => {
                    await this.loadStats();
                    await employeeManager.loadSourcesStats();
                    await this.loadLastSync();
                    await employeeManager.loadUnifiedEmployees(0); // Réinitialiser à la page 0
                    
                    if (resultDiv) {
                        resultDiv.innerHTML = ui.createMessage(
                            'success',
                            'Synchronisation terminée ! Les données ont été mises à jour dans la base unifiée.'
                        );
                    }
                }, CONFIG.ETL_WAIT_TIME);
            } else {
                if (resultDiv) {
                    resultDiv.innerHTML = ui.createMessage(
                        'error',
                        `Erreur : ${response.message}`
                    );
                }
            }
        } catch (error) {
            if (resultDiv) {
                resultDiv.innerHTML = ui.createMessage('error', 'Erreur de connexion');
            }
        } finally {
            ui.setButtonLoading(btn, false, originalContent);
        }
    }
}

// Instance globale du gestionnaire ETL
const etlManager = new ETLManager();

// Fonction globale pour compatibilité HTML
function triggerETL() {
    etlManager.triggerETL(event.target);
}