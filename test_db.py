from app import create_app, db

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        # Create all tables
        db.create_all()
        print("Database tables created successfully!")
        
        # Check if tables exist
        from models.job import CrawlJob, CrawlResult
        print("Tables in database:")
        print(CrawlJob.__table__.columns.keys())
        print(CrawlResult.__table__.columns.keys())