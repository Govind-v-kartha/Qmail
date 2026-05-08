"""
Create spam_patterns table for learning from user feedback
"""

from qmail.app import create_app
from qmail.models.database import db

def create_spam_patterns_table():
    """Create spam_patterns table"""
    app = create_app()
    
    with app.app_context():
        try:
            # Create table using raw SQL
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
            
            print("[SUCCESS] spam_patterns table created!")
            print("\nSpam learning system is now active!")
            print("When users mark emails as spam, the system will:")
            print("  - Learn the sender domain")
            print("  - Automatically filter similar emails")
            print("  - Improve accuracy over time")
            
        except Exception as e:
            print(f"[ERROR] {e}")
            print("\nIf table already exists, this is normal.")

if __name__ == '__main__':
    create_spam_patterns_table()
