from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.providers.mysql.hooks.mysql import MySqlHook
import pandas as pd
import logging

# Configuration
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'etl_employe_sync',
    default_args=default_args,
    description='Synchronisation ETL des employés - CSV, MySQL, PostgreSQL',
    schedule_interval='@daily',
    catchup=False,
    is_paused_upon_creation=False, 
    tags=['etl', 'employes', 'sync', 'exercice14', 'burkinabe'],
)

# ==================== EXTRACTION ====================

def extract_from_csv(**context):
    """Extrait les données du fichier CSV"""
    try:
        logging.info("=== EXTRACTION CSV ===")
        csv_path = '/opt/airflow/data/data.csv'
        
        # CORRECTION: Ajout de l'encodage UTF-8
        df = pd.read_csv(csv_path, encoding='utf-8')
        df['source'] = 'CSV'
        df['source_id'] = df['id']
        
        # Convertir les dates en strings pour XCom
        df['date_embauche'] = df['date_embauche'].astype(str)
        if 'last_updated' in df.columns:
            df['last_updated'] = df['last_updated'].astype(str)

        context['task_instance'].xcom_push(key='csv_data', value=df.to_dict('records'))
        
        logging.info(f"CSV : {len(df)} enregistrements extraits avec succès")
        return {'status': 'success', 'count': len(df)}
    except Exception as e:
        logging.error(f"Erreur lors de l'extraction CSV : {str(e)}")
        raise

def fix_encoding(text):
    """Corrige le double encodage UTF-8 (latin1 -> utf8 mal interprété)"""
    if text is None:
        return text
    if not isinstance(text, str):
        return text
    try:
        if 'Ã' in text or 'Â' in text:
            return text.encode('latin1').decode('utf-8')
    except (UnicodeDecodeError, UnicodeEncodeError):
        pass
    return text

def extract_from_mysql(**context):
    """Extrait les données de la base MySQL"""
    try:
        logging.info("=== EXTRACTION MYSQL ===")
        
        mysql_hook = MySqlHook(mysql_conn_id='mysql_source_conn')
        
        # Exécuter SET NAMES pour forcer UTF-8
        conn = mysql_hook.get_conn()
        cursor = conn.cursor()
        cursor.execute("SET NAMES utf8mb4")
        cursor.execute("SET CHARACTER SET utf8mb4")
        cursor.close()
        
        sql = """
        SELECT id, nom, email, departement, salaire, date_embauche, last_updated
        FROM employes_mysql
        WHERE last_updated >= DATE_SUB(NOW(), INTERVAL 30 DAY)
        """
        
        # Lecture avec pandas
        df = pd.read_sql(sql, conn)
        conn.close()
        
        # CORRECTION AUTOMATIQUE: Réparer l'encodage des champs texte
        logging.info("Correction automatique de l'encodage UTF-8...")
        for col in ['nom', 'email', 'departement']:
            if col in df.columns:
                df[col] = df[col].apply(fix_encoding)
        
        df['source'] = 'MySQL'
        df['source_id'] = df['id']
        
        # Convertir les dates en strings pour XCom
        df['date_embauche'] = df['date_embauche'].astype(str)
        if 'last_updated' in df.columns:
            df['last_updated'] = df['last_updated'].astype(str)

        context['task_instance'].xcom_push(key='mysql_data', value=df.to_dict('records'))
        
        logging.info(f"MySQL : {len(df)} enregistrements extraits avec succès")
        return {'status': 'success', 'count': len(df)}
    except Exception as e:
        logging.error(f"Erreur lors de l'extraction MySQL : {str(e)}")
        raise

