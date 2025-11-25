"""Routes API pour les statistiques"""
from flask import Blueprint, jsonify
from services.db_service import DatabaseService

stats_bp = Blueprint('stats', __name__)
db_service = DatabaseService()

@stats_bp.route('/stats', methods=['GET'])
def get_stats_global():
    """Récupère les statistiques globales"""
    try:
        stats = db_service.get_stats_global()
        
        return jsonify({
            'success': True,
            'data': dict(stats)
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@stats_bp.route('/stats/sources', methods=['GET'])
def get_stats_sources():
    """Récupère les statistiques par source"""
    try:
        stats = db_service.get_stats_by_source()
        
        return jsonify({
            'success': True,
            'data': [dict(s) for s in stats]
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@stats_bp.route('/stats/departements', methods=['GET'])
def get_stats_departements():
    """Récupère les statistiques par département"""
    try:
        stats = db_service.get_stats_by_departement()
        
        return jsonify({
            'success': True,
            'data': [dict(s) for s in stats]
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500