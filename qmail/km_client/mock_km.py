"""
Mock Quantum Key Manager for development and testing
Simulates ETSI GS QKD 014 API without requiring actual QKD hardware
"""

import os
import json
import secrets
import logging
from typing import Dict, Optional, List
from datetime import datetime
import base64
from pathlib import Path
from qmail.km_client.qkd_client import QKDKey

logger = logging.getLogger(__name__)


class MockQKDClient:
    """
    Mock QKD Client for development and testing
    Generates cryptographically secure random keys instead of quantum keys
    Keys are persisted to disk to survive application restarts
    """
    
    def __init__(
        self,
        host: str = "localhost",
        port: int = 8080,
        persist_keys: bool = True,
        key_store_file: str = "instance/mock_qkd_keys.json",
        **kwargs
    ):
        """Initialize Mock QKD Client"""
        self.host = host
        self.port = port
        self.keys_generated = 0
        self.persist_keys = persist_keys
        self.key_store_file = Path(key_store_file)
        self.key_store: Dict[str, bytes] = {}
        
        # Load existing keys from disk if persistent storage is enabled
        if self.persist_keys:
            self._load_keys()
        
        logger.info("Mock QKD Client initialized (simulation mode)")
    
    def _load_keys(self):
        """Load keys from persistent storage"""
        try:
            if self.key_store_file.exists():
                with open(self.key_store_file, 'r') as f:
                    data = json.load(f)
                    # Convert base64 encoded keys back to bytes
                    self.key_store = {
                        key_id: base64.b64decode(key_b64)
                        for key_id, key_b64 in data.get('keys', {}).items()
                    }
                    self.keys_generated = data.get('keys_generated', 0)
                    logger.info(f"Loaded {len(self.key_store)} keys from persistent storage")
        except Exception as e:
            logger.warning(f"Failed to load keys from storage: {e}")
            self.key_store = {}
    
    def _save_keys(self):
        """Save keys to persistent storage"""
        if not self.persist_keys:
            return
        
        try:
            # Ensure directory exists
            self.key_store_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Convert keys to base64 for JSON serialization
            data = {
                'keys': {
                    key_id: base64.b64encode(key_bytes).decode('utf-8')
                    for key_id, key_bytes in self.key_store.items()
                },
                'keys_generated': self.keys_generated,
                'last_updated': datetime.now().isoformat()
            }
            
            with open(self.key_store_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.debug(f"Saved {len(self.key_store)} keys to persistent storage")
        except Exception as e:
            logger.error(f"Failed to save keys to storage: {e}")
    
    @classmethod
    def from_env(cls) -> 'MockQKDClient':
        """Create Mock QKD Client from environment variables"""
        return cls(
            host=os.getenv('QKD_KM_HOST', 'localhost'),
            port=int(os.getenv('QKD_KM_PORT', '8080'))
        )
    
    def get_status(self) -> Dict:
        """Get mock Key Manager status"""
        return {
            "status": "operational",
            "mode": "simulation",
            "keys_generated": self.keys_generated,
            "keys_stored": len(self.key_store),
            "timestamp": datetime.now().isoformat()
        }
    
    def get_key(
        self,
        key_size: int = 256,
        number_of_keys: int = 1,
        extension_mandatory: Optional[List[str]] = None
    ) -> List[QKDKey]:
        """
        Generate mock quantum keys using cryptographically secure random generator
        
        Args:
            key_size: Size of key in bits
            number_of_keys: Number of keys to generate
            extension_mandatory: Ignored in mock
        
        Returns:
            List of QKDKey objects with randomly generated keys
        """
        keys = []
        
        for _ in range(number_of_keys):
            # Generate cryptographically secure random key
            key_bytes = secrets.token_bytes(key_size // 8)
            
            # Generate unique key ID
            self.keys_generated += 1
            key_id = f"MOCK-KEY-{self.keys_generated:08d}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            # Store key for later retrieval
            self.key_store[key_id] = key_bytes
            
            # Create QKDKey object
            qkd_key = QKDKey(
                key_id=key_id,
                key=key_bytes,
                key_size=key_size,
                timestamp=datetime.now()
            )
            
            keys.append(qkd_key)
            logger.info(f"Generated mock key: {key_id} ({key_size} bits)")
        
        # Save keys to persistent storage
        self._save_keys()
        
        return keys
    
    def get_key_by_id(self, key_id: str) -> Optional[QKDKey]:
        """
        Retrieve a mock key by its ID
        
        Args:
            key_id: The ID of the key to retrieve
        
        Returns:
            QKDKey object or None if not found
        """
        if key_id in self.key_store:
            key_bytes = self.key_store[key_id]
            
            qkd_key = QKDKey(
                key_id=key_id,
                key=key_bytes,
                key_size=len(key_bytes) * 8,
                timestamp=datetime.now()
            )
            
            logger.info(f"Retrieved mock key by ID: {key_id}")
            return qkd_key
        
        logger.warning(f"Mock key not found: {key_id}")
        return None
    
    def get_key_with_key_ids(self, key_ids: List[str]) -> List[QKDKey]:
        """Retrieve multiple mock keys by their IDs"""
        keys = []
        for key_id in key_ids:
            key = self.get_key_by_id(key_id)
            if key:
                keys.append(key)
        return keys
    
    def close_key(self, key_id: str) -> bool:
        """
        Remove a key from the mock key store
        
        Args:
            key_id: The ID of the key to remove
        
        Returns:
            True if successful, False otherwise
        """
        if key_id in self.key_store:
            del self.key_store[key_id]
            logger.info(f"Closed mock key: {key_id}")
            # Update persistent storage
            self._save_keys()
            return True
        
        logger.warning(f"Failed to close mock key (not found): {key_id}")
        return False
    
    def clear_all_keys(self):
        """Clear all keys from the mock store (for testing)"""
        count = len(self.key_store)
        self.key_store.clear()
        self._save_keys()
        logger.info(f"Cleared {count} mock keys from store")


def get_qkd_client(use_mock: bool = None) -> 'QKDClient | MockQKDClient':
    """
    Factory function to get appropriate QKD client
    
    Args:
        use_mock: If True, use mock client. If None, check environment
    
    Returns:
        QKD client instance (real or mock)
    """
    if use_mock is None:
        # Check environment variable
        use_mock = os.getenv('QKD_USE_MOCK', 'true').lower() == 'true'
    
    if use_mock:
        logger.info("Using Mock QKD Client (simulation mode)")
        return MockQKDClient.from_env()
    else:
        logger.info("Using Real QKD Client")
        from qmail.km_client.qkd_client import QKDClient
        return QKDClient.from_env()
