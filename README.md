# Formation Manager

Application web de gestion des formations CPF et des bons d'achat associés.

## Fonctionnalités

- Gestion des clients et de leurs formations
- Gestion des bons d'achat (valeur fixe ou pourcentage)
- Synchronisation avec l'API WEDOF
- Gestion des utilisateurs avec différents rôles (superadmin, admin, opérateur)
- Interface multilingue (français, turc)
- Journalisation des actions et des erreurs

## Installation

1. Cloner le dépôt
```bash
git clone https://github.com/BOZYILDIZ/FormationManager.git
cd FormationManager
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

4. Lancer l'application
```bash
python run.py
```

L'application sera accessible à l'adresse http://localhost:5000

## Configuration

### API WEDOF

Pour configurer la connexion à l'API WEDOF :
1. Connectez-vous en tant qu'administrateur
2. Accédez à la page "API WEDOF" dans la barre de navigation
3. Renseignez l'URL, la clé API et le secret API
4. Activez ou désactivez la synchronisation automatique selon vos besoins
5. Cliquez sur "Enregistrer la configuration"

### Utilisateurs par défaut

- Superadmin: admin@example.com / admin123
- Admin: user@example.com / user123
- Opérateur: operateur@example.com / operateur123

## Journalisation

Les journaux sont stockés dans le dossier `instance/logs/` :
- `errors.log` : Erreurs techniques
- `user_actions.log` : Actions des utilisateurs

## Licence

© 2023 Formation Manager 