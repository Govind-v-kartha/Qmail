"""
Create Admin User
"""

import sys
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

from qmail.app import create_app
from qmail.models.database import db, User

def create_admin():
    """Create admin user if doesn't exist"""
    app = create_app()
    
    with app.app_context():
        print("\n" + "="*60)
        print("  Create Admin User")
        print("="*60 + "\n")
        
        # Check if admin exists
        admin = User.query.filter_by(username='admin').first()
        
        if admin:
            print(f"✓ Admin user already exists")
            print(f"  Username: {admin.username}")
            print(f"  Email: {admin.email}")
        else:
            # Create admin user
            admin = User(
                username='admin',
                email='admin@qmail.local'
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            
            print(f"✓ Admin user created successfully!")
            print(f"  Username: admin")
            print(f"  Email: admin@qmail.local")
            print(f"  Password: admin123")
        
        print("\n" + "="*60)
        print("  Done!")
        print("="*60)
        print("\nYou can now login with:")
        print("  Username: admin")
        print("  Password: admin123")
        print("\n")

if __name__ == '__main__':
    create_admin()
