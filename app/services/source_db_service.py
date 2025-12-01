"""Service pour gérer les bases de données sources"""
import pymysql
import psycopg2
from datetime import datetime
import os

class SourceDatabaseService:
    """Gestion des bases de données sources"""
    
    def __init__(self):
        # Configuration MySQL Source
        self.mysql_config = {
            'host': os.getenv('MYSQL_SOURCE_HOST', 'mysql-source'),
            'port': int(os.getenv('MYSQL_SOURCE_PORT', '3306')),
            'database': os.getenv('MYSQL_SOURCE_DB', 'source_db'),
            'user': os.getenv('MYSQL_SOURCE_USER', 'mysqluser'),
            'password': os.getenv('MYSQL_SOURCE_PASSWORD', 'mysqlpass'),
            'charset': 'utf8mb4',
            'autocommit': True  # ← CORRECTION: Lire les données à jour
        }
        
        # Configuration PostgreSQL Source
        self.postgres_config = {
            'host': os.getenv('POSTGRES_SOURCE_HOST', 'postgres-source'),
            'port': int(os.getenv('POSTGRES_SOURCE_PORT', '5432')),
            'database': os.getenv('POSTGRES_SOURCE_DB', 'source_db'),
            'user': os.getenv('POSTGRES_SOURCE_USER', 'sourceuser'),
            'password': os.getenv('POSTGRES_SOURCE_PASSWORD', 'sourcepass'),
            'client_encoding': 'utf8'
        }
    
    # ========== MYSQL ==========
    
    def get_mysql_employees(self, limit=200, offset=0):
        """Récupère les employés de MySQL source"""
        conn = None
        try:
            conn = pymysql.connect(**self.mysql_config)
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            
            query = """
            SELECT id, nom, email, departement, salaire, date_embauche, last_updated
            FROM employes_mysql
            ORDER BY id ASC
            LIMIT %s OFFSET %s
            """
            
            cursor.execute(query, (limit, offset))
            results = cursor.fetchall()
            cursor.close()
            
            return [dict(row) for row in results]
            
        except Exception as e:
            raise Exception(f"Erreur MySQL : {str(e)}")
        finally:
            if conn:
                conn.close()
    
    def get_mysql_employee_by_id(self, employee_id):
        """Récupère un employé MySQL par ID"""
        conn = None
        try:
            conn = pymysql.connect(**self.mysql_config)
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            
            query = "SELECT * FROM employes_mysql WHERE id = %s"
            cursor.execute(query, (employee_id,))
            result = cursor.fetchone()
            cursor.close()
            
            return dict(result) if result else None
            
        except Exception as e:
            raise Exception(f"Erreur MySQL : {str(e)}")
        finally:
            if conn:
                conn.close()
    
    def add_to_mysql(self, data):
        """Ajoute un employé dans MySQL source"""
        conn = None
        try:
            conn = pymysql.connect(**self.mysql_config)
            cursor = conn.cursor()
            
            query = """
            INSERT INTO employes_mysql 
            (nom, email, departement, salaire, date_embauche, last_updated)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            
            cursor.execute(query, (
                data['nom'],
                data['email'],
                data.get('departement'),
                data.get('salaire'),
                data.get('date_embauche'),
                datetime.now()
            ))
            
            conn.commit()
            employe_id = cursor.lastrowid
            cursor.close()
            
            return {
                'success': True,
                'id': employe_id,
                'source': 'MySQL'
            }
            
        except Exception as e:
            if conn:
                conn.rollback()
            raise Exception(f"Erreur MySQL : {str(e)}")
        finally:
            if conn:
                conn.close()
    
    def update_mysql_employee(self, employee_id, data):
        """Met à jour un employé dans MySQL source"""
        conn = None
        try:
            conn = pymysql.connect(**self.mysql_config)
            cursor = conn.cursor()
            
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
            
            fields.append('last_updated = %s')
            values.append(datetime.now())
            values.append(employee_id)
            
            query = f"""
            UPDATE employes_mysql
            SET {', '.join(fields)}
            WHERE id = %s
            """
            
            cursor.execute(query, values)
            conn.commit()
            cursor.close()
            
            return {
                'success': True,
                'id': employee_id,
                'source': 'MySQL'
            }
            
        except Exception as e:
            if conn:
                conn.rollback()
            raise Exception(f"Erreur MySQL : {str(e)}")
        finally:
            if conn:
                conn.close()
    
    def delete_mysql_employee(self, employee_id):
        """Supprime un employé de MySQL source"""
        conn = None
        try:
            conn = pymysql.connect(**self.mysql_config)
            cursor = conn.cursor()
            
            query = "DELETE FROM employes_mysql WHERE id = %s"
            cursor.execute(query, (employee_id,))
            
            conn.commit()
            cursor.close()
            
        except Exception as e:
            if conn:
                conn.rollback()
            raise Exception(f"Erreur MySQL : {str(e)}")
        finally:
            if conn:
                conn.close()
    
    def get_mysql_count(self):
        """Compte les employés dans MySQL"""
        conn = None
        try:
            conn = pymysql.connect(**self.mysql_config)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM employes_mysql")
            count = cursor.fetchone()[0]
            cursor.close()
            return count
        finally:
            if conn:
                conn.close()
    
    # ========== POSTGRESQL ==========
    
    def get_postgresql_employees(self, limit=200, offset=0):
        """Récupère les employés de PostgreSQL source"""
        conn = None
        try:
            conn = psycopg2.connect(**self.postgres_config)
            cursor = conn.cursor()
            
            query = """
            SELECT id, nom, email, departement, salaire, date_embauche, last_updated
            FROM employes_source
            ORDER BY id ASC
            LIMIT %s OFFSET %s
            """
            
            cursor.execute(query, (limit, offset))
            columns = [desc[0] for desc in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]
            cursor.close()
            
            return results
            
        except Exception as e:
            raise Exception(f"Erreur PostgreSQL : {str(e)}")
        finally:
            if conn:
                conn.close()
    
    def get_postgresql_employee_by_id(self, employee_id):
        """Récupère un employé PostgreSQL par ID"""
        conn = None
        try:
            conn = psycopg2.connect(**self.postgres_config)
            cursor = conn.cursor()
            
            query = "SELECT * FROM employes_source WHERE id = %s"
            cursor.execute(query, (employee_id,))
            columns = [desc[0] for desc in cursor.description]
            result = cursor.fetchone()
            cursor.close()
            
            return dict(zip(columns, result)) if result else None
            
        except Exception as e:
            raise Exception(f"Erreur PostgreSQL : {str(e)}")
        finally:
            if conn:
                conn.close()
    
    def add_to_postgresql(self, data):
        """Ajoute un employé dans PostgreSQL source"""
        conn = None
        try:
            conn = psycopg2.connect(**self.postgres_config)
            cursor = conn.cursor()
            
            query = """
            INSERT INTO employes_source 
            (nom, email, departement, salaire, date_embauche, last_updated)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id
            """
            
            cursor.execute(query, (
                data['nom'],
                data['email'],
                data.get('departement'),
                data.get('salaire'),
                data.get('date_embauche'),
                datetime.now()
            ))
            
            employe_id = cursor.fetchone()[0]
            conn.commit()
            cursor.close()
            
            return {
                'success': True,
                'id': employe_id,
                'source': 'PostgreSQL'
            }
            
        except Exception as e:
            if conn:
                conn.rollback()
            raise Exception(f"Erreur PostgreSQL : {str(e)}")
        finally:
            if conn:
                conn.close()
    
    def update_postgresql_employee(self, employee_id, data):
        """Met à jour un employé dans PostgreSQL source"""
        conn = None
        try:
            conn = psycopg2.connect(**self.postgres_config)
            cursor = conn.cursor()
            
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
            
            fields.append('last_updated = %s')
            values.append(datetime.now())
            values.append(employee_id)
            
            query = f"""
            UPDATE employes_source
            SET {', '.join(fields)}
            WHERE id = %s
            """
            
            cursor.execute(query, values)
            conn.commit()
            cursor.close()
            
            return {
                'success': True,
                'id': employee_id,
                'source': 'PostgreSQL'
            }
            
        except Exception as e:
            if conn:
                conn.rollback()
            raise Exception(f"Erreur PostgreSQL : {str(e)}")
        finally:
            if conn:
                conn.close()
    
    def delete_postgresql_employee(self, employee_id):
        """Supprime un employé de PostgreSQL source"""
        conn = None
        try:
            conn = psycopg2.connect(**self.postgres_config)
            cursor = conn.cursor()
            
            query = "DELETE FROM employes_source WHERE id = %s"
            cursor.execute(query, (employee_id,))
            
            conn.commit()
            cursor.close()
            
        except Exception as e:
            if conn:
                conn.rollback()
            raise Exception(f"Erreur PostgreSQL : {str(e)}")
        finally:
            if conn:
                conn.close()
    
    def get_postgresql_count(self):
        """Compte les employés dans PostgreSQL"""
        conn = None
        try:
            conn = psycopg2.connect(**self.postgres_config)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM employes_source")
            count = cursor.fetchone()[0]
            cursor.close()
            return count
        finally:
            if conn:
                conn.close()

                # ========== CSV ==========
    
    def get_csv_count(self):
        """Compte le nombre d'employés dans le fichier CSV"""
        import csv
        
        # Chemins possibles pour le fichier CSV
        possible_paths = [
            os.getenv('CSV_FILE_PATH'),
            '/data/data.csv',
            os.path.join(os.getcwd(), 'data', 'data.csv'),
            '/app/data/data.csv',
        ]
        
        # Trouver le fichier CSV
        csv_file = None
        for path in [p for p in possible_paths if p]:
            if os.path.exists(path):
                csv_file = path
                break
        
        # Si le fichier n'existe pas
        if not csv_file:
            return 0
        
        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                return sum(1 for row in reader)
        except Exception as e:
            print(f"Erreur lors du comptage CSV : {str(e)}")
            return 0
    
    def get_csv_employees(self, limit=200, offset=0):
        """Récupère les employés depuis le fichier CSV"""
        import csv
        
        # Chemins possibles pour le fichier CSV
        possible_paths = [
            os.getenv('CSV_FILE_PATH'),
            '/data/data.csv',
            os.path.join(os.getcwd(), 'data', 'data.csv'),
            '/app/data/data.csv',
        ]
        
        # Trouver le fichier CSV
        csv_file = None
        for path in [p for p in possible_paths if p]:
            if os.path.exists(path):
                csv_file = path
                break
        
        if not csv_file:
            return []
        
        try:
            employees = []
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for i, row in enumerate(reader):
                    # Appliquer la pagination
                    if i < offset:
                        continue
                    if len(employees) >= limit:
                        break
                    
                    employees.append({
                        'id': int(row.get('id', 0)) if row.get('id') else i + 1,
                        'nom': row.get('nom', ''),
                        'email': row.get('email', ''),
                        'departement': row.get('departement', ''),
                        'salaire': float(row.get('salaire', 0)) if row.get('salaire') else 0,
                        'date_embauche': row.get('date_embauche', None)
                    })
            
            return employees
            
        except Exception as e:
            print(f"Erreur lors de la lecture CSV : {str(e)}")
            return []