"""
Implement Critical OWASP Security Fixes
Run this to add essential security protections
"""

import os
import sys

def print_header(text):
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}\n")

def install_dependencies():
    """Install required security packages"""
    print_header("Installing Security Packages")
    
    packages = [
        'flask-talisman',  # Security headers
        'flask-limiter',   # Rate limiting
        'bleach',          # HTML sanitization
        'Flask-WTF',       # CSRF protection
        'cryptography',    # Encryption
    ]
    
    print("Installing:")
    for pkg in packages:
        print(f"  - {pkg}")
    
    print("\nRun this command:")
    print(f"pip install {' '.join(packages)}")
    print("\nPress Enter when done...")
    input()

def create_security_config():
    """Create security configuration file"""
    print_header("Creating Security Configuration")
    
    config_content = '''"""
Security Configuration for QMail
"""

import os
from datetime import timedelta

class SecurityConfig:
    """Security settings"""
    
    # CSRF Protection
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None  # No time limit
    
    # Session Security
    SESSION_COOKIE_SECURE = True  # HTTPS only
    SESSION_COOKIE_HTTPONLY = True  # No JavaScript access
    SESSION_COOKIE_SAMESITE = 'Lax'  # CSRF protection
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)  # 30 min timeout
    
    # Security Headers (Talisman)
    TALISMAN_FORCE_HTTPS = True
    TALISMAN_STRICT_TRANSPORT_SECURITY = True
    TALISMAN_CONTENT_SECURITY_POLICY = {
        'default-src': "'self'",
        'script-src': ["'self'", "'unsafe-inline'", "cdn.jsdelivr.net", "cdnjs.cloudflare.com"],
        'style-src': ["'self'", "'unsafe-inline'", "cdn.jsdelivr.net", "cdnjs.cloudflare.com"],
        'img-src': ["'self'", "data:", "https:"],
        'font-src': ["'self'", "cdn.jsdelivr.net", "cdnjs.cloudflare.com"],
    }
    
    # Rate Limiting
    RATELIMIT_ENABLED = True
    RATELIMIT_STORAGE_URL = "memory://"
    RATELIMIT_DEFAULT = "200 per day, 50 per hour"
    RATELIMIT_HEADERS_ENABLED = True
    
    # Password Encryption Key (for SMTP/IMAP passwords)
    ENCRYPTION_KEY = os.environ.get('ENCRYPTION_KEY', 'CHANGE-THIS-IN-PRODUCTION')
    
    # File Upload Security
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx'}
    
    # Logging
    LOG_SECURITY_EVENTS = True
    LOG_FILE = 'logs/security.log'
'''
    
    with open('qmail/config/security.py', 'w') as f:
        f.write(config_content)
    
    print("✅ Created: qmail/config/security.py")

