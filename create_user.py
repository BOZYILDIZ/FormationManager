from app import create_app, db
from app.models.user import User

app = create_app()
with app.app_context():
    # Supprimer tous les utilisateurs existants
    User.query.delete()
    db.session.commit()
    
    # Créer un nouvel utilisateur admin
    admin = User(email='admin@example.com', role='admin')
    admin.set_password('admin123')
    db.session.add(admin)
    
    # Créer un utilisateur superadmin
    superadmin = User(email='superadmin@example.com', role='superadmin')
    superadmin.set_password('admin123')
    db.session.add(superadmin)
    
    # Créer un utilisateur opérateur
    operateur = User(email='operateur@example.com', role='operateur')
    operateur.set_password('admin123')
    db.session.add(operateur)
    
    db.session.commit()
    print('Utilisateurs créés avec succès')
