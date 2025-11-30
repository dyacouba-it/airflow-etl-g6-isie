SET NAMES utf8mb4;
SET CHARACTER SET utf8mb4;

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
('Valérie Kambou', 'valerie.kambou@entreprise.bf', 'RH', 780000, '2020-02-14'),
('Wendyam Sawadogo', 'wendyam.sawadogo@entreprise.bf', 'Commercial', 810000, '2019-11-07'),
('Yasmine Compaore', 'yasmine.compaore@entreprise.bf', 'Marketing', 750000, '2021-04-22'),
('Zakaria Kabore', 'zakaria.kabore@entreprise.bf', 'Informatique', 980000, '2018-07-15'),
('Adama Guissou', 'adama.guissou@entreprise.bf', 'Operations', 820000, '2020-10-30'),
('Bernadette Zoungrana', 'bernadette.zoungrana@entreprise.bf', 'Qualite', 740000, '2019-06-12'),
('Christophe Nikiema', 'christophe.nikiema@entreprise.bf', 'Maintenance', 695000, '2020-09-08'),
('Djénéba Tapsoba', 'djeneba.tapsoba@entreprise.bf', 'Communication', 725000, '2021-02-17'),
('Édouard Ouattara', 'edouard.ouattara@entreprise.bf', 'Logistique', 765000, '2019-08-23'),
('Fatimata Kindo', 'fatimata.kindo@entreprise.bf', 'Administration', 705000, '2020-12-05'),
('Guillaume Compaoré', 'guillaume.compaore@entreprise.bf', 'Securite', 715000, '2021-06-19'),
('Hamado Yaméogo', 'hamado.yameogo@entreprise.bf', 'Formation', 685000, '2022-01-11'),
('Inès Sawadogo', 'ines.sawadogo@entreprise.bf', 'Recherche', 895000, '2017-04-28'),
('Justin Sankara', 'justin.sankara@entreprise.bf', 'Production', 855000, '2018-11-14'),
('Kadi Kaboré', 'kadi.kabore@entreprise.bf', 'Juridique', 925000, '2019-03-02'),
('Lazare Ouédraogo', 'lazare.ouedraogo@entreprise.bf', 'Achats', 805000, '2020-07-20'),
('Micheline Zongo', 'micheline.zongo@entreprise.bf', 'Ventes', 835000, '2019-09-16'),
('Noaga Ilboudo', 'noaga.ilboudo@entreprise.bf', 'Innovation', 915000, '2018-05-09'),
('Ousséni Traoré', 'ousseni.traore@entreprise.bf', 'Relations Publiques', 765000, '2021-08-03'),
('Pierrette Sana', 'pierrette.sana@entreprise.bf', 'Controle Qualite', 795000, '2020-03-25'),
('Robert Kafando', 'robert.kafando@entreprise.bf', 'Audit Interne', 875000, '2019-12-18'),
('Salamata Compaoré', 'salamata.compaore@entreprise.bf', 'Service Client', 755000, '2020-06-07'),
('Tidiane Ouédraogo', 'tidiane.ouedraogo@entreprise.bf', 'Archives', 685000, '2021-10-22'),
('Viviane Kaboré', 'viviane.kabore@entreprise.bf', 'Informatique', 965000, '2018-02-15'),
('Zacharie Sawadogo', 'zacharie.sawadogo@entreprise.bf', 'RH', 815000, '2019-07-29'),
('Aïssata Nikiéma', 'aissata.nikiema@entreprise.bf', 'Commercial', 825000, '2020-11-12'),
('Basile Yaméogo', 'basile.yameogo@entreprise.bf', 'Marketing', 775000, '2021-05-26'),
('Cécile Sankara', 'cecile.sankara@entreprise.bf', 'Operations', 845000, '2019-10-08'),
('Désiré Zida', 'desire.zida@entreprise.bf', 'Finance', 885000, '2018-06-21'),
('Edwige Ouattara', 'edwige.ouattara@entreprise.bf', 'Logistique', 795000, '2020-08-14'),
('Frédéric Kaboré', 'frederic.kabore@entreprise.bf', 'Administration', 755000, '2021-03-30'),
('Georgette Ilboudo', 'georgette.ilboudo@entreprise.bf', 'Ingenierie', 935000, '2017-09-12'),
('Hervé Compaoré', 'herve.compaore@entreprise.bf', 'Qualite', 775000, '2019-11-25'),
('Irène Zoungrana', 'irene.zoungrana@entreprise.bf', 'Maintenance', 715000, '2020-05-17'),
('Joseph Ouédraogo', 'joseph.ouedraogo@entreprise.bf', 'Communication', 755000, '2021-09-02'),
('Kadidia Sawadogo', 'kadidia.sawadogo@entreprise.bf', 'Formation', 695000, '2020-01-19'),
('Lassané Yaméogo', 'lassane.yameogo@entreprise.bf', 'Securite', 735000, '2019-04-04'),
('Martine Sankara', 'martine.sankara@entreprise.bf', 'Production', 855000, '2018-10-26'),
('Narcisse Kaboré', 'narcisse.kabore@entreprise.bf', 'Achats', 815000, '2020-02-11'),
('Olivia Traoré', 'olivia.traore@entreprise.bf', 'Ventes', 825000, '2019-06-29'),
('Pacôme Nikiéma', 'pacome.nikiema@entreprise.bf', 'Innovation', 905000, '2018-12-15'),
('Raïssa Ouédraogo', 'raissa.ouedraogo@entreprise.bf', 'Juridique', 915000, '2017-07-08'),
('Salif Compaoré', 'salif.compaore@entreprise.bf', 'Relations Publiques', 765000, '2021-11-21'),
('Thérèse Ilboudo', 'therese.ilboudo@entreprise.bf', 'Audit Interne', 865000, '2020-04-03'),
('Urbain Sawadogo', 'urbain.sawadogo@entreprise.bf', 'Service Client', 745000, '2019-08-16'),
('Véronique Kaboré', 'veronique.kabore@entreprise.bf', 'Recherche', 895000, '2018-03-29'),
('Youssouf Yaméogo', 'youssouf.yameogo@entreprise.bf', 'Controle Qualite', 805000, '2020-09-10');

SELECT CONCAT('MySQL Source initialisée avec ', COUNT(*), ' employés') as statut FROM employes_mysql;