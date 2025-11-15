"""
Email Attachment Handler with Quantum Encryption
Handles file attachments with quantum-secure encryption
"""

import os
import mimetypes
import base64
import logging
from typing import List, Dict, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass

from qmail.crypto.message_cipher import MessageCipher
from qmail.crypto.encryption_engine import SecurityLevel

logger = logging.getLogger(__name__)


@dataclass
class Attachment:
    """Represents an email attachment"""
    filename: str
    content: bytes
    content_type: str
    size: int
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'filename': self.filename,
            'content': base64.b64encode(self.content).decode('utf-8'),
            'content_type': self.content_type,
            'size': self.size
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Attachment':
        """Create from dictionary"""
        return cls(
            filename=data['filename'],
            content=base64.b64decode(data['content']),
            content_type=data['content_type'],
            size=data['size']
        )


@dataclass
class EncryptedAttachment:
    """Represents an encrypted attachment"""
    filename: str
    encrypted_content: str  # Base64 encoded
    content_type: str
    original_size: int
    encrypted_size: int
    key_id: str
    security_level: str
    metadata: Dict


class AttachmentHandler:
    """
    Handles file attachments with quantum encryption
    """
    
    def __init__(
        self,
        use_mock_qkd: bool = True,
        max_attachment_size: int = 25 * 1024 * 1024  # 25 MB default
    ):
        """
        Initialize attachment handler
        
        Args:
            use_mock_qkd: Use mock QKD or real hardware
            max_attachment_size: Maximum attachment size in bytes
        """
        self.cipher = MessageCipher(use_mock_qkd=use_mock_qkd)
        self.max_attachment_size = max_attachment_size
        logger.info(f"Attachment handler initialized (max size: {max_attachment_size / 1024 / 1024:.1f} MB)")
    
    def encrypt_file(
        self,
        file_path: str,
        security_level: SecurityLevel = SecurityLevel.QUANTUM_AES
    ) -> EncryptedAttachment:
        """
        Encrypt a file with quantum encryption
        
        Args:
            file_path: Path to file to encrypt
            security_level: Quantum security level
        
        Returns:
            EncryptedAttachment object
        
        Raises:
            ValueError: If file is too large or doesn't exist
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise ValueError(f"File not found: {file_path}")
        
        file_size = file_path.stat().st_size
        if file_size > self.max_attachment_size:
            raise ValueError(
                f"File too large: {file_size / 1024 / 1024:.1f} MB "
                f"(max: {self.max_attachment_size / 1024 / 1024:.1f} MB)"
            )
        
        # Read file content
        with open(file_path, 'rb') as f:
            file_content = f.read()
        
        logger.info(f"Encrypting file: {file_path.name} ({file_size} bytes)")
        
        # Encrypt file content
        encrypted_package = self.cipher.encrypt_message(
            base64.b64encode(file_content).decode('utf-8'),
            security_level
        )
        
        # Determine content type
        content_type, _ = mimetypes.guess_type(str(file_path))
        if not content_type:
            content_type = 'application/octet-stream'
        
        encrypted_attachment = EncryptedAttachment(
            filename=file_path.name,
            encrypted_content=encrypted_package['ciphertext'],
            content_type=content_type,
            original_size=file_size,
            encrypted_size=len(encrypted_package['ciphertext']),
            key_id=encrypted_package['key_id'],
            security_level=encrypted_package['security_level_name'],
            metadata=encrypted_package['metadata']
        )
        
        logger.info(
            f"File encrypted: {file_path.name} "
            f"(key: {encrypted_attachment.key_id}, "
            f"level: {encrypted_attachment.security_level})"
        )
        
        return encrypted_attachment
    
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
        """
        file_size = len(content)
        
        if file_size > self.max_attachment_size:
            raise ValueError(
                f"Attachment too large: {file_size / 1024 / 1024:.1f} MB "
                f"(max: {self.max_attachment_size / 1024 / 1024:.1f} MB)"
            )
        
        logger.info(f"Encrypting attachment: {filename} ({file_size} bytes)")
        
        # Encrypt content (base64 encode first to handle binary data)
        encrypted_package = self.cipher.encrypt_message(
            base64.b64encode(content).decode('utf-8'),
            security_level
        )
        
        # Determine content type
        content_type, _ = mimetypes.guess_type(filename)
        if not content_type:
            content_type = 'application/octet-stream'
        
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
        """
        logger.info(f"Decrypting attachment: {encrypted_attachment.filename}")
        logger.debug(f"  Key ID: {encrypted_attachment.key_id}")
        logger.debug(f"  Security Level: {encrypted_attachment.security_level}")
        logger.debug(f"  Encrypted size: {encrypted_attachment.encrypted_size}")
        logger.debug(f"  Original size: {encrypted_attachment.original_size}")
        logger.debug(f"  Metadata: {encrypted_attachment.metadata}")
        
        try:
            # Reconstruct encrypted package
            encrypted_package = {
                'ciphertext': encrypted_attachment.encrypted_content,
                'key_id': encrypted_attachment.key_id,
                'security_level': SecurityLevel[encrypted_attachment.security_level].value,
                'security_level_name': encrypted_attachment.security_level,
                'metadata': encrypted_attachment.metadata
            }
            
            # Decrypt
            decrypted_b64 = self.cipher.decrypt_message(encrypted_package)
            
            # Decode from base64
            decrypted_content = base64.b64decode(decrypted_b64)
            
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
            logger.error(f"  Metadata: {encrypted_attachment.metadata}")
            raise
    
    def encrypt_multiple_files(
        self,
        file_paths: List[str],
        security_level: SecurityLevel = SecurityLevel.QUANTUM_AES
    ) -> List[EncryptedAttachment]:
        """
        Encrypt multiple files
        
        Args:
            file_paths: List of file paths to encrypt
            security_level: Quantum security level
        
        Returns:
            List of EncryptedAttachment objects
        """
        encrypted_attachments = []
        
        for file_path in file_paths:
            try:
                encrypted = self.encrypt_file(file_path, security_level)
                encrypted_attachments.append(encrypted)
            except Exception as e:
                logger.error(f"Failed to encrypt {file_path}: {e}")
                raise
        
        return encrypted_attachments
    
    def save_attachment(
        self,
        attachment: Attachment,
        output_dir: str = "downloads"
    ) -> str:
        """
        Save decrypted attachment to disk
        
        Args:
            attachment: Attachment object
            output_dir: Directory to save file
        
        Returns:
            Path to saved file
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Avoid filename conflicts
        filename = attachment.filename
        file_path = output_path / filename
        counter = 1
        while file_path.exists():
            name, ext = os.path.splitext(attachment.filename)
            filename = f"{name}_{counter}{ext}"
            file_path = output_path / filename
            counter += 1
        
        # Save file
        with open(file_path, 'wb') as f:
            f.write(attachment.content)
        
        logger.info(f"Attachment saved: {file_path}")
        
        return str(file_path)
    
    def get_attachment_info(self, file_path: str) -> Dict:
        """Get information about a file"""
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise ValueError(f"File not found: {file_path}")
        
        file_size = file_path.stat().st_size
        content_type, _ = mimetypes.guess_type(str(file_path))
        
        return {
            'filename': file_path.name,
            'size': file_size,
            'size_mb': file_size / 1024 / 1024,
            'content_type': content_type or 'application/octet-stream',
            'extension': file_path.suffix,
            'can_encrypt': file_size <= self.max_attachment_size
        }


def is_allowed_file(filename: str, allowed_extensions: Optional[set] = None) -> bool:
    """
    Check if file extension is allowed
    
    Args:
        filename: Name of the file
        allowed_extensions: Set of allowed extensions (with dots)
    
    Returns:
        True if allowed, False otherwise
    """
    if allowed_extensions is None:
        # Default allowed extensions
        allowed_extensions = {
            # Images
            '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg',
            # Documents
            '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
            '.txt', '.rtf', '.odt', '.ods', '.odp',
            # Archives
            '.zip', '.rar', '.tar', '.gz', '.7z',
            # Other
            '.csv', '.json', '.xml'
        }
    
    ext = Path(filename).suffix.lower()
    return ext in allowed_extensions


def format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"


def is_image_file(filename: str = None, content_type: str = None) -> bool:
    """
    Check if a file is an image based on filename or content type
    
    Args:
        filename: Name of the file (optional)
        content_type: MIME content type (optional)
    
    Returns:
        True if image, False otherwise
    """
    # Check by content type
    if content_type:
        return content_type.startswith('image/')
    
    # Check by extension
    if filename:
        image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg', '.ico', '.tiff', '.tif'}
        ext = Path(filename).suffix.lower()
        return ext in image_extensions
    
    return False
