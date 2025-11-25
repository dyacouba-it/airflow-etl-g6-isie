/* ============================================
   API CLIENT - Appels vers le backend Flask
   ============================================ */

/**
 * Classe pour gérer toutes les requêtes API
 */
class APIClient {
    constructor(baseURL = '/api') {
        this.baseURL = baseURL;
    }

    /**
     * Effectue une requête HTTP avec gestion des erreurs améliorée
     */
    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        console.log('[API] Appel:', endpoint);
        
        try {
            const response = await fetch(url, {
                ...options,
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                    ...options.headers
                }
            });
            
            // Vérifier si la réponse est OK
            if (!response.ok) {
                const errorText = await response.text();
                console.error('[API] Erreur HTTP:', response.status, errorText);
                return {
                    success: false,
                    message: `Erreur HTTP ${response.status}: ${response.statusText}`,
                    data: null
                };
            }
            
            const data = await response.json();
            console.log('[API] Réponse:', data);
            return data;
            
        } catch (error) {
            console.error('[API] Erreur:', endpoint, error);
            
            // Retourner un objet d'erreur standardisé
            return {
                success: false,
                message: error.message || 'Erreur de connexion',
                data: null,
                error: error
            };
        }
    }

    // ========== STATISTIQUES ==========
    async getStats(bustCache = false) {
        const params = bustCache ? `?_=${Date.now()}` : '';
        return this.request(`/stats${params}`);
    }

    async getSourcesStats(bustCache = false) {
        const params = bustCache ? `?_=${Date.now()}` : '';
        return this.request(`/sources/stats${params}`);
    }

    async getStatsPerSource(bustCache = false) {
        const params = bustCache ? `?_=${Date.now()}` : '';
        return this.request(`/stats/sources${params}`);
    }

    // ========== EMPLOYÉS BASE UNIFIÉE ==========
    async getUnifiedEmployees(params = {}) {
        const queryString = new URLSearchParams(params).toString();
        const endpoint = queryString ? `/employes?${queryString}` : '/employes';
        return this.request(endpoint);
    }

    async getUnifiedEmployeeById(id) {
        return this.request(`/employes/${id}`);
    }

    // ========== EMPLOYÉS SOURCES ==========
    async getSourceEmployees(source, params = {}) {
        const queryString = new URLSearchParams(params).toString();
        const endpoint = queryString 
            ? `/sources/${source}/employes?${queryString}` 
            : `/sources/${source}/employes`;
        return this.request(endpoint);
    }

    async getSourceEmployeeById(source, id) {
        return this.request(`/sources/${source}/employes/${id}`);
    }

    async createSourceEmployee(source, data) {
        console.log('[API] Création employé dans', source, ':', data);
        return this.request(`/sources/${source}/employes`, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    async updateSourceEmployee(source, id, data) {
        console.log('[API] Mise à jour employé', id, 'dans', source, ':', data);
        return this.request(`/sources/${source}/employes/${id}`, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    }

    async deleteSourceEmployee(source, id) {
        console.log('[API] Suppression employé', id, 'de', source);
        return this.request(`/sources/${source}/employes/${id}`, {
            method: 'DELETE'
        });
    }

    // ========== ETL ==========
    async triggerETL() {
        console.log('[API] Déclenchement ETL');
        return this.request('/etl/trigger', { 
            method: 'POST' 
        });
    }

    async getETLStatus() {
        return this.request('/etl/status');
    }

    async getETLHistory() {
        return this.request('/etl/history');
    }

    async getLastSync() {
        return this.request('/etl/last-sync');
    }
}

// Instance globale du client API
const api = new APIClient();
