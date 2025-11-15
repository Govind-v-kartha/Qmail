# QMail API Documentation

## Overview

Comprehensive API documentation for the QMail quantum-secure email client.

---

## Table of Contents

- [Encryption API](#encryption-api)
- [Email Handler API](#email-handler-api)
- [Quantum Key Manager API](#quantum-key-manager-api)
- [Database Models](#database-models)
- [Usage Examples](#usage-examples)

---

## Encryption API

**Module**: `qmail.crypto.encryption`

### encrypt_message()

```python
def encrypt_message(message: str, key_id: str, security_level: int, recipient: str) -> bytes:
    """Encrypt email message with quantum security."""
```

### decrypt_message()

```python
def decrypt_message(encrypted_data: bytes, key_id: str, security_level: int) -> str:
    """Decrypt encrypted message."""
```

---

## Email Handler API

**Module**: `qmail.email_handler`

### SMTPHandler

```python
class SMTPHandler:
    def send_email(self, from_addr: str, to_addr: str, subject: str, body: bytes) -> bool:
        """Send encrypted email via SMTP."""
```

### IMAPHandler

```python
class IMAPHandler:
    def fetch_emails(self, username: str, password: str, folder: str = "INBOX") -> List[Email]:
        """Fetch emails from IMAP server."""
```

---

## Quantum Key Manager API

**Module**: `qmail.km_client`

### KMClient

```python
class KMClient:
    def get_key(self, number: int = 1, size: int = 256) -> Dict[str, Any]:
        """
        Request quantum keys from Key Manager (ETSI GS QKD 014).
        
        Returns:
            Dictionary with keys array containing key_ID and key material
        """
```

---

## Database Models

**Module**: `qmail.models`

### User

```python
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
```

### Email

```python
class Email(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender = db.Column(db.String(120), nullable=False)
    recipient = db.Column(db.String(120), nullable=False)
    encrypted_body = db.Column(db.LargeBinary)
    key_id = db.Column(db.String(100))
    security_level = db.Column(db.Integer)
```

### Draft

```python
class Draft(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    recipient = db.Column(db.String(120))
    subject = db.Column(db.String(200))
    body = db.Column(db.Text)
    security_level = db.Column(db.Integer, default=2)
```

---

## Usage Examples

### Send Encrypted Email

```python
from qmail.crypto.encryption import encrypt_message
from qmail.km_client import KMClient
from qmail.email_handler import SMTPHandler

# Get quantum key
km = KMClient("localhost", 8080, "sae1", "sae2")
key_response = km.get_key()
key_id = key_response['keys'][0]['key_ID']

# Encrypt message
encrypted = encrypt_message("Hello", key_id, 2, "user@example.com")

# Send email
smtp = SMTPHandler("smtp.gmail.com", 587)
smtp.send_email("sender@example.com", "user@example.com", "Subject", encrypted)
```

### Receive and Decrypt Email

```python
from qmail.email_handler import IMAPHandler
from qmail.crypto.encryption import decrypt_message

# Fetch emails
imap = IMAPHandler("imap.gmail.com", 993)
emails = imap.fetch_emails("user@example.com", "password")

# Decrypt
email = emails[0]
plaintext = decrypt_message(email.body, email.key_id, email.security_level)
```

---

## Error Handling

```python
class QMailError(Exception):
    """Base exception"""

class EncryptionError(QMailError):
    """Encryption failed"""

class DecryptionError(QMailError):
    """Decryption failed"""

class KeyNotFoundError(QMailError):
    """Key not found"""
```

---

## Rate Limiting

- **Authentication**: 5 requests/minute
- **Email sending**: 20 emails/hour  
- **Key requests**: 100 keys/hour
- **Email fetching**: 60 requests/minute


Step 1: Files to Delete
Delete these development/debug markdown files from the root directory:

AUTHENTICATION_SECURITY_COMPLETE.md
AUTH_SECURITY_IMPLEMENTED.md
AUTO_HIDE_REMOVED.md
BUTTONS_FIXED.md
CSRF_COMPOSE_FIX.md
CSRF_FIX_APPLIED.md
CSRF_ISSUES_FIXED.md
DARK_MODE_FIXED.md
DEBUG_DARK_MODE.md
DOCUMENTATION_INDEX.md
EMAIL_ACTIONS_COMPLETE.md
EMAIL_CATEGORIES_SETUP.md
GMAIL_SIDEBAR_LAYOUT.md
NEW_FEATURES_ADDED.md
OWASP_SECURITY_AUDIT.md
QMAIL_USER_GUIDE.md
SECURITY_ARCHITECTURE.md
SECURITY_FEATURES.md
SECURITY_FIXES_APPLIED.md
SECURITY_IMPLEMENTATION_SUMMARY.md
SECURITY_SETUP.md
SETUP_COMPLETE.md
SYNC_ERROR_FIXED.md
TRASH_SQLALCHEMY_ERROR_FIXED.md
TROUBLESHOOTING_SQL_ERRORS.md
UNIQUE_QMAIL_DESIGN.md
Keep these in the docs/ folder - they contain valuable technical documentation.

Now let me create the new professional documentation files:

Remove all unnecessary development/debug markdown files

2
Create comprehensive README.md with proper badges and structure

4 more
Proposed edit
README.md
+311
-115
# QMail - Quantum-Secure Email Client
A quantum-secure email client that integrates Quantum Key Distribution (QKD) with existing email protocols to provide next-generation security.
## 🚀 Quick Start
<div align="center">
# 🔐 QMail - Quantum-Secure Email Client
[![Python Version](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/flask-3.0.0-green.svg)](https://flask.palletsprojects.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
**A next-generation email client leveraging Quantum Key Distribution (QKD) for unconditionally secure communication**
[Features](#-features) • [Installation](#-installation) • [Usage](#-usage) • [Documentation](#-documentation) • [Security](#-security-levels) • [Contributing](#-contributing)
</div>
---
## 📖 Overview
**QMail** is an advanced email client that combines **Quantum Key Distribution (QKD)** with traditional email protocols (SMTP, IMAP, POP3) to deliver quantum-secure communication over existing email infrastructure like Gmail, Yahoo Mail, and Outlook.
Unlike conventional encryption that relies on computational hardness, QMail leverages the laws of quantum mechanics to provide **unconditional security** against both classical and quantum computing threats.
### Why QMail?
- **🔒 Quantum-Secure**: Protection against future quantum computer attacks
- **🔄 Backward Compatible**: Works with existing email infrastructure
- **⚡ Multi-Level Security**: Choose from 4 encryption levels based on your needs
- **🎯 User-Friendly**: Intuitive interface for seamless secure communication
- **🛡️ Future-Proof**: Built on ETSI GS QKD 014 standards
---
## ✨ Features
### Core Capabilities
- **Quantum Key Distribution Integration**: Communicates with Key Manager using ETSI GS QKD 014 REST API
- **Multiple Security Levels**: From quantum one-time pads to classical encryption
- **Email Protocol Support**: Full SMTP, IMAP, and POP3 compatibility
- **Application-Layer Encryption**: Messages encrypted before transmission
- **Attachment Support**: Secure file attachments with quantum encryption
- **Draft Management**: Save and edit encrypted drafts
- **Spam Detection**: Built-in spam filtering and categorization

## Support

- **Documentation**: [GitHub Wiki](https://github.com/yourusername/Qmail/wiki)
- **Issues**: [GitHub Issues](https://github.com/yourusername/Qmail/issues)
- **Email**: api-support@qmail-project.example.com

---

*Last Updated: November 2024 | Version 1.0.0*