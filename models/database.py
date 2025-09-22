from app import db
from models.job import CrawlJob, CrawlResult

def init_db():
    """Initialize the database"""
    db.create_all()
    
def create_tables():
    """Create all tables"""
    db.create_all()
    
def drop_tables():
    """Drop all tables"""
    db.drop_all()