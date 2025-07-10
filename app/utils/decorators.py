from functools import wraps
from flask import abort, current_app
from flask_login import current_user

def superadmin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            current_app.logger.error("Utilisateur non authentifié")
            abort(403)
        
        # Ajouter des logs pour déboguer
        current_app.logger.info(f"Utilisateur: {current_user.email}, Rôle: {current_user.role}")
        
        if not current_user.is_superadmin():
            current_app.logger.error(f"Accès refusé: {current_user.email} n'est pas un superadmin")
            abort(403)
        
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

def admin_or_operateur_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or (not current_user.is_admin() and not current_user.is_operateur()):
            abort(403)
        return f(*args, **kwargs)
    return decorated_function 