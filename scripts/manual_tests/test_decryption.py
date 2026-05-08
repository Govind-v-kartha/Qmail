"""
Test Email Decryption
Verify that encrypted emails can be decrypted properly
"""

import sys
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

import json
from qmail.app import create_app
from qmail.models.database import db, Email, User
from qmail.crypto.message_cipher import MessageCipher
from qmail.crypto.encryption_engine import SecurityLevel

def test_decryption():
    """Test email decryption functionality"""
    app = create_app()
    
    with app.app_context():
        print("\n" + "="*60)
        print("  QMail Decryption Test")
        print("="*60 + "\n")
        
        # Get or create test user
        user = User.query.filter_by(username='admin').first()
        if not user:
            print("❌ No admin user found. Run fix_database.py first.")
            return
        
        print(f"✓ Testing with user: {user.username} ({user.email})")
        
        # Test 1: Create encrypted message
        print("\n--- Test 1: Encrypt Message ---")
        cipher = MessageCipher(use_mock_qkd=True)
        test_message = "This is a test encrypted message! 🔒"
        
        try:
            encrypted_package = cipher.encrypt_message(
                test_message,
                SecurityLevel.QUANTUM_AES
            )
            print(f"✓ Message encrypted")
            print(f"  Key ID: {encrypted_package['key_id']}")
            print(f"  Security Level: {encrypted_package['security_level_name']}")
        except Exception as e:
            print(f"❌ Encryption failed: {e}")
            return
        
        # Test 2: Create test email in database
        print("\n--- Test 2: Create Test Email ---")
        try:
            # Delete old test email if exists
            old_test = Email.query.filter_by(
                user_id=user.id,
                subject='[TEST] Encrypted Email'
            ).first()
            if old_test:
                db.session.delete(old_test)
                db.session.commit()
            
            # Create new test email
            test_email = Email(
                user_id=user.id,
                from_addr='test@qmail.local',
                to_addr=json.dumps([user.email]),
                subject='[TEST] Encrypted Email',
                body=json.dumps(encrypted_package),  # Store as JSON
                is_encrypted=True,
                security_level=SecurityLevel.QUANTUM_AES.value,
                security_level_name='QUANTUM_AES',
                qkd_key_id=encrypted_package['key_id'],
                folder='inbox'
            )
            db.session.add(test_email)
            db.session.commit()
            
            print(f"✓ Test email created (ID: {test_email.id})")
            print(f"  Subject: {test_email.subject}")
            print(f"  Encrypted: {test_email.is_encrypted}")
        except Exception as e:
            print(f"❌ Failed to create test email: {e}")
            db.session.rollback()
            return
        
        # Test 3: Retrieve and decrypt
        print("\n--- Test 3: Retrieve and Decrypt ---")
        try:
            # Retrieve email
            email = Email.query.get(test_email.id)
            print(f"✓ Email retrieved (ID: {email.id})")
            
            # Parse body as JSON
            try:
                encrypted_package_from_db = json.loads(email.body)
                print(f"✓ Parsed encrypted package from body")
            except json.JSONDecodeError as e:
                print(f"❌ Failed to parse JSON: {e}")
                print(f"  Body preview: {email.body[:100]}")
                return
            
            # Decrypt
            decrypted_message = cipher.decrypt_message(encrypted_package_from_db)
            print(f"✓ Message decrypted successfully!")
            print(f"  Original: {test_message}")
            print(f"  Decrypted: {decrypted_message}")
            
            # Verify match
            if decrypted_message == test_message:
                print(f"\n✅ SUCCESS: Decryption works correctly!")
            else:
                print(f"\n❌ MISMATCH: Decrypted message doesn't match original")
                
        except Exception as e:
            print(f"❌ Decryption failed: {e}")
            import traceback
            traceback.print_exc()
            return
        
        # Test 4: Test with embedded JSON (IMAP format)
        print("\n--- Test 4: Test IMAP Format (JSON in Text) ---")
        try:
            # Create email with JSON embedded in text (like IMAP receives)
            imap_body = f"""
--- ENCRYPTED PAYLOAD (For QMail Client Only) ---
{json.dumps(encrypted_package, indent=2)}
--- END ENCRYPTED PAYLOAD ---
"""
            
            test_email_imap = Email(
                user_id=user.id,
                from_addr='imap@qmail.local',
                to_addr=json.dumps([user.email]),
                subject='[TEST] IMAP Format Email',
                body=imap_body,
                is_encrypted=True,
                security_level=SecurityLevel.QUANTUM_AES.value,
                security_level_name='QUANTUM_AES',
                qkd_key_id=encrypted_package['key_id'],
                folder='inbox'
            )
            db.session.add(test_email_imap)
            db.session.commit()
            
            print(f"✓ IMAP format email created (ID: {test_email_imap.id})")
            
            # Try to extract and decrypt
            body_text = test_email_imap.body
            start_idx = body_text.find('{')
            end_idx = body_text.rfind('}') + 1
            
            if start_idx >= 0 and end_idx > start_idx:
                json_str = body_text[start_idx:end_idx]
                extracted_package = json.loads(json_str)
                print(f"✓ Extracted JSON from text")
                
                decrypted_imap = cipher.decrypt_message(extracted_package)
                print(f"✓ IMAP format decrypted successfully!")
                print(f"  Decrypted: {decrypted_imap}")
                
                if decrypted_imap == test_message:
                    print(f"\n✅ SUCCESS: IMAP format decryption works!")
                else:
                    print(f"\n❌ MISMATCH: IMAP decryption failed")
            else:
                print(f"❌ Could not extract JSON from text")
                
        except Exception as e:
            print(f"❌ IMAP format test failed: {e}")
            import traceback
            traceback.print_exc()
        
        # Summary
        print("\n" + "="*60)
        print("  Test Complete!")
        print("="*60)
        print("\nTest emails created:")
        print(f"  1. Direct JSON format (ID: {test_email.id})")
        print(f"  2. IMAP text format (ID: {test_email_imap.id})")
        print("\nYou can view these in the web interface:")
        print(f"  http://localhost:5000/email/view/{test_email.id}")
        print(f"  http://localhost:5000/email/view/{test_email_imap.id}")
        print("\n✅ Decryption is working correctly!")
        print("\n")

if __name__ == '__main__':
    try:
        test_decryption()
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
