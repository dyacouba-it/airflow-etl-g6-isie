-- ========================================================================
--    PostgreSQL Target - Initialisation
-- ========================================================================
-- Ce fichier initialise la base de données cible avec tous les champs
-- nécessaires.
-- ========================================================================

-- Table principale : employes_unified
CREATE TABLE IF NOT EXISTS employes_unified (
    id SERIAL PRIMARY KEY,
    source VARCHAR(20) NOT NULL,
    source_id INTEGER,
    nom VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    departement VARCHAR(50),
    salaire DECIMAL(10,2),
    date_embauche DATE,
    statut VARCHAR(20) DEFAULT 'actif' NOT NULL CHECK (statut IN ('actif', 'inactif')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Commentaires sur les colonnes
COMMENT ON COLUMN employes_unified.statut IS 'Statut de l''employé : actif (présent dans les sources) ou inactif (supprimé des sources)';
COMMENT ON COLUMN employes_unified.source IS 'Source de données : CSV, MySQL, ou PostgreSQL';
COMMENT ON COLUMN employes_unified.source_id IS 'ID dans la base source';
COMMENT ON COLUMN employes_unified.email IS 'Clé unique pour identifier un employé entre les sources';

-- Index pour améliorer les performances
CREATE INDEX IF NOT EXISTS idx_email ON employes_unified(email);
CREATE INDEX IF NOT EXISTS idx_source ON employes_unified(source);
CREATE INDEX IF NOT EXISTS idx_statut ON employes_unified(statut);
CREATE INDEX IF NOT EXISTS idx_email_statut ON employes_unified(email, statut);

-- Table de logs ETL
CREATE TABLE IF NOT EXISTS etl_log (
    id SERIAL PRIMARY KEY,
    dag_run_id VARCHAR(100),
    task_name VARCHAR(100),
    status VARCHAR(20),
    records_processed INTEGER,
    records_inserted INTEGER,
    records_updated INTEGER,
    records_soft_deleted INTEGER,
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Commentaire sur la nouvelle colonne
COMMENT ON COLUMN etl_log.records_soft_deleted IS 'Nombre d''employés marqués comme inactifs lors de cette exécution';

-- Vue pour faciliter les requêtes sur les employés actifs
CREATE OR REPLACE VIEW employes_actifs AS
SELECT * FROM employes_unified WHERE statut = 'actif';

-- Vue pour faciliter les requêtes sur les employés inactifs
CREATE OR REPLACE VIEW employes_inactifs AS
SELECT * FROM employes_unified WHERE statut = 'inactif';

-- Log de succès
DO $$
BEGIN
    RAISE NOTICE '========================================';
    RAISE NOTICE 'PostgreSQL Target initialisée avec succès !';
    RAISE NOTICE '- Table employes_unified créée avec champ statut';
    RAISE NOTICE '- Index créés pour optimiser les requêtes';
    RAISE NOTICE '- Vues employes_actifs et employes_inactifs créées';
    RAISE NOTICE '- Prêt pour l''ETL avec soft delete';
    RAISE NOTICE '========================================';
END $$;
