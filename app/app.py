from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Initialize the database
db = SQLAlchemy()

def create_app():
    # Initialize the Flask app
    app = Flask(__name__)

    # Configure the app (importing configurations from a config file)
    app.config.from_pyfile('config.py')

    # Initialize the database with the app
    db.init_app(app)

    # Import and register blueprints (for modular routes handling)
    from .routes import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app

# To run the app if app.py is called directly
if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
