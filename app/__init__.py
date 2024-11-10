from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Initialisation de l'extension SQLAlchemy
db = SQLAlchemy()
migrate= Migrate()
def create_app():
    # Créer une instance de l'application Flask
    app = Flask(__name__)
    app.config.from_pyfile('../config.py')

    # Initialiser SQLAlchemy avec l'application
    db.init_app(app)

    # Initialiser Flask-Migrate avec l'application et la base de données
    migrate.init_app(app,db)

    # Enregistrer les routes
    from .routes import main
    app.register_blueprint(main)

    # Créer le schéma de la base de données (tables)
    with app.app_context():
        db.create_all()

    return app
