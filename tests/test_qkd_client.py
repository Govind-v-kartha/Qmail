"""
Tests for QKD client
"""

import pytest
from qmail.km_client.mock_km import MockQKDClient


class TestMockQKDClient:
    """Test Mock QKD Client"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.client = MockQKDClient()
    
    def test_client_initialization(self):
        """Test client initializes correctly"""
        assert self.client.host == "localhost"
        assert self.client.port == 8080
        assert self.client.keys_generated == 0
        assert len(self.client.key_store) == 0
    
    def test_get_status(self):
        """Test get status"""
        status = self.client.get_status()
        
        assert status['status'] == 'operational'
        assert status['mode'] == 'simulation'
        assert 'keys_generated' in status
        assert 'timestamp' in status
    
    def test_get_single_key(self):
        """Test getting a single key"""
        keys = self.client.get_key(key_size=256, number_of_keys=1)
        
        assert len(keys) == 1
        assert keys[0].key_size == 256
        assert len(keys[0].key) == 32  # 256 bits = 32 bytes
        assert keys[0].key_id.startswith('MOCK-KEY-')
    
    def test_get_multiple_keys(self):
        """Test getting multiple keys"""
        keys = self.client.get_key(key_size=256, number_of_keys=5)
        
        assert len(keys) == 5
        
        # All keys should be unique
        key_ids = [k.key_id for k in keys]
        assert len(key_ids) == len(set(key_ids))
    
    def test_get_key_by_id(self):
        """Test retrieving key by ID"""
        # Generate a key
        keys = self.client.get_key(key_size=256, number_of_keys=1)
        key_id = keys[0].key_id
        
        # Retrieve it
        retrieved_key = self.client.get_key_by_id(key_id)
        
        assert retrieved_key is not None
        assert retrieved_key.key_id == key_id
        assert retrieved_key.key == keys[0].key
    
    def test_get_nonexistent_key(self):
        """Test retrieving nonexistent key"""
        key = self.client.get_key_by_id('NONEXISTENT-KEY-ID')
        assert key is None
    
    def test_close_key(self):
        """Test closing/deleting a key"""
        # Generate a key
        keys = self.client.get_key(key_size=256, number_of_keys=1)
        key_id = keys[0].key_id
        
        # Verify it exists
        assert self.client.get_key_by_id(key_id) is not None
        
        # Close it
        success = self.client.close_key(key_id)
        assert success is True
        
        # Verify it's gone
        assert self.client.get_key_by_id(key_id) is None
    
    def test_different_key_sizes(self):
        """Test generating keys of different sizes"""
        sizes = [128, 256, 512, 1024]
        
        for size in sizes:
            keys = self.client.get_key(key_size=size, number_of_keys=1)
            assert len(keys[0].key) == size // 8
            assert keys[0].key_size == size
    
    def test_key_uniqueness(self):
        """Test that generated keys are unique"""
        keys = self.client.get_key(key_size=256, number_of_keys=10)
        
        # All keys should be different
        key_values = [k.key for k in keys]
        assert len(key_values) == len(set(key_values))
    
    def test_clear_all_keys(self):
        """Test clearing all keys"""
        # Generate some keys
        self.client.get_key(key_size=256, number_of_keys=5)
        assert len(self.client.key_store) > 0
        
        # Clear all
        self.client.clear_all_keys()
        assert len(self.client.key_store) == 0
