"""
Diagnostic script to check environment and dependencies
Run this to verify QMail is properly configured
"""

import os
import sys
from pathlib import Path

print("=" * 60)
print("QMail Startup Diagnostic")
print("=" * 60)

# Check Python version
print(f"\n✓ Python Version: {sys.version}")

# Check environment variables
print("\nEnvironment Variables:")
env_vars = [
    'FLASK_ENV', 'SECRET_KEY', 'DATABASE_URL', 'FLASK_HOST', 'FLASK_PORT'
]
for var in env_vars:
    value = os.getenv(var)
    if value:
        masked = value[:10] + '***' if len(value) > 10 else value
        print(f"  ✓ {var}: {masked}")
    else:
        print(f"  ✗ {var}: NOT SET (will use default)")

# Check dependencies
print("\nDependencies:")
dependencies = [
    'flask', 'flask_sqlalchemy', 'flask_login', 'flask_wtf',
    'cryptography', 'requests', 'dotenv'
]

for dep in dependencies:
    try:
        __import__(dep.replace('_', '-') if dep != 'dotenv' else 'dotenv')
        print(f"  ✓ {dep}")
    except ImportError:
        print(f"  ✗ {dep}: NOT INSTALLED")

# Check database
print("\nDatabase:")
try:
    from qmail.models.database import db
    db_url = os.getenv('DATABASE_URL', 'sqlite:///qmail.db')
    print(f"  ✓ Database URL: {db_url}")
except Exception as e:
    print(f"  ✗ Database Error: {e}")

# Check Flask app
print("\nFlask Application:")
try:
    from qmail.app import create_app
    app = create_app()
    print(f"  ✓ Flask app created successfully")
    print(f"  ✓ Config name: {os.getenv('FLASK_ENV', 'development')}")
except Exception as e:
    print(f"  ✗ Flask app creation failed: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("Diagnostic Complete")
print("=" * 60)
