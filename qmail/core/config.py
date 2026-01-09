"""
Application configuration
"""

import os
from datetime import timedelta


class Config:
    """Base configuration"""
    
    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY')
    if not SECRET_KEY:
        # Generate a random key if not set (for development only)
        import secrets
        SECRET_KEY = secrets.token_hex(32)
        print(f"WARNING: SECRET_KEY not set. Generated random key: {SECRET_KEY}")
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///qmail.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'connect_args': {'timeout': 15} if 'sqlite' in SQLALCHEMY_DATABASE_URI else {},
        'pool_size': 10 if 'sqlite' not in SQLALCHEMY_DATABASE_URI else None,
        'pool_recycle': 3600 if 'sqlite' not in SQLALCHEMY_DATABASE_URI else None,
    }
    
    # Session
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=int(os.getenv('SESSION_TIMEOUT', 30)))
    
    # Security
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None
    
    # Upload
    MAX_CONTENT_LENGTH = int(os.getenv('MAX_EMAIL_SIZE', 25)) * 1024 * 1024  # MB
    
    # QKD Configuration
    QKD_KM_HOST = os.getenv('QKD_KM_HOST', 'localhost')
    QKD_KM_PORT = int(os.getenv('QKD_KM_PORT', 8080))
    QKD_KM_API_VERSION = os.getenv('QKD_KM_API_VERSION', 'v1')
    QKD_KM_MASTER_SAE_ID = os.getenv('QKD_KM_MASTER_SAE_ID', '')
    QKD_KM_SLAVE_SAE_ID = os.getenv('QKD_KM_SLAVE_SAE_ID', '')
    QKD_KM_USE_HTTPS = os.getenv('QKD_KM_USE_HTTPS', 'false').lower() == 'true'
    QKD_KM_VERIFY_SSL = os.getenv('QKD_KM_VERIFY_SSL', 'true').lower() == 'true'
    QKD_USE_MOCK = os.getenv('QKD_USE_MOCK', 'true').lower() == 'true'
    
    # Email Configuration
    SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
    SMTP_USE_TLS = os.getenv('SMTP_USE_TLS', 'true').lower() == 'true'
    
    IMAP_SERVER = os.getenv('IMAP_SERVER', 'imap.gmail.com')
    IMAP_PORT = int(os.getenv('IMAP_PORT', 993))
    IMAP_USE_SSL = os.getenv('IMAP_USE_SSL', 'true').lower() == 'true'
    
    # Default Security Level
    DEFAULT_SECURITY_LEVEL = int(os.getenv('DEFAULT_SECURITY_LEVEL', 2))
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'qmail.log')


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False


class TestingConfig(Config):
    """Testing configuration"""
    DEBUG = False
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///test_qmail.db'
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False
    
    # Override with more secure defaults
    QKD_USE_MOCK = False
    WTF_CSRF_ENABLED = True


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
