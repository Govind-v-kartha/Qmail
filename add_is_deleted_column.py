"""
Database migration script to add is_deleted column to emails table
Run this once to update your existing database

IMPORTANT: This only works if you have existing data you want to keep.
If you don't have important data, use recreate_database.py instead.
"""

from qmail.app import create_app
from qmail.models.database import db
from sqlalchemy import text

def migrate():
    """Add is_deleted column to emails table"""
    app = create_app()
    
    with app.app_context():
        try:
            # Check if column already exists
            result = db.session.execute(text("PRAGMA table_info(emails)"))
            columns = [row[1] for row in result]
            
            if 'is_deleted' in columns:
                print("✅ Column 'is_deleted' already exists!")
                return
            
            # Add the column
            print("Adding 'is_deleted' column to emails table...")
            db.session.execute(text(
                "ALTER TABLE emails ADD COLUMN is_deleted BOOLEAN DEFAULT 0"
            ))
            db.session.commit()
            print("✅ Successfully added 'is_deleted' column!")
            print("\nNow restart your app: python run.py")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            print("\n⚠️  Migration failed!")
            print("If you don't have important data, run: python recreate_database.py")
            db.session.rollback()

if __name__ == '__main__':
    migrate()
