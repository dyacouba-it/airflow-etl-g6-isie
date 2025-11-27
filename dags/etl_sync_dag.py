# -*- coding: utf-8 -*-
"""
DAG ETL (Version Finale - Production Ready)
- Correction des problèmes de dates
- Gestion robuste des types de données
- Synchronisation correcte actif/inactif
- Logs détaillés pour le débogage
"""
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.providers.mysql.hooks.mysql import MySqlHook
from airflow.exceptions import AirflowException

import pandas as pd
import logging
import traceback
from typing import List, Dict, Any, Optional

# -----------------------
# Configuration du logging
# -----------------------
logger = logging.getLogger(__name__)

# -----------------------
# DAG config
# -----------------------
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
    'email_on_failure': True,
    'email_on_retry': False
}

dag = DAG(
    'etl_employeFN',
    default_args=default_args,
    schedule_interval='@daily',
    catchup=False,
    max_active_runs=1,
    is_paused_upon_creation=False,
    description="ETL synchronisation employés - Version Finale Corrigée",
    tags=['ETL', 'employes', 'production']
)

# -----------------------
# Constantes et utilitaires
# -----------------------
EXPECTED_COLS = ["nom", "email", "departement", "salaire", "date_embauche", "source", "source_id"]
EMAIL_PATTERN = r'^[^@]+@[^@]+\.[^@]+'

def normalize_str(s: Any) -> str:
    """Normalise les chaînes de caractères"""
    if pd.isna(s) or s is None:
        return ''
    return str(s).strip().lower()

def safe_normalize_date(date_val: Any) -> Optional[datetime.date]:
    """Normalise les dates de manière robuste pour la base de données"""
    if date_val is None or pd.isna(date_val) or date_val == '':
        return None
    
    try:
        # Si c'est déjà un objet date/datetime
        if isinstance(date_val, (datetime, pd.Timestamp)):
            return date_val.date() if hasattr(date_val, 'date') else date_val
        
        # Gestion des timestamps numériques (provenant de JSON)
        if isinstance(date_val, (int, float)):
            # Détection si timestamp en millisecondes ou secondes
            if date_val > 1000000000000:  # Millisecondes
                date_val = date_val / 1000
            return datetime.fromtimestamp(date_val).date()
        
        # Gestion des strings
        if isinstance(date_val, str):
            date_val = date_val.strip()
            if not date_val:
                return None
                
        # Conversion via pandas (plus robuste)
        dt = pd.to_datetime(date_val, errors='coerce')
        if pd.isna(dt):
            logger.warning(f"Impossible de parser la date: {date_val}")
            return None
        return dt.date()
        
    except Exception as e:
        logger.warning(f"Erreur normalisation date '{date_val}': {e}")
        return None

def dates_equal(a: Any, b: Any) -> bool:
    """Compare deux dates avec normalisation"""
    d1 = safe_normalize_date(a)
    d2 = safe_normalize_date(b)
    if d1 is None and d2 is None:
        return True
    if d1 is None or d2 is None:
        return False
    return d1 == d2

def ensure_columns(df: pd.DataFrame, cols: List[str] = EXPECTED_COLS) -> pd.DataFrame:
    """Assure que le DataFrame contient toutes les colonnes attendues"""
    for c in cols:
        if c not in df.columns:
            df[c] = None
    return df[cols]

def validate_schema(df: pd.DataFrame) -> None:
    """Valide le schéma et la qualité des données"""
    missing_cols = set(EXPECTED_COLS) - set(df.columns)
    if missing_cols:
        raise AirflowException(f"Colonnes manquantes: {missing_cols}")

def test_database_connection(conn_id: str, db_type: str = 'postgres') -> bool:
    """Teste la connexion à la base de données"""
    try:
        if db_type == 'mysql':
            hook = MySqlHook(mysql_conn_id=conn_id)
        else:
            hook = PostgresHook(postgres_conn_id=conn_id)
        
        conn = hook.get_conn()
        conn.close()
        logger.info(f"✓ Connexion {conn_id} ({db_type}) testée avec succès")
        return True
    except Exception as e:
        logger.error(f"✗ Échec connexion {conn_id} ({db_type}): {e}")
        raise AirflowException(f"Connexion {conn_id} indisponible: {e}")

