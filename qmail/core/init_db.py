"""
Database initialization script
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from qmail.models.database import db, User, Email, Contact, KeyUsageLog, Settings, EmailAttachment
from qmail.app import create_app


def init_database():
    """Initialize the database with tables"""
    app = create_app()
    
    with app.app_context():
        # Create all tables
        db.create_all()
        print("✓ Database tables created successfully")
        
        # Check if admin user exists
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            # Create default admin user
            admin = User(
                username='admin',
                email='admin@qmail.local'
            )
            admin.set_password('admin123')  # Change in production!
            
            db.session.add(admin)
            db.session.commit()
            print("✓ Default admin user created (username: admin, password: admin123)")
            print("  ⚠️  CHANGE THE PASSWORD IN PRODUCTION!")
        else:
            print("✓ Admin user already exists")
        
        print("\n✓ Database initialization complete")
        print(f"  Database location: {app.config['SQLALCHEMY_DATABASE_URI']}")


if __name__ == '__main__':
    init_database()
