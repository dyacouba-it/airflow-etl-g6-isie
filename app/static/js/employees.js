/* ============================================
   EMPLOYEES - Gestion des employés
   ============================================ */

/**
 * Classe pour gérer les employés
 */
class EmployeeManager {
    constructor() {
        // Cache pour les données
        this.unifiedCache = null;
        this.unifiedCacheTime = 0;
        this.cacheDuration = 30000; // 30 secondes
        
        // Cache pour le tableau de bord
        this.dashboardEmployees = null;
        this.dashboardCacheTime = 0;
        
        // Pagination pour l'onglet Base unifiée
        this.unifiedDataPage = 1;
        this.unifiedDataPageSize = 10;
        this.unifiedDataTotal = 0;
        this.unifiedDataEmployees = [];
    }

    /**
     * Invalide le cache
     */
    invalidateCache() {
        this.unifiedCache = null;
        this.unifiedCacheTime = 0;
        this.unifiedDataEmployees = [];
        this.dashboardEmployees = null;
        this.dashboardCacheTime = 0;
        console.log('[EmployeeManager] Cache invalidé');
    }
    
    /**
     * Charge les employés de la base unifiée avec pagination
     */
    async loadUnifiedEmployees(page = 0) {
        try {
            APP_STATE.currentPage = page;
            const offset = page * CONFIG.PAGE_SIZE;
            
            const response = await api.getUnifiedEmployees({ 
                limit: CONFIG.PAGE_SIZE,
                offset: offset
            });
            
            const container = document.getElementById('unified-employees-list');
            
            if (response.success && response.data.length > 0) {
                const total = response.count || 0;
                
                let html = `<div style="margin-bottom: 15px; color: var(--text-secondary);">`;
                html += `<strong>${response.data.length}</strong> employé(s) affiché(s) sur <strong>${total}</strong> total`;
                html += `</div>`;
                
                html += ui.createEmployeeTable(response.data, { 
                    showSource: true 
                });
                
                // Ajouter la pagination
                html += this.createUnifiedPagination(page, total, CONFIG.PAGE_SIZE);
                
                container.innerHTML = html;
            } else {
                container.innerHTML = ui.createMessage(
                    'warning',
                    'Aucun employé dans la base unifiée. Cliquez sur "Lancer ETL" pour synchroniser les données.',
                    'fa-exclamation-triangle'
                );
            }
        } catch (error) {
            document.getElementById('unified-employees-list').innerHTML = ui.createMessage(
                'error',
                'Erreur de chargement'
            );
        }
    }

    /**
     * Crée la pagination pour la base unifiée
     */
    createUnifiedPagination(currentPage, totalItems, pageSize) {
        const totalPages = Math.ceil(totalItems / pageSize);
        
        if (totalPages <= 1) return '';
        
        return `
            <div class="pagination">
                <button onclick="loadUnifiedEmployeesPage(${currentPage - 1})" ${currentPage === 0 ? 'disabled' : ''}>
                    ◀ Précédent
                </button>
                <button class="active">${currentPage + 1} / ${totalPages}</button>
                <button onclick="loadUnifiedEmployeesPage(${currentPage + 1})" ${currentPage >= totalPages - 1 ? 'disabled' : ''}>
                    Suivant ▶
                </button>
            </div>
        `;
    }

    /**
     * Charge les statistiques des sources
     */
    async loadSourcesStats() {
        try {
            const response = await api.getSourcesStats();
            
            if (response.success) {
                ui.updateElement('src-count-csv', response.data.csv || 0);
                ui.updateElement('src-count-mysql', response.data.mysql || 0);
                ui.updateElement('src-count-postgresql', response.data.postgresql || 0);
            }
        } catch (error) {
            console.error('Erreur chargement stats sources:', error);
        }
    }