def extract_from_postgres(**context):
    """Extrait les données de la base PostgreSQL source"""
    try:
        logging.info("=== EXTRACTION POSTGRESQL ===")
        
        pg_hook = PostgresHook(postgres_conn_id='postgres_source_conn')
        sql = """
        SELECT id, nom, email, departement, salaire, date_embauche, last_updated
        FROM employes_source
        WHERE last_updated >= NOW() - INTERVAL '30 days'
        """
        
        df = pg_hook.get_pandas_df(sql)
        df['source'] = 'PostgreSQL'
        df['source_id'] = df['id']
        
        # Convertir les dates en strings pour XCom
        df['date_embauche'] = df['date_embauche'].astype(str)
        if 'last_updated' in df.columns:
            df['last_updated'] = df['last_updated'].astype(str)

        context['task_instance'].xcom_push(key='postgres_data', value=df.to_dict('records'))
        
        logging.info(f"PostgreSQL : {len(df)} enregistrements extraits avec succès")
        return {'status': 'success', 'count': len(df)}
    except Exception as e:
        logging.error(f"Erreur lors de l'extraction PostgreSQL : {str(e)}")
        raise

# ==================== TRANSFORMATION ====================

def transform_data(**context):
    """Transforme et nettoie les données extraites"""
    try:
        logging.info("=== TRANSFORMATION DES DONNÉES ===")
        
        # Récupération des données depuis XCom
        csv_data = context['task_instance'].xcom_pull(key='csv_data', task_ids='extract_csv')
        mysql_data = context['task_instance'].xcom_pull(key='mysql_data', task_ids='extract_mysql')
        postgres_data = context['task_instance'].xcom_pull(key='postgres_data', task_ids='extract_postgres')
        
        # Conversion en DataFrames
        dfs = []
        if csv_data:
            dfs.append(pd.DataFrame(csv_data))
            logging.info(f"CSV : {len(csv_data)} enregistrements")
        if mysql_data:
            dfs.append(pd.DataFrame(mysql_data))
            logging.info(f"MySQL : {len(mysql_data)} enregistrements")
        if postgres_data:
            dfs.append(pd.DataFrame(postgres_data))
            logging.info(f"PostgreSQL : {len(postgres_data)} enregistrements")
        
        if not dfs:
            logging.warning("Aucune donnée à transformer")
            context['task_instance'].xcom_push(key='transformed_data', value=[])
            return {'status': 'empty', 'count': 0}
        
        # Fusion des données
        df = pd.concat(dfs, ignore_index=True)
        logging.info(f"Fusion : {len(df)} enregistrements au total")
        
        # Transformations
        logging.info("Application des transformations...")
        df['email'] = df['email'].str.lower().str.strip()
        df['departement'] = df['departement'].str.title()
        df['salaire'] = pd.to_numeric(df['salaire'], errors='coerce')
        df['date_embauche'] = pd.to_datetime(df['date_embauche'], errors='coerce')
        
        # Nettoyage
        avant_nettoyage = len(df)
        df = df.dropna(subset=['email', 'nom'])
        df = df.drop_duplicates(subset=['email'], keep='last')
        apres_nettoyage = len(df)
        
        if avant_nettoyage != apres_nettoyage:
            logging.info(f"Nettoyage : {avant_nettoyage - apres_nettoyage} doublons/invalides supprimés")
        
        # Convertir TOUTES les colonnes datetime en strings pour XCom
        for col in df.columns:
            if pd.api.types.is_datetime64_any_dtype(df[col]):
                df[col] = df[col].astype(str)

        context['task_instance'].xcom_push(key='transformed_data', value=df.to_dict('records'))
        
        logging.info(f"Transformation terminée : {len(df)} enregistrements prêts")
        return {'status': 'success', 'count': len(df)}
    except Exception as e:
        logging.error(f"Erreur lors de la transformation : {str(e)}")
        raise

# ==================== COMPARAISON ====================

