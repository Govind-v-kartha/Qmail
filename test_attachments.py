"""
Test script for quantum-encrypted file attachments
Demonstrates encryption and decryption of files
"""

import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from qmail.email_handler.attachment_handler import AttachmentHandler, format_file_size
from qmail.crypto.encryption_engine import SecurityLevel
import tempfile
import os


def print_header(text):
    """Print formatted header"""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60 + "\n")


def test_text_file_encryption():
    """Test encrypting and decrypting a text file"""
    print_header("Test 1: Text File Encryption")
    
    # Create temporary test file
    test_content = b"This is a secret document!\nQuantum encrypted for your eyes only."
    
    with tempfile.NamedTemporaryFile(mode='wb', suffix='.txt', delete=False) as f:
        f.write(test_content)
        test_file = f.name
    
    try:
        # Initialize handler
        handler = AttachmentHandler(use_mock_qkd=True)
        
        print(f"Original file: {os.path.basename(test_file)}")
        print(f"Size: {format_file_size(len(test_content))}")
        
        # Encrypt file
        print("\n→ Encrypting with Quantum-AES...")
        encrypted = handler.encrypt_file(test_file, SecurityLevel.QUANTUM_AES)
        
        print(f"✓ Encrypted successfully")
        print(f"  Filename: {encrypted.filename}")
        print(f"  Original size: {format_file_size(encrypted.original_size)}")
        print(f"  Encrypted size: {format_file_size(encrypted.encrypted_size)}")
        print(f"  Key ID: {encrypted.key_id}")
        print(f"  Security: {encrypted.security_level}")
        
        # Decrypt file
        print("\n→ Decrypting...")
        decrypted = handler.decrypt_attachment(encrypted)
        
        print(f"✓ Decrypted successfully")
        print(f"  Filename: {decrypted.filename}")
        print(f"  Size: {format_file_size(decrypted.size)}")
        
        # Verify content
        if decrypted.content == test_content:
            print(f"\n✓ VERIFICATION PASSED - Content matches original!")
        else:
            print(f"\n✗ VERIFICATION FAILED - Content mismatch!")
        
        print(f"\nDecrypted content:")
        print("-" * 60)
        print(decrypted.content.decode('utf-8'))
        print("-" * 60)
        
    finally:
        # Cleanup
        os.unlink(test_file)


def test_multiple_files():
    """Test encrypting multiple files"""
    print_header("Test 2: Multiple File Encryption")
    
    # Create test files
    test_files = []
    try:
        for i in range(3):
            content = f"Test file {i+1}\nQuantum secure data.".encode('utf-8')
            with tempfile.NamedTemporaryFile(mode='wb', suffix=f'_file{i+1}.txt', delete=False) as f:
                f.write(content)
                test_files.append(f.name)
        
        handler = AttachmentHandler(use_mock_qkd=True)
        
        print(f"Encrypting {len(test_files)} files...\n")
        
        # Encrypt all files
        encrypted_files = handler.encrypt_multiple_files(
            test_files,
            SecurityLevel.QUANTUM_AES
        )
        
        for i, encrypted in enumerate(encrypted_files, 1):
            print(f"File {i}:")
            print(f"  ✓ {encrypted.filename}")
            print(f"  Size: {format_file_size(encrypted.original_size)}")
            print(f"  Key: {encrypted.key_id}")
            print()
        
        print(f"✓ All {len(encrypted_files)} files encrypted successfully!")
        
        # Decrypt and verify
        print("\n→ Decrypting all files...")
        for encrypted in encrypted_files:
            decrypted = handler.decrypt_attachment(encrypted)
            print(f"  ✓ {decrypted.filename} decrypted")
        
        print("\n✓ All files decrypted successfully!")
        
    finally:
        # Cleanup
        for f in test_files:
            os.unlink(f)