# -----------------------
# EXTRACTIONS
# -----------------------
def extract_csv(**kwargs) -> str:
    """Extraction CSV"""
    logger.info("=== EXTRACTION CSV ===")
    ti = kwargs['ti']
    
    try:
        df = pd.read_csv('/opt/airflow/data/data.csv', encoding='utf-8')
        df['source'] = 'csv'
        df['source_id'] = df.get('id', pd.Series([None]*len(df))).astype(str)
        df = ensure_columns(df)
        
        validate_schema(df)
        
        ti.xcom_push(key='csv_data', value=df.to_json(date_format='iso'))
        logger.info(f"✓ CSV extrait : {len(df)} lignes")
        return f"CSV extraction ok - {len(df)} lignes"
    except Exception as e:
        logger.error(f"Erreur extraction CSV: {e}")
        ti.xcom_push(key='csv_data', value=pd.DataFrame(columns=EXPECTED_COLS).to_json())
        raise

def extract_mysql(**kwargs) -> str:
    """Extraction MySQL"""
    logger.info("=== EXTRACTION MYSQL ===")
    ti = kwargs['ti']
    
    test_database_connection('mysql_source_conn', 'mysql')
    
    hook = MySqlHook(mysql_conn_id='mysql_source_conn')
    df = hook.get_pandas_df("SELECT id, nom, email, departement, salaire, date_embauche FROM employes_mysql")
    df['source'] = 'mysql'
    df['source_id'] = df['id'].astype(str)
    df = ensure_columns(df)
    
    validate_schema(df)
    
    ti.xcom_push(key='mysql_data', value=df.to_json(date_format='iso'))
    logger.info(f"✓ MySQL extrait : {len(df)} lignes")
    return f"MySQL extraction ok - {len(df)} lignes"

def extract_postgres(**kwargs) -> str:
    """Extraction PostgreSQL"""
    logger.info("=== EXTRACTION POSTGRESQL ===")
    ti = kwargs['ti']
    
    test_database_connection('postgres_source_conn', 'postgres')
    
    hook = PostgresHook(postgres_conn_id='postgres_source_conn')
    df = hook.get_pandas_df("SELECT id, nom, email, departement, salaire, date_embauche FROM employes_source")
    df['source'] = 'postgresql'
    df['source_id'] = df['id'].astype(str)
    df = ensure_columns(df)
    
    validate_schema(df)
    
    ti.xcom_push(key='pgsql_data', value=df.to_json(date_format='iso'))
    logger.info(f"✓ PostgreSQL extrait : {len(df)} lignes")
    return f"PostgreSQL extraction ok - {len(df)} lignes"

# -----------------------
# TRANSFORMATION
# -----------------------
def transform_data(**kwargs) -> str:
    """Transformation et consolidation des données"""
    logger.info("=== TRANSFORMATION ===")
    ti = kwargs['ti']
    
    try:
        # Récupération des données depuis XCom
        csv_j = ti.xcom_pull(key='csv_data') or '[]'
        mysql_j = ti.xcom_pull(key='mysql_data') or '[]'
        pg_j = ti.xcom_pull(key='pgsql_data') or '[]'
        
        dfs = []
        for j, source in zip([csv_j, mysql_j, pg_j], ['csv', 'mysql', 'postgresql']):
            try:
                if not j or j == '[]':
                    logger.info(f"Aucune donnée pour {source}")
                    continue
                d = pd.read_json(j)
                if not d.empty:
                    dfs.append(d)
                    logger.info(f"Données {source}: {len(d)} lignes")
            except Exception as e:
                logger.warning(f"Impossible de parser XCom JSON pour {source}: {e}")

        # Consolidation
        if dfs:
            df = pd.concat(dfs, ignore_index=True, sort=False)
            # Déduplication basée sur l'email (priorité aux dernières occurrences)
            initial_count = len(df)
            df = df.drop_duplicates(subset=['email'], keep='last')
            deduplicated_count = initial_count - len(df)
            if deduplicated_count > 0:
                logger.info(f"Déduplication: {deduplicated_count} doublons supprimés")
        else:
            df = pd.DataFrame(columns=EXPECTED_COLS)
            logger.info("Aucune donnée à transformer")

        # Normalisation des dates pour assurer la cohérence
        df['date_embauche'] = df['date_embauche'].apply(safe_normalize_date)
        
        # Validation finale
        validate_schema(df)
        df = ensure_columns(df)
        
        ti.xcom_push(key='transformed_data', value=df.to_json(date_format='iso'))
        logger.info(f"✓ Transformation terminée: {len(df)} lignes")
        return f"Transformation ok - {len(df)} lignes"
        
    except Exception as e:
        logger.error(f"Erreur transformation: {e}")
        ti.xcom_push(key='transformed_data', value=pd.DataFrame(columns=EXPECTED_COLS).to_json())
        raise AirflowException(f"Échec transformation: {e}")

