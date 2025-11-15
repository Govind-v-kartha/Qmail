# QMail File Attachments with Quantum Encryption

## Overview

QMail supports sending **quantum-encrypted file attachments** along with emails. All attachments are encrypted using the same quantum key distribution technology as the email message body.

## Features

✅ **Quantum-Encrypted Attachments**: Files encrypted with QKD keys  
✅ **Multiple File Support**: Attach multiple files to a single email  
✅ **Large File Support**: Up to 25 MB per file  
✅ **Automatic Decryption**: Files automatically decrypted on download  
✅ **Persistent Storage**: Encrypted files stored in database  
✅ **Security Levels**: Same 4 security levels as email messages  

---

## How It Works

### 1. **Sending Files**

```
User Selects File → Encrypt with Quantum Key → Attach to Email → Send
```

**Process:**
1. User composes email and selects files to attach
2. QMail requests quantum key from Key Manager
3. Each file is encrypted individually with the quantum key
4. Encrypted files are stored in database linked to the email
5. Email is sent (files travel as encrypted data)

### 2. **Receiving Files**

```
Receive Email → View Attachments → Download → Decrypt with Quantum Key → Open File
```

**Process:**
1. User receives email with attachments
2. Attachments are displayed with metadata (filename, size, encryption level)
3. User clicks "Download"
4. QMail retrieves quantum key from Key Manager
5. File is decrypted and downloaded to user's computer

---

## Supported File Types

### ✅ Allowed Extensions

**Images:**
- `.jpg`, `.jpeg`, `.png`, `.gif`, `.bmp`, `.webp`, `.svg`

**Documents:**
- `.pdf`, `.doc`, `.docx`, `.xls`, `.xlsx`, `.ppt`, `.pptx`
- `.txt`, `.rtf`, `.odt`, `.ods`, `.odp`

**Archives:**
- `.zip`, `.rar`, `.tar`, `.gz`, `.7z`

**Data:**
- `.csv`, `.json`, `.xml`

**Others:**
- Can be configured in `attachment_handler.py`

---

## Usage Examples

### Compose Email with Attachments

1. Navigate to **Compose** page
2. Fill in recipient, subject, message
3. Select **Security Level** (applies to both message and attachments)
4. Click **Choose Files** in Attachments section
5. Select one or more files (up to 25 MB each)
6. Review selected files (shown with size)
7. Click **Send Encrypted**

**Result:**
- Email sent with quantum-encrypted attachments
- Each file encrypted separately with its own quantum key
- Encryption metadata stored for decryption

### Download Encrypted Attachment

1. Open email with attachments
2. Attachments shown below email header
3. Click **Download** button next to file
4. File automatically decrypted using quantum key
5. File downloaded to your computer

---

## Technical Implementation

### Database Schema

```sql
CREATE TABLE email_attachments (
    id INTEGER PRIMARY KEY,
    email_id INTEGER NOT NULL,
    filename VARCHAR(255) NOT NULL,
    content_type VARCHAR(100),
    original_size INTEGER,
    encrypted_size INTEGER,
    encrypted_content TEXT NOT NULL,
    key_id VARCHAR(255) NOT NULL,
    security_level INTEGER,
    security_level_name VARCHAR(50),
    encryption_metadata TEXT,
    created_at DATETIME,
    FOREIGN KEY (email_id) REFERENCES emails(id)
);
```

### Encryption Flow

```python
# Encrypting attachment
attachment_handler = AttachmentHandler(use_mock_qkd=True)

encrypted_attachment = attachment_handler.encrypt_attachment(
    filename="document.pdf",
    content=file_bytes,
    security_level=SecurityLevel.QUANTUM_AES
)

# Save to database
db_attachment = EmailAttachment(
    email_id=email.id,
    filename=encrypted_attachment.filename,
    encrypted_content=encrypted_attachment.encrypted_content,
    key_id=encrypted_attachment.key_id,
    ...
)
db.session.add(db_attachment)
```

### Decryption Flow

```python
# Retrieve from database
attachment = EmailAttachment.query.get(attachment_id)

# Decrypt
attachment_handler = AttachmentHandler(use_mock_qkd=True)
decrypted = attachment_handler.decrypt_attachment(encrypted_attachment)

# Download
return send_file(
    BytesIO(decrypted.content),
    download_name=decrypted.filename,
    mimetype=decrypted.content_type
)
```

