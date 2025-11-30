/* ============================================
   UI - Manipulation du DOM et Affichage
   ============================================ */

/**
 * Classe pour gérer l'interface utilisateur
 */
class UIManager {
    /**
     * Met à jour un élément par son ID
     */
    updateElement(id, content) {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = content;
        }
    }

    /**
     * Met à jour le HTML d'un élément
     */
    updateHTML(id, html) {
        const element = document.getElementById(id);
        if (element) {
            element.innerHTML = html;
        }
    }

    /**
     * Affiche/masque un élément
     */
    toggleDisplay(id, show) {
        const element = document.getElementById(id);
        if (element) {
            element.style.display = show ? 'flex' : 'none';
        }
    }

    /**
     * Crée un message
     */
    createMessage(type, text, icon = null) {
        const icons = {
            success: 'fa-check-circle',
            error: 'fa-exclamation-circle',
            warning: 'fa-exclamation-triangle',
            info: 'fa-info-circle'
        };
        
        const iconClass = icon || icons[type] || 'fa-info-circle';
        
        return `
            <div class="message message-${type}">
                <i class="fas ${iconClass}"></i>
                ${text}
            </div>
        `;
    }

    /**
     * Affiche un message dans un conteneur
     */
    showMessage(containerId, type, text) {
        this.updateHTML(containerId, this.createMessage(type, text));
    }

    /**
     * Crée un badge de source
     */
    createSourceBadge(source) {
        const sourceClass = `source-${source.toLowerCase()}`;
        return `<span class="source-badge ${sourceClass}">${source}</span>`;
    }

    /**
     * Formate un montant en FCFA
     */
    formatSalary(salary) {
        return salary ? Math.round(salary).toLocaleString() + ' FCFA' : '-';
    }

    /**
     * Formate une date
     */
    formatDate(dateString) {
        if (!dateString) return '-';
        return new Date(dateString).toLocaleString('fr-FR');
    }

    /**
     * Crée une ligne de tableau pour un employé
     */
    createEmployeeRow(emp, options = {}) {
        const { showId = false, showSource = false, showStatut = false, showActions = false, sourceType = null } = options;
        
        let row = '<tr>';
        
        if (showId) {
            row += `<td>${emp.id}</td>`;
        }
        
        row += `
            <td><strong>${emp.nom}</strong></td>
            <td>${emp.email}</td>
            <td>${emp.departement || '-'}</td>
            <td>${this.formatSalary(emp.salaire)}</td>
            <td style="font-size: 0.9em;">${emp.date_embauche ? new Date(emp.date_embauche).toLocaleDateString('fr-FR') : '-'}</td>
        `;
        
        if (showSource) {
            row += `<td>${this.createSourceBadge(emp.source)}</td>`;
            row += `<td style="font-size: 0.9em; color: #6b7280;">${this.formatDate(emp.updated_at)}</td>`;
        }
        
        if (showStatut) {
            const statut = emp.statut || 'actif';
            const statutClass = statut.toLowerCase() === 'actif' ? 'success' : 'danger';
            const statutIcon = statut.toLowerCase() === 'actif' ? 'check-circle' : 'times-circle';
            row += `<td><span class="source-badge source-badge-${statutClass}"><i class="fas fa-${statutIcon}"></i> ${statut.charAt(0).toUpperCase() + statut.slice(1)}</span></td>`;
        }
        
        if (showActions && sourceType) {
            row += `
                <td>
                    <div class="action-btns">
                        <button class="btn btn-sm btn-primary" onclick='employeeManager.editEmployee("${sourceType}", ${JSON.stringify(emp)})'>
                            <i class="fas fa-edit"></i> Modifier
                        </button>
                        <button class="btn btn-sm btn-danger" onclick='employeeManager.deleteEmployee("${sourceType}", ${emp.id}, "${emp.nom}")'>
                            <i class="fas fa-trash"></i> Supprimer
                        </button>
                    </div>
                </td>
            `;
        }
        
        row += '</tr>';
        return row;
    }

    /**
     * Crée un tableau d'employés
     */
    createEmployeeTable(employees, options = {}) {
        const { showId = false, showSource = false, showStatut = false, showActions = false, sourceType = null } = options;
        
        let html = '<div class="table-container"><table><thead><tr>';
        
        if (showId) html += '<th>ID</th>';
        html += '<th>Nom</th><th>Email</th><th>Département</th><th>Salaire</th><th>Date embauche</th>';
        if (showSource) html += '<th>Source</th><th>Date MAJ</th>';
        if (showStatut) html += '<th>Statut</th>';
        if (showActions) html += '<th>Actions</th>';
        html += '</tr></thead><tbody>';
        
        employees.forEach(emp => {
            html += this.createEmployeeRow(emp, { showId, showSource, showStatut, showActions, sourceType });
        });
        
        html += '</tbody></table></div>';
        return html;
    }

    /**
     * Crée une pagination
     */
    createPagination(currentPage, totalItems, pageSize) {
        const totalPages = Math.ceil(totalItems / pageSize);
        
        if (totalPages <= 1) return '';
        
        return `
            <div class="pagination">
                <button onclick="changePage(-1)" ${currentPage === 0 ? 'disabled' : ''}>
                    ◀ Précédent
                </button>
                <button class="active">${currentPage + 1} / ${totalPages}</button>
                <button onclick="changePage(1)" ${currentPage >= totalPages - 1 ? 'disabled' : ''}>
                    Suivant ▶
                </button>
            </div>
        `;
    }

    /**
     * Active/désactive un bouton avec spinner
     */
    setButtonLoading(button, loading, originalText = null, loadingText = 'Chargement...') {
        if (loading) {
            button.dataset.originalText = button.innerHTML;
            button.innerHTML = `<i class="fas fa-spinner fa-spin"></i> ${loadingText}`;
            button.disabled = true;
        } else {
            button.innerHTML = originalText || button.dataset.originalText || button.innerHTML;
            button.disabled = false;
        }
    }

    /**
     * Affiche/masque le modal
     */
    toggleModal(modalId, show) {
        const modal = document.getElementById(modalId);
        if (modal) {
            if (show) {
                modal.classList.add('active');
            } else {
                modal.classList.remove('active');
            }
        }
    }

    /**
     * Crée les boutons de filtre par statut
     */
    createStatutFilters(currentFilter = 'all', callbackName = 'filterByStatus') {
        return `
            <div style="display: flex; justify-content: center; gap: 10px; margin: 20px 0;">
                <button class="btn ${currentFilter === 'all' ? 'btn-primary' : 'btn-secondary'} status-filter-btn" 
                        onclick="${callbackName}('all')" data-filter="all">
                    <i class="fas fa-list"></i> Tous
                </button>
                <button class="btn ${currentFilter === 'actif' ? 'btn-primary' : 'btn-secondary'} status-filter-btn" 
                        onclick="${callbackName}('actif')" data-filter="actif">
                    <i class="fas fa-check-circle"></i> Actifs
                </button>
                <button class="btn ${currentFilter === 'inactif' ? 'btn-primary' : 'btn-secondary'} status-filter-btn" 
                        onclick="${callbackName}('inactif')" data-filter="inactif">
                    <i class="fas fa-times-circle"></i> Inactifs
                </button>
            </div>
        `;
    }
}

// Instance globale du gestionnaire UI
const ui = new UIManager();