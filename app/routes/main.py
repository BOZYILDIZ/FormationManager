from flask import Blueprint, render_template, redirect, url_for, flash, abort, current_app
from flask_login import login_required, current_user
from app import db
from app.models import Client, Formation, Product, User
from app.utils.decorators import admin_required, admin_or_operateur_required

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('auth.login'))

@main_bp.route('/dashboard')
@login_required
def dashboard():
    # Afficher le tableau de bord en fonction du rôle
    current_app.logger.info(f"Accès au tableau de bord par {current_user.email}, rôle: {current_user.role}")
    
    if current_user.role == 'superadmin':
        # Pour les superadmins, afficher la liste des utilisateurs
        users = User.query.all()
        return render_template('admin/users.html', users=users)
    else:
        # Pour admin et operateur, afficher la liste des clients
        clients = Client.query.all()
        return render_template('main/dashboard.html', clients=clients)

@main_bp.route('/dashboard/sync-status')
@login_required
@admin_required
def sync_status():
    # Cette route pourrait être utilisée pour afficher le statut de la synchronisation API
    return render_template('main/sync_status.html') 