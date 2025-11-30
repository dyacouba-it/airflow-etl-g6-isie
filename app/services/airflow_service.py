"""Service d'intégration avec l'API Airflow"""
import requests
import os
from datetime import datetime

class AirflowService:
    def __init__(self):
        self.base_url = os.getenv('AIRFLOW_URL', 'http://airflow-webserver:8080/api/v1')
        self.dag_id = 'etl_employe'
        self.auth = ('admin', 'admin')
    
    def trigger_dag(self):
        """Déclenche l'exécution du DAG ETL"""
        url = f"{self.base_url}/dags/{self.dag_id}/dagRuns"
        payload = {
            "conf": {},
            "dag_run_id": f"manual_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        }
        
        try:
            response = requests.post(url, json=payload, auth=self.auth)
            response.raise_for_status()
            return {
                'success': True,
                'message': 'ETL déclenché avec succès',
                'data': response.json()
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Erreur lors du déclenchement : {str(e)}'
            }
    
    def get_dag_status(self):
        """Récupère le statut du DAG"""
        url = f"{self.base_url}/dags/{self.dag_id}"
        
        try:
            response = requests.get(url, auth=self.auth)
            response.raise_for_status()
            return {
                'success': True,
                'data': response.json()
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Erreur : {str(e)}'
            }
    
    def get_last_dag_runs(self, limit=5):
        """Récupère les dernières exécutions du DAG"""
        url = f"{self.base_url}/dags/{self.dag_id}/dagRuns"
        params = {'limit': limit, 'order_by': '-execution_date'}
        
        try:
            response = requests.get(url, params=params, auth=self.auth)
            response.raise_for_status()
            return {
                'success': True,
                'data': response.json().get('dag_runs', [])
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Erreur : {str(e)}'
            }