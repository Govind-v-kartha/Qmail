# Receiving Encrypted Attachments - How It Works

## 📧 What the Receiver Sees

When you send an email with quantum-encrypted attachments through QMail, here's what the receiver experiences:

### In Any Email Client (Gmail, Outlook, etc.)

**Email Subject:**
```
[QMail Encrypted] Your Subject (2 attachments)
```

**Email Body:**
```
This is a quantum-encrypted email sent via QMail.

To read this message, you need QMail client with access to the same Quantum Key Manager.

Key ID: MOCK-KEY-00000123-20251012...
Security Level: QUANTUM_AES

Encrypted Attachments: 2
  - document.pdf (QUANTUM_AES encryption)
  - image.png (QUANTUM_AES encryption)

Encrypted content follows:

{
  "ciphertext": "encrypted_message_here...",
  "key_id": "MOCK-KEY-00000123...",
  ...
}
```

**Attachments:**
```
📎 document.pdf.qmail_enc (JSON file with encrypted content)
📎 image.png.qmail_enc (JSON file with encrypted content)
```

---

## 🔐 How Attachments Are Sent

### 1. **Sender Side (Encryption)**

```
User Uploads File → Encrypt with Quantum Key → Package as JSON → Attach to Email → Send
```

**What happens:**
- File content encrypted with quantum key
- Encrypted data + metadata packaged as JSON
- JSON saved as `.qmail_enc` file
- Attached to email as MIME attachment

**Example `.qmail_enc` file:**
```json
{
  "filename": "document.pdf",
  "encrypted_content": "base64_encrypted_data_here...",
  "key_id": "MOCK-KEY-00000123-20251012195640",
  "security_level": 2,
  "security_level_name": "QUANTUM_AES",
  "content_type": "application/pdf",
  "original_size": 1048576,
  "metadata": {
    "algorithm": "AES-256-CBC",
    "iv": "...",
    ...
  }
}
```

### 2. **Receiver Side (Decryption)**

**Option A: Using QMail Client**

```
Receive Email → QMail Detects .qmail_enc → Parse JSON → Retrieve Quantum Key → Decrypt → Download Original File
```

**Steps:**
1. Receiver opens email in QMail
2. QMail detects `X-QKD-Has-Attachments: true` header
3. Parses `.qmail_enc` attachments
4. Extracts `key_id` from each attachment
5. Requests quantum key from Key Manager
6. Decrypts file content
7. Shows as downloadable file with original name

**Option B: Using Regular Email Client (Gmail/Outlook)**

```
Receive Email → See .qmail_enc Files → Download → Open in QMail Manually
```

**Steps:**
1. Download `.qmail_enc` file from email
2. Open QMail application
3. Use "Decrypt File" feature (upload `.qmail_enc`)
4. QMail decrypts and saves original file

---

## 🎯 Decryption Process

### Automatic Decryption (QMail Inbox)

When receiver views email in QMail:

```python
# QMail automatically:
1. Detects encrypted attachments via headers
2. Downloads .qmail_enc files
3. Parses JSON structure
4. Retrieves quantum keys using key_id
5. Decrypts each file
6. Displays as normal attachments
```

**UI Display:**
```
📎 Attachments (2)
┌────────────────────────────────────────────┐
│ 📄 document.pdf                            │
│    Size: 1.0 MB                            │
│    🔒 QUANTUM_AES encryption               │
│    [Download] button                       │
└────────────────────────────────────────────┘
┌────────────────────────────────────────────┐
│ 🖼️ image.png                               │
│    Size: 500 KB                            │
│    🔒 QUANTUM_AES encryption               │
│    [Download] button                       │
└────────────────────────────────────────────┘
```

### Manual Decryption (Standalone Files)

If receiver downloads `.qmail_enc` files manually:

```python
from qmail.email_handler.attachment_handler import AttachmentHandler
import json

# Load encrypted file
with open('document.pdf.qmail_enc', 'r') as f:
    encrypted_data = json.load(f)

# Create EncryptedAttachment object
from qmail.email_handler.attachment_handler import EncryptedAttachment
encrypted_attachment = EncryptedAttachment(
    filename=encrypted_data['filename'],
    encrypted_content=encrypted_data['encrypted_content'],
    content_type=encrypted_data['content_type'],
    original_size=encrypted_data['original_size'],
    encrypted_size=len(encrypted_data['encrypted_content']),
    key_id=encrypted_data['key_id'],
    security_level=encrypted_data['security_level_name'],
    metadata=encrypted_data['metadata']
)

# Decrypt
handler = AttachmentHandler(use_mock_qkd=True)
decrypted = handler.decrypt_attachment(encrypted_attachment)

# Save original file
with open(decrypted.filename, 'wb') as f:
    f.write(decrypted.content)

print(f"Decrypted: {decrypted.filename}")
```

---

## 📋 Email Headers

QMail adds custom headers to indicate encrypted attachments:

```
X-QKD-Encrypted: true
X-QKD-KeyID: MOCK-KEY-00000123-20251012195640
X-QKD-Security-Level: 2
X-QKD-Security-Level-Name: QUANTUM_AES
X-QKD-Has-Attachments: true
X-QKD-Attachment-Count: 2
```

