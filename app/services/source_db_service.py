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
            'charset': 'utf8mb4'
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
    
    def get_mysql_employees(self, limit=100, offset=0):
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
    
    def get_postgresql_employees(self, limit=100, offset=0):
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
                conn.close()    # ========== CSV (avec fallback vers base unifiée) ==========
    
    def get_csv_count(self):
        """
        Compte les employés CSV depuis le fichier source.
        Si le fichier n'est pas trouvé, compte depuis la base unifiée (fallback).
        """
        import sys
        
        try:
            # Chemins possibles pour le fichier CSV (ordre de priorité)
            possible_paths = [
                os.getenv('CSV_FILE_PATH'),                                    # 1. Variable d'environnement
                '/data/data.csv',                                              # 2. Depuis racine projet (Docker)
                os.path.join(os.getcwd(), 'data', 'data.csv'),                # 3. Relatif depuis CWD
                os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'data', 'data.csv'),  # 4. Relatif depuis ce fichier
                '/app/data/data.csv',                                          # 5. Si l'app est dans /app
                '/opt/airflow/data/data.csv',                                  # 6. Si Airflow partage le volume
                os.path.join(os.path.expanduser('~'), 'data', 'data.csv'),   # 7. Home directory
            ]
            
            # Filtrer les None
            possible_paths = [p for p in possible_paths if p]
            
            csv_file = None
            for path in possible_paths:
                print(f"[CSV] Tentative : {path}", file=sys.stderr)
                if os.path.exists(path):
                    csv_file = path
                    print(f"[CSV] ✅ Fichier trouvé : {csv_file}", file=sys.stderr)
                    break
            
            if csv_file:
                # Compter les lignes (en excluant l'en-tête)
                with open(csv_file, 'r', encoding='utf-8') as f:
                    lines = [line for line in f if line.strip()]  # Lignes non vides
                    line_count = len(lines)
                    # Soustraire 1 pour l'en-tête (si présent)
                    data_count = max(0, line_count - 1)
                
                print(f"[CSV] ✅ Fichier : Total lignes={line_count}, Données={data_count}", file=sys.stderr)
                return data_count
            
            # FALLBACK : Compter depuis la base unifiée
            print(f"[CSV] ⚠️ Fichier non trouvé, utilisation du FALLBACK (base unifiée)", file=sys.stderr)
            print(f"[CSV] Chemins testés : {possible_paths}", file=sys.stderr)
            
            try:
                import psycopg2
                target_db = os.getenv('TARGET_DB')
                if not target_db:
                    print(f"[CSV] ❌ TARGET_DB non définie", file=sys.stderr)
                    return 0
                
                conn = psycopg2.connect(target_db)
                cursor = conn.cursor()
                
                # Compter les employés CSV dans la base unifiée
                query = "SELECT COUNT(*) FROM employes_unified WHERE LOWER(source) = 'csv'"
                cursor.execute(query)
                count = cursor.fetchone()[0]
                
                cursor.close()
                conn.close()
                
                print(f"[CSV] ✅ FALLBACK : {count} employés CSV dans la base unifiée", file=sys.stderr)
                return count
                
            except Exception as e:
                print(f"[CSV] ❌ FALLBACK échoué : {str(e)}", file=sys.stderr)
                return 0
        
        except FileNotFoundError as e:
            print(f"[CSV] ❌ FileNotFoundError : {str(e)}", file=sys.stderr)
            return 0
        except Exception as e:
            print(f"[CSV] ❌ Erreur : {type(e).__name__} - {str(e)}", file=sys.stderr)
            import traceback
            traceback.print_exc(file=sys.stderr)
            return 0