    async loadUnifiedEmployees(page = 0) {
        console.log('[EmployeeManager] loadUnifiedEmployees page:', page);
        
        try {
            APP_STATE.currentPage = page;
            
            const container = document.getElementById('unified-employees-list');
            if (!container) {
                console.warn('[EmployeeManager] Container unified-employees-list non trouvé');
                return;
            }
            
            // Charger tous les employés pour avoir le total exact
            // Utiliser le cache si disponible
            const now = Date.now();
            if (!this.dashboardEmployees || (now - this.dashboardCacheTime) > this.cacheDuration) {
                console.log('[EmployeeManager] Chargement depuis API pour tableau de bord...');
                const response = await api.getUnifiedEmployees({ limit: 1000 });
                
                if (response.success && response.data) {
                    this.dashboardEmployees = response.data;
                    this.dashboardCacheTime = now;
                } else {
                    this.dashboardEmployees = [];
                }
            }
            
            const allEmployees = this.dashboardEmployees;
            const total = allEmployees.length;
            
            if (total > 0) {
                // Extraire la page courante
                const startIndex = page * CONFIG.PAGE_SIZE;
                const endIndex = startIndex + CONFIG.PAGE_SIZE;
                const pageData = allEmployees.slice(startIndex, endIndex);
                
                let html = `<div style="margin-bottom: 15px; color: var(--text-secondary); text-align: center;">`;
                html += `<strong>${pageData.length}</strong> employé(s) affiché(s) sur <strong>${total}</strong> total`;
                html += `</div>`;
                
                html += ui.createEmployeeTable(pageData, { 
                    showSource: true 
                });
                
                // Ajouter la pagination
                html += this.createUnifiedPagination(page, total, CONFIG.PAGE_SIZE);
                
                container.innerHTML = html;
            } else {
                container.innerHTML = ui.createMessage(
                    'warning',
                    'Aucun employé dans la base unifiée. Cliquez sur "Lancer ETL" pour synchroniser les données.',
                    'fa-exclamation-triangle'
                );
            }
        } catch (error) {
            console.error('[EmployeeManager] Erreur loadUnifiedEmployees:', error);
            const container = document.getElementById('unified-employees-list');
            if (container) {
                container.innerHTML = ui.createMessage(
                    'error',
                    'Erreur de chargement des employés'
                );
            }
        }
    }

    /**
     * Charge les données pour l'onglet "Base unifiée" avec pagination complète
     */
    async loadUnifiedData(page = 1) {
        console.log('[EmployeeManager] loadUnifiedData page:', page);
        
        const container = document.getElementById('unified-data-container');
        const paginationControls = document.getElementById('unified-pagination-controls');
        
        if (!container) {
            console.warn('[EmployeeManager] Container unified-data-container non trouvé');
            return;
        }
        
        // Afficher le chargement
        container.innerHTML = `
            <div class="loading">
                <div class="spinner"></div>
                Chargement des données...
            </div>
        `;
        
        try {
            // Charger TOUS les employés (avec cache)
            const now = Date.now();
            if (!this.unifiedDataEmployees.length || (now - this.unifiedCacheTime) > this.cacheDuration) {
                console.log('[EmployeeManager] Chargement depuis API...');
                const response = await api.getUnifiedEmployees({ limit: 1000 });
                
                if (response.success && response.data) {
                    this.unifiedDataEmployees = response.data;
                    this.unifiedDataTotal = response.count || response.data.length;
                    this.unifiedCacheTime = now;
                } else {
                    throw new Error(response.message || 'Erreur de chargement');
                }
            }
            
            // Calculer la pagination
            const totalPages = Math.ceil(this.unifiedDataTotal / this.unifiedDataPageSize);
            this.unifiedDataPage = Math.max(1, Math.min(page, totalPages));
            
            // Extraire la page courante
            const startIndex = (this.unifiedDataPage - 1) * this.unifiedDataPageSize;
            const endIndex = startIndex + this.unifiedDataPageSize;
            const pageData = this.unifiedDataEmployees.slice(startIndex, endIndex);
            
            if (pageData.length > 0) {
                let html = `<div style="margin-bottom: 15px; color: var(--text-secondary); text-align: center;">`;
                html += `Affichage de <strong>${startIndex + 1}</strong> à <strong>${Math.min(endIndex, this.unifiedDataTotal)}</strong> sur <strong>${this.unifiedDataTotal}</strong> employés`;
                html += `</div>`;
                
                html += ui.createEmployeeTable(pageData, { 
                    showSource: true 
                });
                
                container.innerHTML = html;
                
                // Mettre à jour les contrôles de pagination
                if (paginationControls) {
                    paginationControls.style.display = totalPages > 1 ? 'flex' : 'none';
                    
                    const pageInfo = document.getElementById('unified-page-info');
                    if (pageInfo) {
                        pageInfo.textContent = `Page ${this.unifiedDataPage} / ${totalPages}`;
                    }
                    
                    // Activer/désactiver les boutons
                    const btnFirst = document.getElementById('unified-btn-first');
                    const btnPrev = document.getElementById('unified-btn-prev');
                    const btnNext = document.getElementById('unified-btn-next');
                    const btnLast = document.getElementById('unified-btn-last');
                    
                    if (btnFirst) btnFirst.disabled = this.unifiedDataPage <= 1;
                    if (btnPrev) btnPrev.disabled = this.unifiedDataPage <= 1;
                    if (btnNext) btnNext.disabled = this.unifiedDataPage >= totalPages;
                    if (btnLast) btnLast.disabled = this.unifiedDataPage >= totalPages;
                }
            } else {
                container.innerHTML = ui.createMessage(
                    'warning',
                    'Aucun employé dans la base unifiée. Cliquez sur "Lancer ETL" pour synchroniser les données.',
                    'fa-exclamation-triangle'
                );
                if (paginationControls) paginationControls.style.display = 'none';
            }
            
        } catch (error) {
            console.error('[EmployeeManager] Erreur loadUnifiedData:', error);
            container.innerHTML = ui.createMessage(
                'error',
                'Erreur de chargement : ' + error.message
            );
            if (paginationControls) paginationControls.style.display = 'none';
        }
    }

