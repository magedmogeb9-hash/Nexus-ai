from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from models import db, TrainingProject, Contract

api_bp = Blueprint('api', __name__)

@api_bp.route('/projects', methods=['GET'])
@login_required
def get_projects():
    projects = TrainingProject.query.filter_by(user_id=current_user.id).all()
    return jsonify([{
        'id': p.id,
        'name': p.name,
        'model_type': p.model_type,
        'base_model': p.base_model,
        'training_method': p.training_method,
        'status': p.status,
        'github_repo': p.github_repo,
        'created_at': str(p.created_at)
    } for p in projects])

@api_bp.route('/projects/<int:project_id>', methods=['GET'])
@login_required
def get_project(project_id):
    project = TrainingProject.query.get_or_404(project_id)
    if project.user_id != current_user.id and not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    return jsonify({
        'id': project.id,
        'name': project.name,
        'description': project.description,
        'model_type': project.model_type,
        'base_model': project.base_model,
        'training_method': project.training_method,
        'status': project.status,
        'github_repo': project.github_repo
    })

@api_bp.route('/contracts', methods=['GET'])
@login_required
def get_contracts():
    contracts = Contract.query.filter_by(user_id=current_user.id).all()
    return jsonify([{
        'id': c.id,
        'company_name': c.company_name,
        'budget': c.budget,
        'status': c.status,
        'created_at': str(c.created_at)
    } for c in contracts])

@api_bp.route('/health')
def health():
    return jsonify({'status': 'ok', 'service': 'AIForge'})