def create_security_middleware():
    """Create security middleware"""
    print_header("Creating Security Middleware")
    
    middleware_content = '''"""
Security Middleware for QMail
"""

from flask import request, session
from flask_talisman import Talisman
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_wtf.csrf import CSRFProtect
from datetime import datetime, timedelta
import logging

# Initialize extensions
csrf = CSRFProtect()
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

# Security logger
security_logger = logging.getLogger('security')
security_logger.setLevel(logging.INFO)
handler = logging.FileHandler('logs/security.log')
handler.setFormatter(logging.Formatter(
    '%(asctime)s - %(levelname)s - %(message)s'
))
security_logger.addHandler(handler)


def init_security(app):
    """Initialize all security features"""
    
    # CSRF Protection
    csrf.init_app(app)
    
    # Rate Limiting
    limiter.init_app(app)
    
    # Security Headers
    csp = {
        'default-src': "'self'",
        'script-src': ["'self'", "'unsafe-inline'", "cdn.jsdelivr.net", "cdnjs.cloudflare.com"],
        'style-src': ["'self'", "'unsafe-inline'", "cdn.jsdelivr.net", "cdnjs.cloudflare.com"],
        'img-src': ["'self'", "data:", "https:"],
        'font-src': ["'self'", "cdn.jsdelivr.net", "cdnjs.cloudflare.com"],
    }
    
    Talisman(app,
        force_https=app.config.get('TALISMAN_FORCE_HTTPS', False),  # False for dev
        strict_transport_security=True,
        content_security_policy=csp,
        content_security_policy_nonce_in=['script-src']
    )
    
    # Session timeout
    @app.before_request
    def check_session_timeout():
        """Check if session has timed out"""
        if 'last_activity' in session:
            last_activity = session['last_activity']
            if datetime.utcnow() - last_activity > timedelta(minutes=30):
                session.clear()
                return redirect(url_for('auth.login'))
        session['last_activity'] = datetime.utcnow()
    
    # Security event logging
    @app.after_request
    def log_security_events(response):
        """Log security-relevant requests"""
        if request.method in ['POST', 'PUT', 'DELETE']:
            security_logger.info(f"{request.method} {request.path} - {response.status_code}")
        return response
    
    print("✅ Security middleware initialized")


def log_auth_event(event_type, username, success=True, ip_address=None):
    """Log authentication events"""
    security_logger.info(
        f"AUTH: {event_type} - User: {username} - "
        f"Success: {success} - IP: {ip_address or 'unknown'}"
    )


def log_security_event(event_type, details):
    """Log general security events"""
    security_logger.warning(f"SECURITY: {event_type} - {details}")
'''
    
    os.makedirs('qmail/security', exist_ok=True)
    with open('qmail/security/middleware.py', 'w') as f:
        f.write(middleware_content)
    
    print("✅ Created: qmail/security/middleware.py")

def create_html_sanitizer():
    """Create HTML sanitization utility"""
    print_header("Creating HTML Sanitizer")
    
    sanitizer_content = '''"""
HTML Sanitization Utility
Prevents XSS attacks in email content
"""

import bleach
from bleach.css_sanitizer import CSSSanitizer

# Allowed HTML tags
ALLOWED_TAGS = [
    'p', 'br', 'strong', 'em', 'u', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    'blockquote', 'code', 'pre', 'hr', 'div', 'span',
    'ul', 'ol', 'li', 'a', 'img', 'table', 'thead', 'tbody', 'tr', 'th', 'td'
]

# Allowed attributes
ALLOWED_ATTRIBUTES = {
    'a': ['href', 'title', 'target'],
    'img': ['src', 'alt', 'title', 'width', 'height'],
    'div': ['class'],
    'span': ['class'],
    'table': ['class'],
    'td': ['colspan', 'rowspan'],
    'th': ['colspan', 'rowspan'],
}

# Allowed CSS properties
css_sanitizer = CSSSanitizer(allowed_css_properties=['color', 'background-color', 'font-weight'])


def sanitize_html(html_content):
    """
    Sanitize HTML content to prevent XSS attacks
    
    Args:
        html_content: Raw HTML string
        
    Returns:
        Sanitized HTML string
    """
    if not html_content:
        return ''
    
    # Clean HTML
    clean_html = bleach.clean(
        html_content,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        css_sanitizer=css_sanitizer,
        strip=True,
        strip_comments=True
    )
    
    # Linkify URLs (make them clickable)
    clean_html = bleach.linkify(clean_html)
    
    return clean_html


def sanitize_text(text_content):
    """
    Sanitize plain text (escape HTML)
    
    Args:
        text_content: Plain text string
        
    Returns:
        HTML-escaped string
    """
    if not text_content:
        return ''
    
    return bleach.clean(text_content, tags=[], strip=True)
'''
    
    with open('qmail/security/sanitizer.py', 'w') as f:
        f.write(sanitizer_content)
    
    print("✅ Created: qmail/security/sanitizer.py")

