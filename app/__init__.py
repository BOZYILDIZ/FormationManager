from flask import Flask, g, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from datetime import datetime
import os
import logging
from logging.handlers import RotatingFileHandler
from apscheduler.schedulers.background import BackgroundScheduler

# Initialisation des extensions
db = SQLAlchemy()
login_manager = LoginManager()
scheduler = BackgroundScheduler()

# Logger pour les actions utilisateur
user_logger = logging.getLogger('user_actions')

def setup_logging(app):
    """Configure le système de journalisation de l'application"""
    # Créer le dossier logs s'il n'existe pas
    logs_dir = os.path.join(app.instance_path, 'logs')
    os.makedirs(logs_dir, exist_ok=True)
    
    # Configuration du logger pour les erreurs
    error_log_file = os.path.join(logs_dir, 'errors.log')
    error_handler = RotatingFileHandler(error_log_file, maxBytes=10485760, backupCount=10)
    error_handler.setLevel(logging.ERROR)
    error_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    error_handler.setFormatter(error_formatter)
    
    # Ajouter le handler au logger de l'application
    app.logger.addHandler(error_handler)
    
    # Configuration du logger pour les actions utilisateur
    user_log_file = os.path.join(logs_dir, 'user_actions.log')
    user_handler = RotatingFileHandler(user_log_file, maxBytes=10485760, backupCount=10)
    user_handler.setLevel(logging.INFO)
    user_formatter = logging.Formatter('%(asctime)s - %(message)s')
    user_handler.setFormatter(user_formatter)
    
    # Configurer le logger des actions utilisateur
    global user_logger
    user_logger.setLevel(logging.INFO)
    user_logger.addHandler(user_handler)
    
    # Définir le niveau de journalisation global
    app.logger.setLevel(logging.INFO)

def log_user_action(message):
    """Journalise une action utilisateur avec son identité"""
    user_email = current_user.email if not current_user.is_anonymous else 'Anonymous'
    user_id = current_user.id if not current_user.is_anonymous else 'N/A'
    user_role = current_user.role if not current_user.is_anonymous else 'N/A'
    
    user_logger.info(f"[{user_email} (ID:{user_id}, Role:{user_role})] {message}")

def create_app(config_class=None):
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev_key_change_in_production')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///' + os.path.join(app.instance_path, 'app.db'))
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialisation des extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Veuillez vous connecter pour accéder à cette page.'
    login_manager.login_message_category = 'info'
    
    # Création du dossier instance si nécessaire
    try:
        os.makedirs(app.instance_path, exist_ok=True)
    except OSError:
        pass
    
    # Configuration du système de journalisation
    setup_logging(app)
    
    # Importation et initialisation du service de localisation
    from app.services.localization import init_localization
    
    @app.before_request
    def before_request():
        # Initialisation de la localisation
        init_localization()
        
        # Journalisation des requêtes (sauf pour les ressources statiques)
        if not request.path.startswith('/static'):
            if current_user.is_authenticated:
                app.logger.info(f"Requête: {request.method} {request.path} - Utilisateur: {current_user.email} (ID:{current_user.id})")
    
    @app.after_request
    def after_request(response):
        # Journalisation des réponses avec code d'erreur
        if response.status_code >= 400:
            if current_user.is_authenticated:
                user_info = f"Utilisateur: {current_user.email} (ID:{current_user.id})"
            else:
                user_info = "Utilisateur: Anonymous"
            app.logger.error(f"Erreur {response.status_code}: {request.method} {request.path} - {user_info}")
        return response
    
    # Ajout d'un context processor pour injecter la variable 'now' dans tous les templates
    @app.context_processor
    def inject_now():
        return {'now': datetime.now()}
    
    # Ajout d'une route pour changer la langue
    from flask import session, redirect, request
    
    @app.route('/set-lang/<lang>')
    def set_lang(lang):
        if lang in ['fr', 'tr']:
            session['lang'] = lang
            if current_user.is_authenticated:
                log_user_action(f"A changé la langue en '{lang}'")
        return redirect(request.referrer or '/')
    
    # Importation et enregistrement des blueprints
    from app.routes.auth import auth_bp
    from app.routes.main import main_bp
    from app.routes.client import client_bp
    from app.routes.admin import admin_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(client_bp)
    app.register_blueprint(admin_bp)
    
    # Gestion des erreurs
    from app.routes.errors import register_error_handlers
    register_error_handlers(app)
    
    # Configuration du scheduler pour la synchronisation API
    from app.services.api_sync import sync_wedof_data, get_api_config
    
    def check_and_sync():
        """Vérifie si une synchronisation automatique est nécessaire"""
        with app.app_context():
            api_config = get_api_config()
            if api_config.get('auto_sync', False):
                app.logger.info("Lancement de la synchronisation automatique")
                sync_wedof_data(app)
    
    # Démarrage du scheduler si pas déjà en cours
    if not scheduler.running:
        # Exécuter toutes les heures
        scheduler.add_job(check_and_sync, 'interval', hours=1, id='wedof_sync')
        scheduler.start()
        app.logger.info("Scheduler démarré pour la synchronisation WEDOF")
    
    # Initialisation de la base de données si elle n'existe pas
    with app.app_context():
        db.create_all()
        
        # Vérifier si un superadmin existe déjà
        from app.models import User
        admin = User.query.filter_by(email='admin@example.com').first()
        if not admin:
            # Créer un superadmin
            admin = User(email='admin@example.com', role='superadmin')
            admin.set_password('admin123')
            
            # Créer un utilisateur admin
            user_admin = User(email='user@example.com', role='admin')
            user_admin.set_password('user123')
            
            # Créer un opérateur
            operateur = User(email='operateur@example.com', role='operateur')
            operateur.set_password('operateur123')
            
            db.session.add_all([admin, user_admin, operateur])
            db.session.commit()
            
            app.logger.info('Base de données initialisée avec les utilisateurs par défaut')
    
    return app

# Import des modèles pour qu'ils soient disponibles pour les migrations
from app.models import User, Formation, Client, Product 