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

def _run_light_migrations(app):
    from sqlalchemy import text
    with app.app_context():
        # Ensure tables exist
        db.create_all()
        try:
            # Add run_id column to crawl_result if missing
            result = db.session.execute(text("PRAGMA table_info(crawl_result);"))
            cols = [row[1] for row in result]
            if 'run_id' not in cols:
                app.logger.info('Migrating: adding run_id to crawl_result')
                db.session.execute(text("ALTER TABLE crawl_result ADD COLUMN run_id INTEGER"))
                db.session.commit()
        except Exception as e:
            app.logger.error(f"Migration error: {e}")


def create_app():
    app = Flask(__name__, 
                template_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'web', 'templates'),
                static_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'web', 'static'))
    app.config['SECRET_KEY'] = 'your-secret-key-here'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///crawler.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize extensions
    db.init_app(app)
    
    # Auto create tables & run light migrations on startup
    with app.app_context():
        try:
            from models import job  # ensure models are imported
            db.create_all()
            _run_light_migrations(app)
        except Exception as e:
            app.logger.error(f"Auto DB init failed: {e}")
    
    # Register blueprints
    from web import bp as web_bp
    app.register_blueprint(web_bp, url_prefix='')
    
    # Set up logging for the app
    app.logger.setLevel(logging.INFO)
    
    return app