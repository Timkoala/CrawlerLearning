from app import db
from datetime import datetime
import json

class CrawlJob(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    target_url = db.Column(db.String(500), nullable=False)
    max_depth = db.Column(db.Integer, default=1)
    custom_rules = db.Column(db.Text)  # Store custom rules as JSON string
    status = db.Column(db.String(20), default='saved')  # saved, running, completed, failed, stopped
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<CrawlJob {self.name}>'
        
    def to_dict(self):
        result = {
            'id': self.id,
            'name': self.name,
            'target_url': self.target_url,
            'max_depth': self.max_depth,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        # Add custom rules if they exist
        if self.custom_rules:
            try:
                result['custom_rules'] = json.loads(self.custom_rules)
            except:
                result['custom_rules'] = self.custom_rules
                
        return result

class CrawlResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('crawl_job.id'), nullable=False)
    url = db.Column(db.String(500), nullable=False)
    title = db.Column(db.String(200))
    content = db.Column(db.Text)
    scraped_data = db.Column(db.Text)  # Store all scraped data as JSON string
    scraped_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    job = db.relationship('CrawlJob', backref=db.backref('results', lazy=True))
    
    def __repr__(self):
        return f'<CrawlResult {self.url}>'
        
    def to_dict(self):
        result = {
            'id': self.id,
            'job_id': self.job_id,
            'url': self.url,
            'title': self.title,
            'content': self.content,
            'scraped_at': self.scraped_at.isoformat() if self.scraped_at else None
        }
        
        # Add scraped data if it exists
        if self.scraped_data:
            try:
                result['scraped_data'] = json.loads(self.scraped_data)
            except:
                result['scraped_data'] = self.scraped_data
                
        return result