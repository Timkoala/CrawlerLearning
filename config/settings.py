# Application settings

class Config:
    # Database settings
    SQLALCHEMY_DATABASE_URI = 'sqlite:///crawler.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Secret key for sessions
    SECRET_KEY = 'your-secret-key-here'
    
    # Crawler settings
    DEFAULT_USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    DEFAULT_DELAY = 1  # seconds
    DEFAULT_CONCURRENT_REQUESTS = 16
    DEFAULT_DOWNLOAD_DELAY = 3  # seconds
    
    # Proxy settings
    PROXY_ENABLED = False
    PROXY_LIST = []
    
    # Retry settings
    RETRY_ENABLED = True
    RETRY_TIMES = 3