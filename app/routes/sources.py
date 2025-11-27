"""Routes API pour gérer les bases sources"""
from flask import Blueprint, jsonify, request
from services.source_db_service import SourceDatabaseService

sources_bp = Blueprint('sources', __name__)
source_service = SourceDatabaseService()

# ==================== MYSQL ====================

@sources_bp.route('/sources/mysql/employes', methods=['GET'])
def get_mysql_employes():
    """Liste des employés MySQL source"""
    try:
        limit = int(request.args.get('limit', 100))
        offset = int(request.args.get('offset', 0))
        
        employes = source_service.get_mysql_employees(limit, offset)
        count = source_service.get_mysql_count()
        
        return jsonify({
            'success': True,
            'source': 'MySQL',
            'count': len(employes),
            'total': count,
            'data': employes
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@sources_bp.route('/sources/mysql/employes', methods=['POST'])
def add_to_mysql():
    """Ajoute un employé dans MySQL source"""
    try:
        data = request.get_json()
        
        # Validation
        required = ['nom', 'email', 'departement', 'salaire']
        for field in required:
            if field not in data:
                return jsonify({
                    'success': False,
                    'message': f'Champ requis : {field}'
                }), 400
        
        result = source_service.add_to_mysql(data)
        
        return jsonify({
            'success': True,
            'message': f'Employé ajouté dans MySQL source (ID: {result["id"]})',
            'data': result
        }), 201
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@sources_bp.route('/sources/mysql/employes/<int:employe_id>', methods=['GET'])
def get_mysql_employe(employe_id):
    """Récupère un employé MySQL par son ID"""
    try:
        employe = source_service.get_mysql_employee_by_id(employe_id)
        
        if not employe:
            return jsonify({
                'success': False,
                'message': 'Employé non trouvé dans MySQL'
            }), 404
        
        return jsonify({
            'success': True,
            'data': employe
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@sources_bp.route('/sources/mysql/employes/<int:employe_id>', methods=['PUT'])
def update_mysql_employe(employe_id):
    """Met à jour un employé dans MySQL source"""
    try:
        data = request.get_json()
        
        # Vérifier que l'employé existe
        employe = source_service.get_mysql_employee_by_id(employe_id)
        if not employe:
            return jsonify({
                'success': False,
                'message': 'Employé non trouvé dans MySQL'
            }), 404
        
        # Mise à jour
        result = source_service.update_mysql_employee(employe_id, data)
        
        return jsonify({
            'success': True,
            'message': 'Employé MySQL mis à jour avec succès',
            'data': result
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@sources_bp.route('/sources/mysql/employes/<int:employe_id>', methods=['DELETE'])
def delete_mysql_employe(employe_id):
    """Supprime un employé de MySQL source"""
    try:
        # Vérifier que l'employé existe
        employe = source_service.get_mysql_employee_by_id(employe_id)
        if not employe:
            return jsonify({
                'success': False,
                'message': 'Employé non trouvé dans MySQL'
            }), 404
        
        # Suppression
        source_service.delete_mysql_employee(employe_id)
        
        return jsonify({
            'success': True,
            'message': 'Employé supprimé de MySQL source'
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


# ==================== POSTGRESQL ====================

@sources_bp.route('/sources/postgresql/employes', methods=['GET'])
def get_postgresql_employes():
    """Liste des employés PostgreSQL source"""
    try:
        limit = int(request.args.get('limit', 100))
        offset = int(request.args.get('offset', 0))
        
        employes = source_service.get_postgresql_employees(limit, offset)
        count = source_service.get_postgresql_count()
        
        return jsonify({
            'success': True,
            'source': 'PostgreSQL',
            'count': len(employes),
            'total': count,
            'data': employes
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@sources_bp.route('/sources/postgresql/employes', methods=['POST'])
def add_to_postgresql():
    """Ajoute un employé dans PostgreSQL source"""
    try:
        data = request.get_json()
        
        # Validation
        required = ['nom', 'email', 'departement', 'salaire']
        for field in required:
            if field not in data:
                return jsonify({
                    'success': False,
                    'message': f'Champ requis : {field}'
                }), 400
        
        result = source_service.add_to_postgresql(data)
        
        return jsonify({
            'success': True,
            'message': f'Employé ajouté dans PostgreSQL source (ID: {result["id"]})',
            'data': result
        }), 201
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@sources_bp.route('/sources/postgresql/employes/<int:employe_id>', methods=['GET'])
def get_postgresql_employe(employe_id):
    """Récupère un employé PostgreSQL par son ID"""
    try:
        employe = source_service.get_postgresql_employee_by_id(employe_id)
        
        if not employe:
            return jsonify({
                'success': False,
                'message': 'Employé non trouvé dans PostgreSQL'
            }), 404
        
        return jsonify({
            'success': True,
            'data': employe
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@sources_bp.route('/sources/postgresql/employes/<int:employe_id>', methods=['PUT'])
def update_postgresql_employe(employe_id):
    """Met à jour un employé dans PostgreSQL source"""
    try:
        data = request.get_json()
        
        # Vérifier que l'employé existe
        employe = source_service.get_postgresql_employee_by_id(employe_id)
        if not employe:
            return jsonify({
                'success': False,
                'message': 'Employé non trouvé dans PostgreSQL'
            }), 404
        
        # Mise à jour
        result = source_service.update_postgresql_employee(employe_id, data)
        
        return jsonify({
            'success': True,
            'message': 'Employé PostgreSQL mis à jour avec succès',
            'data': result
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@sources_bp.route('/sources/postgresql/employes/<int:employe_id>', methods=['DELETE'])
def delete_postgresql_employe(employe_id):
    """Supprime un employé de PostgreSQL source"""
    try:
        # Vérifier que l'employé existe
        employe = source_service.get_postgresql_employee_by_id(employe_id)
        if not employe:
            return jsonify({
                'success': False,
                'message': 'Employé non trouvé dans PostgreSQL'
            }), 404
        
        # Suppression
        source_service.delete_postgresql_employee(employe_id)
        
        return jsonify({
            'success': True,
            'message': 'Employé supprimé de PostgreSQL source'
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


# ==================== STATISTIQUES ====================

@sources_bp.route('/sources/stats', methods=['GET'])
def get_sources_stats():
    """Compte les employés PAR SOURCE depuis employes_unified"""
    try:
        # Importer db_service pour accéder à employes_unified
        from services.db_service import DatabaseService
        db_service = DatabaseService()
        
        # Récupérer les stats groupées par source
        stats_list = db_service.get_stats_by_source()
        
        # Transformer en dictionnaire {csv: X, mysql: Y, postgresql: Z}
        stats = {'csv': 0, 'mysql': 0, 'postgresql': 0}
        
        for row in stats_list:
            source = row['source'].lower()
            if source in stats:
                stats[source] = int(row['count'])
        
        return jsonify({
            'success': True,
            'data': stats
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500
# ==================== CSV SOURCE (LECTURE FICHIER) ====================

@sources_bp.route('/sources/csv/employes', methods=['GET'])
def get_csv_employees():
    """Lit les employés directement depuis le fichier CSV"""
    import csv
    import os
    
    try:
        # Chemins possibles
        possible_paths = [
            os.getenv('CSV_FILE_PATH'),
            '/data/data.csv',
            os.path.join(os.getcwd(), 'data', 'data.csv'),
            '/app/data/data.csv',
        ]
        
        csv_file = None
        for path in [p for p in possible_paths if p]:
            if os.path.exists(path):
                csv_file = path
                break
        
        if not csv_file:
            return jsonify({
                'success': False,
                'message': 'Fichier CSV non trouvé',
                'data': [],
                'total': 0
            }), 404
        
        # Lire le CSV
        employees = []
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                employees.append({
                    'id': len(employees) + 1,  # ID temporaire
                    'nom': row.get('nom', ''),
                    'email': row.get('email', ''),
                    'departement': row.get('departement', ''),
                    'salaire': float(row.get('salaire', 0)) if row.get('salaire') else 0,
                    'date_embauche': row.get('date_embauche', None)
                })
        
        return jsonify({
            'success': True,
            'data': employees,
            'total': len(employees)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e),
            'data': [],
            'total': 0
        }), 500
