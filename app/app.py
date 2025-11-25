"""Application Flask principale"""
from flask import Flask, jsonify, render_template
from flask_cors import CORS
import os
import sys

# Ajouter le répertoire courant au path
sys.path.insert(0, os.path.dirname(__file__))

# Import des routes avec chemins relatifs
from routes.employes import employes_bp
from routes.stats import stats_bp
from routes.etl import etl_bp
from routes.sources import sources_bp

def create_app():
    """Factory pour créer l'application Flask"""
    app = Flask(__name__)
    
    # Configuration
    app.config['JSON_AS_ASCII'] = False  # Support des caractères UTF-8
    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
    
    # CORS
    CORS(app)
    
    # Enregistrement des blueprints
    app.register_blueprint(employes_bp, url_prefix='/api')
    app.register_blueprint(stats_bp, url_prefix='/api')
    app.register_blueprint(etl_bp, url_prefix='/api')
    app.register_blueprint(sources_bp, url_prefix='/api')
    
    # Route racine
    @app.route('/')
    def index():
        """Page d'accueil"""
        return render_template('index.html')
    
    # Health check
    @app.route('/health')
    def health():
        """Endpoint de santé"""
        return jsonify({
            'status': 'healthy',
            'service': 'ETL Employes API',
            'version': '1.0.0'
        }), 200
    
    # Documentation API
    @app.route('/api')
    def api_docs():
        """Documentation de l'API"""
        return jsonify({
            'service': 'API REST - Gestion des Employés',
            'version': '1.0.0',
            'endpoints': {
                'employes': {
                    'GET /api/employes': 'Liste tous les employés (filtres: source, departement, limit, offset)',
                    'GET /api/employes/<id>': 'Détails d\'un employé'
                },
                'stats': {
                    'GET /api/stats': 'Statistiques globales',
                    'GET /api/stats/sources': 'Statistiques par source',
                    'GET /api/stats/departements': 'Statistiques par département'
                },
                'etl': {
                    'POST /api/etl/trigger': 'Déclenche le DAG ETL',
                    'GET /api/etl/status': 'Statut du DAG',
                    'GET /api/etl/history': 'Historique des exécutions',
                    'GET /api/etl/last-sync': 'Info dernière synchronisation'
                },
                'health': {
                    'GET /health': 'Santé de l\'application'
                }
            }
        }), 200
    
    return app

# Point d'entrée
if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)