These headers help QMail automatically detect and process encrypted content.

---

## 🔄 Complete Flow

### Sender → Receiver

```
┌─────────────┐                                ┌─────────────┐
│   Sender    │                                │  Receiver   │
│   (Alice)   │                                │    (Bob)    │
└──────┬──────┘                                └──────┬──────┘
       │                                               │
       │ 1. Attach file.pdf                          │
       ├──────────────────────────────────────────────►
       │                                               │
       │ 2. Request Quantum Key                       │
       ├─────────► QKD Key Manager                    │
       │             ↓                                 │
       │          Generate Key                         │
       │          MOCK-KEY-123                         │
       │             ↓                                 │
       │ 3. Encrypt file.pdf with key                 │
       │                                               │
       │ 4. Package as file.pdf.qmail_enc             │
       │                                               │
       │ 5. Send email via SMTP                       │
       │    ├─ Subject: [QMail Encrypted] ...         │
       │    ├─ Body: Encrypted JSON                   │
       │    └─ Attachment: file.pdf.qmail_enc         │
       ├──────────────────────────────────────────────►
       │                                               │
       │                          6. Receive email     │
       │                          View in QMail        │
       │                                   ↓           │
       │                          7. Detect .qmail_enc │
       │                          Parse JSON           │
       │                          Extract key_id       │
       │                                   ↓           │
       │                          8. Request Key       │
       │       QKD Key Manager ◄───────────┤           │
       │             ↓                     │           │
       │       Retrieve Key                │           │
       │       MOCK-KEY-123                │           │
       │             ├──────────────────────►          │
       │                                   ↓           │
       │                          9. Decrypt file      │
       │                          Get original file.pdf│
       │                                   ↓           │
       │                          10. Download file.pdf│
       │◄──────────────────────────────────┤           │
```

---

## ✅ Verification

### Check If Attachments Are Sent

**1. Send test email with attachment:**
```bash
# In QMail web interface:
1. Compose new email
2. Attach a file (e.g., test.pdf)
3. Send to your own email address
```

**2. Check in regular email client (Gmail/Outlook):**
- You should see: `[QMail Encrypted] Your Subject (1 attachment)`
- You should see attachment: `test.pdf.qmail_enc`
- Download `.qmail_enc` file and verify it's valid JSON

**3. Check in QMail:**
- Open the received email in QMail
- Should show: "Attachments (1)"
- Should display: `test.pdf` (not `.qmail_enc`)
- Click Download → Should decrypt and download original file

---

## 🔧 Troubleshooting

### Issue: Receiver doesn't see attachments

**Possible causes:**
1. Email client blocking `.qmail_enc` files
2. Attachments too large (exceeded size limit)
3. SMTP server stripped attachments

**Solutions:**
- Check spam/junk folder
- Verify email headers (X-QKD-Has-Attachments should be true)
- Check SMTP server logs
- Try smaller file size

### Issue: Can't decrypt .qmail_enc file

**Causes:**
- Quantum key not found in Key Manager
- Key expired or deleted
- Wrong Key Manager configuration

**Solutions:**
1. Verify key exists:
   ```bash
   # Check if key is in storage
   cat instance/mock_qkd_keys.json
   ```

2. Check key ID matches:
   ```bash
   # Compare key_id in .qmail_enc with key store
   ```

3. Re-send email if key lost

### Issue: Attachments show as .qmail_enc in QMail

**Cause:**
- QMail not detecting encrypted format
- IMAP parser not recognizing headers

**Solution:**
- Check X-QKD headers present in email
- Update IMAP handler to parse .qmail_enc
- Manually decrypt using attachment handler

---

## 🎨 UI Improvements

### Show Encryption Status

In email view, attachments display:
```
📎 document.pdf
   Size: 1.0 MB
   🔒 QUANTUM_AES encryption
   🔑 Key: MOCK-KEY-00000123...
   [Download] [View Info]
```

### Download Progress

When downloading large files:
```
Downloading document.pdf...
├─ Retrieving quantum key... ✓
├─ Decrypting file... ▓▓▓▓▓▓▓░░░ 70%
└─ Saving to disk...
```

---

## 📝 Summary

**For Receivers:**

**Using QMail Client:**
✅ Automatic decryption  
✅ Shows original filenames  
✅ One-click download  
✅ Transparent experience  

**Using Regular Email Client:**
⚠️ Sees `.qmail_enc` files  
⚠️ Needs QMail to decrypt  
⚠️ Manual process  

**Best Practice:** Both sender and receiver should use QMail for seamless quantum-encrypted file transfer!

---

## 🔗 Related Documentation

- [ATTACHMENTS.md](ATTACHMENTS.md) - Complete attachment documentation
- [ATTACHMENT_QUICKSTART.md](../ATTACHMENT_QUICKSTART.md) - Quick start guide
- [TROUBLESHOOTING.md](../TROUBLESHOOTING.md) - General troubleshooting

**Last Updated:** October 12, 2025