def compare_and_prepare(**context):
    """Compare les données avec la base cible et prépare les opérations"""
    try:
        logging.info("=== COMPARAISON ET PRÉPARATION ===")
        
        transformed_data = context['task_instance'].xcom_pull(
            key='transformed_data', 
            task_ids='transform_data'
        )
        
        if not transformed_data:
            logging.warning("Aucune donnée à comparer")
            context['task_instance'].xcom_push(key='insert_data', value=[])
            context['task_instance'].xcom_push(key='update_data', value=[])
            return {'inserts': 0, 'updates': 0}
        
        df_new = pd.DataFrame(transformed_data)
        pg_hook = PostgresHook(postgres_conn_id='postgres_target_conn')
        
        logging.info("Récupération des données existantes...")
        sql_existing = "SELECT source, source_id, email, salaire, departement FROM employes_unified"
        df_existing = pg_hook.get_pandas_df(sql_existing)
        logging.info(f"Base cible : {len(df_existing)} enregistrements existants")
        
        inserts = []
        updates = []
        
        logging.info("Analyse des différences...")
        for _, row in df_new.iterrows():
            existing = df_existing[df_existing['email'] == row['email']]
            
            if existing.empty:
                # Nouvel enregistrement
                inserts.append(row.to_dict())
            else:
                # Vérifier si mise à jour nécessaire
                ex_row = existing.iloc[0]
                if (str(ex_row['salaire']) != str(row['salaire']) or 
                    str(ex_row['departement']) != str(row['departement'])):
                    updates.append(row.to_dict())
        
        context['task_instance'].xcom_push(key='insert_data', value=inserts)
        context['task_instance'].xcom_push(key='update_data', value=updates)
        
        logging.info(f"Résultat : {len(inserts)} insertions, {len(updates)} mises à jour à effectuer")
        return {'inserts': len(inserts), 'updates': len(updates)}
        
    except Exception as e:
        logging.error(f"Erreur lors de la comparaison : {str(e)}")
        raise

# ==================== CHARGEMENT ====================

