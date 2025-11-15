"""
Database Migration: Add preview_text and preview_html fields to emails table
"""

import sqlite3
import os

# Database path
DB_PATH = 'instance/qmail.db'

def migrate():
    """Add preview fields to emails table"""
    
    if not os.path.exists(DB_PATH):
        print(f"❌ Database not found at {DB_PATH}")
        return False
    
    print(f"🔄 Connecting to database: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(emails)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'preview_text' in columns and 'preview_html' in columns:
            print("✅ Columns already exist! No migration needed.")
            return True
        
        print("📝 Adding new columns...")
        
        # Add preview_text column
        if 'preview_text' not in columns:
            cursor.execute("""
                ALTER TABLE emails 
                ADD COLUMN preview_text VARCHAR(500)
            """)
            print("✅ Added preview_text column")
        
        # Add preview_html column
        if 'preview_html' not in columns:
            cursor.execute("""
                ALTER TABLE emails 
                ADD COLUMN preview_html TEXT
            """)
            print("✅ Added preview_html column")
        
        # Commit changes
        conn.commit()
        print("✅ Migration completed successfully!")
        
        # Verify
        cursor.execute("PRAGMA table_info(emails)")
        columns = [row[1] for row in cursor.fetchall()]
        print(f"\n📋 Current columns in emails table:")
        for col in columns:
            print(f"   - {col}")
        
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        conn.rollback()
        return False
        
    finally:
        conn.close()

if __name__ == '__main__':
    print("=" * 60)
    print("  Database Migration: Add HTML Preview Fields")
    print("=" * 60)
    
    success = migrate()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ Migration completed! You can now run the app.")
        print("   Run: python run.py")
    else:
        print("❌ Migration failed. Please check the error above.")
    print("=" * 60)
