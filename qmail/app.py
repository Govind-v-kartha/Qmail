"""
QMail Flask Application
"""

import os
import logging
from flask import Flask
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_talisman import Talisman
from dotenv import load_dotenv

from qmail.models.database import db, User
from qmail.core.config import config

# Load environment variables
load_dotenv()

# Initialize CSRF protection
csrf = CSRFProtect()


def create_app(config_name=None):
    """
    Application factory
    
    Args:
        config_name: Configuration name (development, testing, production)
    
    Returns:
        Flask application instance
    """
    app = Flask(__name__)
    
    # Load configuration
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    
    # Initialize CSRF protection
    csrf.init_app(app)
    
    # Initialize security headers (disabled HTTPS for development)
    # TEMPORARILY DISABLED TALISMAN FOR DEBUGGING
    # csp = {
    #     'default-src': "'self'",
    #     'script-src': ["'self'", "'unsafe-inline'", "cdn.jsdelivr.net", "cdnjs.cloudflare.com"],
    #     'style-src': ["'self'", "'unsafe-inline'", "cdn.jsdelivr.net", "cdnjs.cloudflare.com"],
    #     'img-src': ["'self'", "data:", "https:"],
    #     'font-src': ["'self'", "cdn.jsdelivr.net", "cdnjs.cloudflare.com"],
    # }
    
    # Talisman(app,
    #     force_https=False,  # Set to True in production
    #     strict_transport_security=False,  # Set to True in production
    #     content_security_policy=csp,
    #     content_security_policy_nonce_in=['script-src']
    # )
    
    # Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, app.config['LOG_LEVEL']),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(app.config['LOG_FILE']),
            logging.StreamHandler()
        ]
    )
    
    # Register blueprints
    from qmail.core.routes import auth, main, email_routes, api
    
    app.register_blueprint(auth.bp)
    app.register_blueprint(main.bp)
    app.register_blueprint(email_routes.bp)
    app.register_blueprint(api.bp)
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
