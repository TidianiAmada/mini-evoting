from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_pyfile('../config.py')

    db.init_app(app)

    # Register routes
    from .routes import main
    app.register_blueprint(main)
    # Create database schema
    # Create database schema
    with app.app_context():
        db.create_all()
        
    return app
