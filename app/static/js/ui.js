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
        const sourceClass = `source-${(source || 'unknown').toLowerCase()}`;
        return `<span class="source-badge ${sourceClass}">${source || 'N/A'}</span>`;
    }

    /**
     * Formate un montant en FCFA
     */
    formatSalary(salary) {
        if (!salary && salary !== 0) return '-';
        return Math.round(salary).toLocaleString('fr-FR') + ' FCFA';
    }

    /**
     * Formate une date d'embauche en français (JJ/MM/AAAA)
     */
    formatDateEmbauche(dateString) {
        if (!dateString || dateString === 'null' || dateString === 'undefined' || dateString === 'None') {
            return '-';
        }
        
        try {
            // Extraire seulement la partie date si c'est un datetime
            const datePart = String(dateString).split('T')[0];
            const parts = datePart.split('-');
            
            if (parts.length === 3) {
                const year = parts[0];
                const month = parts[1];
                const day = parts[2];
                
                // Vérifier que c'est une date valide
                if (year && month && day && year.length === 4) {
                    return `${day}/${month}/${year}`;
                }
            }
            
            // Essayer de parser comme date
            const date = new Date(dateString);
            if (!isNaN(date.getTime())) {
                const day = String(date.getDate()).padStart(2, '0');
                const month = String(date.getMonth() + 1).padStart(2, '0');
                const year = date.getFullYear();
                return `${day}/${month}/${year}`;
            }
            
            return dateString || '-';
        } catch (e) {
            console.warn('[UI] Erreur formatage date embauche:', dateString, e);
            return '-';
        }
    }

    /**
     * Formate une date de mise à jour (datetime complet) en français
     */
    formatDateMAJ(dateString) {
        if (!dateString || dateString === 'null' || dateString === 'undefined' || dateString === 'None') {
            return '-';
        }
        
        try {
            const date = new Date(dateString);
            
            // Vérifier si la date est valide
            if (isNaN(date.getTime())) {
                return '-';
            }
            
            // Formater en français
            const day = String(date.getDate()).padStart(2, '0');
            const month = String(date.getMonth() + 1).padStart(2, '0');
            const year = date.getFullYear();
            const hours = String(date.getHours()).padStart(2, '0');
            const minutes = String(date.getMinutes()).padStart(2, '0');
            const seconds = String(date.getSeconds()).padStart(2, '0');
            
            return `${day}/${month}/${year} ${hours}:${minutes}:${seconds}`;
        } catch (e) {
            console.warn('[UI] Erreur formatage date MAJ:', dateString, e);
            return '-';
        }
    }

    /**
     * Échappe une chaîne pour utilisation dans un attribut HTML
     */
    escapeHtml(str) {
        if (!str) return '';
        return String(str)
            .replace(/&/g, '&amp;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#39;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;');
    }

    /**
     * Encode une chaîne pour utilisation dans onclick
     */
    encodeForOnclick(str) {
        if (!str) return '';
        return encodeURIComponent(String(str));
    }

    /**
     * Crée une ligne de tableau pour un employé
     */
    createEmployeeRow(emp, options = {}) {
        const { showId = false, showSource = false, showActions = false, sourceType = null } = options;
        
        let row = '<tr>';
        
        if (showId) {
            row += `<td>${emp.id || '-'}</td>`;
        }
        
        row += `
            <td><strong>${this.escapeHtml(emp.nom)}</strong></td>
            <td>${this.escapeHtml(emp.email)}</td>
            <td>${this.escapeHtml(emp.departement) || '-'}</td>
            <td>${this.formatSalary(emp.salaire)}</td>
            <td>${this.formatDateEmbauche(emp.date_embauche)}</td>
        `;
        
        if (showSource) {
            row += `<td>${this.createSourceBadge(emp.source)}</td>`;
            row += `<td style="font-size: 0.9em; color: var(--text-secondary);">${this.formatDateMAJ(emp.updated_at)}</td>`;
        }
        
        if (showActions && sourceType) {
            // Utiliser l'ID de l'employé pour éviter les problèmes d'échappement
            const escapedNom = this.encodeForOnclick(emp.nom);
            
            row += `
                <td>
                    <div class="action-btns">
                        <button class="btn btn-sm btn-primary" onclick="editSourceEmployee('${sourceType}', ${emp.id})" title="Modifier cet employé">
                            <i class="fas fa-edit"></i> Modifier
                        </button>
                        <button class="btn btn-sm btn-danger" onclick="deleteSourceEmployee('${sourceType}', ${emp.id}, '${escapedNom}')" title="Supprimer cet employé">
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
        const { showId = false, showSource = false, showActions = false, sourceType = null } = options;
        
        if (!employees || employees.length === 0) {
            return this.createMessage('info', 'Aucun employé à afficher');
        }
        
        let html = '<div class="table-container"><table><thead><tr>';
        
        if (showId) html += '<th>ID</th>';
        html += '<th>Nom</th><th>Email</th><th>Département</th><th>Salaire</th><th>Date embauche</th>';
        if (showSource) html += '<th>Source</th><th>Date MAJ</th>';
        if (showActions) html += '<th>Actions</th>';
        html += '</tr></thead><tbody>';
        
        employees.forEach(emp => {
            html += this.createEmployeeRow(emp, { showId, showSource, showActions, sourceType });
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
                    <i class="fas fa-angle-left"></i> Précédent
                </button>
                <button class="active" disabled>Page ${currentPage + 1} / ${totalPages}</button>
                <button onclick="changePage(1)" ${currentPage >= totalPages - 1 ? 'disabled' : ''}>
                    Suivant <i class="fas fa-angle-right"></i>
                </button>
            </div>
        `;
    }

    /**
     * Active/désactive un bouton avec spinner
     */
    setButtonLoading(button, loading, originalText = null, loadingText = 'Chargement...') {
        if (!button) return;
        
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
                // Focus sur le premier input
                setTimeout(() => {
                    const firstInput = modal.querySelector('input:not([type="hidden"])');
                    if (firstInput) firstInput.focus();
                }, 100);
            } else {
                modal.classList.remove('active');
            }
        }
    }
}

// Instance globale du gestionnaire UI
const ui = new UIManager();