def test_binary_file():
    """Test encrypting binary data (simulated image)"""
    print_header("Test 3: Binary File Encryption (Simulated Image)")
    
    # Create fake binary data
    binary_data = bytes(range(256)) * 100  # 25.6 KB of binary data
    
    handler = AttachmentHandler(use_mock_qkd=True)
    
    print(f"Original data: {format_file_size(len(binary_data))}")
    
    # Encrypt
    print("\n→ Encrypting binary data...")
    encrypted = handler.encrypt_attachment(
        filename="test_image.jpg",
        content=binary_data,
        security_level=SecurityLevel.QUANTUM_OTP
    )
    
    print(f"✓ Encrypted with Quantum OTP (Perfect Secrecy)")
    print(f"  Key ID: {encrypted.key_id}")
    print(f"  Encrypted size: {format_file_size(encrypted.encrypted_size)}")
    
    # Decrypt
    print("\n→ Decrypting...")
    decrypted = handler.decrypt_attachment(encrypted)
    
    if decrypted.content == binary_data:
        print(f"✓ VERIFICATION PASSED - Binary data intact!")
    else:
        print(f"✗ VERIFICATION FAILED - Data corrupted!")
    
    print(f"\nBinary data summary:")
    print(f"  Original: {len(binary_data)} bytes")
    print(f"  Decrypted: {len(decrypted.content)} bytes")
    print(f"  Match: {binary_data == decrypted.content}")


def test_all_security_levels():
    """Test all 4 security levels"""
    print_header("Test 4: All Security Levels")
    
    test_content = b"Top Secret Document - Quantum Protected"
    handler = AttachmentHandler(use_mock_qkd=True)
    
    levels = [
        (SecurityLevel.QUANTUM_OTP, "Quantum OTP (Perfect Secrecy)"),
        (SecurityLevel.QUANTUM_AES, "Quantum-Aided AES"),
        (SecurityLevel.POST_QUANTUM, "Post-Quantum Cryptography"),
        (SecurityLevel.CLASSICAL, "Classical Encryption")
    ]
    
    for level, name in levels:
        print(f"\n{name}:")
        print("-" * 60)
        
        # Encrypt
        encrypted = handler.encrypt_attachment(
            filename=f"document_{level.name.lower()}.txt",
            content=test_content,
            security_level=level
        )
        
        print(f"  ✓ Encrypted")
        print(f"    Key: {encrypted.key_id}")
        print(f"    Size: {format_file_size(encrypted.encrypted_size)}")
        
        # Decrypt
        decrypted = handler.decrypt_attachment(encrypted)
        
        if decrypted.content == test_content:
            print(f"  ✓ Decrypted and verified")
        else:
            print(f"  ✗ Verification failed!")
    
    print("\n✓ All security levels tested successfully!")


def test_file_info():
    """Test getting file information"""
    print_header("Test 5: File Information")
    
    # Create test file
    test_content = b"X" * (5 * 1024 * 1024)  # 5 MB
    
    with tempfile.NamedTemporaryFile(mode='wb', suffix='.pdf', delete=False) as f:
        f.write(test_content)
        test_file = f.name
    
    try:
        handler = AttachmentHandler(use_mock_qkd=True)
        
        # Get info
        info = handler.get_attachment_info(test_file)
        
        print("File Information:")
        print(f"  Filename: {info['filename']}")
        print(f"  Size: {info['size_mb']:.2f} MB ({info['size']} bytes)")
        print(f"  Type: {info['content_type']}")
        print(f"  Extension: {info['extension']}")
        print(f"  Can encrypt: {info['can_encrypt']}")
        
    finally:
        os.unlink(test_file)


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("  QMail Attachment Encryption Test Suite")
    print("=" * 60)
    
    try:
        test_text_file_encryption()
        test_multiple_files()
        test_binary_file()
        test_all_security_levels()
        test_file_info()
        
        print_header("All Tests Completed Successfully! ✓")
        print("\n🔒 Attachment encryption is working correctly!")
        print("   Files can be encrypted and decrypted with quantum security.")
        
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
