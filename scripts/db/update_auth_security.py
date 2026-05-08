"""
Update database for authentication security features
"""

from qmail.app import create_app
from qmail.models.database import db

def update_auth_security():
    """Add security columns to users table"""
    app = create_app()
    
    with app.app_context():
        print("[INFO] Updating authentication security...")
        
        try:
            with db.engine.connect() as conn:
                # Check existing columns
                result = conn.execute(db.text("PRAGMA table_info(users)"))
                columns = [row[1] for row in result]
                
                print(f"[INFO] Current columns: {', '.join(columns)}")
                
                # Add is_verified
                if 'is_verified' not in columns:
                    print("[ADDING] is_verified column...")
                    conn.execute(db.text("ALTER TABLE users ADD COLUMN is_verified BOOLEAN DEFAULT 0"))
                    conn.commit()
                    print("[OK] Added is_verified")
                else:
                    print("[OK] is_verified already exists")
                
                # Add reset_token
                if 'reset_token' not in columns:
                    print("[ADDING] reset_token column...")
                    conn.execute(db.text("ALTER TABLE users ADD COLUMN reset_token VARCHAR(100)"))
                    conn.commit()
                    print("[OK] Added reset_token")
                else:
                    print("[OK] reset_token already exists")
                
                # Add reset_token_expiry
                if 'reset_token_expiry' not in columns:
                    print("[ADDING] reset_token_expiry column...")
                    conn.execute(db.text("ALTER TABLE users ADD COLUMN reset_token_expiry TIMESTAMP"))
                    conn.commit()
                    print("[OK] Added reset_token_expiry")
                else:
                    print("[OK] reset_token_expiry already exists")
                
                # Add failed_login_attempts
                if 'failed_login_attempts' not in columns:
                    print("[ADDING] failed_login_attempts column...")
                    conn.execute(db.text("ALTER TABLE users ADD COLUMN failed_login_attempts INTEGER DEFAULT 0"))
                    conn.commit()
                    print("[OK] Added failed_login_attempts")
                else:
                    print("[OK] failed_login_attempts already exists")
                
                # Add account_locked_until
                if 'account_locked_until' not in columns:
                    print("[ADDING] account_locked_until column...")
                    conn.execute(db.text("ALTER TABLE users ADD COLUMN account_locked_until TIMESTAMP"))
                    conn.commit()
                    print("[OK] Added account_locked_until")
                else:
                    print("[OK] account_locked_until already exists")
            
            print("\n[SUCCESS] Authentication security updated!")
            print("\nNew features available:")
            print("  - Password strength validation")
            print("  - Account lockout (5 failed attempts = 30 min lock)")
            print("  - Password reset with secure tokens")
            print("  - Username recovery via email")
            print("  - Failed login tracking")
            print("  - Automatic account unlock")
            
            print("\nNext steps:")
            print("1. Implement password reset routes")
            print("2. Add forgot password/username forms")
            print("3. Configure email sending (optional)")
            print("4. Test account lockout feature")
            
        except Exception as e:
            print(f"\n[ERROR] {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    update_auth_security()