# -----------------------
# COMPARAISON ET PREPARATION
# -----------------------
def compare_and_prepare(**kwargs) -> str:
    """Compare les données et prépare les inserts/updates"""
    logger.info("=== COMPARAISON ET PREPARATION ===")
    ti = kwargs['ti']
    
    try:
        tjson = ti.xcom_pull(key='transformed_data')
        if not tjson:
            logger.info("Aucune donnée transformée -> rien à comparer")
            ti.xcom_push(key='inserts', value=[])
            ti.xcom_push(key='updates', value=[])
            return "0/0"

        df_new = pd.read_json(tjson)
        if df_new.empty:
            logger.info("DataFrame transformé vide -> rien à comparer")
            ti.xcom_push(key='inserts', value=[])
            ti.xcom_push(key='updates', value=[])
            return "0/0"

        # Lecture des données existantes - TOUS les statuts
        test_database_connection('postgres_target_conn', 'postgres')
        hook = PostgresHook(postgres_conn_id='postgres_target_conn')
        
        try:
            # Lire TOUS les enregistrements, pas seulement les actifs
            df_existing = hook.get_pandas_df("SELECT * FROM employes_unified")
        except Exception as e:
            logger.warning(f"Impossible de lire table cible (supposée vide): {e}")
            df_existing = pd.DataFrame(columns=EXPECTED_COLS + ['statut'])

        # Index par email pour une recherche rapide
        existing_map = {}
        if not df_existing.empty:
            for _, r in df_existing.iterrows():
                email_key = normalize_str(r.get('email'))
                if email_key:  # Ignorer les emails vides
                    existing_map[email_key] = r

        # Comparaison
        inserts = []
        updates = []
        
        for _, row in df_new.iterrows():
            email = normalize_str(row.get('email'))
            if not email:
                logger.warning("Ligne sans email ignorée")
                continue
                
            existing_row = existing_map.get(email)
            
            if existing_row is None:
                # NOUVEL enregistrement
                inserts.append(row.to_dict())
            else:
                # ENREGISTREMENT EXISTANT - vérifier si besoin de mise à jour
                needs_update = False
                
                # Vérifier les changements de données
                nom_change = normalize_str(existing_row.get('nom')) != normalize_str(row.get('nom'))
                dept_change = normalize_str(existing_row.get('departement')) != normalize_str(row.get('departement'))
                
                # Comparaison robuste des salaires
                try:
                    ex_s = float(existing_row.get('salaire', 0)) if existing_row.get('salaire') not in (None, '', 'NULL') else 0.0
                    new_s = float(row.get('salaire', 0)) if row.get('salaire') not in (None, '', 'NULL') else 0.0
                    salaire_change = abs(ex_s - new_s) > 0.01
                except (ValueError, TypeError) as e:
                    logger.warning(f"Erreur conversion salaire pour {email}: {e}")
                    salaire_change = str(existing_row.get('salaire')) != str(row.get('salaire'))
                
                date_change = not dates_equal(existing_row.get('date_embauche'), row.get('date_embauche'))
                
                # Vérifier si l'enregistrement est inactif (doit être réactivé)
                statut_inactif = existing_row.get('statut') == 'inactif'
                
                # Mise à jour nécessaire si données changées OU statut inactif
                if any([nom_change, dept_change, salaire_change, date_change, statut_inactif]):
                    updates.append(row.to_dict())
                    logger.debug(f"Mise à jour nécessaire pour {email}: "
                               f"nom={nom_change}, dept={dept_change}, salaire={salaire_change}, "
                               f"date={date_change}, inactif={statut_inactif}")

        # Push des résultats
        ti.xcom_push(key='inserts', value=inserts or [])
        ti.xcom_push(key='updates', value=updates or [])
        logger.info(f"Comparaison: inserts={len(inserts)} updates={len(updates)}")
        return f"{len(inserts)}/{len(updates)}"
        
    except Exception as e:
        logger.error(f"Erreur compare_and_prepare: {e}")
        ti.xcom_push(key='inserts', value=[])
        ti.xcom_push(key='updates', value=[])
        raise AirflowException(f"Échec comparaison: {e}")

