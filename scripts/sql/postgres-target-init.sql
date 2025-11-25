-- PostgreSQL Target - Initialisation avec données
CREATE TABLE IF NOT EXISTS employes_unified (
    id SERIAL PRIMARY KEY,
    source VARCHAR(20) NOT NULL,
    source_id INTEGER,
    nom VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    departement VARCHAR(50),
    salaire DECIMAL(10,2),
    date_embauche DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_email ON employes_unified(email);
CREATE INDEX IF NOT EXISTS idx_source ON employes_unified(source);

-- Table de logs ETL
CREATE TABLE IF NOT EXISTS etl_log (
    id SERIAL PRIMARY KEY,
    dag_run_id VARCHAR(100),
    task_name VARCHAR(100),
    status VARCHAR(20),
    records_processed INTEGER,
    records_inserted INTEGER,
    records_updated INTEGER,
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Log
DO $$
BEGIN
    RAISE NOTICE 'PostgreSQL Target initialisée - Prêt pour ETL';
END $$;