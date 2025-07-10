from app import create_app, scheduler
import os
import atexit

app = create_app()

# Enregistrer une fonction pour arrêter le scheduler lors de l'arrêt de l'application
atexit.register(lambda: scheduler.shutdown(wait=False))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000))) 