import requests
import json
import os
from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, jsonify
from flask_login import login_required
from app import db, log_user_action
from app.models import User, Client, Formation
from app.utils.decorators import admin_required, superadmin_required
from app.services.api_sync import manual_sync_wedof

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Chemin du fichier de configuration API
API_CONFIG_FILE = 'instance/api_config.json'

def get_api_config():
    """Récupère la configuration API depuis le fichier JSON"""
    if not os.path.exists(API_CONFIG_FILE):
        return {
            'url': 'https://api.wedof.com/formations',
            'key': '',
            'secret': '',
            'auto_sync': False,
            'sync_interval': 24,
            'last_sync': None,
            'sync_stats': {}
        }
    
    try:
        with open(API_CONFIG_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        current_app.logger.error(f"Erreur lors de la lecture de la configuration API: {str(e)}")
        return {
            'url': 'https://api.wedof.com/formations',
            'key': '',
            'secret': '',
            'auto_sync': False,
            'sync_interval': 24,
            'last_sync': None,
            'sync_stats': {}
        }

def save_api_config(config):
    """Sauvegarde la configuration API dans un fichier JSON"""
    # Créer le répertoire si nécessaire
    os.makedirs(os.path.dirname(API_CONFIG_FILE), exist_ok=True)
    
    try:
        with open(API_CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
        return True
    except Exception as e:
        current_app.logger.error(f"Erreur lors de la sauvegarde de la configuration API: {str(e)}")
        return False

@admin_bp.route('/users')
@login_required
@superadmin_required
def users():
    users = User.query.all()
    log_user_action("A consulté la liste des utilisateurs")
    return render_template('admin/users.html', users=users)

@admin_bp.route('/users/create', methods=['GET', 'POST'])
@login_required
@superadmin_required
def create_user():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role')
        
        # Vérifier si l'utilisateur existe déjà
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Un utilisateur avec cet email existe déjà', 'danger')
            return redirect(url_for('admin.create_user'))
        
        # Créer le nouvel utilisateur
        user = User(email=email, role=role)
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        log_user_action(f"A créé un nouvel utilisateur: {email} avec le rôle {role}")
        flash(f'Utilisateur {email} créé avec succès', 'success')
        return redirect(url_for('admin.users'))
    
    return render_template('admin/create_user.html')

@admin_bp.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
@superadmin_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    
    if request.method == 'POST':
        email = request.form.get('email')
        role = request.form.get('role')
        password = request.form.get('password')
        
        # Vérifier si l'email est déjà utilisé par un autre utilisateur
        existing_user = User.query.filter_by(email=email).first()
        if existing_user and existing_user.id != user.id:
            flash('Cet email est déjà utilisé par un autre utilisateur', 'danger')
            return redirect(url_for('admin.edit_user', user_id=user.id))
        
        old_email = user.email
        old_role = user.role
        
        user.email = email
        user.role = role
        
        if password:
            user.set_password(password)
            log_user_action(f"A modifié le mot de passe de l'utilisateur: {email}")
        
        changes = []
        if old_email != email:
            changes.append(f"email: {old_email} -> {email}")
        if old_role != role:
            changes.append(f"rôle: {old_role} -> {role}")
        
        db.session.commit()
        
        if changes:
            log_user_action(f"A modifié l'utilisateur ID:{user_id} - {', '.join(changes)}")
        
        flash('Utilisateur mis à jour avec succès', 'success')
        return redirect(url_for('admin.users'))
    
    return render_template('admin/edit_user.html', user=user)

@admin_bp.route('/users/<int:user_id>/delete', methods=['POST'])
@login_required
@superadmin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    
    if user.is_superadmin():
        flash('Impossible de supprimer un super administrateur', 'danger')
        return redirect(url_for('admin.users'))
    
    email = user.email
    role = user.role
    
    db.session.delete(user)
    db.session.commit()
    
    log_user_action(f"A supprimé l'utilisateur: {email} (rôle: {role})")
    flash('Utilisateur supprimé avec succès', 'success')
    return redirect(url_for('admin.users'))

@admin_bp.route('/sync-api', methods=['GET', 'POST'])
@login_required
@admin_required
def sync_api():
    api_config = get_api_config()
    
    # Convertir la date de dernière synchronisation en objet datetime si elle existe
    last_sync = None
    if api_config.get('last_sync'):
        try:
            last_sync = datetime.fromisoformat(api_config['last_sync'])
        except:
            last_sync = None
    
    if request.method == 'POST':
        success, message = manual_sync_wedof()
        
        if success:
            # Mettre à jour la date de dernière synchronisation et les statistiques
            api_config['last_sync'] = datetime.now().isoformat()
            api_config['sync_stats'] = {
                'new_clients': int(message.split(' ')[2]),  # Extraire le nombre de nouveaux clients
                'updated_clients': int(message.split(' ')[5])  # Extraire le nombre de clients mis à jour
            }
            save_api_config(api_config)
            
            log_user_action(f"A lancé une synchronisation manuelle avec l'API WEDOF - {message}")
            flash(message, 'success')
        else:
            log_user_action(f"Échec de synchronisation avec l'API WEDOF - {message}")
            flash(message, 'danger')
        
        return redirect(url_for('admin.sync_api'))
    
    log_user_action("A consulté la page de configuration API WEDOF")
    return render_template('admin/sync_api.html', 
                          api_config=api_config,
                          last_sync=last_sync,
                          sync_stats=api_config.get('sync_stats', {}))

@admin_bp.route('/save-api-config', methods=['POST'])
@login_required
@admin_required
def save_api_config():
    api_url = request.form.get('api_url')
    api_key = request.form.get('api_key')
    api_secret = request.form.get('api_secret')
    auto_sync = 'auto_sync' in request.form
    sync_interval = int(request.form.get('sync_interval', 24))
    
    # Récupérer la configuration existante
    api_config = get_api_config()
    
    # Vérifier les changements pour la journalisation
    changes = []
    if api_config.get('url') != api_url:
        changes.append(f"URL: {api_config.get('url')} -> {api_url}")
    if api_config.get('key') != api_key:
        changes.append("Clé API modifiée")
    if api_config.get('secret') != api_secret:
        changes.append("Secret API modifié")
    if api_config.get('auto_sync') != auto_sync:
        changes.append(f"Synchronisation auto: {api_config.get('auto_sync')} -> {auto_sync}")
    if api_config.get('sync_interval') != sync_interval:
        changes.append(f"Intervalle: {api_config.get('sync_interval')}h -> {sync_interval}h")
    
    # Mettre à jour la configuration
    api_config['url'] = api_url
    api_config['key'] = api_key
    api_config['secret'] = api_secret
    api_config['auto_sync'] = auto_sync
    api_config['sync_interval'] = sync_interval
    
    # Sauvegarder la configuration
    if save_api_config(api_config):
        if changes:
            log_user_action(f"A modifié la configuration API WEDOF - {', '.join(changes)}")
        flash('Configuration API sauvegardée avec succès', 'success')
    else:
        log_user_action("Échec de sauvegarde de la configuration API WEDOF")
        flash('Erreur lors de la sauvegarde de la configuration API', 'danger')
    
    return redirect(url_for('admin.sync_api')) 