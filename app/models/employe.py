"""Modèle de données pour les employés"""

class Employe:
    def __init__(self, id, source, source_id, nom, email, departement, salaire, date_embauche, created_at, updated_at):
        self.id = id
        self.source = source
        self.source_id = source_id
        self.nom = nom
        self.email = email
        self.departement = departement
        self.salaire = float(salaire) if salaire else None
        self.date_embauche = str(date_embauche) if date_embauche else None
        self.created_at = str(created_at) if created_at else None
        self.updated_at = str(updated_at) if updated_at else None
    
    def to_dict(self):
        """Convertit l'employé en dictionnaire"""
        return {
            'id': self.id,
            'source': self.source,
            'source_id': self.source_id,
            'nom': self.nom,
            'email': self.email,
            'departement': self.departement,
            'salaire': self.salaire,
            'date_embauche': self.date_embauche,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }