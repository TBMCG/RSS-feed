import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Flask configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Session configuration for persistent login
    SESSION_TYPE = 'filesystem'
    SESSION_COOKIE_SECURE = True  # Required for HTTPS in production
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'None'  # Allow cross-domain cookies
    SESSION_PERMANENT = True
    PERMANENT_SESSION_LIFETIME = 86400  # 24 hours in seconds
    
    # Microsoft Azure AD configuration
    CLIENT_ID = os.environ.get('MICROSOFT_CLIENT_ID')
    CLIENT_SECRET = os.environ.get('MICROSOFT_CLIENT_SECRET')
    AUTHORITY = os.environ.get('AUTHORITY') or f"https://login.microsoftonline.com/{os.environ.get('MICROSOFT_TENANT_ID', 'common')}"
    REDIRECT_PATH = '/auth/callback'  # OAuth callback endpoint
    SCOPE = ['User.ReadBasic.All']  # Microsoft Graph permissions
    
    # Domain whitelist for access control
    ALLOWED_DOMAINS = ['tbmcg.com']
    
    # Database configuration
    DATABASE_URL = os.environ.get('DATABASE_URL') or 'mssql+pymssql://localhost/tbmcg_news_dashboard'
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Database connection pool settings for Azure SQL
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,          # Number of connections to maintain
        'pool_timeout': 30,        # Timeout for getting connection from pool
        'pool_recycle': 1800,     # Recycle connections after 30 minutes
        'pool_pre_ping': True,    # Validate connections before use
        'max_overflow': 20,       # Additional connections beyond pool_size
        'connect_args': {
            'timeout': 30,        # Connection timeout in seconds
            'login_timeout': 30   # Login timeout in seconds
        }
    }
    
    # Frontend URL for redirects (Netlify URL in production)
    FRONTEND_URL = os.environ.get('FRONTEND_URL', 'http://localhost:5000')