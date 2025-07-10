import requests
import json
from datetime import datetime, timedelta
from flask import current_app, flash
from app import db
from app.models import Client, Formation
import os

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

def get_wedof_data():
    """
    Récupère les données depuis l'API WEDOF.
    Pour le développement, on simule une réponse API avec les formations réelles.
    """
    try:
        # Récupérer la configuration API
        api_config = get_api_config()
        
        # Dans un environnement de production, on utiliserait :
        if api_config['key'] and api_config['secret']:
            try:
                response = requests.get(
                    api_config['url'],
                    headers={
                        'Authorization': f"Bearer {api_config['key']}",
                        'X-API-Secret': api_config['secret']
                    },
                    timeout=10
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    current_app.logger.error(f"Erreur API WEDOF: {response.status_code} - {response.text}")
            except Exception as e:
                current_app.logger.error(f"Erreur lors de la connexion à l'API WEDOF: {str(e)}")
        
        # Pour le développement ou en cas d'erreur, on simule des données
        current_app.logger.info("Utilisation des données de développement pour WEDOF API")
        data = [
            # Formations Microsoft Office
            {
                "client_name": "Jean Dupont",
                "client_email": "jean.dupont@example.com",
                "client_phone": "+33612345678",
                "formation_title": "Microsoft Word – Niveau 1",
                "formation_price": 500.0,
                "formation_status": "validé",
                "formation_code": "RS6964",
                "invoice_date": "2023-05-15",
                "payment_received": True,
                "cpf_id": "CPF-1234567"
            },
            {
                "client_name": "Marie Martin",
                "client_email": "marie.martin@example.com",
                "client_phone": "+33687654321",
                "formation_title": "Microsoft Word – Niveau 2",
                "formation_price": 800.0,
                "formation_status": "accepté",
                "formation_code": "RS6964",
                "invoice_date": "2023-06-01",
                "payment_received": False,
                "cpf_id": "CPF-2345678"
            },
            {
                "client_name": "Pierre Durand",
                "client_email": "pierre.durand@example.com",
                "client_phone": "+33678901234",
                "formation_title": "Microsoft Excel",
                "formation_price": 1100.0,
                "formation_status": "validé",
                "formation_code": "RS5252",
                "invoice_date": "2023-07-10",
                "payment_received": True,
                "cpf_id": "CPF-3456789"
            },
            {
                "client_name": "Sophie Lefebvre",
                "client_email": "sophie.lefebvre@example.com",
                "client_phone": "+33654321098",
                "formation_title": "Microsoft Outlook",
                "formation_price": 1400.0,
                "formation_status": "accepté",
                "formation_code": "RS6958",
                "invoice_date": None,
                "payment_received": False
            },
            # Formations DigComp
            {
                "client_name": "Thomas Bernard",
                "client_email": "thomas.bernard@example.com",
                "client_phone": "+33612345987",
                "formation_title": "Formation DigComp (Tosa) – Compétences numériques",
                "formation_price": 2000.0,
                "formation_status": "validé",
                "formation_code": "RS5893",
                "invoice_date": "2023-04-20",
                "payment_received": True
            },
            # Autres formations
            {
                "client_name": "Julie Petit",
                "client_email": "julie.petit@example.com",
                "client_phone": "+33678563412",
                "formation_title": "Microsoft PowerPoint",
                "formation_price": 2300.0,
                "formation_status": "validé",
                "formation_code": "RS6961",
                "invoice_date": "2023-03-15",
                "payment_received": True
            },
            {
                "client_name": "Lucas Moreau",
                "client_email": "lucas.moreau@example.com",
                "client_phone": "+33698765432",
                "formation_title": "Photoshop",
                "formation_price": 2900.0,
                "formation_status": "refusé",
                "formation_code": "RS6959",
                "invoice_date": None,
                "payment_received": False
            },
            {
                "client_name": "Emma Dubois",
                "client_email": "emma.dubois@example.com",
                "client_phone": "+33623456789",
                "formation_title": "WordPress",
                "formation_price": 3200.0,
                "formation_status": "validé",
                "formation_code": "RS6965",
                "invoice_date": "2023-06-25",
                "payment_received": True
            },
            {
                "client_name": "Léo Martin",
                "client_email": "leo.martin@example.com",
                "client_phone": "+33634567890",
                "formation_title": "Python",
                "formation_price": 3400.0,
                "formation_status": "accepté",
                "formation_code": "RS6962",
                "invoice_date": "2023-07-05",
                "payment_received": False
            },
            {
                "client_name": "Chloé Roux",
                "client_email": "chloe.roux@example.com",
                "client_phone": "+33645678901",
                "formation_title": "Microsoft VBA",
                "formation_price": 3800.0,
                "formation_status": "validé",
                "formation_code": "RS6963",
                "invoice_date": "2023-05-10",
                "payment_received": True
            },
            {
                "client_name": "Hugo Leroy",
                "client_email": "hugo.leroy@example.com",
                "client_phone": "+33656789012",
                "formation_title": "Illustrator",
                "formation_price": 4400.0,
                "formation_status": "accepté",
                "formation_code": "RS6956",
                "invoice_date": None,
                "payment_received": False
            },
            {
                "client_name": "Inès Girard",
                "client_email": "ines.girard@example.com",
                "client_phone": "+33667890123",
                "formation_title": "InDesign",
                "formation_price": 4800.0,
                "formation_status": "validé",
                "formation_code": "RS6957",
                "invoice_date": "2023-04-15",
                "payment_received": True
            },
            {
                "client_name": "Nathan Fournier",
                "client_email": "nathan.fournier@example.com",
                "client_phone": "+33678901234",
                "formation_title": "AutoCAD",
                "formation_price": 5000.0,
                "formation_status": "accepté",
                "formation_code": "RS6955",
                "invoice_date": "2023-06-20",
                "payment_received": False
            },
            # Bilans de compétences
            {
                "client_name": "Camille Morel",
                "client_email": "camille.morel@example.com",
                "client_phone": "+33689012345",
                "formation_title": "Bilan de compétences - Standard",
                "formation_price": 1500.0,
                "formation_status": "validé",
                "formation_code": "BC001",
                "invoice_date": "2023-07-01",
                "payment_received": True
            },
            {
                "client_name": "Antoine Dupuis",
                "client_email": "antoine.dupuis@example.com",
                "client_phone": "+33690123456",
                "formation_title": "Bilan de compétences - Approfondi",
                "formation_price": 2500.0,
                "formation_status": "accepté",
                "formation_code": "BC002",
                "invoice_date": "2023-06-15",
                "payment_received": False
            },
            {
                "client_name": "Sarah Lambert",
                "client_email": "sarah.lambert@example.com",
                "client_phone": "+33601234567",
                "formation_title": "Bilan de compétences - Carrière",
                "formation_price": 3000.0,
                "formation_status": "validé",
                "formation_code": "BC003",
                "invoice_date": "2023-05-20",
                "payment_received": True
            }
        ]
        
        return data
    
    except Exception as e:
        current_app.logger.error(f"Erreur lors de la récupération des données WEDOF: {str(e)}")
        return []

def sync_wedof_data(app):
    """
    Synchronise les données de l'API WEDOF avec la base de données locale.
    Cette fonction est appelée périodiquement par le scheduler.
    """
    with app.app_context():
        current_app.logger.info("Début de la synchronisation WEDOF")
        
        data = get_wedof_data()
        
        new_clients = 0
        updated_clients = 0
        
        for item in data:
            # Rechercher ou créer la formation
            formation = Formation.query.filter_by(title=item['formation_title']).first()
            
            if not formation:
                formation = Formation(
                    title=item['formation_title'],
                    price=item['formation_price'],
                    status=item['formation_status'],
                    code=item.get('formation_code', '')  # Ajout du code RS
                )
                db.session.add(formation)
                db.session.flush()  # Pour obtenir l'ID de la formation
            else:
                # Mise à jour des informations de la formation
                formation.price = item['formation_price']
                formation.status = item['formation_status']
                if 'formation_code' in item:
                    formation.code = item['formation_code']
            
            # Rechercher par CPF ID d'abord, puis par email si pas trouvé
            client = None
            if 'cpf_id' in item and item['cpf_id']:
                client = Client.query.filter_by(cpf_id=item['cpf_id']).first()
            
            if not client:
                client = Client.query.filter_by(email=item['client_email']).first()
            
            if not client:
                # Nouveau client
                client = Client(
                    name=item['client_name'],
                    email=item['client_email'],
                    phone=item['client_phone'],
                    formation_id=formation.id,
                    cpf_id=item.get('cpf_id', '')
                )
                
                # Calculer la valeur du bon d'achat (30% par défaut)
                client.update_bon_value()
                
                # Gérer la date de facturation et le statut de paiement
                if 'invoice_date' in item and item['invoice_date']:
                    client.invoice_date = datetime.strptime(item['invoice_date'], '%Y-%m-%d')
                    client.update_expected_payment_date()
                
                client.payment_received = item.get('payment_received', False)
                
                db.session.add(client)
                new_clients += 1
            else:
                # Mise à jour du client existant
                client.name = item['client_name']
                client.phone = item.get('phone', client.phone)
                
                # Mettre à jour la formation si elle a changé
                if client.formation_id != formation.id:
                    client.formation_id = formation.id
                    client.update_bon_value()
                
                # Mettre à jour le CPF ID s'il est fourni
                if 'cpf_id' in item and item['cpf_id']:
                    client.cpf_id = item['cpf_id']
                
                # Gérer la date de facturation et le statut de paiement
                if 'invoice_date' in item and item['invoice_date']:
                    new_invoice_date = datetime.strptime(item['invoice_date'], '%Y-%m-%d')
                    if not client.invoice_date or client.invoice_date != new_invoice_date:
                        client.invoice_date = new_invoice_date
                        client.update_expected_payment_date()
                
                if 'payment_received' in item:
                    client.payment_received = item['payment_received']
                
                updated_clients += 1
        
        db.session.commit()
        
        current_app.logger.info(f"Synchronisation WEDOF terminée: {new_clients} nouveaux clients, {updated_clients} clients mis à jour")
        return {
            "new_clients": new_clients,
            "updated_clients": updated_clients,
            "total": len(data)
        }

def manual_sync_wedof():
    """
    Fonction pour déclencher manuellement la synchronisation depuis une route
    """
    try:
        result = sync_wedof_data(current_app._get_current_object())
        return True, f"Synchronisation réussie: {result['new_clients']} nouveaux clients, {result['updated_clients']} clients mis à jour sur {result['total']} au total"
    except Exception as e:
        current_app.logger.error(f"Erreur lors de la synchronisation manuelle: {str(e)}")
        return False, f"Erreur lors de la synchronisation: {str(e)}" 