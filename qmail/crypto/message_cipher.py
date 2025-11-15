"""
Message Cipher - High-level interface for email encryption
"""

import json
import base64
import logging
from typing import Tuple, Dict
from qmail.crypto.encryption_engine import EncryptionEngine, SecurityLevel
from qmail.km_client.mock_km import get_qkd_client
from qmail.km_client.qkd_client import QKDKey

logger = logging.getLogger(__name__)


class MessageCipher:
    """
    High-level interface for encrypting and decrypting email messages
    """
    
    def __init__(self, use_mock_qkd: bool = True):
        """
        Initialize message cipher
        
        Args:
            use_mock_qkd: Use mock QKD client (default: True for development)
        """
        self.qkd_client = get_qkd_client(use_mock=use_mock_qkd)
        self.encryption_engine = EncryptionEngine()
        logger.info("Message cipher initialized")
    
    def encrypt_message(
        self,
        message: str,
        security_level: SecurityLevel = SecurityLevel.QUANTUM_AES,
        recipient_id: str = None
    ) -> Dict:
        """
        Encrypt an email message
        
        Args:
            message: Plain text message to encrypt
            security_level: Security level to use
            recipient_id: Optional recipient identifier
        
        Returns:
            Dictionary containing encrypted message and metadata
        """
        try:
            # Convert message to bytes
            plaintext = message.encode('utf-8')
            
            # Determine required key size based on security level
            if security_level == SecurityLevel.QUANTUM_OTP:
                # OTP requires key size >= message size
                key_size = max(len(plaintext) * 8, 256)
            else:
                # Other levels can use standard key size
                key_size = 256
            
            # Request quantum key from KM
            logger.info(f"Requesting quantum key for encryption (level: {security_level.name})")
            keys = self.qkd_client.get_key(key_size=key_size, number_of_keys=1)
            
            if not keys:
                raise Exception("Failed to obtain quantum key")
            
            qkd_key = keys[0]
            logger.info(f"Obtained quantum key: {qkd_key.key_id}")
            
            # Encrypt message
            ciphertext, metadata = self.encryption_engine.encrypt(
                plaintext=plaintext,
                key=qkd_key.key,
                security_level=security_level
            )
            
            # Prepare encrypted message package
            encrypted_package = {
                'ciphertext': base64.b64encode(ciphertext).decode('utf-8'),
                'key_id': qkd_key.key_id,
                'security_level': security_level.value,
                'security_level_name': security_level.name,
                'metadata': metadata,
                'recipient_id': recipient_id
            }
            
            logger.info(f"Message encrypted successfully (key: {qkd_key.key_id})")
            return encrypted_package
            
        except Exception as e:
            logger.error(f"Encryption failed: {e}")
            raise
    
    def decrypt_message(self, encrypted_package: Dict) -> str:
        """
        Decrypt an encrypted email message
        
        Args:
            encrypted_package: Dictionary containing encrypted message and metadata
        
        Returns:
            Decrypted plain text message
        """
        try:
            # Extract encrypted data
            ciphertext = base64.b64decode(encrypted_package['ciphertext'])
            key_id = encrypted_package['key_id']
            metadata = encrypted_package['metadata']
            
            logger.info(f"Decrypting message with key: {key_id}")
            
            # Retrieve quantum key from KM
            qkd_key = self.qkd_client.get_key_by_id(key_id)
            
            if not qkd_key:
                raise Exception(f"Failed to retrieve quantum key: {key_id}")
            
            logger.info(f"Retrieved quantum key: {qkd_key.key_id}")
            
            # Decrypt message
            plaintext = self.encryption_engine.decrypt(
                ciphertext=ciphertext,
                key=qkd_key.key,
                metadata=metadata
            )
            
            # Convert bytes to string
            message = plaintext.decode('utf-8')
            
            logger.info(f"Message decrypted successfully")
            return message
            
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            raise
    
    def encrypt_message_to_json(
        self,
        message: str,
        security_level: SecurityLevel = SecurityLevel.QUANTUM_AES
    ) -> str:
        """
        Encrypt message and return as JSON string
        
        Args:
            message: Plain text message
            security_level: Security level to use
        
        Returns:
            JSON string containing encrypted package
        """
        encrypted_package = self.encrypt_message(message, security_level)
        return json.dumps(encrypted_package, indent=2)
    
    def decrypt_message_from_json(self, json_data: str) -> str:
        """
        Decrypt message from JSON string
        
        Args:
            json_data: JSON string containing encrypted package
        
        Returns:
            Decrypted plain text message
        """
        encrypted_package = json.loads(json_data)
        return self.decrypt_message(encrypted_package)
    
    def get_key_manager_status(self) -> Dict:
        """Get status of the Key Manager"""
        return self.qkd_client.get_status()
