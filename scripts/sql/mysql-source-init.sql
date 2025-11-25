-- MySQL Source - Initialisation avec données
CREATE TABLE IF NOT EXISTS employes_mysql (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nom VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    departement VARCHAR(50),
    salaire DECIMAL(10,2),
    date_embauche DATE,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Insertion des employés
INSERT IGNORE INTO employes_mysql (nom, email, departement, salaire, date_embauche) VALUES
('Rasmané Ouedraogo', 'rasmane.ouedraogo@entreprise.bf', 'Direction Generale', 1200000, '2017-01-10'),
('Safiatou Sankara', 'safiatou.sankara@entreprise.bf', 'Finance', 850000, '2019-05-18'),
('Tegawendé Ilboudo', 'tegawende.ilboudo@entreprise.bf', 'Ingenierie', 920000, '2018-09-23'),
('Valérie Kambou', 'valerie.kambou@entreprise.bf', 'Ressources Humaines', 780000, '2020-02-14'),
('Wendyam Sawadogo', 'wendyam.sawadogo@entreprise.bf', 'Commercial', 810000, '2019-11-07'),
('Yasmine Compaore', 'yasmine.compaore@entreprise.bf', 'Marketing', 750000, '2021-04-22'),
('Zakaria Kabore', 'zakaria.kabore@entreprise.bf', 'Informatique', 980000, '2018-07-15'),
('Adama Guissou', 'adama.guissou@entreprise.bf', 'Operations', 820000, '2020-10-30');

SELECT CONCAT('MySQL Source initialisée avec ', COUNT(*), ' employés') as statut FROM employes_mysql;