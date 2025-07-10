"""
Service de localisation pour gérer les traductions
"""
from flask import g, request, session
from app.translations.fr import fr
from app.translations.tr import tr

def get_locale():
    """
    Détermine la locale à utiliser en fonction de la session, 
    des paramètres de requête ou de la langue par défaut.
    """
    # Vérifier si la langue est spécifiée dans la requête
    if request.args.get('lang'):
        lang = request.args.get('lang')
        if lang in ['fr', 'tr']:
            session['lang'] = lang
            return lang
    
    # Vérifier si la langue est stockée en session
    if 'lang' in session:
        return session['lang']
    
    # Langue par défaut
    return 'fr'

def init_localization():
    """
    Initialise les variables de localisation pour la requête en cours.
    Cette fonction doit être appelée avant chaque requête.
    """
    # Déterminer la langue à utiliser
    g.lang = get_locale()
    
    # Charger les traductions correspondantes
    if g.lang == 'tr':
        g.translations = tr
    else:
        g.translations = fr
    
    # Fonction de traduction accessible dans les templates
    def translate(key):
        """
        Traduit une clé dans la langue actuelle.
        Si la clé n'existe pas, retourne la clé elle-même.
        """
        return g.translations.get(key, key)
    
    g.translate = translate 