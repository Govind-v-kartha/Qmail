# QMail Encryption System - Attachment Encryption

## 📚 Table of Contents
1. [Overview](#overview)
2. [AttachmentHandler Class](#attachmenthandler-class)
3. [File Encryption Process](#file-encryption-process)
4. [File Decryption Process](#file-decryption-process)
5. [MIME Integration](#mime-integration)
6. [Size Limitations](#size-limitations)
7. [Complete Code Examples](#complete-code-examples)
8. [Troubleshooting](#troubleshooting)

---

## 1. Overview

The **AttachmentHandler** class (`qmail/email_handler/attachment_handler.py`) handles encryption and decryption of file attachments. It uses the same quantum encryption as messages but is optimized for binary file data.

**File:** `qmail/email_handler/attachment_handler.py`  
**Primary Classes:** `AttachmentHandler`, `EncryptedAttachment`, `Attachment`  
**Purpose:** Quantum-secure file encryption

---

## 2. AttachmentHandler Class

### Class Structure

```python
class AttachmentHandler:
    """
    Handles file attachments with quantum encryption
    """
    
    def __init__(
        self,
        use_mock_qkd: bool = True,
        max_attachment_size: int = 25 * 1024 * 1024  # 25 MB
    ):
        """
        Initialize attachment handler
        
        Args:
            use_mock_qkd: Use Mock QKD or Real QKD
            max_attachment_size: Maximum file size in bytes
        """
        self.cipher = MessageCipher(use_mock_qkd=use_mock_qkd)
        self.max_attachment_size = max_attachment_size
        
        logger.info(
            f"Attachment handler initialized "
            f"(max size: {max_attachment_size / 1024 / 1024:.1f} MB)"
        )
```

### Data Classes

#### Attachment (Plaintext)

```python
@dataclass
class Attachment:
    """Represents a plaintext (unencrypted) attachment"""
    filename: str          # Original filename
    content: bytes         # File content (binary)
    content_type: str      # MIME type (e.g., 'image/jpeg')
    size: int              # Size in bytes
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'filename': self.filename,
            'content': base64.b64encode(self.content).decode('utf-8'),
            'content_type': self.content_type,
            'size': self.size
        }
```

#### EncryptedAttachment

```python
@dataclass
class EncryptedAttachment:
    """Represents an encrypted attachment"""
    filename: str              # Original filename
    encrypted_content: str     # Base64 encoded ciphertext
    content_type: str          # MIME type
    original_size: int         # Original file size
    encrypted_size: int        # Encrypted size
    key_id: str               # Quantum key ID
    security_level: str       # Security level name
    metadata: Dict            # Encryption metadata
```

### Key Methods

```python
class AttachmentHandler:
    
    # Encrypt from file on disk
    def encrypt_file(
        self,
        file_path: str,
        security_level: SecurityLevel = SecurityLevel.QUANTUM_AES
    ) -> EncryptedAttachment
    
    # Encrypt from memory (uploaded file)
    def encrypt_attachment(
        self,
        filename: str,
        content: bytes,
        security_level: SecurityLevel = SecurityLevel.QUANTUM_AES
    ) -> EncryptedAttachment
    
    # Decrypt attachment
    def decrypt_attachment(
        self,
        encrypted_attachment: EncryptedAttachment
    ) -> Attachment
    
    # Encrypt multiple files
    def encrypt_multiple_files(
        self,
        file_paths: List[str],
        security_level: SecurityLevel = SecurityLevel.QUANTUM_AES
    ) -> List[EncryptedAttachment]
    
    # Save decrypted file
    def save_attachment(
        self,
        attachment: Attachment,
        output_dir: str = 'downloads'
    ) -> str
```

---

## 3. File Encryption Process

### Step-by-Step Flow

```
File on Disk / Uploaded File
        │
        ▼
┌─────────────────────────────────────────────┐
│ Step 1: Read File Content                   │
│ with open(file_path, 'rb') as f:           │
│     content = f.read()                      │
│ Result: Binary data (bytes)                 │
└────────────────┬────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────┐
│ Step 2: Validate File Size                  │
│ if len(content) > max_size:                 │
│     raise ValueError("File too large")      │
└────────────────┬────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────┐
│ Step 3: Base64 Encode Content               │
│ content_b64 = base64.b64encode(content)     │
│ Binary → ASCII string                       │
│ Why? MessageCipher expects string input     │
└────────────────┬────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────┐
│ Step 4: Encrypt with MessageCipher          │
│ encrypted_pkg = cipher.encrypt_message(     │
│     message=content_b64,                    │
│     security_level=QUANTUM_AES              │
│ )                                           │
│ Returns: Encrypted package dict             │
└────────────────┬────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────┐
│ Step 5: Determine Content Type              │
│ import mimetypes                            │
│ content_type, _ = mimetypes.guess_type(     │
│     filename                                │
│ )                                           │
│ Example: 'image/jpeg', 'application/pdf'    │
└────────────────┬────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────┐
│ Step 6: Create EncryptedAttachment          │
│ EncryptedAttachment(                        │
│     filename=filename,                      │
│     encrypted_content=pkg['ciphertext'],    │
│     content_type=content_type,              │
│     original_size=len(content),             │
│     encrypted_size=len(pkg['ciphertext']),  │
│     key_id=pkg['key_id'],                   │
│     security_level=pkg['security_level'],   │
│     metadata=pkg['metadata']                │
│ )                                           │
└────────────────┬────────────────────────────┘
                 │
                 ▼
    EncryptedAttachment Object
```

### Code Implementation

```python
def encrypt_attachment(
    self,
    filename: str,
    content: bytes,
    security_level: SecurityLevel = SecurityLevel.QUANTUM_AES
) -> EncryptedAttachment:
    """
    Encrypt attachment content (for uploaded files)
    
    Args:
        filename: Name of the file
        content: Binary content of the file
        security_level: Quantum security level
    
    Returns:
        EncryptedAttachment object
    
    Example:
        handler = AttachmentHandler(use_mock_qkd=True)
        
        # Read file
        with open('document.pdf', 'rb') as f:
            content = f.read()
        
        # Encrypt
        encrypted = handler.encrypt_attachment(
            filename='document.pdf',
            content=content,
            security_level=SecurityLevel.QUANTUM_AES
        )
        
        print(f"Encrypted: {encrypted.filename}")
        print(f"Key: {encrypted.key_id}")
    """
    file_size = len(content)
    
    # Step 2: Validate size
    if file_size > self.max_attachment_size:
        raise ValueError(
            f"Attachment too large: {file_size / 1024 / 1024:.1f} MB "
            f"(max: {self.max_attachment_size / 1024 / 1024:.1f} MB)"
        )
    
    logger.info(f"Encrypting attachment: {filename} ({file_size} bytes)")
    
    # Step 3: Base64 encode content
    # (MessageCipher expects string, not bytes)
    content_b64 = base64.b64encode(content).decode('utf-8')
    logger.debug(f"Base64 encoded size: {len(content_b64)} chars")
    
    # Step 4: Encrypt with MessageCipher
    encrypted_package = self.cipher.encrypt_message(
        content_b64,
        security_level
    )
    
    logger.debug(f"Encrypted package created (key: {encrypted_package['key_id']})")
    
    # Step 5: Determine content type
    content_type, _ = mimetypes.guess_type(filename)
    if not content_type:
        content_type = 'application/octet-stream'
    
    logger.debug(f"Content type: {content_type}")
    
    # Step 6: Create EncryptedAttachment
    encrypted_attachment = EncryptedAttachment(
        filename=filename,
        encrypted_content=encrypted_package['ciphertext'],
        content_type=content_type,
        original_size=file_size,
        encrypted_size=len(encrypted_package['ciphertext']),
        key_id=encrypted_package['key_id'],
        security_level=encrypted_package['security_level_name'],
        metadata=encrypted_package['metadata']
    )
    
    logger.info(
        f"Attachment encrypted: {filename} "
        f"(key: {encrypted_attachment.key_id})"
    )
    
    return encrypted_attachment
```

---

## 4. File Decryption Process

### Step-by-Step Flow

```
EncryptedAttachment Object
        │
        ▼
┌─────────────────────────────────────────────┐
│ Step 1: Reconstruct Encrypted Package       │
│ encrypted_pkg = {                           │
│     'ciphertext': enc_att.encrypted_content,│
│     'key_id': enc_att.key_id,               │
│     'metadata': enc_att.metadata,           │
│     ...                                     │
│ }                                           │
└────────────────┬────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────┐
│ Step 2: Decrypt with MessageCipher          │
│ decrypted_b64 = cipher.decrypt_message(     │
│     encrypted_pkg                           │
│ )                                           │
│ Returns: Base64 string                      │
└────────────────┬────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────┐
│ Step 3: Base64 Decode to Binary             │
│ content = base64.b64decode(decrypted_b64)   │
│ ASCII string → Binary data                  │
└────────────────┬────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────┐
│ Step 4: Create Attachment Object            │
│ Attachment(                                 │
│     filename=original_filename,             │
│     content=binary_content,                 │
│     content_type=mime_type,                 │
│     size=len(content)                       │
│ )                                           │
└────────────────┬────────────────────────────┘
                 │
                 ▼
      Attachment Object (Decrypted)
```

### Code Implementation

```python
def decrypt_attachment(
    self,
    encrypted_attachment: EncryptedAttachment
) -> Attachment:
    """
    Decrypt an encrypted attachment
    
    Args:
        encrypted_attachment: EncryptedAttachment object
    
    Returns:
        Attachment object with decrypted content
    
    Example:
        handler = AttachmentHandler(use_mock_qkd=True)
        
        # Decrypt
        decrypted = handler.decrypt_attachment(encrypted_attachment)
        
        # Save to disk
        with open(decrypted.filename, 'wb') as f:
            f.write(decrypted.content)
    """
    logger.info(f"Decrypting attachment: {encrypted_attachment.filename}")
    logger.debug(f"  Key ID: {encrypted_attachment.key_id}")
    logger.debug(f"  Security Level: {encrypted_attachment.security_level}")
    logger.debug(f"  Encrypted size: {encrypted_attachment.encrypted_size}")
    logger.debug(f"  Original size: {encrypted_attachment.original_size}")
    
    try:
        # Step 1: Reconstruct encrypted package
        encrypted_package = {
            'ciphertext': encrypted_attachment.encrypted_content,
            'key_id': encrypted_attachment.key_id,
            'security_level': SecurityLevel[encrypted_attachment.security_level].value,
            'security_level_name': encrypted_attachment.security_level,
            'metadata': encrypted_attachment.metadata
        }
        
        logger.debug("Encrypted package reconstructed")
        
        # Step 2: Decrypt with MessageCipher
        decrypted_b64 = self.cipher.decrypt_message(encrypted_package)
        logger.debug(f"Decrypted base64 length: {len(decrypted_b64)} chars")
        
        # Step 3: Base64 decode to get original binary content
        decrypted_content = base64.b64decode(decrypted_b64)
        logger.debug(f"Decoded binary length: {len(decrypted_content)} bytes")
        
        # Step 4: Create Attachment object
        attachment = Attachment(
            filename=encrypted_attachment.filename,
            content=decrypted_content,
            content_type=encrypted_attachment.content_type,
            size=len(decrypted_content)
        )
        
        logger.info(f"Attachment decrypted: {attachment.filename} ({attachment.size} bytes)")
        
        return attachment
        
    except Exception as e:
        logger.error(f"Failed to decrypt attachment {encrypted_attachment.filename}: {e}")
        logger.error(f"  Key ID: {encrypted_attachment.key_id}")
        logger.error(f"  Security Level: {encrypted_attachment.security_level}")
        raise
```

---

## 5. MIME Integration

### Sending Attachments via Email

```python
# File: qmail/email_handler/smtp_handler.py

def send_encrypted_email(
    self,
    from_addr: str,
    to_addrs: List[str],
    subject: str,
    encrypted_package: Dict,
    encrypted_attachments: Optional[List[Dict]] = None
) -> bool:
    """Send email with encrypted attachments"""
    
    # Convert encrypted attachments to MIME format
    smtp_attachments = []
    
    if encrypted_attachments:
        for att in encrypted_attachments:
            # Create JSON package for attachment
            att_package = {
                'filename': att.get('filename'),
                'encrypted_content': att.get('encrypted_content'),
                'key_id': att.get('key_id'),
                'security_level': att.get('security_level'),
                'security_level_name': att.get('security_level_name'),
                'content_type': att.get('content_type'),
                'original_size': att.get('original_size'),
                'metadata': att.get('metadata')
            }
            
            # Encode as JSON and convert to bytes
            att_data = json.dumps(att_package, indent=2).encode('utf-8')
            
            # Add .qmail_enc extension
            filename = f"{att.get('filename', 'attachment')}.qmail_enc"
            
            smtp_attachments.append({
                'filename': filename,
                'data': att_data
            })
    
    # Send via SMTP with attachments
    return self.send_email(
        from_addr=from_addr,
        to_addrs=to_addrs,
        subject=subject,
        body=plain_notice,
        attachments=smtp_attachments
    )
```

### Receiving Attachments from Email

```python
# File: qmail/email_handler/imap_handler.py

def _extract_attachments(self, msg: email.message.Message) -> List[Dict]:
    """Extract attachments from email message"""
    attachments = []
    
    if msg.is_multipart():
        for part in msg.walk():
            if 'attachment' in str(part.get('Content-Disposition', '')):
                filename = part.get_filename()
                
                if filename:
                    payload = part.get_payload(decode=True)
                    
                    attachment_data = {
                        'filename': filename,
                        'content_type': part.get_content_type(),
                        'size': len(payload),
                        'data': payload
                    }
                    
                    # Check if encrypted QMail attachment
                    if filename.endswith('.qmail_enc'):
                        try:
                            # Parse JSON
                            encrypted_package = json.loads(payload.decode('utf-8'))
                            attachment_data['is_encrypted'] = True
                            attachment_data['encrypted_package'] = encrypted_package
                            attachment_data['original_filename'] = encrypted_package.get('filename')
                            attachment_data['key_id'] = encrypted_package.get('key_id')
                        except:
                            attachment_data['is_encrypted'] = False
                    
                    attachments.append(attachment_data)
    
    return attachments
```

---

## 6. Size Limitations

### Why Size Matters

**Different security levels have different limitations:**

| Security Level | Key Size | Best For | File Size Limit |
|---------------|----------|----------|-----------------|
| **QUANTUM_OTP** | = file size | Short messages | ⚠️ **< 1 MB** (key size issue) |
| **QUANTUM_AES** | 256 bits (fixed) | **All files** ✅ | Up to 25 MB |
| **POST_QUANTUM** | 256 bits (fixed) | All files | Up to 25 MB |
| **CLASSICAL** | 256 bits (fixed) | All files | Up to 25 MB |

### OTP Limitation Explained

```python
# Why OTP is problematic for large files:

original_file = 1_048_576  # 1 MB file
base64_encoded = int(original_file * 1.34)  # ~1.4 MB
required_key_size = base64_encoded * 8  # ~11.2 million bits!

# This is too large for practical quantum key generation
# and storage in Mock QKD
```

### Recommended Configuration

```python
# For attachments, always use QUANTUM_AES
handler = AttachmentHandler(
    use_mock_qkd=True,
    max_attachment_size=25 * 1024 * 1024  # 25 MB
)

# Encrypt with QUANTUM_AES (safe for any file size up to limit)
encrypted = handler.encrypt_attachment(
    filename='large_file.pdf',
    content=file_content,
    security_level=SecurityLevel.QUANTUM_AES  # ✅ Recommended
)
```

---

## 7. Complete Code Examples

### Example 1: Encrypt and Decrypt File

```python
from qmail.email_handler.attachment_handler import AttachmentHandler
from qmail.crypto.encryption_engine import SecurityLevel

# Initialize handler
handler = AttachmentHandler(use_mock_qkd=True)

# Read file
with open('document.pdf', 'rb') as f:
    content = f.read()

print(f"Original size: {len(content)} bytes")

# Encrypt
encrypted = handler.encrypt_attachment(
    filename='document.pdf',
    content=content,
    security_level=SecurityLevel.QUANTUM_AES
)

print(f"Encrypted with key: {encrypted.key_id}")
print(f"Encrypted size: {encrypted.encrypted_size} bytes")

# Decrypt
decrypted = handler.decrypt_attachment(encrypted)

print(f"Decrypted size: {decrypted.size} bytes")

# Verify
if decrypted.content == content:
    print("✓ Encryption/Decryption successful!")
else:
    print("✗ Content mismatch!")

# Save decrypted file
with open('decrypted_document.pdf', 'wb') as f:
    f.write(decrypted.content)
```

### Example 2: Encrypt Multiple Files

```python
handler = AttachmentHandler(use_mock_qkd=True)

# List of files to encrypt
files = [
    'document1.pdf',
    'image.jpg',
    'data.csv'
]

# Encrypt all
encrypted_files = handler.encrypt_multiple_files(
    files,
    security_level=SecurityLevel.QUANTUM_AES
)

print(f"Encrypted {len(encrypted_files)} files:")
for enc in encrypted_files:
    print(f"  - {enc.filename}: {enc.key_id}")

# Decrypt all
for enc in encrypted_files:
    dec = handler.decrypt_attachment(enc)
    print(f"Decrypted: {dec.filename} ({dec.size} bytes)")
```

### Example 3: Using with Flask Upload

```python
from flask import request
from werkzeug.utils import secure_filename

@app.route('/upload', methods=['POST'])
def upload_file():
    # Get uploaded file
    file = request.files['attachment']
    
    if file:
        # Secure filename
        filename = secure_filename(file.filename)
        
        # Read content
        content = file.read()
        
        # Initialize handler
        handler = AttachmentHandler(use_mock_qkd=True)
        
        # Encrypt
        encrypted = handler.encrypt_attachment(
            filename=filename,
            content=content,
            security_level=SecurityLevel.QUANTUM_AES
        )
        
        # Save to database
        db_attachment = EmailAttachment(
            filename=encrypted.filename,
            encrypted_content=encrypted.encrypted_content,
            key_id=encrypted.key_id,
            # ... other fields
        )
        db.session.add(db_attachment)
        db.session.commit()
        
        return {'success': True, 'attachment_id': db_attachment.id}
```

### Example 4: Download Encrypted Attachment

```python
from flask import send_file
from io import BytesIO

@app.route('/download/<int:attachment_id>')
def download_attachment(attachment_id):
    # Get from database
    db_attachment = EmailAttachment.query.get_or_404(attachment_id)
    
    # Initialize handler
    handler = AttachmentHandler(use_mock_qkd=True)
    
    # Create EncryptedAttachment object
    encrypted = EncryptedAttachment(
        filename=db_attachment.filename,
        encrypted_content=db_attachment.encrypted_content,
        content_type=db_attachment.content_type,
        original_size=db_attachment.original_size,
        encrypted_size=db_attachment.encrypted_size,
        key_id=db_attachment.key_id,
        security_level=db_attachment.security_level_name,
        metadata=json.loads(db_attachment.encryption_metadata)
    )
    
    # Decrypt
    decrypted = handler.decrypt_attachment(encrypted)
    
    # Send file
    return send_file(
        BytesIO(decrypted.content),
        as_attachment=True,
        download_name=decrypted.filename,
        mimetype=decrypted.content_type
    )
```

---

## 8. Troubleshooting

### Issue 1: "Key too short for OTP decryption"

**Cause:** File too large for OTP encryption

**Solution:**
```python
# Use QUANTUM_AES instead of OTP
encrypted = handler.encrypt_attachment(
    filename='large_file.pdf',
    content=content,
    security_level=SecurityLevel.QUANTUM_AES  # ✅ Use this
    # NOT SecurityLevel.QUANTUM_OTP  # ❌ Avoid for files
)
```

### Issue 2: "Attachment too large"

**Cause:** File exceeds `max_attachment_size`

**Solutions:**
```python
# Option 1: Increase limit
handler = AttachmentHandler(
    use_mock_qkd=True,
    max_attachment_size=50 * 1024 * 1024  # 50 MB
)

# Option 2: Compress file before encrypting
import gzip
compressed = gzip.compress(file_content)
encrypted = handler.encrypt_attachment('file.gz', compressed)

# Option 3: Split into smaller chunks
```

### Issue 3: File content corrupted after decryption

**Causes:**
- Wrong key retrieved
- Database corruption
- Encoding issues

**Debug:**
```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Verify key ID
print(f"Encrypting with key: {encrypted.key_id}")
print(f"Decrypting with key: {encrypted.key_id}")

# Check sizes
print(f"Original: {original_size} bytes")
print(f"Encrypted: {encrypted.encrypted_size} bytes")
print(f"Decrypted: {decrypted.size} bytes")

# Compare checksums
import hashlib
original_hash = hashlib.sha256(original_content).hexdigest()
decrypted_hash = hashlib.sha256(decrypted.content).hexdigest()
print(f"Hashes match: {original_hash == decrypted_hash}")
```

### Issue 4: Cannot retrieve quantum key

**Cause:** Key deleted or not persisted

**Solution:**
```python
# Ensure Mock QKD persistence enabled
qkd_client = MockQKDClient(persist_keys=True)

# Check if key exists
key = qkd_client.get_key_by_id(key_id)
if not key:
    print(f"Key not found: {key_id}")
    print("Check instance/mock_qkd_keys.json")
```

---

## Summary

**AttachmentHandler provides:**
- ✅ Quantum-secure file encryption
- ✅ Support for any file type
- ✅ Base64 encoding for binary safety
- ✅ Integration with email MIME
- ✅ Multiple file support
- ✅ Size validation
- ✅ Error handling

**Best Practices:**
1. ✅ Always use **QUANTUM_AES** for attachments
2. ✅ Validate file size before encryption
3. ✅ Use secure_filename() for uploaded files
4. ✅ Enable key persistence for Mock QKD
5. ✅ Log encryption/decryption for debugging

---

## Next Steps

Continue reading:
- **Part 6:** [Code Reference](06_CODE_REFERENCE.md)

---

**Document:** Part 5 of 6  
**Last Updated:** October 12, 2025
