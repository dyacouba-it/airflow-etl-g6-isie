"""Routes API pour l'ETL et l'intégration Airflow"""
from flask import Blueprint, jsonify
from services.airflow_service import AirflowService
from services.db_service import DatabaseService

etl_bp = Blueprint('etl', __name__)
airflow_service = AirflowService()
db_service = DatabaseService()

@etl_bp.route('/etl/trigger', methods=['POST'])
def trigger_etl():
    """Déclenche l'exécution du DAG ETL"""
    result = airflow_service.trigger_dag()
    
    if result['success']:
        return jsonify(result), 200
    else:
        return jsonify(result), 500

@etl_bp.route('/etl/status', methods=['GET'])
def get_etl_status():
    """Récupère le statut du DAG ETL"""
    result = airflow_service.get_dag_status()
    
    if result['success']:
        return jsonify(result), 200
    else:
        return jsonify(result), 500

@etl_bp.route('/etl/history', methods=['GET'])
def get_etl_history():
    """Récupère l'historique des exécutions ETL"""
    result = airflow_service.get_last_dag_runs()
    
    if result['success']:
        return jsonify(result), 200
    else:
        return jsonify(result), 500

@etl_bp.route('/etl/last-sync', methods=['GET'])
def get_last_sync():
    """Récupère les informations de la dernière synchronisation"""
    try:
        info = db_service.get_last_sync_info()
        
        return jsonify({
            'success': True,
            'data': dict(info)
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500