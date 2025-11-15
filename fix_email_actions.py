"""
Fix email actions - ensure all columns and tables exist
"""

from qmail.app import create_app
from qmail.models.database import db

def fix_email_actions():
    """Ensure all required columns and tables exist"""
    app = create_app()
    
    with app.app_context():
        print("[INFO] Checking database...")
        
        try:
            # Check and add columns to emails table
            with db.engine.connect() as conn:
                # Get existing columns
                result = conn.execute(db.text("PRAGMA table_info(emails)"))
                columns = [row[1] for row in result]
                
                print(f"[INFO] Found columns: {', '.join(columns)}")
                
                # Add is_important if missing
                if 'is_important' not in columns:
                    print("[FIXING] Adding is_important column...")
                    conn.execute(db.text("ALTER TABLE emails ADD COLUMN is_important BOOLEAN DEFAULT 0"))
                    conn.commit()
                    print("[OK] Added is_important column")
                else:
                    print("[OK] is_important column exists")
                
                # Add is_spam if missing
                if 'is_spam' not in columns:
                    print("[FIXING] Adding is_spam column...")
                    conn.execute(db.text("ALTER TABLE emails ADD COLUMN is_spam BOOLEAN DEFAULT 0"))
                    conn.commit()
                    print("[OK] Added is_spam column")
                else:
                    print("[OK] is_spam column exists")
                
                # Add category if missing
                if 'category' not in columns:
                    print("[FIXING] Adding category column...")
                    conn.execute(db.text("ALTER TABLE emails ADD COLUMN category VARCHAR(50)"))
                    conn.commit()
                    print("[OK] Added category column")
                else:
                    print("[OK] category column exists")
            
            # Create spam_patterns table if not exists
            print("\n[INFO] Checking spam_patterns table...")
            with db.engine.connect() as conn:
                conn.execute(db.text("""
                    CREATE TABLE IF NOT EXISTS spam_patterns (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        sender_domain VARCHAR(255),
                        sender_pattern VARCHAR(255),
                        subject_keywords TEXT,
                        pattern_type VARCHAR(50),
                        match_count INTEGER DEFAULT 1,
                        correct_count INTEGER DEFAULT 1,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users (id)
                    )
                """))
                conn.commit()
                print("[OK] spam_patterns table ready")
            
            print("\n[SUCCESS] All database fixes applied!")
            print("\nYou can now:")
            print("  - Star emails")
            print("  - Mark emails as important")
            print("  - Report spam")
            print("  - System will learn from spam reports")
            
        except Exception as e:
            print(f"\n[ERROR] {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    fix_email_actions()
