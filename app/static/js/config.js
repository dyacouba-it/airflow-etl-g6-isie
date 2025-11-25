/* ============================================
   CONFIGURATION ET CONSTANTES
   ============================================ */

const CONFIG = {
    // Pagination
    PAGE_SIZE: 10,
    
    // Délais
    ETL_WAIT_TIME: 15000, // 15 secondes
    MESSAGE_TIMEOUT: 1000, // 1 seconde
    
    // Limites API
    DEFAULT_LIMIT: 100,
    
    // Sources de données
    SOURCES: {
        CSV: 'CSV',
        MYSQL: 'mysql',
        POSTGRESQL: 'postgresql'
    },
    
    // Couleurs des sources pour les graphiques
    SOURCE_COLORS: {
        CSV: '#10b981',
        csv: '#10b981',
        MySQL: '#3b82f6',
        mysql: '#3b82f6',
        PostgreSQL: '#f59e0b',
        postgresql: '#f59e0b',
        Manuel: '#8b5cf6'
    }
};

// État global de l'application
const APP_STATE = {
    currentPage: 0,
    currentSourceFilter: null,
    sourceChart: null
};

// Export pour utilisation dans d'autres modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { CONFIG, APP_STATE };
}
