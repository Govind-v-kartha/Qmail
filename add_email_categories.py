"""
Add email categories (spam, important, promotional) to database
"""

from qmail.app import create_app
from qmail.models.database import db

def add_email_categories():
    """Add new columns to emails table"""
    app = create_app()
    
    with app.app_context():
        try:
            # Add new columns using raw SQL
            with db.engine.connect() as conn:
                # Check if columns exist
                result = conn.execute(db.text("PRAGMA table_info(emails)"))
                columns = [row[1] for row in result]
                
                # Add is_important if not exists
                if 'is_important' not in columns:
                    conn.execute(db.text("ALTER TABLE emails ADD COLUMN is_important BOOLEAN DEFAULT 0"))
                    conn.commit()
                    print("[OK] Added is_important column")
                
                # Add is_spam if not exists
                if 'is_spam' not in columns:
                    conn.execute(db.text("ALTER TABLE emails ADD COLUMN is_spam BOOLEAN DEFAULT 0"))
                    conn.commit()
                    print("[OK] Added is_spam column")
                
                # Add category if not exists
                if 'category' not in columns:
                    conn.execute(db.text("ALTER TABLE emails ADD COLUMN category VARCHAR(50)"))
                    conn.commit()
                    print("[OK] Added category column")
            
            print("\n[SUCCESS] Database migration completed successfully!")
            print("\nNew features added:")
            print("  - Spam folder")
            print("  - Important flag")
            print("  - Promotional category (auto-classification)")
            print("  - Social category")
            print("  - Updates category")
            print("  - Forums category")
            
        except Exception as e:
            print(f"[ERROR] {e}")
            print("\nIf columns already exist, this is normal.")

if __name__ == '__main__':
    add_email_categories()
