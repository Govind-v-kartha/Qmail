"""
Tests for message cipher
"""

import pytest
import json
from qmail.crypto.message_cipher import MessageCipher
from qmail.crypto.encryption_engine import SecurityLevel


class TestMessageCipher:
    """Test MessageCipher functionality"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.cipher = MessageCipher(use_mock_qkd=True)
        self.test_message = "Hello, this is a quantum-encrypted message!"
    
    def test_encrypt_decrypt_message(self):
        """Test basic encrypt/decrypt flow"""
        # Encrypt
        encrypted_package = self.cipher.encrypt_message(
            self.test_message,
            SecurityLevel.QUANTUM_AES
        )
        
        # Verify package structure
        assert 'ciphertext' in encrypted_package
        assert 'key_id' in encrypted_package
        assert 'security_level' in encrypted_package
        assert 'metadata' in encrypted_package
        
        # Decrypt
        decrypted_message = self.cipher.decrypt_message(encrypted_package)
        assert decrypted_message == self.test_message
    
    def test_all_security_levels(self):
        """Test encryption with all security levels"""
        for level in SecurityLevel:
            encrypted_package = self.cipher.encrypt_message(
                self.test_message,
                level
            )
            
            decrypted_message = self.cipher.decrypt_message(encrypted_package)
            assert decrypted_message == self.test_message
    
    def test_json_serialization(self):
        """Test JSON serialization/deserialization"""
        # Encrypt to JSON
        json_data = self.cipher.encrypt_message_to_json(
            self.test_message,
            SecurityLevel.QUANTUM_AES
        )
        
        # Verify it's valid JSON
        encrypted_package = json.loads(json_data)
        assert 'ciphertext' in encrypted_package
        
        # Decrypt from JSON
        decrypted_message = self.cipher.decrypt_message_from_json(json_data)
        assert decrypted_message == self.test_message
    
    def test_different_messages(self):
        """Test with various message contents"""
        messages = [
            "Short",
            "Medium length message",
            "Very long message " * 100,
            "Special characters: !@#$%^&*()",
            "Unicode: 你好世界 🚀",
        ]
        
        for msg in messages:
            encrypted_package = self.cipher.encrypt_message(
                msg,
                SecurityLevel.QUANTUM_AES
            )
            
            decrypted_message = self.cipher.decrypt_message(encrypted_package)
            assert decrypted_message == msg
    
    def test_get_km_status(self):
        """Test getting Key Manager status"""
        status = self.cipher.get_key_manager_status()
        
        assert 'status' in status
        assert status['status'] == 'operational'
        assert status['mode'] == 'simulation'
