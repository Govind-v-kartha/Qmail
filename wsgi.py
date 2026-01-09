"""
WSGI entrypoint for production deployment on Vercel
"""

import os
import sys
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

# Set production environment
os.environ['FLASK_ENV'] = 'production'

from app import app

# For Vercel serverless functions
handler = app
