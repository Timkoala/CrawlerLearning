import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db

def init_database():
    """Initialize the database"""
    app = create_app()
    with app.app_context():
        # Drop all tables first (optional, for clean start)
        # db.drop_all()
        
        # Create all tables
        db.create_all()
        print("Database initialized successfully!")

if __name__ == '__main__':
    init_database()