# QMail Encryption System - Overview & Architecture

## 📚 Table of Contents
1. [Introduction](#introduction)
2. [System Architecture](#system-architecture)
3. [Core Components](#core-components)
4. [Encryption Flow](#encryption-flow)
5. [Security Levels](#security-levels)
6. [Directory Structure](#directory-structure)

---

## 1. Introduction

QMail is a **quantum-secure email system** that uses **Quantum Key Distribution (QKD)** to encrypt email messages and attachments. Unlike traditional email encryption, QMail leverages quantum physics principles to provide theoretically unbreakable encryption.

### Key Features
- ✅ **4 Security Levels**: From perfect secrecy (OTP) to classical encryption
- ✅ **Quantum Key Distribution**: Keys generated using quantum mechanics
- ✅ **Message Encryption**: Email body encrypted with quantum keys
- ✅ **Attachment Encryption**: Files encrypted separately with quantum keys
- ✅ **Mock QKD Support**: Simulated QKD for development/testing
- ✅ **Persistent Keys**: Keys survive application restarts

---

## 2. System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        QMail Application                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐     ┌──────────────┐    ┌──────────────┐  │
│  │   Web UI     │────▶│   Routes     │───▶│   Models     │ │
│  │ (Templates)  │     │(email_routes)│    │ (Database)   ││
│  └──────────────┘     └──────────────┘    └──────────────┘│
│         │                     │                             │
│         │                     ▼                             │
│         │         ┌───────────────────────┐                │
│         │         │   Email Handlers      │                │
│         └────────▶│ - EmailManager        │                │
│                   │ - SMTPHandler         │                │
│                   │ - IMAPHandler         │                │
│                   │ - AttachmentHandler   │                │
│                   └───────────┬───────────┘                │
│                               │                            │
│                               ▼                            │
│                   ┌───────────────────────┐                │
│                   │  Crypto Layer         │                │
│                   │ - MessageCipher       │                │
│                   │ - EncryptionEngine    │                │
│                   └───────────┬───────────┘                │
│                               │                            │
│                               ▼                            │
│                   ┌───────────────────────┐                │
│                   │  QKD Client Layer     │                │
│                   │ - QKDClient (Real)    │                │
│                   │ - MockQKDClient       │                │
│                   └───────────┬───────────┘                │
│                               │                            │
└───────────────────────────────┼────────────────────────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │   Key Manager (KM)    │
                    │ - Quantum Hardware    │
                    │ - Key Storage         │
                    │ - Key Generation      │
                    └───────────────────────┘
```

---

## 3. Core Components

### 3.1 Crypto Layer

**Location:** `qmail/crypto/`

#### `encryption_engine.py`
- **Purpose:** Implements 4 encryption algorithms
- **Classes:** `EncryptionEngine`
- **Methods:**
  - `encrypt()` - Encrypts plaintext with quantum key
  - `decrypt()` - Decrypts ciphertext with quantum key
  - `_encrypt_otp()` - One-Time Pad encryption
  - `_encrypt_quantum_aes()` - Quantum-enhanced AES
  - `_encrypt_post_quantum()` - Post-quantum algorithms
  - `_encrypt_classical()` - Standard AES-256

#### `message_cipher.py`
- **Purpose:** High-level message encryption interface
- **Classes:** `MessageCipher`
- **Methods:**
  - `encrypt_message()` - Encrypts email message
  - `decrypt_message()` - Decrypts email message
  - Handles key requests from QKD
  - Manages encryption packages

### 3.2 QKD Client Layer

**Location:** `qmail/km_client/`

#### `qkd_client.py`
- **Purpose:** Interface to real Quantum Key Manager
- **Classes:** `QKDClient`, `QKDKey`
- **Methods:**
  - `get_key()` - Request quantum keys
  - `get_key_by_id()` - Retrieve specific key
  - `get_status()` - Check KM status
  - `close_key()` - Delete used keys

#### `mock_km.py`
- **Purpose:** Simulates QKD for development
- **Classes:** `MockQKDClient`
- **Features:**
  - Generates cryptographically secure random keys
  - Persistent storage (survives restarts)
  - Compatible with real QKD interface
  - JSON key storage

### 3.3 Email Handlers

**Location:** `qmail/email_handler/`

#### `email_manager.py`
- **Purpose:** High-level email operations
- **Methods:**
  - `send_encrypted_email()` - Send encrypted email
  - `fetch_and_decrypt_emails()` - Receive and decrypt

#### `smtp_handler.py`
- **Purpose:** Sends emails via SMTP
- **Methods:**
  - `send_email()` - Standard SMTP send
  - `send_encrypted_email()` - Send with encryption metadata

#### `imap_handler.py`
- **Purpose:** Receives emails via IMAP
- **Methods:**
  - `fetch_emails()` - Get emails from server
  - `_extract_attachments()` - Parse email attachments

#### `attachment_handler.py`
- **Purpose:** Encrypts/decrypts file attachments
- **Classes:** `AttachmentHandler`, `EncryptedAttachment`
- **Methods:**
  - `encrypt_file()` - Encrypt file from disk
  - `encrypt_attachment()` - Encrypt file content
  - `decrypt_attachment()` - Decrypt attachment

### 3.4 Web Layer

**Location:** `qmail/core/routes/`

#### `email_routes.py`
- **Purpose:** Flask routes for email operations
- **Routes:**
  - `/email/compose` - Compose and send emails
  - `/email/inbox` - View inbox
  - `/email/view/<id>` - View email details
  - `/email/sync` - Sync from IMAP
  - `/email/attachment/<id>/download` - Download attachment

### 3.5 Database Models

**Location:** `qmail/models/`

#### `database.py`
- **Models:**
  - `User` - User accounts
  - `Email` - Email messages
  - `EmailAttachment` - File attachments
  - `Contact` - Address book
  - `KeyUsageLog` - Track key usage
  - `Settings` - User settings

---

## 4. Encryption Flow

### 4.1 Sending Encrypted Email

```
User Composes Email
        │
        ▼
┌───────────────────┐
│  email_routes.py  │ - Receives form data
│  /compose (POST)  │ - Validates input
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│ EmailManager      │ - Coordinates encryption
│ send_encrypted_   │ - Calls MessageCipher
│ email()           │
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│ MessageCipher     │ - Requests quantum key
│ encrypt_message() │ - Encrypts message body
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│ QKDClient         │ - Requests key from KM
│ get_key()         │ - Returns QKDKey object
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│ Key Manager (KM)  │ - Generates quantum key
│                   │ - Returns key + key_id
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│ EncryptionEngine  │ - Encrypts with algorithm
│ encrypt()         │ - Returns ciphertext
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│ SMTPHandler       │ - Adds encryption headers
│ send_encrypted_   │ - Sends via SMTP
│ email()           │
└─────────┬─────────┘
          │
          ▼
    Email Sent! ✉️
```

### 4.2 Receiving Encrypted Email

```
Email Arrives in Inbox
        │
        ▼
┌───────────────────┐
│ IMAPHandler       │ - Fetches from IMAP
│ fetch_emails()    │ - Parses MIME message
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│ email_routes.py   │ - Saves to database
│ /sync             │ - Detects encryption
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│ User Views Email  │ - Clicks on email
│ /view/<id>        │
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│ MessageCipher     │ - Extracts key_id
│ decrypt_message() │ - Requests key
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│ QKDClient         │ - Retrieves key by ID
│ get_key_by_id()   │
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│ Key Manager (KM)  │ - Returns stored key
│                   │
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│ EncryptionEngine  │ - Decrypts ciphertext
│ decrypt()         │ - Returns plaintext
└─────────┬─────────┘
          │
          ▼
    Message Displayed! 📖
```

---

## 5. Security Levels

QMail supports 4 security levels, each with different properties:

| Level | Name | Algorithm | Key Size | Use Case |
|-------|------|-----------|----------|----------|
| **1** | QUANTUM_OTP | One-Time Pad | Variable (= plaintext size) | Perfect secrecy, short messages |
| **2** | QUANTUM_AES | AES-256-CBC with quantum key | 256 bits (32 bytes) | **Recommended**, fast, any size |
| **3** | POST_QUANTUM | CRYSTALS-Kyber + AES | 256 bits | Future-proof, quantum-resistant |
| **4** | CLASSICAL | AES-256-GCM | 256 bits | Testing, standard encryption |

### Security Level Details

#### Level 1: QUANTUM_OTP
```python
SecurityLevel.QUANTUM_OTP = 1

Properties:
- Perfect theoretical security
- Key must be ≥ message size
- XOR operation: ciphertext = plaintext ⊕ key
- Key used only once
- Best for: Very sensitive, short messages

Limitations:
- Large key requirement
- Not practical for large files
```

#### Level 2: QUANTUM_AES (Recommended)
```python
SecurityLevel.QUANTUM_AES = 2

Properties:
- Fast encryption/decryption
- Fixed 256-bit key size
- AES-256-CBC mode
- Quantum-generated key
- Best for: All use cases, attachments

Advantages:
- Works with any file size
- High performance
- Quantum-enhanced security
```

#### Level 3: POST_QUANTUM
```python
SecurityLevel.POST_QUANTUM = 3

Properties:
- Resistant to quantum computer attacks
- CRYSTALS-Kyber key encapsulation
- AES-256-GCM encryption
- Future-proof
- Best for: Long-term security

Features:
- Protects against future quantum computers
- Hybrid approach
```

#### Level 4: CLASSICAL
```python
SecurityLevel.CLASSICAL = 4

Properties:
- Standard AES-256-GCM
- No quantum components
- Fast and reliable
- Best for: Testing, non-sensitive data

Use Cases:
- Development testing
- Compatibility testing
- Non-sensitive emails
```

---

## 6. Directory Structure

```
qmail/
├── crypto/                      # Encryption implementation
│   ├── __init__.py
│   ├── encryption_engine.py    # Core encryption algorithms
│   └── message_cipher.py       # High-level message encryption
│
├── km_client/                   # Quantum Key Manager clients
│   ├── __init__.py
│   ├── qkd_client.py           # Real QKD client interface
│   └── mock_km.py              # Mock QKD for development
│
├── email_handler/               # Email processing
│   ├── __init__.py
│   ├── email_manager.py        # High-level email operations
│   ├── smtp_handler.py         # SMTP sending
│   ├── imap_handler.py         # IMAP receiving
│   └── attachment_handler.py   # File encryption
│
├── models/                      # Database models
│   ├── __init__.py
│   └── database.py             # SQLAlchemy models
│
├── core/                        # Application core
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── email_routes.py    # Email web routes
│   │   └── auth_routes.py     # Authentication routes
│   └── init_db.py              # Database initialization
│
├── templates/                   # HTML templates
│   ├── base.html
│   ├── email/
│   │   ├── compose.html       # Compose form
│   │   ├── inbox.html         # Inbox list
│   │   └── view.html          # Email view
│   └── auth/
│       ├── login.html
│       └── register.html
│
└── static/                      # CSS, JS, images
    ├── css/
    │   └── style.css
    └── js/
        └── main.js

instance/                        # Instance-specific data
├── qmail.db                    # SQLite database
└── mock_qkd_keys.json          # Persistent key storage
```

---

## 7. Key Concepts

### 7.1 Quantum Key Distribution (QKD)

**What is it?**
- Uses quantum mechanics to generate and distribute encryption keys
- Any eavesdropping attempt disturbs quantum states (detectable)
- Provides information-theoretic security

**In QMail:**
- Mock QKD: Uses cryptographically secure random number generator
- Real QKD: Connects to actual quantum hardware via HTTP API
- Keys stored with unique IDs
- Keys can be retrieved for decryption

### 7.2 Encryption Package

Every encrypted message creates a package:

```python
encrypted_package = {
    'ciphertext': 'base64_encoded_encrypted_data',
    'key_id': 'MOCK-KEY-00000123-20251012195640',
    'security_level': 2,
    'security_level_name': 'QUANTUM_AES',
    'metadata': {
        'algorithm': 'AES-256-CBC',
        'iv': 'initialization_vector',
        'timestamp': '2025-10-12T19:56:40'
    }
}
```

### 7.3 Key Management

**Key Lifecycle:**
```
Generate → Store → Use → Retrieve → (Optional) Delete
```

**Key Storage:**
- Real QKD: Stored in quantum hardware Key Manager
- Mock QKD: Stored in `instance/mock_qkd_keys.json`
- Keys persist across application restarts
- Keys indexed by unique `key_id`

### 7.4 Email Headers

QMail adds custom headers to encrypted emails:

```
X-QKD-Encrypted: true
X-QKD-KeyID: MOCK-KEY-00000123-20251012195640
X-QKD-Security-Level: 2
X-QKD-Security-Level-Name: QUANTUM_AES
X-QKD-Has-Attachments: true
X-QKD-Attachment-Count: 2
```

These headers help QMail:
- Detect encrypted emails during IMAP sync
- Extract key IDs for decryption
- Show security level in UI
- Handle attachments correctly

---

## 8. Data Flow Summary

### Encryption Data Flow
```
Plaintext → Base64 Encode → Encrypt with Quantum Key → Base64 Encode → Store/Send
```

### Decryption Data Flow
```
Stored/Received → Base64 Decode → Decrypt with Quantum Key → Base64 Decode → Plaintext
```

### Attachment Data Flow
```
File → Read Bytes → Base64 Encode → Encrypt → JSON Package → MIME Attachment → Send
```

---

## 9. Configuration

### Environment Variables

```env
# QKD Configuration
QKD_USE_MOCK=true                    # Use Mock QKD (true) or Real QKD (false)
QKD_KM_HOST=localhost                # Key Manager hostname
QKD_KM_PORT=8080                     # Key Manager port

# Email Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
IMAP_SERVER=imap.gmail.com
IMAP_PORT=993

# Security
DEFAULT_SECURITY_LEVEL=2             # Default to QUANTUM_AES
MAX_ATTACHMENT_SIZE=25               # MB
```

---

## 10. Next Steps

Continue reading:
- **Part 2:** [Encryption Algorithms Details](02_ENCRYPTION_ALGORITHMS.md)
- **Part 3:** [Key Management System](03_KEY_MANAGEMENT.md)
- **Part 4:** [Message Encryption Flow](04_MESSAGE_ENCRYPTION.md)
- **Part 5:** [Attachment Encryption](05_ATTACHMENT_ENCRYPTION.md)
- **Part 6:** [Code Reference](06_CODE_REFERENCE.md)

---

**Document:** Part 1 of 6  
**Last Updated:** October 12, 2025  
**Author:** QMail Development Team
