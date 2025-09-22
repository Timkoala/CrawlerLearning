# Security settings

class SecurityConfig:
    # Secret key for sessions
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-here')
    
    # API key for protecting API endpoints
    API_KEY = os.environ.get('API_KEY', 'default-api-key')
    
    # Database settings
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///crawler.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Security headers
    SECURITY_HEADERS = {
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'DENY',
        'X-XSS-Protection': '1; mode=block',
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
        'Content-Security-Policy': "default-src 'self'"
    }