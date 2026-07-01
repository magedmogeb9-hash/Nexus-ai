from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db, User, TrainingProject, Contract, Payment
from functools import wraps

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Admin access required', 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/admin')
@login_required
@admin_required
def admin_dashboard():
    users = User.query.all()
    projects = TrainingProject.query.all()
    contracts = Contract.query.all()
    payments = Payment.query.all()
    stats = {
        'total_users': len(users),
        'total_projects': len(projects),
        'total_revenue': sum(p.amount for p in payments if p.status == 'completed'),
        'active_subs': len([u for u in users if u.subscription_plan != 'free'])
    }
    return render_template('admin_dashboard.html', users=users, projects=projects,
                           contracts=contracts, payments=payments, stats=stats)

@admin_bp.route('/admin/verify-user/<int:user_id>')
@login_required
@admin_required
def verify_user(user_id):
    user = User.query.get_or_404(user_id)
    user.is_verified = True
    db.session.commit()
    flash(f'User {user.email} verified', 'success')
    return redirect(url_for('admin.admin_dashboard'))

@admin_bp.route('/admin/delete-user/<int:user_id>')
@login_required
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash(f'User deleted', 'success')
    return redirect(url_for('admin.admin_dashboard'))
