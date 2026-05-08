"""
Recreate database with updated schema
This will create all tables with the new is_deleted column

RUN THIS TO FIX THE OPERATIONALERROR!
"""

import os
from qmail.app import create_app
from qmail.models.database import db

def recreate_database():
    """Recreate all database tables"""
    app = create_app()
    
    with app.app_context():
        print("\n" + "="*50)
        print("FIXING DATABASE - OPERATIONALERROR")
        print("="*50 + "\n")
        
        # Check if database exists
        db_path = os.path.join(os.path.dirname(__file__), 'qmail.db')
        if os.path.exists(db_path):
            print(f"📁 Found database: {db_path}")
        
        print("🔄 Recreating database tables...")
        
        # Drop all tables
        db.drop_all()
        print("✅ Dropped all old tables")
        
        # Create all tables with new schema
        db.create_all()
        print("✅ Created all tables with updated schema")
        print("✅ Added 'is_deleted' column to emails table")
        
        print("\n" + "="*50)
        print("✅ DATABASE FIXED SUCCESSFULLY!")
        print("="*50)
        print("\n⚠️  Note: All existing data has been cleared")
        print("\n🚀 Now start your app:")
        print("   python run.py")
        print("\nThen:")
        print("   1. Register/Login")
        print("   2. Use inbox, trash, and all features")
        print("   3. Everything will work! ✅")
        print("\n")

if __name__ == '__main__':
    recreate_database()