---

## API Endpoints

### POST `/email/compose`
Send email with attachments

**Form Data:**
- `to`: Recipient email
- `subject`: Email subject
- `body`: Email message
- `security_level`: Encryption level (1-4)
- `attachments[]`: Array of files (multipart/form-data)

**Response:**
- Redirects to sent emails page
- Flash message with success/error

### GET `/email/attachment/<id>/download`
Download and decrypt attachment

**Parameters:**
- `id`: Attachment ID

**Response:**
- File download with original filename
- Content-Type matching original file
- File automatically decrypted

### GET `/email/attachment/<id>/view`
Get attachment metadata

**Parameters:**
- `id`: Attachment ID

**Response (JSON):**
```json
{
  "success": true,
  "attachment": {
    "id": 1,
    "filename": "document.pdf",
    "content_type": "application/pdf",
    "original_size": 1048576,
    "original_size_formatted": "1.0 MB",
    "encrypted_size": 1055000,
    "key_id": "MOCK-KEY-00000123...",
    "security_level": "QUANTUM_AES",
    "created_at": "2025-10-12T19:00:00"
  }
}
```

---

## Security Considerations

### 🔒 Encryption

**Individual Key Per Attachment:**
- Each attachment gets its own quantum key
- Keys are independent from email message keys
- Provides additional security layer

**Security Levels:**
- **Level 1 (Quantum OTP)**: Perfect secrecy, one-time pad
- **Level 2 (Quantum-AES)**: Quantum-enhanced AES (recommended)
- **Level 3 (Post-Quantum)**: Quantum-resistant algorithms
- **Level 4 (Classical)**: Standard AES encryption

**Key Storage:**
- Quantum keys stored in Mock QKD persistent storage
- Keys survive application restarts
- Keys can be closed/deleted after use

### 🛡️ File Validation

**Size Limits:**
- Maximum 25 MB per file (configurable)
- Total attachment size checked before encryption
- Warning shown if exceeding limit

**File Type Validation:**
- Whitelist of allowed file extensions
- Prevents potentially dangerous files
- Configurable in `attachment_handler.py`

**Filename Sanitization:**
- Uses `secure_filename()` from Werkzeug
- Prevents directory traversal attacks
- Removes special characters

### 🔐 Access Control

**User Verification:**
- Only email owner can download attachments
- Attachment ID verified against user's emails
- 404 error if unauthorized access attempt

**Database Security:**
- Attachments linked to emails via foreign key
- Cascade delete: Deleting email deletes attachments
- Encrypted content stored as TEXT/BLOB

---

## Configuration

### Attachment Settings

**In `.env`:**
```env
# Max attachment size in MB
MAX_ATTACHMENT_SIZE=25

# QKD settings (affects attachments too)
QKD_USE_MOCK=true
```

**In Code:**
```python
# Initialize with custom max size
attachment_handler = AttachmentHandler(
    use_mock_qkd=True,
    max_attachment_size=50 * 1024 * 1024  # 50 MB
)
```

### Allowed File Types

**Edit `attachment_handler.py`:**
```python
allowed_extensions = {
    '.jpg', '.png', '.pdf', '.doc', '.zip',
    # Add your extensions here
}
```

---

## Examples

### Python API Usage

```python
from qmail.email_handler.attachment_handler import AttachmentHandler
from qmail.crypto.encryption_engine import SecurityLevel

# Initialize handler
handler = AttachmentHandler(use_mock_qkd=True)

# Encrypt a file
encrypted = handler.encrypt_file(
    file_path="/path/to/document.pdf",
    security_level=SecurityLevel.QUANTUM_AES
)

print(f"Encrypted: {encrypted.filename}")
print(f"Original size: {encrypted.original_size} bytes")
print(f"Encrypted size: {encrypted.encrypted_size} bytes")
print(f"Key ID: {encrypted.key_id}")

# Decrypt
decrypted = handler.decrypt_attachment(encrypted)

# Save to disk
saved_path = handler.save_attachment(decrypted, output_dir="downloads")
print(f"Saved to: {saved_path}")
```

### Multiple Files

