"""
QMail Demo Script
Demonstrates quantum encryption/decryption functionality
"""

import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from qmail.crypto.message_cipher import MessageCipher
from qmail.crypto.encryption_engine import SecurityLevel
from qmail.km_client.mock_km import MockQKDClient


def print_header(text):
    """Print formatted header"""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60 + "\n")


def demo_encryption_levels():
    """Demonstrate all encryption levels"""
    print_header("QMail Encryption Demo")
    
    # Initialize cipher
    cipher = MessageCipher(use_mock_qkd=True)
    
    # Test message
    original_message = "Hello! This is a quantum-encrypted message from QMail. 🔒"
    print(f"Original Message:\n{original_message}\n")
    
    # Test all security levels
    levels = [
        (SecurityLevel.QUANTUM_OTP, "Quantum OTP (Perfect Secrecy)"),
        (SecurityLevel.QUANTUM_AES, "Quantum-Aided AES"),
        (SecurityLevel.POST_QUANTUM, "Post-Quantum Cryptography"),
        (SecurityLevel.CLASSICAL, "Classical Encryption")
    ]
    
    for level, name in levels:
        print(f"\n{'-' * 60}")
        print(f"Security Level: {name}")
        print(f"{'-' * 60}")
        
        # Encrypt
        encrypted_package = cipher.encrypt_message(original_message, level)
        
        print(f"✓ Encrypted successfully")
        print(f"  Key ID: {encrypted_package['key_id']}")
        print(f"  Ciphertext (first 50 chars): {encrypted_package['ciphertext'][:50]}...")
        
        # Decrypt
        decrypted_message = cipher.decrypt_message(encrypted_package)
        
        print(f"✓ Decrypted successfully")
        print(f"  Decrypted: {decrypted_message}")
        
        # Verify
        if decrypted_message == original_message:
            print(f"✓ Verification PASSED - Messages match!")
        else:
            print(f"✗ Verification FAILED - Messages don't match!")


def demo_qkd_client():
    """Demonstrate QKD client functionality"""
    print_header("Quantum Key Manager Demo")
    
    client = MockQKDClient()
    
    # Get status
    status = client.get_status()
    print(f"Key Manager Status:")
    print(f"  Mode: {status['mode']}")
    print(f"  Status: {status['status']}")
    print(f"  Keys Generated: {status['keys_generated']}")
    
    # Generate keys
    print(f"\nGenerating quantum keys...")
    keys = client.get_key(key_size=256, number_of_keys=3)
    
    for i, key in enumerate(keys, 1):
        print(f"\nKey {i}:")
        print(f"  ID: {key.key_id}")
        print(f"  Size: {key.key_size} bits")
        print(f"  Key (hex): {key.key.hex()[:50]}...")
        print(f"  Timestamp: {key.timestamp}")
    
    # Retrieve by ID
    print(f"\nRetrieving key by ID...")
    retrieved = client.get_key_by_id(keys[0].key_id)
    if retrieved:
        print(f"✓ Successfully retrieved: {retrieved.key_id}")
    
    # Close key
    print(f"\nClosing key...")
    success = client.close_key(keys[0].key_id)
    if success:
        print(f"✓ Key closed successfully")


def demo_full_workflow():
    """Demonstrate complete email encryption workflow"""
    print_header("Complete Email Encryption Workflow")
    
    # Step 1: Initialize
    print("Step 1: Initialize Message Cipher")
    cipher = MessageCipher(use_mock_qkd=True)
    print("✓ Cipher initialized with Mock QKD")
    
    # Step 2: Compose message
    print("\nStep 2: Compose Email")
    email_message = """
Subject: Quantum-Secure Message

Dear Bob,

This email is encrypted using Quantum Key Distribution (QKD).
Any attempt to intercept this message will be detected!

Best regards,
Alice
    """.strip()
    print(f"✓ Message composed ({len(email_message)} characters)")
    
    # Step 3: Select security level
    print("\nStep 3: Select Security Level")
    security_level = SecurityLevel.QUANTUM_AES
    print(f"✓ Selected: {security_level.name}")
    
    # Step 4: Encrypt
    print("\nStep 4: Request Quantum Key & Encrypt")
    encrypted_package = cipher.encrypt_message(email_message, security_level)
    print(f"✓ Message encrypted")
    print(f"  Key ID: {encrypted_package['key_id']}")
    print(f"  Security Level: {encrypted_package['security_level_name']}")
    
    # Step 5: Transmit (simulated)
    print("\nStep 5: Transmit via Email Server")
    print("✓ [Simulated] Encrypted message sent via SMTP")
    
    # Step 6: Receive (simulated)
    print("\nStep 6: Receive via Email Server")
    print("✓ [Simulated] Encrypted message received via IMAP")
    
    # Step 7: Decrypt
    print("\nStep 7: Retrieve Quantum Key & Decrypt")
    decrypted_message = cipher.decrypt_message(encrypted_package)
    print(f"✓ Message decrypted successfully")
    
    # Step 8: Verify
    print("\nStep 8: Verify Message Integrity")
    if decrypted_message == email_message:
        print("✓ SUCCESS - Message integrity verified!")
        print(f"\nDecrypted Message:\n{'-' * 60}")
        print(decrypted_message)
        print('-' * 60)
    else:
        print("✗ FAILED - Message corrupted!")


def main():
    """Main demo function"""
    print("\n" + "=" * 60)
    print("  QMail - Quantum-Secure Email Client")
    print("  Demonstration Script")
    print("=" * 60)
    
    demos = [
        ("1", "Encryption Levels Demo", demo_encryption_levels),
        ("2", "QKD Client Demo", demo_qkd_client),
        ("3", "Full Email Workflow Demo", demo_full_workflow),
        ("4", "Run All Demos", None)
    ]
    
    print("\nAvailable Demos:")
    for num, name, _ in demos:
        print(f"  {num}. {name}")
    
    choice = input("\nSelect demo (1-4) or 'q' to quit: ").strip()
    
    if choice == 'q':
        print("\nGoodbye!")
        return
    
    if choice == '4':
        demo_encryption_levels()
        demo_qkd_client()
        demo_full_workflow()
    elif choice in ['1', '2', '3']:
        demos[int(choice) - 1][2]()
    else:
        print("Invalid choice!")
        return
    
    print("\n" + "=" * 60)
    print("  Demo Complete!")
    print("=" * 60 + "\n")


if __name__ == '__main__':
    main()
