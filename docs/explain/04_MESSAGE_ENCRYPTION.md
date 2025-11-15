# QMail Encryption System - Message Encryption Flow

## 📚 Table of Contents
1. [Overview](#overview)
2. [MessageCipher Class](#messagecipher-class)
3. [Encryption Process](#encryption-process)
4. [Decryption Process](#decryption-process)
5. [Encrypted Package Structure](#encrypted-package-structure)
6. [Complete Code Walkthrough](#complete-code-walkthrough)
7. [Error Handling](#error-handling)
8. [Real-World Examples](#real-world-examples)

---

## 1. Overview

The **MessageCipher** class (`qmail/crypto/message_cipher.py`) provides a high-level interface for encrypting and decrypting email messages. It coordinates between the QKD client (for key management) and the EncryptionEngine (for actual encryption).

**File:** `qmail/crypto/message_cipher.py`  
**Primary Class:** `MessageCipher`  
**Purpose:** High-level message encryption/decryption

---

## 2. MessageCipher Class

### Class Definition

```python
class MessageCipher:
    """
    High-level interface for encrypting/decrypting email messages
    Coordinates QKD key management and encryption operations
    """
    
    def __init__(self, use_mock_qkd: bool = True):
        """
        Initialize MessageCipher
        
        Args:
            use_mock_qkd: Use Mock QKD (True) or Real QKD (False)
        """
        # Initialize QKD client
        if use_mock_qkd:
            self.qkd_client = MockQKDClient()
        else:
            self.qkd_client = QKDClient.from_env()
        
        # Initialize encryption engine
        self.encryption_engine = EncryptionEngine()
        
        logger.info("Message cipher initialized")
```

### Key Methods

```python
class MessageCipher:
    
    def encrypt_message(
        self,
        message: str,
        security_level: SecurityLevel = SecurityLevel.QUANTUM_AES,
        recipient_id: str = None
    ) -> Dict
    
    def decrypt_message(
        self,
        encrypted_package: Dict
    ) -> str
    
    def encrypt_message_to_json(
        self,
        message: str,
        security_level: SecurityLevel = SecurityLevel.QUANTUM_AES
    ) -> str
    
    def decrypt_message_from_json(
        self,
        json_data: str
    ) -> str
```

---

## 3. Encryption Process

### Step-by-Step Flow

```
User Message (Plaintext)
        │
        ▼
┌─────────────────────────────────────────────┐
│ Step 1: Convert to Bytes                    │
│ message.encode('utf-8')                     │
│ "Hello World" → b'Hello World'              │
└────────────────┬────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────┐
│ Step 2: Determine Key Size                  │
│                                             │
│ If OTP: key_size = max(len(plaintext)*8, 256)│
│ Else:   key_size = 256                      │
└────────────────┬────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────┐
│ Step 3: Request Quantum Key                 │
│ qkd_client.get_key(key_size, number=1)     │
│ Returns: QKDKey object                      │
│   - key_id: "MOCK-KEY-00000123..."         │
│   - key: bytes (quantum-generated)          │
│   - key_size: 256 bits                      │
└────────────────┬────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────┐
│ Step 4: Encrypt with EncryptionEngine       │
│ encryption_engine.encrypt(                  │
│     plaintext=plaintext_bytes,              │
│     key=quantum_key,                        │
│     security_level=QUANTUM_AES              │
│ )                                           │
│ Returns: (ciphertext_bytes, metadata_dict)  │
└────────────────┬────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────┐
│ Step 5: Base64 Encode Ciphertext            │
│ base64.b64encode(ciphertext)                │
│ Binary data → ASCII string                  │
└────────────────┬────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────┐
│ Step 6: Create Encrypted Package            │
│ {                                           │
│   'ciphertext': 'base64_string',           │
│   'key_id': 'MOCK-KEY-...',                │
│   'security_level': 2,                      │
│   'security_level_name': 'QUANTUM_AES',    │
│   'metadata': {...},                        │
│   'recipient_id': 'bob@example.com'         │
│ }                                           │
└────────────────┬────────────────────────────┘
                 │
                 ▼
        Encrypted Package (Dict)
```

### Code Implementation

```python
def encrypt_message(
    self,
    message: str,
    security_level: SecurityLevel = SecurityLevel.QUANTUM_AES,
    recipient_id: str = None
) -> Dict:
    """
    Encrypt an email message using quantum keys
    
    Args:
        message: Plain text message to encrypt
        security_level: Security level (1-4)
        recipient_id: Optional recipient identifier
    
    Returns:
        Dictionary containing encrypted message and metadata
    
    Example:
        cipher = MessageCipher(use_mock_qkd=True)
        encrypted = cipher.encrypt_message(
            message="Secret message",
            security_level=SecurityLevel.QUANTUM_AES
        )
        # Returns: {'ciphertext': '...', 'key_id': '...', ...}
    """
    try:
        # Step 1: Convert message to bytes
        plaintext = message.encode('utf-8')
        logger.debug(f"Plaintext length: {len(plaintext)} bytes")
        
        # Step 2: Determine required key size
        if security_level == SecurityLevel.QUANTUM_OTP:
            # OTP requires key size >= message size
            key_size = max(len(plaintext) * 8, 256)
            logger.debug(f"OTP: requesting {key_size}-bit key")
        else:
            # Other levels use standard key size
            key_size = 256
            logger.debug(f"Standard: requesting {key_size}-bit key")
        
        # Step 3: Request quantum key from KM
        logger.info(f"Requesting quantum key for encryption (level: {security_level.name})")
        keys = self.qkd_client.get_key(key_size=key_size, number_of_keys=1)
        
        if not keys:
            raise Exception("Failed to obtain quantum key")
        
        qkd_key = keys[0]
        logger.info(f"Obtained quantum key: {qkd_key.key_id}")
        logger.debug(f"Key size: {len(qkd_key.key)} bytes ({len(qkd_key.key) * 8} bits)")
        
        # Step 4: Encrypt message
        logger.debug(f"Encrypting with {security_level.name}")
        ciphertext, metadata = self.encryption_engine.encrypt(
            plaintext=plaintext,
            key=qkd_key.key,
            security_level=security_level
        )
        logger.debug(f"Ciphertext length: {len(ciphertext)} bytes")
        
        # Step 5: Base64 encode ciphertext
        ciphertext_b64 = base64.b64encode(ciphertext).decode('utf-8')
        
        # Step 6: Prepare encrypted message package
        encrypted_package = {
            'ciphertext': ciphertext_b64,
            'key_id': qkd_key.key_id,
            'security_level': security_level.value,
            'security_level_name': security_level.name,
            'metadata': metadata,
            'recipient_id': recipient_id,
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"Message encrypted successfully (key: {qkd_key.key_id})")
        logger.debug(f"Encrypted package size: {len(str(encrypted_package))} bytes")
        
        return encrypted_package
        
    except Exception as e:
        logger.error(f"Encryption failed: {e}")
        logger.exception("Full traceback:")
        raise
```

---

## 4. Decryption Process

### Step-by-Step Flow

```
Encrypted Package (Dict)
        │
        ▼
┌─────────────────────────────────────────────┐
│ Step 1: Extract Components                  │
│ - ciphertext (base64)                       │
│ - key_id                                    │
│ - metadata                                  │
└────────────────┬────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────┐
│ Step 2: Base64 Decode Ciphertext            │
│ base64.b64decode(ciphertext_b64)           │
│ ASCII string → Binary data                  │
└────────────────┬────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────┐
│ Step 3: Retrieve Quantum Key                │
│ qkd_client.get_key_by_id(key_id)           │
│ Returns: QKDKey object with same key        │
└────────────────┬────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────┐
│ Step 4: Decrypt with EncryptionEngine       │
│ encryption_engine.decrypt(                  │
│     ciphertext=ciphertext_bytes,            │
│     key=quantum_key,                        │
│     metadata=metadata                       │
│ )                                           │
│ Returns: plaintext_bytes                    │
└────────────────┬────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────┐
│ Step 5: Convert to String                   │
│ plaintext_bytes.decode('utf-8')             │
│ b'Hello World' → "Hello World"              │
└────────────────┬────────────────────────────┘
                 │
                 ▼
        Decrypted Message (String)
```

### Code Implementation

```python
def decrypt_message(self, encrypted_package: Dict) -> str:
    """
    Decrypt an encrypted email message
    
    Args:
        encrypted_package: Dictionary containing encrypted message
    
    Returns:
        Decrypted plain text message
    
    Example:
        cipher = MessageCipher(use_mock_qkd=True)
        plaintext = cipher.decrypt_message(encrypted_package)
        # Returns: "Secret message"
    """
    try:
        # Step 1: Extract encrypted data
        ciphertext_b64 = encrypted_package['ciphertext']
        key_id = encrypted_package['key_id']
        metadata = encrypted_package['metadata']
        
        logger.debug(f"Ciphertext (b64) length: {len(ciphertext_b64)} chars")
        logger.debug(f"Key ID: {key_id}")
        
        # Step 2: Base64 decode ciphertext
        ciphertext = base64.b64decode(ciphertext_b64)
        logger.debug(f"Ciphertext (binary) length: {len(ciphertext)} bytes")
        
        # Step 3: Retrieve quantum key from KM
        logger.info(f"Decrypting message with key: {key_id}")
        qkd_key = self.qkd_client.get_key_by_id(key_id)
        
        if not qkd_key:
            raise Exception(f"Failed to retrieve quantum key: {key_id}")
        
        logger.info(f"Retrieved quantum key: {qkd_key.key_id}")
        logger.debug(f"Key size: {len(qkd_key.key)} bytes")
        
        # Step 4: Decrypt message
        security_level = metadata.get('security_level')
        logger.debug(f"Decrypting with level: {security_level}")
        
        plaintext = self.encryption_engine.decrypt(
            ciphertext=ciphertext,
            key=qkd_key.key,
            metadata=metadata
        )
        logger.debug(f"Plaintext length: {len(plaintext)} bytes")
        
        # Step 5: Convert bytes to string
        message = plaintext.decode('utf-8')
        
        logger.info(f"Message decrypted successfully")
        logger.debug(f"Message length: {len(message)} characters")
        
        return message
        
    except Exception as e:
        logger.error(f"Decryption failed: {e}")
        logger.exception("Full traceback:")
        raise
```

---

## 5. Encrypted Package Structure

### Complete Package

```python
encrypted_package = {
    # Encrypted message content (base64 encoded)
    'ciphertext': 'YWJjZGVmZ2hpamtsbW5vcHFyc3R1dnd4eXo=',
    
    # Quantum key identifier
    'key_id': 'MOCK-KEY-00000123-20251012195640',
    
    # Security level (1-4)
    'security_level': 2,
    
    # Security level name
    'security_level_name': 'QUANTUM_AES',
    
    # Algorithm-specific metadata
    'metadata': {
        'security_level': SecurityLevel.QUANTUM_AES,
        'algorithm': 'AES-256-CBC',
        'iv': 'base64_encoded_iv',
        'plaintext_length': 19
    },
    
    # Optional: recipient identifier
    'recipient_id': 'bob@example.com',
    
    # Timestamp
    'timestamp': '2025-10-12T19:56:40.123456'
}
```

### Metadata by Security Level

#### Level 1: OTP
```python
metadata = {
    'security_level': SecurityLevel.QUANTUM_OTP,
    'algorithm': 'OTP',
    'plaintext_length': 19
}
```

#### Level 2: Quantum-AES
```python
metadata = {
    'security_level': SecurityLevel.QUANTUM_AES,
    'algorithm': 'AES-256-CBC',
    'iv': 'base64_encoded_initialization_vector',
    'plaintext_length': 19
}
```

#### Level 3: Post-Quantum
```python
metadata = {
    'security_level': SecurityLevel.POST_QUANTUM,
    'algorithm': 'CRYSTALS-Kyber-AES-256-GCM',
    'nonce': 'base64_encoded_nonce',
    'plaintext_length': 19
}
```

#### Level 4: Classical
```python
metadata = {
    'security_level': SecurityLevel.CLASSICAL,
    'algorithm': 'AES-256-GCM',
    'nonce': 'base64_encoded_nonce'
}
```

---

## 6. Complete Code Walkthrough

### Scenario: Sending Encrypted Email

```python
# File: qmail/core/routes/email_routes.py

@bp.route('/compose', methods=['POST'])
@login_required
def compose():
    # Step 1: Get form data
    to_addr = request.form.get('to')
    subject = request.form.get('subject')
    body = request.form.get('body')
    security_level = int(request.form.get('security_level', 2))
    
    # Step 2: Initialize EmailManager
    email_manager = get_email_manager()
    
    # Step 3: Send encrypted email
    # This calls MessageCipher.encrypt_message() internally
    success = email_manager.send_encrypted_email(
        from_addr=current_user.email,
        to_addrs=[to_addr],
        subject=subject,
        message=body,
        security_level=SecurityLevel(security_level)
    )
    
    if success:
        # Step 4: Save to database
        email = Email(
            user_id=current_user.id,
            from_addr=current_user.email,
            to_addr=json.dumps([to_addr]),
            subject=subject,
            body=body,  # Store encrypted package
            is_encrypted=True,
            security_level=security_level
        )
        db.session.add(email)
        db.session.commit()
```

### Inside EmailManager

```python
# File: qmail/email_handler/email_manager.py

def send_encrypted_email(
    self,
    from_addr: str,
    to_addrs: List[str],
    subject: str,
    message: str,
    security_level: SecurityLevel = SecurityLevel.QUANTUM_AES
) -> bool:
    try:
        logger.info(f"Sending encrypted email to {len(to_addrs)} recipient(s)")
        
        # Call MessageCipher to encrypt
        encrypted_package = self.message_cipher.encrypt_message(
            message=message,
            security_level=security_level
        )
        
        # Send via SMTP
        success = self.smtp_handler.send_encrypted_email(
            from_addr=from_addr,
            to_addrs=to_addrs,
            subject=subject,
            encrypted_package=encrypted_package
        )
        
        return success
        
    except Exception as e:
        logger.error(f"Error sending encrypted email: {e}")
        return False
```

### Receiving and Decrypting

```python
# File: qmail/core/routes/email_routes.py

@bp.route('/view/<int:email_id>')
@login_required
def view(email_id):
    # Step 1: Get email from database
    email = Email.query.filter_by(
        id=email_id,
        user_id=current_user.id
    ).first_or_404()
    
    # Step 2: If encrypted, decrypt it
    if email.is_encrypted:
        try:
            # Parse encrypted package from body
            encrypted_package = json.loads(email.body)
            
            # Initialize MessageCipher
            cipher = MessageCipher(use_mock_qkd=True)
            
            # Decrypt message
            decrypted_body = cipher.decrypt_message(encrypted_package)
            
        except Exception as e:
            decrypted_body = None
            decryption_error = str(e)
    else:
        decrypted_body = email.body
        decryption_error = None
    
    # Step 3: Render template
    return render_template(
        'email/view.html',
        email=email,
        decrypted_body=decrypted_body,
        decryption_error=decryption_error
    )
```

---

## 7. Error Handling

### Common Errors

#### 1. Key Not Found

```python
class KeyNotFoundError(Exception):
    """Raised when quantum key cannot be retrieved"""
    pass

# Usage:
try:
    qkd_key = self.qkd_client.get_key_by_id(key_id)
    if not qkd_key:
        raise KeyNotFoundError(f"Key not found: {key_id}")
except KeyNotFoundError as e:
    logger.error(f"Decryption failed: {e}")
    # Show user-friendly error
    flash("Cannot decrypt: encryption key not available", 'error')
```

#### 2. Key Too Short (OTP)

```python
try:
    ciphertext, metadata = self.encryption_engine.encrypt(
        plaintext=plaintext,
        key=quantum_key,
        security_level=SecurityLevel.QUANTUM_OTP
    )
except EncryptionError as e:
    if "Key too short" in str(e):
        logger.error(f"OTP key insufficient: {e}")
        # Suggest using different security level
        flash("File too large for OTP encryption. Use Quantum-AES instead.", 'warning')
```

#### 3. Decryption Failed

```python
try:
    plaintext = self.encryption_engine.decrypt(
        ciphertext=ciphertext,
        key=quantum_key,
        metadata=metadata
    )
except DecryptionError as e:
    logger.error(f"Decryption failed: {e}")
    # Could be wrong key, corrupted data, or algorithm mismatch
    flash("Cannot decrypt message. The encryption key may be invalid.", 'error')
```

### Error Recovery

```python
def decrypt_message_safe(self, encrypted_package: Dict) -> Optional[str]:
    """
    Safely decrypt message with error handling
    
    Returns None if decryption fails
    """
    try:
        return self.decrypt_message(encrypted_package)
    except KeyNotFoundError:
        logger.warning("Key not found, cannot decrypt")
        return None
    except DecryptionError:
        logger.warning("Decryption failed")
        return None
    except Exception as e:
        logger.error(f"Unexpected error during decryption: {e}")
        return None
```

---

## 8. Real-World Examples

### Example 1: Basic Encryption

```python
from qmail.crypto.message_cipher import MessageCipher
from qmail.crypto.encryption_engine import SecurityLevel

# Initialize
cipher = MessageCipher(use_mock_qkd=True)

# Encrypt
message = "This is a secret message!"
encrypted = cipher.encrypt_message(
    message=message,
    security_level=SecurityLevel.QUANTUM_AES
)

print(f"Ciphertext: {encrypted['ciphertext'][:50]}...")
print(f"Key ID: {encrypted['key_id']}")
print(f"Security: {encrypted['security_level_name']}")

# Decrypt
decrypted = cipher.decrypt_message(encrypted)
print(f"Decrypted: {decrypted}")

# Verify
assert decrypted == message
print("✓ Encryption/Decryption successful!")
```

### Example 2: Testing All Security Levels

```python
cipher = MessageCipher(use_mock_qkd=True)
message = "Test message for all security levels"

levels = [
    SecurityLevel.QUANTUM_OTP,
    SecurityLevel.QUANTUM_AES,
    SecurityLevel.POST_QUANTUM,
    SecurityLevel.CLASSICAL
]

for level in levels:
    print(f"\nTesting {level.name}:")
    
    # Encrypt
    encrypted = cipher.encrypt_message(message, level)
    print(f"  Key ID: {encrypted['key_id']}")
    print(f"  Ciphertext size: {len(encrypted['ciphertext'])} chars")
    
    # Decrypt
    decrypted = cipher.decrypt_message(encrypted)
    
    # Verify
    if decrypted == message:
        print(f"  ✓ Success!")
    else:
        print(f"  ✗ Failed!")
```

### Example 3: JSON Serialization

```python
# Encrypt and serialize to JSON
json_encrypted = cipher.encrypt_message_to_json(
    message="Secret data",
    security_level=SecurityLevel.QUANTUM_AES
)

# Save to file
with open('encrypted_message.json', 'w') as f:
    f.write(json_encrypted)

print("Encrypted message saved to file")

# Later: Load and decrypt
with open('encrypted_message.json', 'r') as f:
    json_data = f.read()

decrypted = cipher.decrypt_message_from_json(json_data)
print(f"Decrypted: {decrypted}")
```

### Example 4: Error Handling

```python
cipher = MessageCipher(use_mock_qkd=True)

# Encrypt a message
encrypted = cipher.encrypt_message("Test", SecurityLevel.QUANTUM_AES)

# Simulate key deletion
key_id = encrypted['key_id']
cipher.qkd_client.close_key(key_id)

# Try to decrypt
try:
    decrypted = cipher.decrypt_message(encrypted)
    print(f"Decrypted: {decrypted}")
except Exception as e:
    print(f"Error: {e}")
    print("Key was deleted, cannot decrypt!")
```

### Example 5: Performance Measurement

```python
import time

cipher = MessageCipher(use_mock_qkd=True)
message = "Performance test message " * 100  # ~2.5 KB

for level in [SecurityLevel.QUANTUM_AES, SecurityLevel.POST_QUANTUM]:
    # Measure encryption time
    start = time.time()
    encrypted = cipher.encrypt_message(message, level)
    encrypt_time = time.time() - start
    
    # Measure decryption time
    start = time.time()
    decrypted = cipher.decrypt_message(encrypted)
    decrypt_time = time.time() - start
    
    print(f"\n{level.name}:")
    print(f"  Encryption: {encrypt_time*1000:.2f} ms")
    print(f"  Decryption: {decrypt_time*1000:.2f} ms")
    print(f"  Total: {(encrypt_time + decrypt_time)*1000:.2f} ms")
```

---

## Summary

The **MessageCipher** class provides:
- ✅ Simple API for message encryption/decryption
- ✅ Automatic quantum key management
- ✅ Support for 4 security levels
- ✅ JSON serialization support
- ✅ Comprehensive error handling
- ✅ Logging for debugging

**Key Takeaways:**
1. Encryption always involves: QKD key request → Encrypt → Package
2. Decryption always involves: Extract key_id → Retrieve key → Decrypt
3. Security level determines key size and algorithm
4. All encrypted packages are JSON-serializable
5. Keys persist across application restarts (Mock QKD)

---

## Next Steps

Continue reading:
- **Part 5:** [Attachment Encryption](05_ATTACHMENT_ENCRYPTION.md)
- **Part 6:** [Code Reference](06_CODE_REFERENCE.md)

---

**Document:** Part 4 of 6  
**Last Updated:** October 12, 2025
