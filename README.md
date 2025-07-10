# Formation Manager

Une application web pour gérer les formations, les bons d'achat et les commandes de produits.

## Fonctionnalités

- Synchronisation avec l'API WEDOF toutes les 60 secondes
- Calcul automatique des bons d'achat (30% du prix de la formation)
- Gestion des clients et de leurs formations
- Suivi des produits commandés avec le bon d'achat
- Système d'authentification avec différents rôles utilisateur (superadmin, admin, operateur)

## Rôles utilisateur

- **superadmin**: Gestion des utilisateurs uniquement
- **admin**: Gestion des clients, formations et produits
- **operateur**: Consultation des clients et marquage des produits comme livrés

## Installation

1. Cloner le dépôt
```bash
git clone <url-du-depot>
cd Training_Check_Platform
```

2. Créer un environnement virtuel et l'activer
```bash
python -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate
```

3. Installer les dépendances
```bash
pip install -r requirements.txt
```

4. Initialiser la base de données
```bash
flask init-db
```

5. Lancer l'application
```bash
flask run
```

## Utilisation

1. Accéder à l'application via http://localhost:5000
2. Se connecter avec les identifiants par défaut:
   - Superadmin: admin@example.com / admin123
   - Admin: user@example.com / user123
   - Opérateur: operateur@example.com / operateur123

## Structure du projet

```
Training_Check_Platform/
  ├── app/                      # Package principal de l'application
  │   ├── models/               # Modèles de données
  │   ├── routes/               # Routes et vues
  │   ├── services/             # Services (API sync, etc.)
  │   ├── static/               # Fichiers statiques (CSS, JS, images)
  │   ├── templates/            # Templates HTML
  │   └── utils/                # Utilitaires
  ├── migrations/               # Migrations de base de données
  ├── run.py                    # Point d'entrée de l'application
  └── requirements.txt          # Dépendances Python
```

## Déploiement

Pour déployer l'application en production:

1. Configurer les variables d'environnement:
   - `SECRET_KEY`: Clé secrète pour la sécurité de l'application
   - `DATABASE_URL`: URL de la base de données (si différente de SQLite)

2. Exécuter avec Gunicorn:
```bash
gunicorn "app:create_app()"
```

## Développement

Pour contribuer au développement:

1. Créer une branche pour votre fonctionnalité
```bash
git checkout -b ma-nouvelle-fonctionnalite
```

2. Effectuer vos modifications et les tester

3. Soumettre une pull request 