def create_rate_limit_config():
    """Create rate limiting configuration"""
    print_header("Creating Rate Limit Configuration")
    
    rate_limit_content = '''"""
Rate Limiting Configuration
Prevents abuse and brute force attacks
"""

from qmail.security.middleware import limiter

# Authentication endpoints - strict limits
auth_limit = limiter.limit("5 per minute")

# Email actions - moderate limits
email_action_limit = limiter.limit("30 per minute")

# API endpoints - generous limits
api_limit = limiter.limit("100 per minute")

# Password reset - very strict
password_reset_limit = limiter.limit("3 per hour")
'''
    
    with open('qmail/security/rate_limits.py', 'w') as f:
        f.write(rate_limit_content)
    
    print("✅ Created: qmail/security/rate_limits.py")

def create_requirements_security():
    """Create security requirements file"""
    print_header("Creating Security Requirements")
    
    requirements = '''# Security Dependencies
flask-talisman==1.1.0      # Security headers
flask-limiter==3.5.0       # Rate limiting
bleach==6.1.0              # HTML sanitization
Flask-WTF==1.2.1           # CSRF protection
cryptography==41.0.7       # Encryption
python-dotenv==1.0.0       # Environment variables
'''
    
    with open('requirements-security.txt', 'w') as f:
        f.write(requirements)
    
    print("✅ Created: requirements-security.txt")

def create_env_template():
    """Create .env template"""
    print_header("Creating Environment Template")
    
    env_content = '''# QMail Security Configuration
# Copy this to .env and fill in your values

# Flask Secret Key (generate with: python -c "import secrets; print(secrets.token_hex(32))")
SECRET_KEY=your-secret-key-here

# Encryption Key for SMTP/IMAP passwords
ENCRYPTION_KEY=your-encryption-key-here

# Database
DATABASE_URL=sqlite:///qmail.db

# Email Configuration (optional)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password

# Security Settings
DEBUG=False
TESTING=False
TALISMAN_FORCE_HTTPS=True

# Session
SESSION_COOKIE_SECURE=True
SESSION_COOKIE_HTTPONLY=True
'''
    
    with open('.env.template', 'w') as f:
        f.write(env_content)
    
    print("✅ Created: .env.template")
    print("\n⚠️  IMPORTANT: Copy .env.template to .env and fill in your values!")

def print_summary():
    """Print implementation summary"""
    print_header("Security Implementation Complete!")
    
    print("""
✅ Created Security Files:
   - qmail/config/security.py
   - qmail/security/middleware.py
   - qmail/security/sanitizer.py
   - qmail/security/rate_limits.py
   - requirements-security.txt
   - .env.template

📋 Next Steps:

1. Install security packages:
   pip install -r requirements-security.txt

2. Copy environment template:
   cp .env.template .env

3. Generate secret keys:
   python -c "import secrets; print('SECRET_KEY=' + secrets.token_hex(32))"
   python -c "import secrets; print('ENCRYPTION_KEY=' + secrets.token_hex(32))"

4. Add to .env file

5. Update app.py to use security middleware (see OWASP_SECURITY_AUDIT.md)

6. Update email view template to use sanitizer

7. Add CSRF tokens to forms

8. Test all functionality

📚 Documentation:
   - OWASP_SECURITY_AUDIT.md - Full security audit
   - See "Quick Fixes" section for code examples

⚠️  CRITICAL: Do NOT commit .env to git!
   Add .env to .gitignore
""")

def main():
    """Main execution"""
    print_header("QMail Security Implementation")
    print("This script will create security configuration files")
    print("and provide instructions for implementing OWASP protections.")
    print("\nPress Enter to continue...")
    input()
    
    try:
        # Create directories
        os.makedirs('qmail/config', exist_ok=True)
        os.makedirs('qmail/security', exist_ok=True)
        os.makedirs('logs', exist_ok=True)
        
        # Create files
        install_dependencies()
        create_security_config()
        create_security_middleware()
        create_html_sanitizer()
        create_rate_limit_config()
        create_requirements_security()
        create_env_template()
        
        # Summary
        print_summary()
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
