"""
Fix Database Schema Issues
Handles migration for recent changes
"""

import os
import sys
import shutil
from datetime import datetime

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

from qmail.app import create_app
from qmail.models.database import db

def backup_database():
    """Create backup of existing database"""
    db_path = 'instance/qmail.db'
    if os.path.exists(db_path):
        backup_path = f'instance/qmail.db.backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
        shutil.copy2(db_path, backup_path)
        print(f"✓ Database backed up to: {backup_path}")
        return True
    return False

def fix_database():
    """Fix database schema issues"""
    app = create_app()
    
    with app.app_context():
        print("\n" + "="*60)
        print("  QMail Database Fix Utility")
        print("="*60 + "\n")
        
        # Backup first
        print("Step 1: Backing up database...")
        backup_database()
        
        print("\nStep 2: Checking database schema...")
        
        try:
            # Try to query - this will fail if schema is wrong
            from qmail.models.database import Email, EmailAttachment
            
            # Test Email model
            try:
                test_email = Email.query.first()
                print("✓ Email table schema OK")
            except Exception as e:
                print(f"⚠ Email table needs update: {e}")
                print("  Recreating Email table...")
                db.drop_all()
                db.create_all()
                print("✓ Email table recreated")
            
            # Test EmailAttachment model
            try:
                test_attachment = EmailAttachment.query.first()
                print("✓ EmailAttachment table schema OK")
            except Exception as e:
                print(f"⚠ EmailAttachment table needs update: {e}")
                print("  Recreating EmailAttachment table...")
                db.drop_all()
                db.create_all()
                print("✓ EmailAttachment table recreated")
                
        except Exception as e:
            print(f"⚠ Database schema error detected: {e}")
            print("\nStep 3: Recreating database with new schema...")
            
            # Drop all tables and recreate
            db.drop_all()
            db.create_all()
            
            print("✓ Database recreated with new schema")
            
            # Create default admin user
            from qmail.models.database import User
            admin = User.query.filter_by(username='admin').first()
            if not admin:
                admin = User(
                    username='admin',
                    email='admin@qmail.local'
                )
                admin.set_password('admin123')
                db.session.add(admin)
                db.session.commit()
                print("✓ Default admin user created")
                print("  Username: admin")
                print("  Password: admin123")
        
        print("\n" + "="*60)
        print("  Database Fix Complete!")
        print("="*60)
        print("\nNext steps:")
        print("1. Restart your application: python run.py")
        print("2. Login with: admin / admin123")
        print("3. Configure your email settings")
        print("\n")

if __name__ == '__main__':
    try:
        fix_database()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nIf the error persists, try:")
        print("1. Delete instance/qmail.db")
        print("2. Run: python -m qmail.core.init_db")
        print("3. Restart application")
