"""Service de connexion à la base de données PostgreSQL"""
import psycopg2
from psycopg2.extras import RealDictCursor
import os

class DatabaseService:
    def __init__(self):
        self.conn_params = {
            'host': os.getenv('POSTGRES_HOST', 'postgres-target'),
            'port': os.getenv('POSTGRES_PORT', '5432'),
            'database': os.getenv('POSTGRES_DB', 'target_db'),
            'user': os.getenv('POSTGRES_USER', 'targetuser'),
            'password': os.getenv('POSTGRES_PASSWORD', 'targetpass'),
            'client_encoding': 'utf8'
        }
    
    def get_connection(self):
        """Crée une connexion à la base de données"""
        return psycopg2.connect(**self.conn_params)
    
    def execute_query(self, query, params=None, fetch_one=False):
        """Exécute une requête SQL"""
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute(query, params)
            
            if fetch_one:
                result = cursor.fetchone()
            else:
                result = cursor.fetchall()
            
            cursor.close()
            return result
        except Exception as e:
            raise Exception(f"Erreur base de données : {str(e)}")
        finally:
            if conn:
                conn.close()
    
    def get_all_employes(self, source=None, departement=None, statut=None, limit=200, offset=0):
        """Récupère tous les employés avec filtres optionnels"""
        query = "SELECT * FROM employes_unified WHERE 1=1"
        params = []
        
        if source:
            query += " AND source = %s"
            params.append(source)
        
        if departement:
            query += " AND departement = %s"
            params.append(departement)

        if statut:
            #query += " AND statut = %s"
            query += " AND statut ILIKE %s"
            params.append(statut)

        query += " ORDER BY id LIMIT %s OFFSET %s"
        params.extend([limit, offset])
        
        return self.execute_query(query, params)
    
    def get_employe_by_id(self, employe_id):
        """Récupère un employé par son ID"""
        query = "SELECT * FROM employes_unified WHERE id = %s"
        return self.execute_query(query, (employe_id,), fetch_one=True)
    
    def get_stats_global(self):
        """Récupère les statistiques globales"""
        query = """
        SELECT 
            COUNT(*) as total_employes,
            COUNT(DISTINCT source) as nb_sources,
            COUNT(DISTINCT departement) as nb_departements,
            AVG(salaire) as salaire_moyen,
            MIN(salaire) as salaire_min,
            MAX(salaire) as salaire_max
        FROM employes_unified
        """
        return self.execute_query(query, fetch_one=True)
    
    def get_stats_by_source(self):
        """Récupère les statistiques par source"""
        query = """
        SELECT 
            source,
            COUNT(*) as count,
            AVG(salaire) as salaire_moyen
        FROM employes_unified
        GROUP BY source
        ORDER BY source
        """
        return self.execute_query(query)
    
    def get_stats_by_departement(self):
        """Récupère les statistiques par département"""
        query = """
        SELECT 
            departement,
            COUNT(*) as count,
            AVG(salaire) as salaire_moyen
        FROM employes_unified
        GROUP BY departement
        ORDER BY count DESC
        """
        return self.execute_query(query)
    
    def get_last_sync_info(self):
        """Récupère les informations de la dernière synchronisation"""
        query = """
        SELECT 
            MAX(updated_at) as derniere_maj,
            COUNT(*) as total
        FROM employes_unified
        """
        return self.execute_query(query, fetch_one=True)
    
    def create_employe(self, data):
        """Crée un nouvel employé"""
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            query = """
            INSERT INTO employes_unified 
            (source, source_id, nom, email, departement, salaire, date_embauche, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING *
            """
            
            from datetime import datetime
            cursor.execute(query, (
                data.get('source', 'Manuel'),
                data.get('source_id'),
                data['nom'],
                data['email'],
                data['departement'],
                data['salaire'],
                data.get('date_embauche'),
                datetime.now(),
                datetime.now()
            ))
            
            result = cursor.fetchone()
            conn.commit()
            cursor.close()
            
            return dict(result)
        except Exception as e:
            if conn:
                conn.rollback()
            raise Exception(f"Erreur création : {str(e)}")
        finally:
            if conn:
                conn.close()
    
    def update_employe(self, employe_id, data):
        """Met à jour un employé"""
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            # Construire la requête dynamiquement
            fields = []
            values = []
            
            if 'nom' in data:
                fields.append('nom = %s')
                values.append(data['nom'])
            if 'email' in data:
                fields.append('email = %s')
                values.append(data['email'])
            if 'departement' in data:
                fields.append('departement = %s')
                values.append(data['departement'])
            if 'salaire' in data:
                fields.append('salaire = %s')
                values.append(data['salaire'])
            if 'date_embauche' in data:
                fields.append('date_embauche = %s')
                values.append(data['date_embauche'])
            
            from datetime import datetime
            fields.append('updated_at = %s')
            values.append(datetime.now())
            values.append(employe_id)
            
            query = f"""
            UPDATE employes_unified
            SET {', '.join(fields)}
            WHERE id = %s
            RETURNING *
            """
            
            cursor.execute(query, values)
            result = cursor.fetchone()
            conn.commit()
            cursor.close()
            
            return dict(result)
        except Exception as e:
            if conn:
                conn.rollback()
            raise Exception(f"Erreur mise à jour : {str(e)}")
        finally:
            if conn:
                conn.close()
    
    def delete_employe(self, employe_id):
        """Supprime un employé"""
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            query = "DELETE FROM employes_unified WHERE id = %s"
            cursor.execute(query, (employe_id,))
            
            conn.commit()
            cursor.close()
        except Exception as e:
            if conn:
                conn.rollback()
            raise Exception(f"Erreur suppression : {str(e)}")
        finally:
            if conn:
                conn.close()