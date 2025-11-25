-- PostgreSQL Source - Initialisation avec données
CREATE TABLE IF NOT EXISTS employes_source (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    departement VARCHAR(50),
    salaire DECIMAL(10,2),
    date_embauche DATE,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insertion des employés
INSERT INTO employes_source (nom, email, departement, salaire, date_embauche) VALUES
('Béatrice Zoungrana', 'beatrice.zoungrana@entreprise.bf', 'Qualité', 740000, '2019-03-20'),
('Charles Tiendrébéogo', 'charles.tiendrebeogo@entreprise.bf', 'Maintenance', 690000, '2020-08-12'),
('Djénéba Dao', 'djeneba.dao@entreprise.bf', 'Communication', 720000, '2021-01-08'),
('Ernest Kanazoé', 'ernest.kanazoe@entreprise.bf', 'Logistique', 760000, '2019-06-25'),
('Françoise Nabaloum', 'francoise.nabaloum@entreprise.bf', 'Administration', 700000, '2020-11-17'),
('Georges Yaméogo', 'georges.yameogo@entreprise.bf', 'Sécurité', 710000, '2021-07-04'),
('Huguette Koudougou', 'huguette.koudougou@entreprise.bf', 'Formation', 680000, '2022-02-28')
ON CONFLICT (email) DO NOTHING;

-- Message de confirmation
DO $$
BEGIN
    RAISE NOTICE 'PostgreSQL Source initialisée avec % employés', (SELECT COUNT(*) FROM employes_source);
END $$;