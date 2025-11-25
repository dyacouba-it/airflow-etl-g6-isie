/* ============================================
   MAIN - Initialisation et Navigation
   ============================================ */

/**
 * Classe principale pour gérer l'application
 */
class AppManager {
    constructor() {
        this.initialized = false;
        this.darkMode = localStorage.getItem('darkMode') === 'true';
    }

    /**
     * Initialise l'application
     */
    async init() {
        if (this.initialized) {
            console.log('[AppManager] Déjà initialisé');
            return;
        }
        
        console.log('[AppManager] Initialisation de l\'application ETL...');
        console.log('[AppManager] Chargement des données initiales...');
        
        try {
            // Appliquer le thème sauvegardé
            this.applyTheme();
            
            // Charger toutes les données initiales en parallèle avec cache-busting
            const results = await Promise.allSettled([
                etlManager.loadStats(true),
                employeeManager.loadSourcesStats(true),
                etlManager.loadLastSync(),
                employeeManager.loadUnifiedEmployees(0)
            ]);
            
            // Log des résultats
            const taskNames = ['loadStats', 'loadSourcesStats', 'loadLastSync', 'loadUnifiedEmployees'];
            results.forEach((result, index) => {
                if (result.status === 'fulfilled') {
                    console.log(`[AppManager] ✓ ${taskNames[index]} OK`);
                } else {
                    console.error(`[AppManager] ✗ ${taskNames[index]} ERREUR:`, result.reason);
                }
            });
            
            // Configurer les événements
            this.setupEventListeners();
            
            this.initialized = true;
            console.log('[AppManager] Application initialisée avec succès');
            
        } catch (error) {
            console.error('[AppManager] Erreur lors de l\'initialisation:', error);
        }
    }

    /**
     * Applique le thème (clair/sombre)
     */
    applyTheme() {
        if (this.darkMode) {
            document.documentElement.setAttribute('data-theme', 'dark');
        } else {
            document.documentElement.removeAttribute('data-theme');
        }
        
        // Mettre à jour l'icône
        const icon = document.querySelector('.theme-toggle i');
        if (icon) {
            icon.className = this.darkMode ? 'fas fa-sun' : 'fas fa-moon';
        }
    }

    /**
     * Toggle le mode sombre
     */
    toggleDarkMode() {
        this.darkMode = !this.darkMode;
        localStorage.setItem('darkMode', this.darkMode);
        this.applyTheme();
    }

    /**
     * Configure les écouteurs d'événements
     */
    setupEventListeners() {
        // Fermeture du modal en cliquant à l'extérieur
        window.onclick = (event) => {
            const modal = document.getElementById('editModal');
            if (event.target === modal) {
                ui.toggleModal('editModal', false);
            }
        };

        // Support du clavier
        document.addEventListener('keydown', (event) => {
            // ESC pour fermer modal
            if (event.key === 'Escape') {
                ui.toggleModal('editModal', false);
            }
        });
        
        console.log('[AppManager] Event listeners configurés');
    }

    /**
     * Change d'onglet
     */
    switchTab(tabName, tabElement) {
        console.log('[AppManager] Changement d\'onglet:', tabName);
        
        // Masquer tous les contenus
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.remove('active');
        });
        
        // Désactiver tous les onglets
        document.querySelectorAll('.tab').forEach(tab => {
            tab.classList.remove('active');
        });
        
        // Activer l'onglet sélectionné
        const tabContent = document.getElementById(`tab-${tabName}`);
        if (tabContent) {
            tabContent.classList.add('active');
        }
        
        if (tabElement) {
            tabElement.classList.add('active');
        }
        
        // Charger les données spécifiques si nécessaire avec cache-busting
        switch (tabName) {
            case 'dashboard':
                etlManager.loadStats(true);
                break;
            case 'unified':
                // Charger les données pour l'onglet "Base unifiée"
                employeeManager.loadUnifiedData(1);
                break;
            case 'sources':
                employeeManager.loadSourcesStats(true);
                break;
        }
    }

    /**
     * Actualise toutes les données
     */
    async refreshAll() {
        console.log('[AppManager] Actualisation de toutes les données...');
        
        // Invalider les caches
        if (typeof employeeManager !== 'undefined') {
            employeeManager.invalidateCache();
        }
        
        // Réinitialiser et recharger
        this.initialized = false;
        await this.init();
    }
}

// Instance globale de l'application
const app = new AppManager();

// Fonction globale pour compatibilité HTML
function switchTab(tabName) {
    const tabElement = event ? event.target.closest('.tab') : null;
    app.switchTab(tabName, tabElement);
}

// Fonction globale pour le toggle du mode sombre
function toggleDarkMode() {
    app.toggleDarkMode();
}

// Fonction globale pour rafraîchir
function refreshAll() {
    app.refreshAll();
}

// Initialiser au chargement de la page
window.addEventListener('load', () => {
    app.init();
});

// Gestion des erreurs globales non capturées
window.addEventListener('error', (event) => {
    console.error('[Global Error]', event.error);
});

window.addEventListener('unhandledrejection', (event) => {
    console.error('[Unhandled Promise Rejection]', event.reason);
});
