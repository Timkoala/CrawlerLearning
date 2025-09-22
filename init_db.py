import os
import sys

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from models.database import init_db

def init_database():
    """Initialize the database"""
    app = create_app()
    with app.app_context():
        init_db()
        print("Database initialized successfully!")

if __name__ == '__main__':
    init_database()