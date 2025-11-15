# QMail Encryption System - Complete Code Reference

## 📚 Table of Contents
1. [Quick Reference](#quick-reference)
2. [Crypto Layer API](#crypto-layer-api)
3. [QKD Client API](#qkd-client-api)
4. [Email Handler API](#email-handler-api)
5. [Database Models](#database-models)
6. [Helper Functions](#helper-functions)
7. [Configuration](#configuration)

---

## 1. Quick Reference

### Most Common Operations

```python
# Initialize encryption
from qmail.crypto.message_cipher import MessageCipher
from qmail.crypto.encryption_engine import SecurityLevel

cipher = MessageCipher(use_mock_qkd=True)

# Encrypt message
encrypted = cipher.encrypt_message(
    message="Hello World",
    security_level=SecurityLevel.QUANTUM_AES
)

# Decrypt message
decrypted = cipher.decrypt_message(encrypted)

# Encrypt file
from qmail.email_handler.attachment_handler import AttachmentHandler

handler = AttachmentHandler(use_mock_qkd=True)
with open('file.pdf', 'rb') as f:
    content = f.read()

encrypted_file = handler.encrypt_attachment(
    filename='file.pdf',
    content=content,
    security_level=SecurityLevel.QUANTUM_AES
)

# Decrypt file
decrypted_file = handler.decrypt_attachment(encrypted_file)
```

---

## 2. Crypto Layer API

### 2.1 SecurityLevel (Enum)

**File:** `qmail/crypto/encryption_engine.py`

```python
class SecurityLevel(Enum):
    """Enumeration of security levels"""
    QUANTUM_OTP = 1        # One-Time Pad
    QUANTUM_AES = 2        # Quantum-AES (Recommended)
    POST_QUANTUM = 3       # Post-Quantum Cryptography
    CLASSICAL = 4          # Classical AES
```

**Usage:**
```python
from qmail.crypto.encryption_engine import SecurityLevel

level = SecurityLevel.QUANTUM_AES
print(level.value)  # 2
print(level.name)   # 'QUANTUM_AES'
```

---

### 2.2 EncryptionEngine Class

**File:** `qmail/crypto/encryption_engine.py`

#### Constructor

```python
EncryptionEngine(security_level: SecurityLevel = SecurityLevel.QUANTUM_AES)
```

**Parameters:**
- `security_level` (SecurityLevel): Default security level

**Example:**
```python
from qmail.crypto.encryption_engine import EncryptionEngine, SecurityLevel

engine = EncryptionEngine(SecurityLevel.QUANTUM_AES)
```

#### Methods

##### encrypt()

```python
encrypt(
    plaintext: bytes,
    key: bytes,
    security_level: SecurityLevel = None
) -> Tuple[bytes, dict]
```

**Parameters:**
- `plaintext` (bytes): Data to encrypt
- `key` (bytes): Encryption key
- `security_level` (SecurityLevel, optional): Override default level

**Returns:**
- `Tuple[bytes, dict]`: (ciphertext, metadata)

**Example:**
```python
plaintext = b"Secret message"
key = secrets.token_bytes(32)  # 256-bit key

ciphertext, metadata = engine.encrypt(
    plaintext=plaintext,
    key=key,
    security_level=SecurityLevel.QUANTUM_AES
)

print(f"Ciphertext: {ciphertext.hex()[:32]}...")
print(f"Metadata: {metadata}")
```

##### decrypt()

```python
decrypt(
    ciphertext: bytes,
    key: bytes,
    metadata: dict
) -> bytes
```

**Parameters:**
- `ciphertext` (bytes): Encrypted data
- `key` (bytes): Decryption key (must match encryption key)
- `metadata` (dict): Encryption metadata

**Returns:**
- `bytes`: Decrypted plaintext

**Example:**
```python
plaintext = engine.decrypt(
    ciphertext=ciphertext,
    key=key,
    metadata=metadata
)

print(f"Plaintext: {plaintext.decode('utf-8')}")
```

##### Private Methods (Algorithm-Specific)

```python
_encrypt_otp(plaintext: bytes, key: bytes) -> Tuple[bytes, dict]
_decrypt_otp(ciphertext: bytes, key: bytes, metadata: dict) -> bytes

_encrypt_quantum_aes(plaintext: bytes, key: bytes) -> Tuple[bytes, dict]
_decrypt_quantum_aes(ciphertext: bytes, key: bytes, metadata: dict) -> bytes

_encrypt_post_quantum(plaintext: bytes, key: bytes) -> Tuple[bytes, dict]
_decrypt_post_quantum(ciphertext: bytes, key: bytes, metadata: dict) -> bytes

_encrypt_classical(plaintext: bytes, key: bytes) -> Tuple[bytes, dict]
_decrypt_classical(ciphertext: bytes, key: bytes, metadata: dict) -> bytes
```

---

### 2.3 MessageCipher Class

**File:** `qmail/crypto/message_cipher.py`

#### Constructor

```python
MessageCipher(use_mock_qkd: bool = True)
```

**Parameters:**
- `use_mock_qkd` (bool): Use Mock QKD (True) or Real QKD (False)

**Example:**
```python
from qmail.crypto.message_cipher import MessageCipher

cipher = MessageCipher(use_mock_qkd=True)
```

#### Methods

##### encrypt_message()

```python
encrypt_message(
    message: str,
    security_level: SecurityLevel = SecurityLevel.QUANTUM_AES,
    recipient_id: str = None
) -> Dict
```

**Parameters:**
- `message` (str): Plain text message to encrypt
- `security_level` (SecurityLevel): Security level to use
- `recipient_id` (str, optional): Recipient identifier

**Returns:**
- `Dict`: Encrypted package containing:
  - `ciphertext` (str): Base64 encoded ciphertext
  - `key_id` (str): Quantum key identifier
  - `security_level` (int): Security level value
  - `security_level_name` (str): Security level name
  - `metadata` (dict): Encryption metadata
  - `recipient_id` (str): Recipient (if provided)
  - `timestamp` (str): Encryption timestamp

**Example:**
```python
encrypted = cipher.encrypt_message(
    message="Top secret information",
    security_level=SecurityLevel.QUANTUM_AES,
    recipient_id="bob@example.com"
)

print(f"Key ID: {encrypted['key_id']}")
print(f"Security: {encrypted['security_level_name']}")
```

##### decrypt_message()

```python
decrypt_message(encrypted_package: Dict) -> str
```

**Parameters:**
- `encrypted_package` (Dict): Encrypted package from encrypt_message()

**Returns:**
- `str`: Decrypted plain text message

**Raises:**
- `Exception`: If key not found or decryption fails

**Example:**
```python
try:
    plaintext = cipher.decrypt_message(encrypted)
    print(f"Decrypted: {plaintext}")
except Exception as e:
    print(f"Decryption failed: {e}")
```

##### encrypt_message_to_json()

```python
encrypt_message_to_json(
    message: str,
    security_level: SecurityLevel = SecurityLevel.QUANTUM_AES
) -> str
```

**Parameters:**
- `message` (str): Plain text message
- `security_level` (SecurityLevel): Security level

**Returns:**
- `str`: JSON string of encrypted package

**Example:**
```python
json_encrypted = cipher.encrypt_message_to_json(
    message="Secret",
    security_level=SecurityLevel.QUANTUM_AES
)

# Save to file
with open('encrypted.json', 'w') as f:
    f.write(json_encrypted)
```

##### decrypt_message_from_json()

```python
decrypt_message_from_json(json_data: str) -> str
```

**Parameters:**
- `json_data` (str): JSON string from encrypt_message_to_json()

**Returns:**
- `str`: Decrypted plain text message

**Example:**
```python
with open('encrypted.json', 'r') as f:
    json_data = f.read()

plaintext = cipher.decrypt_message_from_json(json_data)
print(f"Decrypted: {plaintext}")
```

##### get_key_manager_status()

```python
get_key_manager_status() -> Dict
```

**Returns:**
- `Dict`: Key Manager status information

**Example:**
```python
status = cipher.get_key_manager_status()
print(f"Status: {status['status']}")
print(f"Keys generated: {status.get('keys_generated', 0)}")
```

---

## 3. QKD Client API

### 3.1 QKDKey (Data Class)

**File:** `qmail/km_client/qkd_client.py`

```python
@dataclass
class QKDKey:
    """Represents a quantum key"""
    key_id: str              # Unique key identifier
    key: bytes               # The actual key bytes
    key_size: int            # Key size in bits
    timestamp: datetime      # When generated
```

**Methods:**
```python
def to_dict(self) -> Dict:
    """Convert to dictionary"""
    return {
        'key_id': self.key_id,
        'key': base64.b64encode(self.key).decode('utf-8'),
        'key_size': self.key_size,
        'timestamp': self.timestamp.isoformat()
    }
```

---

### 3.2 QKDClient Class (Real QKD)

**File:** `qmail/km_client/qkd_client.py`

#### Constructor

```python
QKDClient(
    host: str = 'localhost',
    port: int = 8080,
    use_https: bool = False,
    cert_path: Optional[str] = None
)
```

**Parameters:**
- `host` (str): Key Manager hostname
- `port` (int): Key Manager port
- `use_https` (bool): Use HTTPS
- `cert_path` (str, optional): SSL certificate path

**Example:**
```python
from qmail.km_client.qkd_client import QKDClient

client = QKDClient(
    host='qkd.example.com',
    port=8080,
    use_https=True
)
```

#### Methods

##### get_status()

```python
get_status() -> Dict
```

**Returns:**
- `Dict`: Key Manager status

**Example:**
```python
status = client.get_status()
print(f"Status: {status['status']}")
print(f"Available keys: {status.get('available_keys', 0)}")
```

##### get_key()

```python
get_key(
    key_size: int = 256,
    number_of_keys: int = 1,
    extension_mandatory: Optional[List[str]] = None
) -> List[QKDKey]
```

**Parameters:**
- `key_size` (int): Key size in bits
- `number_of_keys` (int): Number of keys to request
- `extension_mandatory` (List[str], optional): Extensions

**Returns:**
- `List[QKDKey]`: List of quantum keys

**Example:**
```python
keys = client.get_key(key_size=256, number_of_keys=2)

for key in keys:
    print(f"Key ID: {key.key_id}")
    print(f"Size: {key.key_size} bits")
```

##### get_key_by_id()

```python
get_key_by_id(key_id: str) -> Optional[QKDKey]
```

**Parameters:**
- `key_id` (str): Key identifier

**Returns:**
- `QKDKey` or `None`: Key object or None if not found

**Example:**
```python
key = client.get_key_by_id('QKD-KEY-ABC123')

if key:
    print(f"Found key: {key.key_id}")
else:
    print("Key not found")
```

##### close_key()

```python
close_key(key_id: str) -> bool
```

**Parameters:**
- `key_id` (str): Key to delete

**Returns:**
- `bool`: True if successful

**Example:**
```python
success = client.close_key('QKD-KEY-ABC123')
print(f"Deleted: {success}")
```

##### from_env() (Class Method)

```python
@classmethod
from_env(cls) -> QKDClient
```

**Returns:**
- `QKDClient`: Client configured from environment variables

**Example:**
```python
# Uses QKD_KM_HOST and QKD_KM_PORT from .env
client = QKDClient.from_env()
```

---

### 3.3 MockQKDClient Class

**File:** `qmail/km_client/mock_km.py`

#### Constructor

```python
MockQKDClient(
    host: str = 'localhost',
    port: int = 8080,
    persist_keys: bool = True
)
```

**Parameters:**
- `host` (str): Ignored (for compatibility)
- `port` (int): Ignored (for compatibility)
- `persist_keys` (bool): Save keys to disk

**Example:**
```python
from qmail.km_client.mock_km import MockQKDClient

mock_client = MockQKDClient(persist_keys=True)
```

#### Methods

Same interface as `QKDClient`:
- `get_status()` → Dict
- `get_key(...)` → List[QKDKey]
- `get_key_by_id(...)` → Optional[QKDKey]
- `close_key(...)` → bool
- `from_env()` → MockQKDClient (class method)

**Additional Methods:**

##### _save_keys()

```python
_save_keys() -> None
```

Saves keys to `instance/mock_qkd_keys.json`

##### _load_keys()

```python
_load_keys() -> None
```

Loads keys from persistent storage

---

## 4. Email Handler API

### 4.1 AttachmentHandler Class

**File:** `qmail/email_handler/attachment_handler.py`

#### Data Classes

##### Attachment

```python
@dataclass
class Attachment:
    """Plaintext attachment"""
    filename: str
    content: bytes
    content_type: str
    size: int
    
    def to_dict(self) -> Dict
```

##### EncryptedAttachment

```python
@dataclass
class EncryptedAttachment:
    """Encrypted attachment"""
    filename: str
    encrypted_content: str
    content_type: str
    original_size: int
    encrypted_size: int
    key_id: str
    security_level: str
    metadata: Dict
```

#### Constructor

```python
AttachmentHandler(
    use_mock_qkd: bool = True,
    max_attachment_size: int = 25 * 1024 * 1024
)
```

**Parameters:**
- `use_mock_qkd` (bool): Use Mock QKD
- `max_attachment_size` (int): Max file size in bytes

**Example:**
```python
from qmail.email_handler.attachment_handler import AttachmentHandler

handler = AttachmentHandler(
    use_mock_qkd=True,
    max_attachment_size=50 * 1024 * 1024  # 50 MB
)
```

#### Methods

##### encrypt_file()

```python
encrypt_file(
    file_path: str,
    security_level: SecurityLevel = SecurityLevel.QUANTUM_AES
) -> EncryptedAttachment
```

**Parameters:**
- `file_path` (str): Path to file
- `security_level` (SecurityLevel): Security level

**Returns:**
- `EncryptedAttachment`: Encrypted file

**Example:**
```python
encrypted = handler.encrypt_file(
    file_path='/path/to/document.pdf',
    security_level=SecurityLevel.QUANTUM_AES
)

print(f"Encrypted: {encrypted.filename}")
print(f"Key: {encrypted.key_id}")
```

##### encrypt_attachment()

```python
encrypt_attachment(
    filename: str,
    content: bytes,
    security_level: SecurityLevel = SecurityLevel.QUANTUM_AES
) -> EncryptedAttachment
```

**Parameters:**
- `filename` (str): File name
- `content` (bytes): File content
- `security_level` (SecurityLevel): Security level

**Returns:**
- `EncryptedAttachment`: Encrypted attachment

**Example:**
```python
with open('file.pdf', 'rb') as f:
    content = f.read()

encrypted = handler.encrypt_attachment(
    filename='file.pdf',
    content=content,
    security_level=SecurityLevel.QUANTUM_AES
)
```

##### decrypt_attachment()

```python
decrypt_attachment(
    encrypted_attachment: EncryptedAttachment
) -> Attachment
```

**Parameters:**
- `encrypted_attachment` (EncryptedAttachment): Encrypted file

**Returns:**
- `Attachment`: Decrypted attachment

**Example:**
```python
decrypted = handler.decrypt_attachment(encrypted)

# Save to disk
with open(decrypted.filename, 'wb') as f:
    f.write(decrypted.content)
```

##### encrypt_multiple_files()

```python
encrypt_multiple_files(
    file_paths: List[str],
    security_level: SecurityLevel = SecurityLevel.QUANTUM_AES
) -> List[EncryptedAttachment]
```

**Parameters:**
- `file_paths` (List[str]): List of file paths
- `security_level` (SecurityLevel): Security level

**Returns:**
- `List[EncryptedAttachment]`: List of encrypted files

**Example:**
```python
files = ['file1.pdf', 'file2.jpg', 'file3.doc']
encrypted_files = handler.encrypt_multiple_files(files)

for enc in encrypted_files:
    print(f"Encrypted: {enc.filename}")
```

##### save_attachment()

```python
save_attachment(
    attachment: Attachment,
    output_dir: str = 'downloads'
) -> str
```

**Parameters:**
- `attachment` (Attachment): Decrypted attachment
- `output_dir` (str): Output directory

**Returns:**
- `str`: Path to saved file

**Example:**
```python
saved_path = handler.save_attachment(
    attachment=decrypted,
    output_dir='downloads'
)

print(f"Saved to: {saved_path}")
```

##### get_attachment_info()

```python
get_attachment_info(file_path: str) -> Dict
```

**Parameters:**
- `file_path` (str): Path to file

**Returns:**
- `Dict`: File information

**Example:**
```python
info = handler.get_attachment_info('large_file.pdf')

print(f"Filename: {info['filename']}")
print(f"Size: {info['size_mb']:.2f} MB")
print(f"Type: {info['content_type']}")
print(f"Can encrypt: {info['can_encrypt']}")
```

---

### 4.2 EmailManager Class

**File:** `qmail/email_handler/email_manager.py`

#### Constructor

```python
EmailManager(
    smtp_config: Dict,
    imap_config: Dict,
    use_mock_qkd: bool = True
)
```

**Parameters:**
- `smtp_config` (Dict): SMTP configuration
- `imap_config` (Dict): IMAP configuration
- `use_mock_qkd` (bool): Use Mock QKD

**Example:**
```python
from qmail.email_handler.email_manager import EmailManager

smtp_config = {
    'smtp_server': 'smtp.gmail.com',
    'smtp_port': 587,
    'username': 'user@gmail.com',
    'password': 'app_password'
}

imap_config = {
    'imap_server': 'imap.gmail.com',
    'imap_port': 993,
    'username': 'user@gmail.com',
    'password': 'app_password'
}

manager = EmailManager(smtp_config, imap_config, use_mock_qkd=True)
```

#### Methods

##### send_encrypted_email()

```python
send_encrypted_email(
    from_addr: str,
    to_addrs: List[str],
    subject: str,
    message: str,
    security_level: SecurityLevel = SecurityLevel.QUANTUM_AES,
    cc_addrs: Optional[List[str]] = None,
    encrypted_attachments: Optional[List[Dict]] = None
) -> bool
```

**Parameters:**
- `from_addr` (str): Sender email
- `to_addrs` (List[str]): Recipients
- `subject` (str): Email subject
- `message` (str): Message body
- `security_level` (SecurityLevel): Security level
- `cc_addrs` (List[str], optional): CC recipients
- `encrypted_attachments` (List[Dict], optional): Encrypted files

**Returns:**
- `bool`: True if successful

**Example:**
```python
success = manager.send_encrypted_email(
    from_addr='alice@example.com',
    to_addrs=['bob@example.com'],
    subject='Confidential',
    message='Secret information',
    security_level=SecurityLevel.QUANTUM_AES
)

print(f"Sent: {success}")
```

##### fetch_and_decrypt_emails()

```python
fetch_and_decrypt_emails(
    folder: str = 'INBOX',
    limit: int = 20
) -> List[Dict]
```

**Parameters:**
- `folder` (str): IMAP folder name
- `limit` (int): Max emails to fetch

**Returns:**
- `List[Dict]`: List of email dictionaries

**Example:**
```python
emails = manager.fetch_and_decrypt_emails(folder='INBOX', limit=10)

for email in emails:
    print(f"From: {email['from']}")
    print(f"Subject: {email['subject']}")
    if email.get('decrypted_body'):
        print(f"Body: {email['decrypted_body']}")
```

---

## 5. Database Models

**File:** `qmail/models/database.py`

### 5.1 User Model

```python
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    emails = db.relationship('Email', backref='user', lazy='dynamic')
    contacts = db.relationship('Contact', backref='user', lazy='dynamic')
```

### 5.2 Email Model

```python
class Email(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message_id = db.Column(db.String(255), unique=True)
    from_addr = db.Column(db.String(255), nullable=False)
    to_addr = db.Column(db.Text)
    cc_addr = db.Column(db.Text)
    subject = db.Column(db.String(255))
    body = db.Column(db.Text)
    is_encrypted = db.Column(db.Boolean, default=False)
    security_level = db.Column(db.Integer)
    security_level_name = db.Column(db.String(50))
    qkd_key_id = db.Column(db.String(255))
    is_read = db.Column(db.Boolean, default=False)
    is_sent = db.Column(db.Boolean, default=False)
    folder = db.Column(db.String(50), default='inbox')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    received_at = db.Column(db.DateTime)
    sent_at = db.Column(db.DateTime)
    
    # Relationships
    attachments = db.relationship('EmailAttachment', backref='email', 
                                 lazy='dynamic', cascade='all, delete-orphan')
```

### 5.3 EmailAttachment Model

```python
class EmailAttachment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email_id = db.Column(db.Integer, db.ForeignKey('email.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    content_type = db.Column(db.String(100))
    original_size = db.Column(db.Integer)
    encrypted_size = db.Column(db.Integer)
    encrypted_content = db.Column(db.Text, nullable=False)
    key_id = db.Column(db.String(255), nullable=False)
    security_level = db.Column(db.Integer)
    security_level_name = db.Column(db.String(50))
    encryption_metadata = db.Column(db.Text)
    is_encrypted = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
```

---

## 6. Helper Functions

### 6.1 File Size Formatting

```python
def format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format"""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"
```

**Example:**
```python
print(format_file_size(1024))           # "1.0 KB"
print(format_file_size(1048576))        # "1.0 MB"
print(format_file_size(5242880))        # "5.0 MB"
```

### 6.2 Filename Validation

```python
def is_allowed_file(filename: str) -> bool:
    """Check if file extension is allowed"""
    allowed_extensions = {
        '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg',
        '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
        '.txt', '.rtf', '.odt', '.ods', '.odp',
        '.zip', '.rar', '.tar', '.gz', '.7z',
        '.csv', '.json', '.xml'
    }
    
    ext = os.path.splitext(filename)[1].lower()
    return ext in allowed_extensions
```

**Example:**
```python
print(is_allowed_file('document.pdf'))   # True
print(is_allowed_file('image.jpg'))      # True
print(is_allowed_file('virus.exe'))      # False
```

---

## 7. Configuration

### 7.1 Environment Variables

```bash
# QKD Configuration
QKD_USE_MOCK=true
QKD_KM_HOST=localhost
QKD_KM_PORT=8080

# Email Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password

IMAP_SERVER=imap.gmail.com
IMAP_PORT=993
IMAP_USERNAME=your_email@gmail.com
IMAP_PASSWORD=your_app_password

# Security
DEFAULT_SECURITY_LEVEL=2
MAX_ATTACHMENT_SIZE=25

# Database
DATABASE_URL=sqlite:///instance/qmail.db

# Flask
SECRET_KEY=your-secret-key-here
FLASK_ENV=development
```

### 7.2 Loading Configuration

```python
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Access variables
qkd_host = os.getenv('QKD_KM_HOST', 'localhost')
qkd_port = int(os.getenv('QKD_KM_PORT', '8080'))
use_mock = os.getenv('QKD_USE_MOCK', 'true').lower() == 'true'

print(f"QKD: {qkd_host}:{qkd_port} (mock={use_mock})")
```

---

## Summary

This reference covers:
- ✅ All public APIs
- ✅ Method signatures
- ✅ Parameters and return types
- ✅ Usage examples
- ✅ Database models
- ✅ Helper functions
- ✅ Configuration

**For more details, see:**
- Part 1: [Overview & Architecture](01_OVERVIEW_ARCHITECTURE.md)
- Part 2: [Encryption Algorithms](02_ENCRYPTION_ALGORITHMS.md)
- Part 3: [Key Management](03_KEY_MANAGEMENT.md)
- Part 4: [Message Encryption](04_MESSAGE_ENCRYPTION.md)
- Part 5: [Attachment Encryption](05_ATTACHMENT_ENCRYPTION.md)

---

**Document:** Part 6 of 6  
**Last Updated:** October 12, 2025  
**Status:** Complete ✅
