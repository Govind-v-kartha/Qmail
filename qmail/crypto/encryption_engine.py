"""
Encryption Engine for QMail
Implements 4 security levels:
1. Quantum Secure (One-Time Pad)
2. Quantum-Aided AES
3. Post-Quantum Cryptography
4. Classical Encryption
"""

import os
import logging
import hashlib
from enum import IntEnum
from typing import Tuple, Optional
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.backends import default_backend
from Crypto.Cipher import AES as PyCryptoAES
from Crypto.Util.Padding import pad, unpad
import base64

logger = logging.getLogger(__name__)


class SecurityLevel(IntEnum):
    """Encryption security levels"""
    QUANTUM_OTP = 1      # Quantum Secure (One-Time Pad)
    QUANTUM_AES = 2      # Quantum-Aided AES
    POST_QUANTUM = 3     # Post-Quantum Cryptography
    CLASSICAL = 4        # Classical Encryption


class EncryptionError(Exception):
    """Base exception for encryption errors"""
    pass


class DecryptionError(Exception):
    """Base exception for decryption errors"""
    pass


class EncryptionEngine:
    """
    Main encryption engine supporting multiple security levels
    """
    
    def __init__(self, security_level: SecurityLevel = SecurityLevel.QUANTUM_AES):
        """
        Initialize encryption engine
        
        Args:
            security_level: Default security level to use
        """
        self.security_level = security_level
        logger.info(f"Encryption engine initialized with security level: {security_level.name}")
    
    def encrypt(
        self,
        plaintext: bytes,
        key: bytes,
        security_level: Optional[SecurityLevel] = None
    ) -> Tuple[bytes, dict]:
        """
        Encrypt data using specified security level
        
        Args:
            plaintext: Data to encrypt
            key: Encryption key (quantum or classical)
            security_level: Security level to use (overrides default)
        
        Returns:
            Tuple of (ciphertext, metadata)
        """
        level = security_level or self.security_level
        
        logger.debug(f"Encrypting {len(plaintext)} bytes with level {level.name}")
        
        if level == SecurityLevel.QUANTUM_OTP:
            return self._encrypt_otp(plaintext, key)
        elif level == SecurityLevel.QUANTUM_AES:
            return self._encrypt_quantum_aes(plaintext, key)
        elif level == SecurityLevel.POST_QUANTUM:
            return self._encrypt_pqc(plaintext, key)
        elif level == SecurityLevel.CLASSICAL:
            return self._encrypt_classical(plaintext, key)
        else:
            raise EncryptionError(f"Unknown security level: {level}")
    
    def decrypt(
        self,
        ciphertext: bytes,
        key: bytes,
        metadata: dict
    ) -> bytes:
        """
        Decrypt data using metadata information
        
        Args:
            ciphertext: Encrypted data
            key: Decryption key
            metadata: Encryption metadata
        
        Returns:
            Decrypted plaintext
        """
        level = SecurityLevel(metadata.get('security_level', SecurityLevel.QUANTUM_AES))
        
        logger.debug(f"Decrypting {len(ciphertext)} bytes with level {level.name}")
        
        if level == SecurityLevel.QUANTUM_OTP:
            return self._decrypt_otp(ciphertext, key, metadata)
        elif level == SecurityLevel.QUANTUM_AES:
            return self._decrypt_quantum_aes(ciphertext, key, metadata)
        elif level == SecurityLevel.POST_QUANTUM:
            return self._decrypt_pqc(ciphertext, key, metadata)
        elif level == SecurityLevel.CLASSICAL:
            return self._decrypt_classical(ciphertext, key, metadata)
        else:
            raise DecryptionError(f"Unknown security level: {level}")
    
    # Level 1: Quantum Secure (One-Time Pad)
    def _encrypt_otp(self, plaintext: bytes, key: bytes) -> Tuple[bytes, dict]:
        """
        Encrypt using One-Time Pad (perfect secrecy)
        
        The quantum key must be at least as long as the plaintext
        """
        if len(key) < len(plaintext):
            raise EncryptionError(
                f"OTP requires key length >= plaintext length "
                f"(key: {len(key)}, plaintext: {len(plaintext)})"
            )
        
        # XOR plaintext with quantum key
        ciphertext = bytes(p ^ k for p, k in zip(plaintext, key[:len(plaintext)]))
        
        metadata = {
            'security_level': SecurityLevel.QUANTUM_OTP,
            'algorithm': 'OTP',
            'plaintext_length': len(plaintext)
        }
        
        logger.info(f"OTP encryption: {len(plaintext)} bytes")
        return ciphertext, metadata
    
    def _decrypt_otp(self, ciphertext: bytes, key: bytes, metadata: dict) -> bytes:
        """Decrypt OTP ciphertext"""
        plaintext_length = metadata.get('plaintext_length', len(ciphertext))
        
        if len(key) < plaintext_length:
            raise DecryptionError("Key too short for OTP decryption")
        
        # XOR ciphertext with quantum key
        plaintext = bytes(c ^ k for c, k in zip(ciphertext, key[:plaintext_length]))
        
        logger.info(f"OTP decryption: {len(plaintext)} bytes")
        return plaintext
    
    # Level 2: Quantum-Aided AES
    def _encrypt_quantum_aes(self, plaintext: bytes, quantum_key: bytes) -> Tuple[bytes, dict]:
        """
        Encrypt using AES with quantum-derived key
        
        Uses quantum key to derive AES session key
        """
        # Derive AES key from quantum key using SHA-256
        aes_key = hashlib.sha256(quantum_key).digest()[:32]  # AES-256
        
        # Generate random IV
        iv = os.urandom(16)
        
        # Encrypt using AES-CBC
        cipher = Cipher(
            algorithms.AES(aes_key),
            modes.CBC(iv),
            backend=default_backend()
        )
        encryptor = cipher.encryptor()
        
        # Pad plaintext to AES block size
        padded_plaintext = pad(plaintext, AES.block_size)
        ciphertext = encryptor.update(padded_plaintext) + encryptor.finalize()
        
        metadata = {
            'security_level': SecurityLevel.QUANTUM_AES,
            'algorithm': 'AES-256-CBC',
            'iv': base64.b64encode(iv).decode('utf-8')
        }
        
        logger.info(f"Quantum-AES encryption: {len(plaintext)} bytes")
        return ciphertext, metadata
    
    def _decrypt_quantum_aes(
        self,
        ciphertext: bytes,
        quantum_key: bytes,
        metadata: dict
    ) -> bytes:
        """Decrypt Quantum-AES ciphertext"""
        # Derive AES key from quantum key
        aes_key = hashlib.sha256(quantum_key).digest()[:32]
        
        # Retrieve IV from metadata
        iv = base64.b64decode(metadata['iv'])
        
        # Decrypt using AES-CBC
        cipher = Cipher(
            algorithms.AES(aes_key),
            modes.CBC(iv),
            backend=default_backend()
        )
        decryptor = cipher.decryptor()
        
        padded_plaintext = decryptor.update(ciphertext) + decryptor.finalize()
        plaintext = unpad(padded_plaintext, AES.block_size)
        
        logger.info(f"Quantum-AES decryption: {len(plaintext)} bytes")
        return plaintext
    
    # Level 3: Post-Quantum Cryptography
    def _encrypt_pqc(self, plaintext: bytes, key: bytes) -> Tuple[bytes, dict]:
        """
        Encrypt using Post-Quantum Cryptography
        
        Note: This is a placeholder implementation using AES
        In production, use NIST PQC algorithms (Kyber, Dilithium)
        """
        logger.warning("PQC encryption: Using AES placeholder (implement Kyber for production)")
        
        # Derive encryption key
        pqc_key = hashlib.sha256(key).digest()[:32]
        iv = os.urandom(16)
        
        # Use AES-GCM for authenticated encryption
        cipher = Cipher(
            algorithms.AES(pqc_key),
            modes.GCM(iv),
            backend=default_backend()
        )
        encryptor = cipher.encryptor()
        
        ciphertext = encryptor.update(plaintext) + encryptor.finalize()
        
        metadata = {
            'security_level': SecurityLevel.POST_QUANTUM,
            'algorithm': 'PQC-AES-GCM',  # Should be 'Kyber' in production
            'iv': base64.b64encode(iv).decode('utf-8'),
            'tag': base64.b64encode(encryptor.tag).decode('utf-8')
        }
        
        logger.info(f"PQC encryption: {len(plaintext)} bytes")
        return ciphertext, metadata
    
    def _decrypt_pqc(self, ciphertext: bytes, key: bytes, metadata: dict) -> bytes:
        """Decrypt PQC ciphertext"""
        # Derive decryption key
        pqc_key = hashlib.sha256(key).digest()[:32]
        
        # Retrieve IV and authentication tag
        iv = base64.b64decode(metadata['iv'])
        tag = base64.b64decode(metadata['tag'])
        
        # Decrypt using AES-GCM
        cipher = Cipher(
            algorithms.AES(pqc_key),
            modes.GCM(iv, tag),
            backend=default_backend()
        )
        decryptor = cipher.decryptor()
        
        plaintext = decryptor.update(ciphertext) + decryptor.finalize()
        
        logger.info(f"PQC decryption: {len(plaintext)} bytes")
        return plaintext
    
    # Level 4: Classical Encryption
    def _encrypt_classical(self, plaintext: bytes, key: bytes) -> Tuple[bytes, dict]:
        """
        Encrypt using classical AES encryption
        
        Standard AES-256 without quantum enhancement
        """
        # Use key directly or derive if needed
        if len(key) < 32:
            aes_key = hashlib.sha256(key).digest()[:32]
        else:
            aes_key = key[:32]
        
        iv = os.urandom(16)
        
        # Use PyCrypto for classical AES
        cipher = PyCryptoAES.new(aes_key, PyCryptoAES.MODE_CBC, iv)
        padded_plaintext = pad(plaintext, PyCryptoAES.block_size)
        ciphertext = cipher.encrypt(padded_plaintext)
        
        metadata = {
            'security_level': SecurityLevel.CLASSICAL,
            'algorithm': 'AES-256-CBC',
            'iv': base64.b64encode(iv).decode('utf-8')
        }
        
        logger.info(f"Classical encryption: {len(plaintext)} bytes")
        return ciphertext, metadata
    
    def _decrypt_classical(self, ciphertext: bytes, key: bytes, metadata: dict) -> bytes:
        """Decrypt classical AES ciphertext"""
        # Use key directly or derive if needed
        if len(key) < 32:
            aes_key = hashlib.sha256(key).digest()[:32]
        else:
            aes_key = key[:32]
        
        iv = base64.b64decode(metadata['iv'])
        
        # Decrypt using PyCrypto
        cipher = PyCryptoAES.new(aes_key, PyCryptoAES.MODE_CBC, iv)
        padded_plaintext = cipher.decrypt(ciphertext)
        plaintext = unpad(padded_plaintext, PyCryptoAES.block_size)
        
        logger.info(f"Classical decryption: {len(plaintext)} bytes")
        return plaintext


# Compatibility import for AES block size
class AES:
    block_size = 16  # AES block size in bytes
