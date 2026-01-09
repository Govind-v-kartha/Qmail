"""
Flask app entrypoint for Vercel deployment
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import and create the Flask app
from qmail.app import create_app

# Create the Flask application instance
app = create_app()

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