    /**
     * Change de page pour l'onglet Base unifiée
     */
    changeUnifiedPage(direction) {
        const totalPages = Math.ceil(this.unifiedDataTotal / this.unifiedDataPageSize);
        let newPage = this.unifiedDataPage;
        
        switch (direction) {
            case 'first':
                newPage = 1;
                break;
            case 'prev':
                newPage = Math.max(1, this.unifiedDataPage - 1);
                break;
            case 'next':
                newPage = Math.min(totalPages, this.unifiedDataPage + 1);
                break;
            case 'last':
                newPage = totalPages;
                break;
            default:
                if (typeof direction === 'number') {
                    newPage = direction;
                }
        }
        
        if (newPage !== this.unifiedDataPage) {
            this.loadUnifiedData(newPage);
        }
    }

    /**
     * Charge les employés d'une source spécifique
     * Charge toujours depuis les sources directes
     */
    async loadSourceEmployees(source) {
        const sourceMap = {
            'csv': { name: 'CSV', type: 'csv' },
            'mysql': { name: 'MySQL', type: 'mysql' },
            'postgresql': { name: 'PostgreSQL', type: 'postgresql' }
        };
        
        const sourceInfo = sourceMap[source.toLowerCase()];
        if (!sourceInfo) return;
        
        try {
            let employees, total;
            
            // Pour TOUTES les sources, charger depuis la SOURCE directe
            const response = await api.getSourceEmployees(sourceInfo.type, { 
                limit: CONFIG.DEFAULT_LIMIT 
            });
            
            employees = response.data;
            total = response.total || response.count || (employees ? employees.length : 0);
            
            if (source.toLowerCase() === 'csv') {
                // CSV est en lecture seule
                this.displayReadOnlyEmployees(employees, sourceInfo.name);
            } else {
                // MySQL et PostgreSQL sont modifiables
                this.displayEditableEmployees(employees, sourceInfo.name, sourceInfo.type, total);
            }
        } catch (error) {
            console.error('Erreur chargement employés source:', error);
            ui.showMessage('source-employees-list', 'error', 'Erreur de chargement');
        }
    }

