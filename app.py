from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
import logging

# Configure logging for the Flask app
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Initialize extensions
db = SQLAlchemy()

def create_app():
    app = Flask(__name__, 
                template_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'web', 'templates'),
                static_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'web', 'static'))
    app.config['SECRET_KEY'] = 'your-secret-key-here'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///crawler.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize extensions
    db.init_app(app)
    
    # Register blueprints
    from web import bp as web_bp
    app.register_blueprint(web_bp, url_prefix='')
    
    # Set up logging for the app
    app.logger.setLevel(logging.INFO)
    
    return app