"""
Flask app entrypoint for Vercel deployment
Optimized for serverless environment
"""

import os
import sys
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set environment for Vercel
if os.getenv('VERCEL'):
    os.environ['FLASK_ENV'] = 'production'

# Configure logging early
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

logger.info("Starting QMail Flask app initialization...")

try:
    logger.info("Importing Flask app factory...")
    from qmail.app import create_app
    
    logger.info("Creating Flask application instance...")
    app = create_app()
    
    logger.info("Initializing database...")
    with app.app_context():
        from qmail.models.database import db
        # Create tables if they don't exist
        db.create_all()
        logger.info("Database tables created successfully")
    
    logger.info("Flask app initialized successfully!")
        
except Exception as e:
    logger.error(f"FATAL ERROR: Failed to initialize Flask app: {str(e)}")
    import traceback
    logger.error(traceback.format_exc())
    print(f"ERROR: Failed to initialize Flask app: {str(e)}", file=sys.stderr)
    raise

if __name__ == '__main__':
    # Get configuration from environment
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_PORT', 5000))
    debug = os.getenv('FLASK_ENV', 'development') == 'development'
    
    # Display user-friendly URL
    display_host = 'localhost' if host == '0.0.0.0' else host

    print("=" * 60)
    print("  QMail - Quantum-Secure Email Client")
    print("=" * 60)
    print(f"  Running on: http://{display_host}:{port}")
    print(f"  Environment: {os.getenv('FLASK_ENV', 'development')}")
    print(f"  Debug Mode: {debug}")
    print("=" * 60)
    print("\n  Press Ctrl+C to quit\n")

    app.run(host=host, port=port, debug=debug)