# -----------------------
# DETECTION SUPPRESSIONS
# -----------------------
def detect_deletions(**kwargs) -> Dict[str, Any]:
    """Détecte les suppressions - Version corrigée"""
    logger.info("=== DETECTION SUPPRESSIONS ===")
    ti = kwargs['ti']
    
    try:
        tjson = ti.xcom_pull(key='transformed_data')
        if not tjson:
            logger.info("Aucune donnée transformée -> aucune détection")
            return {'status': 'success', 'count': 0}

        df_new = pd.read_json(tjson)
        if df_new.empty:
            logger.info("DataFrame transformé vide -> aucune détection")
            return {'status': 'success', 'count': 0}

        # Test connexion
        test_database_connection('postgres_target_conn', 'postgres')
        hook = PostgresHook(postgres_conn_id='postgres_target_conn')
        
        # Récupération des enregistrements actifs seulement
        df_existing = hook.get_pandas_df("SELECT * FROM employes_unified WHERE statut='actif'")
        
        if df_existing.empty:
            logger.info("Aucun enregistrement actif existant -> aucune suppression")
            return {'status': 'success', 'count': 0}

        # Comparaison par EMAIL seulement (plus robuste)
        existing_emails = set(df_existing['email'].astype(str).apply(normalize_str))
        new_emails = set(df_new['email'].astype(str).apply(normalize_str))
        
        # Supprimer les emails vides
        existing_emails = {e for e in existing_emails if e}
        new_emails = {e for e in new_emails if e}
        
        # Emails à marquer comme inactif : présents dans existing mais PAS dans new
        to_soft_delete = existing_emails - new_emails
        
        logger.info(f"Emails existants: {len(existing_emails)}, Nouveaux emails: {len(new_emails)}, À supprimer: {len(to_soft_delete)}")
        
        if to_soft_delete:
            conn = hook.get_conn()
            cur = conn.cursor()
            deleted_count = 0
            
            try:
                # Marquer comme inactif par email
                emails_list = list(to_soft_delete)
                placeholders = ','.join(['%s'] * len(emails_list))
                
                query = f"""
                    UPDATE employes_unified
                    SET statut='inactif', updated_at = NOW()
                    WHERE email IN ({placeholders}) AND statut='actif'
                """
                
                cur.execute(query, emails_list)
                deleted_count = cur.rowcount
                conn.commit()
                logger.info(f"✓ Soft-delete terminé: {deleted_count} enregistrements")
                
                # Log des emails supprimés pour vérification
                for email in list(to_soft_delete)[:5]:  # Premier 5 seulement
                    logger.info(f"Supprimé: {email}")
                    
            except Exception as e:
                conn.rollback()
                raise e
            finally:
                cur.close()
                conn.close()
                
            return {'status': 'success', 'count': deleted_count}
        else:
            logger.info("Aucune suppression détectée")
            return {'status': 'success', 'count': 0}
            
    except Exception as e:
        logger.error(f"Erreur detect_deletions: {e}")
        return {'status': 'error', 'count': 0, 'message': str(e)}

