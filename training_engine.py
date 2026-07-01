from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from models import db, TrainingProject
import os

training_bp = Blueprint('training', __name__)

SUPPORTED_MODELS = {
    'LLM': ['meta-llama/Llama-3.1-8B', 'deepseek-ai/DeepSeek-R1', 'Qwen/Qwen2.5-7B', 'mistralai/Mistral-7B-v0.3'],
    'Vision': ['openai/clip-vit-base-patch32', 'google/vit-base-patch16-224'],
    'Audio': ['openai/whisper-base', 'facebook/wav2vec2-base'],
    'Embedding': ['sentence-transformers/all-MiniLM-L6-v2', 'BAAI/bge-large-en-v1.5']
}

TRAINING_METHODS = ['SFT', 'LoRA', 'QLoRA', 'DPO', 'RL']

@training_bp.route('/training')
@login_required
def training_page():
    projects = TrainingProject.query.filter_by(user_id=current_user.id).all()
    return render_template('training.html', projects=projects, models=SUPPORTED_MODELS, methods=TRAINING_METHODS)

@training_bp.route('/projects')
@login_required
def projects():
    projects = TrainingProject.query.filter_by(user_id=current_user.id).all()
    return render_template('projects.html', projects=projects)

@training_bp.route('/create-project', methods=['POST'])
@login_required
def create_project():
    name = request.form.get('name')
    description = request.form.get('description')
    model_type = request.form.get('model_type')
    base_model = request.form.get('base_model')
    training_method = request.form.get('training_method')

    if not all([name, model_type, base_model, training_method]):
        flash('All fields are required', 'danger')
        return redirect(url_for('training.training_page'))

    project = TrainingProject(
        user_id=current_user.id,
        name=name,
        description=description,
        model_type=model_type,
        base_model=base_model,
        training_method=training_method,
        status='draft'
    )
    db.session.add(project)
    db.session.commit()
    flash(f'Project "{name}" created successfully!', 'success')
    return redirect(url_for('training.projects'))

@training_bp.route('/start-training/<int:project_id>', methods=['POST'])
@login_required
def start_training(project_id):
    project = TrainingProject.query.get_or_404(project_id)
    if project.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403

    project.status = 'training'
    db.session.commit()
    # هنا يمكن إضافة منطق التدريب الفعلي (Celery, background thread, إلخ)
    return jsonify({'status': 'started', 'project_id': project_id})

@training_bp.route('/project-status/<int:project_id>')
@login_required
def project_status(project_id):
    project = TrainingProject.query.get_or_404(project_id)
    if project.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    return jsonify({'status': project.status, 'name': project.name})