    /**
     * Affiche les employés en lecture seule (CSV)
     */
    displayReadOnlyEmployees(employees, sourceName) {
        const container = document.getElementById('source-employees-list');
        
        if (!employees || employees.length === 0) {
            container.innerHTML = ui.createMessage('info', `Aucun employé trouvé pour ${sourceName}`);
            return;
        }
        
        const start = APP_STATE.currentPage * CONFIG.PAGE_SIZE;
        const end = start + CONFIG.PAGE_SIZE;
        const pageData = employees.slice(start, end);
        
        let html = `<h3 style="margin-bottom: 20px; color: var(--primary);">Employés ${sourceName} (${employees.length} au total)</h3>`;
        html += ui.createEmployeeTable(pageData, { showId: false, showSource: false });
        html += ui.createPagination(APP_STATE.currentPage, employees.length, CONFIG.PAGE_SIZE);
        
        container.innerHTML = html;
    }

    /**
     * Affiche les employés modifiables (MySQL, PostgreSQL)
     */
    displayEditableEmployees(employees, sourceName, sourceType, total) {
        const container = document.getElementById('source-employees-list');
        
        if (!employees || employees.length === 0) {
            container.innerHTML = ui.createMessage('info', `Aucun employé trouvé dans ${sourceName} source`);
            return;
        }
        
        const start = APP_STATE.currentPage * CONFIG.PAGE_SIZE;
        const end = start + CONFIG.PAGE_SIZE;
        const pageData = employees.slice(start, end);
        
        let html = `<h3 style="margin-bottom: 20px; color: var(--primary);">Employés ${sourceName} Source (${total} au total)</h3>`;
        html += ui.createEmployeeTable(pageData, { 
            showId: true, 
            showActions: true, 
            sourceType: sourceType 
        });
        html += ui.createPagination(APP_STATE.currentPage, employees.length, CONFIG.PAGE_SIZE);
        
        container.innerHTML = html;
    }

    /**
     * Sélectionne une source
     */
    selectSource(source, element) {
        APP_STATE.currentSourceFilter = source;
        APP_STATE.currentPage = 0;
        
        // Mettre à jour l'état actif des cartes
        document.querySelectorAll('.source-stat-card').forEach(card => {
            card.classList.remove('active');
        });
        if (element) {
            element.closest('.source-stat-card').classList.add('active');
        }
        
        this.loadSourceEmployees(source);
    }

    /**
     * Change de page
     */
    changePage(direction) {
        APP_STATE.currentPage += direction;
        if (APP_STATE.currentSourceFilter) {
            this.loadSourceEmployees(APP_STATE.currentSourceFilter);
        }
    }

    /**
     * Ajoute un employé dans une source
     */
    async addEmployee(event, source) {
        event.preventDefault();
        
        const form = event.target;
        const submitBtn = form.querySelector('button[type="submit"]');
        const messageDiv = document.getElementById(`${source}-message`);
        
        const data = {
            nom: document.getElementById(`${source}-nom`).value,
            email: document.getElementById(`${source}-email`).value,
            departement: document.getElementById(`${source}-departement`).value,
            salaire: parseFloat(document.getElementById(`${source}-salaire`).value),
            date_embauche: document.getElementById(`${source}-date`).value || null
        };
        
        ui.setButtonLoading(submitBtn, true, null, 'Ajout en cours...');
        
        try {
            const result = await api.createSourceEmployee(source, data);
            
            if (result.success) {
                messageDiv.innerHTML = ui.createMessage('success', result.message);
                form.reset();
                this.loadSourcesStats();
                
                setTimeout(() => {
                    messageDiv.innerHTML += ui.createMessage(
                        'warning',
                        "N'oubliez pas de cliquer sur \"Lancer ETL\" pour synchroniser vers la base unifiée !",
                        'fa-exclamation-triangle'
                    );
                }, CONFIG.MESSAGE_TIMEOUT);
            } else {
                messageDiv.innerHTML = ui.createMessage('error', result.message);
            }
        } catch (error) {
            messageDiv.innerHTML = ui.createMessage('error', 'Erreur de connexion');
        } finally {
            ui.setButtonLoading(submitBtn, false);
        }
    }