# -----------------------
# CHARGEMENT (CORRIGÉ - Gestion robuste des dates)
# -----------------------
def load_to_target(**kwargs) -> str:
    """Chargement sécurisé avec gestion robuste des types de données"""
    logger.info("=== CHARGEMENT ===")
    ti = kwargs['ti']
    
    inserts = ti.xcom_pull(key='inserts') or []
    updates = ti.xcom_pull(key='updates') or []
    
    if not inserts and not updates:
        logger.info("Aucun insert ni update. Rien à charger.")
        return "Aucune modification détectée."

    test_database_connection('postgres_target_conn', 'postgres')
    hook = PostgresHook(postgres_conn_id='postgres_target_conn')
    
    inserted = 0
    updated = 0
    errors = 0

    # TRAITEMENT DES INSERTIONS
    if inserts:
        logger.info(f"Traitement de {len(inserts)} insertions")
        conn = hook.get_conn()
        cur = conn.cursor()
        
        try:
            for i, row in enumerate(inserts):
                try:
                    # Préparation des données avec types corrects
                    source = str(row.get('source', ''))
                    source_id = str(row.get('source_id', ''))
                    nom = str(row.get('nom', ''))
                    email = str(row.get('email', ''))
                    departement = str(row.get('departement', ''))
                    
                    # Gestion robuste du salaire
                    try:
                        salaire = float(row.get('salaire', 0)) if row.get('salaire') not in [None, ''] else 0.0
                    except (ValueError, TypeError):
                        salaire = 0.0
                    
                    # Normalisation de la date
                    date_embauche = safe_normalize_date(row.get('date_embauche'))
                    
                    cur.execute("""
                        INSERT INTO employes_unified 
                        (source, source_id, nom, email, departement, salaire, date_embauche, statut, updated_at)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, 'actif', NOW())
                    """, (source, source_id, nom, email, departement, salaire, date_embauche))
                    inserted += 1
                    
                    # Commit tous les 10 enregistrements pour éviter les bloquages
                    if (i + 1) % 10 == 0:
                        conn.commit()
                        logger.info(f"Commit intermédiaire après {i + 1} insertions")
                        
                except Exception as e:
                    errors += 1
                    logger.error(f"Erreur insertion {row.get('email')}: {e}")
                    # Rollback de la transaction courante et continuation
                    conn.rollback()
                    continue
                    
            conn.commit()
            logger.info(f"✓ Insertions terminées: {inserted} réussies, {errors} erreurs")
            
        except Exception as e:
            conn.rollback()
            logger.error(f"Erreur générale lors des insertions: {e}")
        finally:
            cur.close()
            conn.close()

    # TRAITEMENT DES MISES À JOUR
    if updates:
        logger.info(f"Traitement de {len(updates)} mises à jour")
        conn = hook.get_conn()
        cur = conn.cursor()
        
        try:
            for i, row in enumerate(updates):
                try:
                    # Préparation des données avec types corrects
                    nom = str(row.get('nom', ''))
                    departement = str(row.get('departement', ''))
                    email = str(row.get('email', ''))
                    
                    # Gestion robuste du salaire
                    try:
                        salaire = float(row.get('salaire', 0)) if row.get('salaire') not in [None, ''] else 0.0
                    except (ValueError, TypeError):
                        salaire = 0.0
                    
                    # Normalisation de la date
                    date_embauche = safe_normalize_date(row.get('date_embauche'))
                    
                    cur.execute("""
                        UPDATE employes_unified 
                        SET nom=%s, departement=%s, salaire=%s, date_embauche=%s, 
                            statut='actif', updated_at=NOW()
                        WHERE email=%s
                    """, (nom, departement, salaire, date_embauche, email))
                    
                    if cur.rowcount > 0:
                        updated += 1
                        logger.debug(f"Mis à jour: {email}")
                    else:
                        logger.warning(f"Aucune ligne mise à jour pour {email}")
                    
                    # Commit tous les 10 enregistrements
                    if (i + 1) % 10 == 0:
                        conn.commit()
                        logger.info(f"Commit intermédiaire après {i + 1} mises à jour")
                        
                except Exception as e:
                    errors += 1
                    logger.error(f"Erreur mise à jour {row.get('email')}: {e}")
                    conn.rollback()
                    continue
                    
            conn.commit()
            logger.info(f"✓ Mises à jour terminées: {updated} réussies, {errors} erreurs")
            
        except Exception as e:
            conn.rollback()
            logger.error(f"Erreur générale lors des mises à jour: {e}")
        finally:
            cur.close()
            conn.close()

    logger.info(f"✓ Chargement terminé: {inserted} inserts, {updated} updates, {errors} erreurs")
    
    if errors > 0:
        return f"Chargement terminé avec {errors} erreurs ({inserted} inserts, {updated} updates)"
    else:
        return f"Chargement terminé ({inserted} inserts, {updated} updates)"

