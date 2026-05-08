"""
Flask app entrypoint for Vercel deployment.

The Vercel Python runtime statically scans this module for a top-level
``app`` symbol, so the assignment must NOT be nested inside a try/except
or any other compound statement.
"""

import os
import sys
import logging

from dotenv import load_dotenv

# Load environment variables from .env (no-op on Vercel where env is injected)
load_dotenv()

# Set production environment when running on Vercel
if os.getenv('VERCEL'):
    os.environ.setdefault('FLASK_ENV', 'production')

# Configure logging early
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)
logger.info("Starting QMail Flask app initialization...")

from qmail.app import create_app  # noqa: E402

# Top-level WSGI app for Vercel / gunicorn / wsgi.py
app = create_app()

# Vercel also looks for ``handler`` in some runtimes
handler = app

logger.info("Flask app initialized successfully!")


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
