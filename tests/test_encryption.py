"""
Tests for encryption engine
"""

import pytest
from qmail.crypto.encryption_engine import EncryptionEngine, SecurityLevel


class TestEncryptionEngine:
    """Test encryption engine functionality"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.engine = EncryptionEngine()
        self.test_message = b"This is a test message for QMail encryption"
        self.test_key = b"0123456789abcdef" * 4  # 64 bytes = 512 bits
    
    def test_otp_encryption_decryption(self):
        """Test OTP encryption and decryption"""
        # Encrypt
        ciphertext, metadata = self.engine.encrypt(
            self.test_message,
            self.test_key,
            SecurityLevel.QUANTUM_OTP
        )
        
        assert ciphertext != self.test_message
        assert metadata['security_level'] == SecurityLevel.QUANTUM_OTP
        assert metadata['algorithm'] == 'OTP'
        
        # Decrypt
        decrypted = self.engine.decrypt(ciphertext, self.test_key, metadata)
        assert decrypted == self.test_message
    
    def test_quantum_aes_encryption_decryption(self):
        """Test Quantum-AES encryption and decryption"""
        # Encrypt
        ciphertext, metadata = self.engine.encrypt(
            self.test_message,
            self.test_key,
            SecurityLevel.QUANTUM_AES
        )
        
        assert ciphertext != self.test_message
        assert metadata['security_level'] == SecurityLevel.QUANTUM_AES
        assert metadata['algorithm'] == 'AES-256-CBC'
        assert 'iv' in metadata
        
        # Decrypt
        decrypted = self.engine.decrypt(ciphertext, self.test_key, metadata)
        assert decrypted == self.test_message
    
    def test_pqc_encryption_decryption(self):
        """Test PQC encryption and decryption"""
        # Encrypt
        ciphertext, metadata = self.engine.encrypt(
            self.test_message,
            self.test_key,
            SecurityLevel.POST_QUANTUM
        )
        
        assert ciphertext != self.test_message
        assert metadata['security_level'] == SecurityLevel.POST_QUANTUM
        assert 'iv' in metadata
        assert 'tag' in metadata
        
        # Decrypt
        decrypted = self.engine.decrypt(ciphertext, self.test_key, metadata)
        assert decrypted == self.test_message
    
    def test_classical_encryption_decryption(self):
        """Test classical encryption and decryption"""
        # Encrypt
        ciphertext, metadata = self.engine.encrypt(
            self.test_message,
            self.test_key,
            SecurityLevel.CLASSICAL
        )
        
        assert ciphertext != self.test_message
        assert metadata['security_level'] == SecurityLevel.CLASSICAL
        assert metadata['algorithm'] == 'AES-256-CBC'
        
        # Decrypt
        decrypted = self.engine.decrypt(ciphertext, self.test_key, metadata)
        assert decrypted == self.test_message
    
    def test_all_security_levels(self):
        """Test all security levels work correctly"""
        for level in SecurityLevel:
            # Ensure key is long enough for OTP
            key = self.test_key * 2 if level == SecurityLevel.QUANTUM_OTP else self.test_key
            
            ciphertext, metadata = self.engine.encrypt(
                self.test_message,
                key,
                level
            )
            
            decrypted = self.engine.decrypt(ciphertext, key, metadata)
            assert decrypted == self.test_message, f"Failed for level {level.name}"
    
    def test_different_messages(self):
        """Test encryption with different message lengths"""
        messages = [
            b"Short",
            b"Medium length message for testing",
            b"Very long message " * 100
        ]
        
        for msg in messages:
            key = self.test_key * 10  # Long key for OTP
            
            ciphertext, metadata = self.engine.encrypt(
                msg,
                key,
                SecurityLevel.QUANTUM_AES
            )
            
            decrypted = self.engine.decrypt(ciphertext, key, metadata)
            assert decrypted == msg