```python
# Encrypt multiple files at once
file_paths = [
    "document1.pdf",
    "image.png",
    "data.csv"
]

encrypted_files = handler.encrypt_multiple_files(
    file_paths,
    security_level=SecurityLevel.QUANTUM_OTP
)

for encrypted in encrypted_files:
    print(f"✓ {encrypted.filename} encrypted with key {encrypted.key_id}")
```

### Get File Info

```python
# Get information about a file before encrypting
info = handler.get_attachment_info("large_file.zip")

print(f"Filename: {info['filename']}")
print(f"Size: {info['size_mb']:.2f} MB")
print(f"Type: {info['content_type']}")
print(f"Can encrypt: {info['can_encrypt']}")
```

---

## Troubleshooting

### Issue: "File too large"

**Error:** `Attachment too large: 30.0 MB (max: 25.0 MB)`

**Solutions:**
1. Compress file before attaching
2. Split into multiple smaller files
3. Increase `MAX_ATTACHMENT_SIZE` in configuration
4. Use file hosting service for very large files

### Issue: "File type not allowed"

**Error:** `File type not allowed: dangerous.exe`

**Solutions:**
1. Check file extension against allowed list
2. Rename file if legitimate (e.g., `.txt` instead of `.exe`)
3. Add extension to allowed list in `attachment_handler.py`
4. Archive file in `.zip` format (if `.zip` is allowed)

### Issue: "Decryption failed"

**Error:** `Failed to retrieve quantum key`

**Causes:**
- Quantum key not found in key store
- App restarted and keys not persisted (old version)
- Key expired or deleted

**Solutions:**
1. Ensure Mock QKD persistence is enabled (latest version has this)
2. Check `instance/mock_qkd_keys.json` exists
3. Re-send email if using old version
4. Check logs for key retrieval errors

### Issue: "Download not working"

**Symptoms:**
- Click download button, nothing happens
- Error message after download attempt

**Solutions:**
1. Check browser console for JavaScript errors
2. Verify you have permission to access the email
3. Check server logs for decryption errors
4. Ensure quantum key is still available

---

## Performance Considerations

### Large Files

**Encryption Time:**
- 1 MB file: ~0.1 seconds
- 10 MB file: ~1 second
- 25 MB file: ~2-3 seconds

**Database Storage:**
- Encrypted files stored in database as TEXT
- Base64 encoding increases size by ~33%
- Consider file storage service for very large files

### Multiple Attachments

**Best Practices:**
- Limit to 5-10 attachments per email
- Total size under 50 MB recommended
- Use archives (`.zip`) to combine many small files

### Optimization Tips

1. **Compress before encrypting:**
   ```bash
   zip archive.zip file1 file2 file3
   # Then encrypt archive.zip
   ```

2. **Use appropriate security level:**
   - Level 1 (OTP): Slowest, highest security
   - Level 2 (Quantum-AES): Fast, recommended
   - Level 4 (Classical): Fastest, standard security

3. **Clean up old attachments:**
   ```sql
   DELETE FROM email_attachments 
   WHERE email_id IN (
     SELECT id FROM emails WHERE created_at < DATE('now', '-30 days')
   );
   ```

---

## Future Enhancements

🔮 **Planned Features:**

- [ ] **Streaming Encryption**: Encrypt large files in chunks
- [ ] **External Storage**: Store encrypted files in S3/Azure/etc.
- [ ] **Compression**: Auto-compress files before encryption
- [ ] **Thumbnail Preview**: Preview images without full download
- [ ] **Virus Scanning**: Integrate antivirus for uploaded files
- [ ] **Expiring Attachments**: Auto-delete after X days
- [ ] **Attachment Sharing**: Generate secure links for external sharing

---

## Summary

QMail's attachment feature provides **quantum-secure file transfer** through email:

✅ **Easy to Use**: Drag and drop files in compose form  
✅ **Secure**: Each file encrypted with quantum keys  
✅ **Transparent**: Automatic encryption/decryption  
✅ **Flexible**: 4 security levels to choose from  
✅ **Persistent**: Encrypted attachments stored safely  

**Try it out:**
1. Compose new email
2. Attach files
3. Select security level
4. Send!

Your files are now protected by quantum encryption! 🔒