def load_to_target(**context):
    """Charge les données dans la base PostgreSQL cible"""
    try:
        logging.info("=== CHARGEMENT DANS LA BASE CIBLE ===")
        
        insert_data = context['task_instance'].xcom_pull(key='insert_data', task_ids='compare_and_prepare')
        update_data = context['task_instance'].xcom_pull(key='update_data', task_ids='compare_and_prepare')
        
        pg_hook = PostgresHook(postgres_conn_id='postgres_target_conn')
        conn = pg_hook.get_conn()
        cursor = conn.cursor()
        
        inserts_count = 0
        updates_count = 0
        
        try:
            # Insertions
            if insert_data:
                logging.info(f"Insertion de {len(insert_data)} nouveaux enregistrements...")
                insert_sql = """
                INSERT INTO employes_unified 
                (source, source_id, nom, email, departement, salaire, date_embauche, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                for record in insert_data:
                    cursor.execute(insert_sql, (
                        record['source'],
                        record.get('source_id'),
                        record['nom'],
                        record['email'],
                        record['departement'],
                        record['salaire'],
                        record['date_embauche'],
                        datetime.now(),
                        datetime.now()
                    ))
                    inserts_count += 1
                logging.info(f"{inserts_count} enregistrements insérés")
            
            # Mises à jour
            if update_data:
                logging.info(f"Mise à jour de {len(update_data)} enregistrements...")
                update_sql = """
                UPDATE employes_unified
                SET salaire = %s, departement = %s, updated_at = %s
                WHERE email = %s
                """
                for record in update_data:
                    cursor.execute(update_sql, (
                        record['salaire'],
                        record['departement'],
                        datetime.now(),
                        record['email']
                    ))
                    updates_count += 1
                logging.info(f"{updates_count} enregistrements mis à jour")
            
            conn.commit()
            logging.info(f"Chargement terminé avec succès")
            logging.info(f"Récapitulatif : {inserts_count} insertions, {updates_count} mises à jour")
            
            return {'inserts': inserts_count, 'updates': updates_count}
        except Exception as e:
            conn.rollback()
            logging.error(f"Rollback effectué suite à l'erreur")
            raise
        finally:
            cursor.close()
            conn.close()
    except Exception as e:
        logging.error(f"Erreur lors du chargement : {str(e)}")
        raise

# ==================== VALIDATION ====================

def validate_data(**context):
    """Valide l'intégrité des données dans la base cible"""
    try:
        logging.info("=== VALIDATION DES DONNÉES ===")
        
        pg_hook = PostgresHook(postgres_conn_id='postgres_target_conn')
        
        # Comptage total
        logging.info("Comptage des enregistrements...")
        total_sql = "SELECT COUNT(*) as total FROM employes_unified"
        total_records = pg_hook.get_first(total_sql)[0]
        logging.info(f"Total : {total_records} employés dans la base unifiée")
        
        # Comptage par source
        source_sql = "SELECT source, COUNT(*) as count FROM employes_unified GROUP BY source ORDER BY source"
        source_counts = pg_hook.get_pandas_df(source_sql)
        for _, row in source_counts.iterrows():
            logging.info(f"{row['source']} : {row['count']} employés")
        
        # Vérification doublons
        logging.info("Vérification des doublons...")
        duplicates_sql = """
        SELECT email, COUNT(*) as count
        FROM employes_unified
        GROUP BY email
        HAVING COUNT(*) > 1
        """
        duplicates_df = pg_hook.get_pandas_df(duplicates_sql)
        
        if len(duplicates_df) > 0:
            logging.warning(f"{len(duplicates_df)} doublons détectés !")
        else:
            logging.info("Aucun doublon détecté")
        
        # Vérification valeurs nulles
        logging.info("Vérification de l'intégrité...")
        null_check_sql = """
        SELECT 
            SUM(CASE WHEN email IS NULL THEN 1 ELSE 0 END) as null_emails,
            SUM(CASE WHEN nom IS NULL THEN 1 ELSE 0 END) as null_names,
            SUM(CASE WHEN salaire < 0 THEN 1 ELSE 0 END) as negative_salaries
        FROM employes_unified
        """
        null_result = pg_hook.get_first(null_check_sql)
        
        if null_result[0] > 0:
            logging.warning(f"{null_result[0]} emails NULL détectés")
        if null_result[1] > 0:
            logging.warning(f"{null_result[1]} noms NULL détectés")
        if null_result[2] > 0:
            logging.warning(f"{null_result[2]} salaires négatifs détectés")
        
        validation_passed = (
            len(duplicates_df) == 0 and 
            null_result[0] == 0 and 
            null_result[1] == 0 and
            null_result[2] == 0
        )
        
        results = {
            'total_records': total_records,
            'duplicates_found': len(duplicates_df),
            'null_emails': null_result[0],
            'null_names': null_result[1],
            'negative_salaries': null_result[2],
            'validation_passed': validation_passed
        }
        
        if validation_passed:
            logging.info(f"Validation réussie : Toutes les vérifications sont passées")
            logging.info(f"{total_records} employés correctement synchronisés")
        else:
            logging.warning(f"Validation terminée avec des avertissements")
        
        return results
    except Exception as e:
        logging.error(f"Erreur lors de la validation : {str(e)}")
        raise

# ==================== DÉFINITION DES TÂCHES ====================

task_extract_csv = PythonOperator(
    task_id='extract_csv',
    python_callable=extract_from_csv,
    dag=dag,
)

task_extract_mysql = PythonOperator(
    task_id='extract_mysql',
    python_callable=extract_from_mysql,
    dag=dag,
)

task_extract_postgres = PythonOperator(
    task_id='extract_postgres',
    python_callable=extract_from_postgres,
    dag=dag,
)

task_transform = PythonOperator(
    task_id='transform_data',
    python_callable=transform_data,
    dag=dag,
)

task_compare = PythonOperator(
    task_id='compare_and_prepare',
    python_callable=compare_and_prepare,
    dag=dag,
)

task_load = PythonOperator(
    task_id='load_to_target',
    python_callable=load_to_target,
    dag=dag,
)

task_validate = PythonOperator(
    task_id='validate_data',
    python_callable=validate_data,
    dag=dag,
)

# ==================== DÉPENDANCES ====================

[task_extract_csv, task_extract_mysql, task_extract_postgres] >> task_transform >> task_compare >> task_load >> task_validate
