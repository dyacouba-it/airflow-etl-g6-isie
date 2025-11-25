/* ============================================
   CHARTS - Gestion des graphiques
   ============================================ */

/**
 * Classe pour gérer les graphiques
 */
class ChartsManager {
    constructor() {
        this.charts = {};
        this.chartJsReady = false;
        this.checkChartJs();
    }

    /**
     * Vérifie si Chart.js est disponible
     */
    checkChartJs() {
        if (typeof Chart !== 'undefined') {
            this.chartJsReady = true;
            console.log('[ChartsManager] Chart.js est disponible');
        } else {
            console.warn('[ChartsManager] Chart.js non disponible, graphiques désactivés');
            this.chartJsReady = false;
        }
    }

    /**
     * Détruit un graphique existant
     */
    destroyChart(chartName) {
        if (this.charts[chartName]) {
            try {
                this.charts[chartName].destroy();
            } catch (e) {
                console.warn('[ChartsManager] Erreur lors de la destruction du graphique:', e);
            }
            this.charts[chartName] = null;
        }
    }

    /**
     * Crée ou met à jour le graphique de répartition par source
     */
    createSourceChart(sourcesData) {
        // Revérifier si Chart.js est disponible
        if (typeof Chart === 'undefined') {
            console.warn('[ChartsManager] Chart.js non disponible');
            this.showChartFallback();
            return;
        }
        
        this.chartJsReady = true;
        this.destroyChart('sourceChart');
        
        const ctx = document.getElementById('sourceChart');
        if (!ctx) {
            console.warn('[ChartsManager] Canvas sourceChart non trouvé');
            return;
        }
        
        // Vérifier les données
        if (!sourcesData || !Array.isArray(sourcesData) || sourcesData.length === 0) {
            console.warn('[ChartsManager] Pas de données pour le graphique');
            return;
        }
        
        const labels = sourcesData.map(s => s.source || 'Inconnu');
        const data = sourcesData.map(s => s.count || 0);
        
        // Couleurs par source
        const colorMap = {
            'CSV': '#10b981',
            'csv': '#10b981',
            'MySQL': '#3b82f6',
            'mysql': '#3b82f6',
            'PostgreSQL': '#f59e0b',
            'postgresql': '#f59e0b'
        };
        
        const colors = labels.map(label => colorMap[label] || '#6b7280');
        
        try {
            this.charts.sourceChart = new Chart(ctx.getContext('2d'), {
                type: 'doughnut',
                data: {
                    labels: labels,
                    datasets: [{
                        data: data,
                        backgroundColor: colors,
                        borderWidth: 2,
                        borderColor: '#ffffff'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'right',
                            labels: {
                                font: {
                                    size: 14,
                                    family: "'Inter', sans-serif"
                                },
                                padding: 20,
                                usePointStyle: true
                            }
                        },
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    const label = context.label || '';
                                    const value = context.parsed || 0;
                                    const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                    const percentage = total > 0 ? ((value / total) * 100).toFixed(1) : 0;
                                    return `${label}: ${value} (${percentage}%)`;
                                }
                            }
                        }
                    }
                }
            });
            
            console.log('[ChartsManager] Graphique créé avec succès');
            
        } catch (error) {
            console.error('[ChartsManager] Erreur création graphique:', error);
            this.showChartFallback();
        }
    }

    /**
     * Affiche un fallback si Chart.js n'est pas disponible
     */
    showChartFallback() {
        const ctx = document.getElementById('sourceChart');
        if (ctx && ctx.parentElement) {
            ctx.parentElement.innerHTML = `
                <div style="text-align: center; padding: 40px; color: #6b7280;">
                    <i class="fas fa-chart-pie" style="font-size: 3em; margin-bottom: 15px; opacity: 0.5;"></i>
                    <p>Graphique non disponible</p>
                    <small>Chart.js n'a pas pu être chargé</small>
                </div>
            `;
        }
    }

    /**
     * Met à jour tous les graphiques
     */
    async updateCharts() {
        try {
            const sourcesData = await api.getStatsPerSource();
            if (sourcesData.success && sourcesData.data) {
                this.createSourceChart(sourcesData.data);
            }
        } catch (error) {
            console.error('[ChartsManager] Erreur mise à jour graphiques:', error);
        }
    }
}

// Instance globale du gestionnaire de graphiques
const chartsManager = new ChartsManager();