# -----------------------
# VALIDATION FINALE
# -----------------------
def validate_data(**kwargs) -> str:
    """Validation finale des données chargées"""
    logger.info("=== VALIDATION ===")
    
    test_database_connection('postgres_target_conn', 'postgres')
    hook = PostgresHook(postgres_conn_id='postgres_target_conn')
    
    try:
        # Statistiques générales
        df_total = hook.get_pandas_df("SELECT COUNT(*) AS total FROM employes_unified")
        total = int(df_total.iloc[0]['total'])
        
        # Statistiques par statut
        df_stat = hook.get_pandas_df("""
            SELECT statut, COUNT(*) as count 
            FROM employes_unified 
            GROUP BY statut
            ORDER BY statut
        """)
        
        # Statistiques par source
        df_source = hook.get_pandas_df("""
            SELECT source, COUNT(*) as count 
            FROM employes_unified 
            WHERE statut = 'actif'
            GROUP BY source
            ORDER BY source
        """)
        
        # Log des résultats
        logger.info(f"=== RAPPORT DE SYNCHRONISATION ===")
        logger.info(f"Total en base: {total}")
        
        if not df_stat.empty:
            for _, r in df_stat.iterrows():
                logger.info(f" - Statut '{r['statut']}': {r['count']} enregistrements")
        
        if not df_source.empty:
            logger.info("Répartition par source (actifs):")
            for _, r in df_source.iterrows():
                logger.info(f" - Source '{r['source']}': {r['count']} employés")
        
        # Validation de cohérence
        df_active = hook.get_pandas_df("SELECT COUNT(*) as active_count FROM employes_unified WHERE statut='actif'")
        active_count = int(df_active.iloc[0]['active_count'])
        
        if active_count == 0 and total > 0:
            logger.error("❌ CRITIQUE: Aucun employé actif en base!")
            raise AirflowException("Aucun employé actif après synchronisation")
        elif active_count > 0:
            logger.info(f"✓ {active_count} employés actifs synchronisés")

        return f"Validation OK - {total} total ({active_count} actifs)"
        
    except Exception as e:
        logger.error(f"Erreur validation: {e}")
        raise AirflowException(f"Échec validation: {e}")

# -----------------------
# Tâches du DAG
# -----------------------
t_csv = PythonOperator(task_id='extract_csv', python_callable=extract_csv, dag=dag)
t_mysql = PythonOperator(task_id='extract_mysql', python_callable=extract_mysql, dag=dag)
t_pgsql = PythonOperator(task_id='extract_pgsql', python_callable=extract_postgres, dag=dag)
t_transform = PythonOperator(task_id='transform', python_callable=transform_data, dag=dag)
t_compare = PythonOperator(task_id='compare_data', python_callable=compare_and_prepare, dag=dag)
t_delete = PythonOperator(task_id='detect_deletions', python_callable=detect_deletions, dag=dag)
t_load = PythonOperator(task_id='load_data', python_callable=load_to_target, trigger_rule='all_done', dag=dag)
t_validate = PythonOperator(task_id='validate', python_callable=validate_data, trigger_rule='all_done', dag=dag)

# -----------------------
# Ordre d'exécution
# -----------------------
[t_csv, t_mysql, t_pgsql] >> t_transform >> t_compare >> t_delete >> t_load >> t_validate