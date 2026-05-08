"""
QMail Flask Application
"""

import os
import logging
from flask import Flask
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
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

    # Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    
    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))
    
    # Configure logging - only use StreamHandler for Vercel (read-only file system)
    log_handlers = [logging.StreamHandler()]
    
    # Only add FileHandler in development mode
    if os.getenv('FLASK_ENV', 'development') == 'development':
        try:
            log_handlers.insert(0, logging.FileHandler(app.config['LOG_FILE']))
        except (OSError, IOError):
            # If file write fails (e.g., read-only filesystem), just use console
            pass
    
    logging.basicConfig(
        level=getattr(logging, app.config['LOG_LEVEL']),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=log_handlers
    )
    
    # Register blueprints
    try:
        from qmail.core.routes import auth, main, email_routes, api
        
        app.register_blueprint(auth.bp)
        app.register_blueprint(main.bp)
        app.register_blueprint(email_routes.bp)
        app.register_blueprint(api.bp)
    except ImportError as e:
        app.logger.warning(f"Could not import all blueprints: {e}")
    
    # Add health check endpoint
    @app.route('/health', methods=['GET'])
    def health_check():
        """Health check endpoint for Vercel"""
        return {'status': 'healthy', 'message': 'QMail server is running'}, 200
    
    # Error handlers
    @app.errorhandler(500)
    def internal_error(error):
        """Handle internal server errors"""
        app.logger.error(f'Server Error: {error}')
        return {
            'error': 'Internal Server Error',
            'message': str(error),
            'status': 500
        }, 500
    
    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 errors"""
        return {
            'error': 'Not Found',
            'message': 'The requested resource was not found',
            'status': 404
        }, 404
    
    # Create database tables and seed default admin user
    with app.app_context():
        db.create_all()
        _ensure_default_admin(app)

    return app


def _ensure_default_admin(app):
    """Create a default admin account on first boot.

    Username / password / email are configurable via env vars:
      DEFAULT_ADMIN_USERNAME (default: 'admin')
      DEFAULT_ADMIN_PASSWORD (default: 'admin')
      DEFAULT_ADMIN_EMAIL    (default: 'admin@qmail.local')

    Set DEFAULT_ADMIN_DISABLE=true in production to skip seeding entirely.
    """
    if os.getenv('DEFAULT_ADMIN_DISABLE', 'false').lower() == 'true':
        return

    username = os.getenv('DEFAULT_ADMIN_USERNAME', 'admin')
    password = os.getenv('DEFAULT_ADMIN_PASSWORD', 'admin')
    email = os.getenv('DEFAULT_ADMIN_EMAIL', 'admin@qmail.local')

    try:
        existing = User.query.filter_by(username=username).first()
        if existing:
            return

        admin = User(username=username, email=email, is_verified=True)
        admin.set_password(password)
        db.session.add(admin)
        db.session.commit()

        app.logger.warning(
            "Created default admin account '%s' with the default password. "
            "Change it immediately or set DEFAULT_ADMIN_PASSWORD / "
            "DEFAULT_ADMIN_DISABLE env vars before deploying to production.",
            username,
        )
    except Exception as e:  # pragma: no cover - defensive bootstrap
        db.session.rollback()
        app.logger.error("Failed to seed default admin user: %s", e)


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
