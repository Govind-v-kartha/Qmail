"""
Quantum Key Manager Client
Implements ETSI GS QKD 014 REST-based API for key retrieval
"""

import os
import logging
import requests
from typing import Dict, Optional, List
from dataclasses import dataclass
from datetime import datetime
import base64

logger = logging.getLogger(__name__)


@dataclass
class QKDKey:
    """Represents a quantum key retrieved from the Key Manager"""
    key_id: str
    key: bytes
    key_size: int
    timestamp: datetime
    
    def to_dict(self) -> Dict:
        """Convert to dictionary representation"""
        return {
            'key_id': self.key_id,
            'key': base64.b64encode(self.key).decode('utf-8'),
            'key_size': self.key_size,
            'timestamp': self.timestamp.isoformat()
        }


class QKDClientError(Exception):
    """Base exception for QKD client errors"""
    pass


class QKDConnectionError(QKDClientError):
    """Raised when connection to Key Manager fails"""
    pass


class QKDKeyRetrievalError(QKDClientError):
    """Raised when key retrieval fails"""
    pass


class QKDClient:
    """
    Client for interacting with Quantum Key Manager
    Implements ETSI GS QKD 014 REST-based API
    """
    
    def __init__(
        self,
        host: str = "localhost",
        port: int = 8080,
        api_version: str = "v1",
        master_sae_id: str = "",
        slave_sae_id: str = "",
        use_https: bool = False,
        verify_ssl: bool = True,
        timeout: int = 30
    ):
        """
        Initialize QKD Client
        
        Args:
            host: Key Manager hostname
            port: Key Manager port
            api_version: API version (default: v1)
            master_sae_id: Master SAE (Secure Application Entity) ID
            slave_sae_id: Slave SAE ID
            use_https: Use HTTPS instead of HTTP
            verify_ssl: Verify SSL certificates
            timeout: Request timeout in seconds
        """
        self.host = host
        self.port = port
        self.api_version = api_version
        self.master_sae_id = master_sae_id
        self.slave_sae_id = slave_sae_id
        self.use_https = use_https
        self.verify_ssl = verify_ssl
        self.timeout = timeout
        
        # Build base URL
        protocol = "https" if use_https else "http"
        self.base_url = f"{protocol}://{host}:{port}/api/{api_version}"
        
        logger.info(f"QKD Client initialized: {self.base_url}")
    
    @classmethod
    def from_env(cls) -> 'QKDClient':
        """Create QKD Client from environment variables"""
        return cls(
            host=os.getenv('QKD_KM_HOST', 'localhost'),
            port=int(os.getenv('QKD_KM_PORT', '8080')),
            api_version=os.getenv('QKD_KM_API_VERSION', 'v1'),
            master_sae_id=os.getenv('QKD_KM_MASTER_SAE_ID', ''),
            slave_sae_id=os.getenv('QKD_KM_SLAVE_SAE_ID', ''),
            use_https=os.getenv('QKD_KM_USE_HTTPS', 'false').lower() == 'true',
            verify_ssl=os.getenv('QKD_KM_VERIFY_SSL', 'true').lower() == 'true'
        )
    
    def get_status(self) -> Dict:
        """
        Get Key Manager status
        
        Returns:
            Dictionary containing status information
        """
        try:
            url = f"{self.base_url}/keys/{self.master_sae_id}/status"
            response = requests.get(
                url,
                timeout=self.timeout,
                verify=self.verify_ssl
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Failed to get KM status: {e}")
            raise QKDConnectionError(f"Failed to connect to Key Manager: {e}")
    
    def get_key(
        self,
        key_size: int = 256,
        number_of_keys: int = 1,
        extension_mandatory: Optional[List[str]] = None
    ) -> List[QKDKey]:
        """
        Request new quantum keys from Key Manager
        
        Args:
            key_size: Size of key in bits (default: 256)
            number_of_keys: Number of keys to retrieve (default: 1)
            extension_mandatory: Optional list of mandatory extensions
        
        Returns:
            List of QKDKey objects
        """
        try:
            url = f"{self.base_url}/keys/{self.master_sae_id}/enc_keys"
            
            # Prepare request payload according to ETSI GS QKD 014
            payload = {
                "number": number_of_keys,
                "size": key_size
            }
            
            if extension_mandatory:
                payload["extension_mandatory"] = extension_mandatory
            
            # Add slave SAE ID if provided
            if self.slave_sae_id:
                payload["slave_SAE_ID"] = self.slave_sae_id
            
            logger.debug(f"Requesting {number_of_keys} key(s) of size {key_size} bits")
            
            response = requests.post(
                url,
                json=payload,
                timeout=self.timeout,
                verify=self.verify_ssl,
                headers={'Content-Type': 'application/json'}
            )
            response.raise_for_status()
            
            # Parse response
            data = response.json()
            keys = []
            
            # Handle response format according to ETSI GS QKD 014
            if 'keys' in data:
                for key_data in data['keys']:
                    key = QKDKey(
                        key_id=key_data['key_ID'],
                        key=base64.b64decode(key_data['key']),
                        key_size=len(base64.b64decode(key_data['key'])) * 8,
                        timestamp=datetime.now()
                    )
                    keys.append(key)
                    logger.info(f"Retrieved key: {key.key_id} ({key.key_size} bits)")
            
            return keys
            
        except requests.RequestException as e:
            logger.error(f"Failed to retrieve key: {e}")
            raise QKDKeyRetrievalError(f"Key retrieval failed: {e}")
    
    def get_key_by_id(self, key_id: str) -> Optional[QKDKey]:
        """
        Retrieve a specific key by its ID
        
        Args:
            key_id: The ID of the key to retrieve
        
        Returns:
            QKDKey object or None if not found
        """
        try:
            url = f"{self.base_url}/keys/{self.master_sae_id}/dec_keys"
            
            payload = {
                "key_ID": key_id
            }
            
            logger.debug(f"Retrieving key with ID: {key_id}")
            
            response = requests.post(
                url,
                json=payload,
                timeout=self.timeout,
                verify=self.verify_ssl,
                headers={'Content-Type': 'application/json'}
            )
            response.raise_for_status()
            
            data = response.json()
            
            if 'keys' in data and len(data['keys']) > 0:
                key_data = data['keys'][0]
                key = QKDKey(
                    key_id=key_data['key_ID'],
                    key=base64.b64decode(key_data['key']),
                    key_size=len(base64.b64decode(key_data['key'])) * 8,
                    timestamp=datetime.now()
                )
                logger.info(f"Retrieved key by ID: {key.key_id}")
                return key
            
            return None
            
        except requests.RequestException as e:
            logger.error(f"Failed to retrieve key by ID: {e}")
            raise QKDKeyRetrievalError(f"Key retrieval by ID failed: {e}")
    
    def get_key_with_key_ids(self, key_ids: List[str]) -> List[QKDKey]:
        """
        Retrieve multiple keys by their IDs
        
        Args:
            key_ids: List of key IDs to retrieve
        
        Returns:
            List of QKDKey objects
        """
        keys = []
        for key_id in key_ids:
            key = self.get_key_by_id(key_id)
            if key:
                keys.append(key)
        return keys
    
    def close_key(self, key_id: str) -> bool:
        """
        Close/delete a key from the Key Manager
        
        Args:
            key_id: The ID of the key to close
        
        Returns:
            True if successful, False otherwise
        """
        try:
            url = f"{self.base_url}/keys/{self.master_sae_id}/close"
            
            payload = {
                "key_ID": key_id
            }
            
            response = requests.post(
                url,
                json=payload,
                timeout=self.timeout,
                verify=self.verify_ssl,
                headers={'Content-Type': 'application/json'}
            )
            response.raise_for_status()
            
            logger.info(f"Closed key: {key_id}")
            return True
            
        except requests.RequestException as e:
            logger.error(f"Failed to close key: {e}")
            return False
