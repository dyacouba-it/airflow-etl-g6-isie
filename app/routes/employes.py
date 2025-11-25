"""Routes API pour la gestion des employés"""
from flask import Blueprint, jsonify, request
from services.db_service import DatabaseService
from datetime import datetime

employes_bp = Blueprint('employes', __name__)
db_service = DatabaseService()

@employes_bp.route('/employes', methods=['GET'])
def get_employes():
    """Récupère la liste des employés avec filtres optionnels"""
    try:
        source = request.args.get('source')
        departement = request.args.get('departement')
        limit = int(request.args.get('limit', 100))
        offset = int(request.args.get('offset', 0))
        
        employes = db_service.get_all_employes(source, departement, limit, offset)
        
        return jsonify({
            'success': True,
            'count': len(employes),
            'data': [dict(emp) for emp in employes]
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@employes_bp.route('/employes/<int:employe_id>', methods=['GET'])
def get_employe(employe_id):
    """Récupère un employé par son ID"""
    try:
        employe = db_service.get_employe_by_id(employe_id)
        
        if not employe:
            return jsonify({
                'success': False,
                'message': 'Employé non trouvé'
            }), 404
        
        return jsonify({
            'success': True,
            'data': dict(employe)
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@employes_bp.route('/employes', methods=['POST'])
def create_employe():
    """Crée un nouvel employé"""
    try:
        data = request.get_json()
        
        # Validation
        required_fields = ['nom', 'email', 'departement', 'salaire']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'message': f'Champ requis manquant : {field}'
                }), 400
        
        # Création
        result = db_service.create_employe(data)
        
        return jsonify({
            'success': True,
            'message': 'Employé créé avec succès',
            'data': result
        }), 201
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@employes_bp.route('/employes/<int:employe_id>', methods=['PUT'])
def update_employe(employe_id):
    """Met à jour un employé"""
    try:
        data = request.get_json()
        
        # Vérifier que l'employé existe
        employe = db_service.get_employe_by_id(employe_id)
        if not employe:
            return jsonify({
                'success': False,
                'message': 'Employé non trouvé'
            }), 404
        
        # Mise à jour
        result = db_service.update_employe(employe_id, data)
        
        return jsonify({
            'success': True,
            'message': 'Employé mis à jour avec succès',
            'data': result
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@employes_bp.route('/employes/<int:employe_id>', methods=['DELETE'])
def delete_employe(employe_id):
    """Supprime un employé"""
    try:
        # Vérifier que l'employé existe
        employe = db_service.get_employe_by_id(employe_id)
        if not employe:
            return jsonify({
                'success': False,
                'message': 'Employé non trouvé'
            }), 404
        
        # Suppression
        db_service.delete_employe(employe_id)
        
        return jsonify({
            'success': True,
            'message': 'Employé supprimé avec succès'
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500