    /**
     * Ouvre le modal d'édition
     */
    editEmployee(source, emp) {
        document.getElementById('editModalTitle').textContent = `Modifier l'employé (${source.toUpperCase()})`;
        document.getElementById('edit-source').value = source;
        document.getElementById('edit-id').value = emp.id;
        document.getElementById('edit-nom').value = emp.nom;
        document.getElementById('edit-email').value = emp.email;
        document.getElementById('edit-departement').value = emp.departement || '';
        document.getElementById('edit-salaire').value = emp.salaire || '';
        document.getElementById('edit-date').value = emp.date_embauche ? emp.date_embauche.split('T')[0] : '';
        document.getElementById('edit-modal-message').innerHTML = '';
        ui.toggleModal('editModal', true);
    }

    /**
     * Sauvegarde les modifications
     */
    async saveEdit(event) {
        event.preventDefault();
        
        const source = document.getElementById('edit-source').value;
        const id = document.getElementById('edit-id').value;
        const data = {
            nom: document.getElementById('edit-nom').value,
            email: document.getElementById('edit-email').value,
            departement: document.getElementById('edit-departement').value,
            salaire: parseFloat(document.getElementById('edit-salaire').value),
            date_embauche: document.getElementById('edit-date').value || null
        };
        
        try {
            const result = await api.updateSourceEmployee(source, id, data);
            
            if (result.success) {
                ui.showMessage('edit-modal-message', 'success', result.message);
                
                setTimeout(() => {
                    ui.toggleModal('editModal', false);
                    this.loadSourcesStats();
                    if (APP_STATE.currentSourceFilter === source) {
                        this.loadSourceEmployees(source);
                    }
                }, 1500);
            } else {
                ui.showMessage('edit-modal-message', 'error', result.message);
            }
        } catch (error) {
            ui.showMessage('edit-modal-message', 'error', 'Erreur de connexion');
        }
    }

    /**
     * Supprime un employé
     */
    async deleteEmployee(source, id, nom) {
        if (!confirm(`Êtes-vous sûr de vouloir supprimer "${nom}" de la base ${source.toUpperCase()} ?\n\nCette action nécessitera un "Lancer ETL" pour être reflétée dans la base unifiée.`)) {
            return;
        }
        
        try {
            const result = await api.deleteSourceEmployee(source, id);
            
            if (result.success) {
                alert('✓ ' + result.message);
                this.loadSourcesStats();
                this.loadSourceEmployees(source);
            } else {
                alert('✗ ' + result.message);
            }
        } catch (error) {
            alert('✗ Erreur de connexion');
        }
    }
}

// Instance globale du gestionnaire d'employés
const employeeManager = new EmployeeManager();

// Fonctions globales pour compatibilité HTML
function loadUnifiedEmployees() {
    employeeManager.loadUnifiedEmployees();
}

function loadUnifiedEmployeesPage(page) {
    employeeManager.loadUnifiedEmployees(page);
}

function loadSourcesData() {
    employeeManager.loadSourcesStats();
}

function selectSource(source) {
    employeeManager.selectSource(source, event.target);
}

function changePage(direction) {
    employeeManager.changePage(direction);
}

function addToSource(event, source) {
    employeeManager.addEmployee(event, source);
}

function editSourceEmployee(source, emp) {
    employeeManager.editEmployee(source, emp);
}

function saveEdit(event) {
    employeeManager.saveEdit(event);
}

function deleteSourceEmployee(source, id, nom) {
    employeeManager.deleteEmployee(source, id, nom);
}

function closeEditModal() {
    ui.toggleModal('editModal', false);
}

// ========== FONCTIONS GLOBALES POUR BASE UNIFIÉE ==========

/**
 * Charge les données de la base unifiée (bouton Actualiser)
 */
function loadUnifiedData() {
    employeeManager.loadUnifiedData(employeeManager.unifiedDataPage || 1);
}

/**
 * Change de page dans la base unifiée
 * @param {string|number} action - 'first', 'prev', 'next', 'last' ou numéro de page
 */
function changeUnifiedPage(action) {
    employeeManager.changeUnifiedPage(action);
}
