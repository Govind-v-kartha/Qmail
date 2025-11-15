# QMail Encryption System - Key Management System (QKD)

## 📚 Table of Contents
1. [Overview](#overview)
2. [Quantum Key Distribution Basics](#quantum-key-distribution-basics)
3. [QKD Client Architecture](#qkd-client-architecture)
4. [Real QKD Client](#real-qkd-client)
5. [Mock QKD Client](#mock-qkd-client)
6. [Key Lifecycle](#key-lifecycle)
7. [Persistent Storage](#persistent-storage)
8. [Code Implementation](#code-implementation)

---

## 1. Overview

The **Key Management System** is responsible for generating, storing, and distributing quantum keys used for encryption. QMail supports both **Real QKD** (using actual quantum hardware) and **Mock QKD** (for development/testing).

**Files:**
- `qmail/km_client/qkd_client.py` - Real QKD client
- `qmail/km_client/mock_km.py` - Mock QKD client

---

## 2. Quantum Key Distribution Basics

### What is QKD?

**Quantum Key Distribution (QKD)** uses quantum mechanics to securely distribute encryption keys:

1. **Quantum Properties:** Uses quantum states (photon polarization)
2. **Eavesdropping Detection:** Any measurement disturbs quantum states
3. **Provable Security:** Based on physics, not computational complexity
4. **Secure Channel:** Creates shared secret keys between parties

###

 How QKD Works (Simplified)

```
Alice (Sender)              Quantum Channel              Bob (Receiver)
     │                                                         │
     ├─── Send photons with random polarization ────────────▶│
     │                                                         │
     │◄── Acknowledge received photons ──────────────────────┤
     │                                                         │
     ├─── Share measurement bases ──────────────────────────▶│
     │                                                         │
     │◄── Confirm matching measurements ─────────────────────┤
     │                                                         │
     └─── Shared Secret Key Generated ───────────────────────┘
```

### Key Properties

- **Random:** Keys are truly random (quantum randomness)
- **Secure:** Eavesdropping is detectable
- **One-time:** Keys should be used once (OTP) or limited times
- **Distributed:** Both parties get the same key

---

## 3. QKD Client Architecture

### Interface Design

Both Real and Mock QKD clients implement the same interface for seamless switching:

```python
class QKDClientInterface:
    """Common interface for all QKD clients"""
    
    def get_status(self) -> Dict:
        """Get Key Manager status"""
        pass
    
    def get_key(self, key_size: int, number_of_keys: int) -> List[QKDKey]:
        """Request quantum keys"""
        pass
    
    def get_key_by_id(self, key_id: str) -> Optional[QKDKey]:
        """Retrieve specific key"""
        pass
    
    def close_key(self, key_id: str) -> bool:
        """Delete used key"""
        pass
```

### QKDKey Data Class

```python
@dataclass
class QKDKey:
    """Represents a quantum key"""
    key_id: str              # Unique identifier
    key: bytes               # The actual key bytes
    key_size: int            # Size in bits
    timestamp: datetime      # When generated
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'key_id': self.key_id,
            'key': base64.b64encode(self.key).decode('utf-8'),
            'key_size': self.key_size,
            'timestamp': self.timestamp.isoformat()
        }
```

---

## 4. Real QKD Client

### Overview

**File:** `qmail/km_client/qkd_client.py`

The Real QKD Client connects to actual quantum hardware Key Manager via HTTP REST API.

### Configuration

```python
class QKDClient:
    def __init__(
        self,
        host: str = 'localhost',
        port: int = 8080,
        use_https: bool = False,
        cert_path: Optional[str] = None
    ):
        """
        Initialize QKD Client
        
        Args:
            host: Key Manager hostname
            port: Key Manager port
            use_https: Use HTTPS connection
            cert_path: Path to SSL certificate
        """
        self.base_url = f"{'https' if use_https else 'http'}://{host}:{port}"
        self.session = requests.Session()
        
        if cert_path:
            self.session.verify = cert_path
```

### API Endpoints

#### 1. Get Status

```python
def get_status(self) -> Dict:
    """
    Get Key Manager status
    
    Returns:
        Dictionary with KM status information
    
    Example response:
        {
            "status": "operational",
            "qkd_link_status": "active",
            "available_keys": 1523,
            "queue_length": 42
        }
    """
    response = self.session.get(f"{self.base_url}/api/v1/status")
    response.raise_for_status()
    return response.json()
```

#### 2. Get Keys

```python
def get_key(
    self,
    key_size: int = 256,
    number_of_keys: int = 1,
    extension_mandatory: Optional[List[str]] = None
) -> List[QKDKey]:
    """
    Request quantum keys from Key Manager
    
    Args:
        key_size: Size of key in bits (e.g., 256, 512)
        number_of_keys: Number of keys to request
        extension_mandatory: Optional extensions
    
    Returns:
        List of QKDKey objects
    
    API Request:
        POST /api/v1/keys/get
        {
            "key_size": 256,
            "number": 1
        }
    
    API Response:
        {
            "keys": [
                {
                    "key_ID": "QKD-KEY-ABC123...",
                    "key": "base64_encoded_key_bytes"
                }
            ]
        }
    """
    payload = {
        'key_size': key_size,
        'number': number_of_keys
    }
    
    if extension_mandatory:
        payload['extension_mandatory'] = extension_mandatory
    
    response = self.session.post(
        f"{self.base_url}/api/v1/keys/get",
        json=payload
    )
    response.raise_for_status()
    
    data = response.json()
    keys = []
    
    for key_data in data.get('keys', []):
        qkd_key = QKDKey(
            key_id=key_data['key_ID'],
            key=base64.b64decode(key_data['key']),
            key_size=key_size,
            timestamp=datetime.now()
        )
        keys.append(qkd_key)
    
    logger.info(f"Obtained {len(keys)} quantum key(s) from KM")
    return keys
```

#### 3. Get Key By ID

```python
def get_key_by_id(self, key_id: str) -> Optional[QKDKey]:
    """
    Retrieve a specific key by its ID
    
    Args:
        key_id: The key identifier
    
    Returns:
        QKDKey object or None if not found
    
    API Request:
        GET /api/v1/keys/{key_id}
    
    API Response:
        {
            "key_ID": "QKD-KEY-ABC123...",
            "key": "base64_encoded_key_bytes",
            "key_size": 256
        }
    """
    response = self.session.get(
        f"{self.base_url}/api/v1/keys/{key_id}"
    )
    
    if response.status_code == 404:
        logger.warning(f"Key not found: {key_id}")
        return None
    
    response.raise_for_status()
    data = response.json()
    
    qkd_key = QKDKey(
        key_id=data['key_ID'],
        key=base64.b64decode(data['key']),
        key_size=data.get('key_size', len(data['key']) * 8),
        timestamp=datetime.now()
    )
    
    logger.info(f"Retrieved quantum key: {key_id}")
    return qkd_key
```

#### 4. Close Key

```python
def close_key(self, key_id: str) -> bool:
    """
    Delete a used key from Key Manager
    
    Args:
        key_id: The key to delete
    
    Returns:
        True if successful
    
    API Request:
        DELETE /api/v1/keys/{key_id}
    """
    response = self.session.delete(
        f"{self.base_url}/api/v1/keys/{key_id}"
    )
    
    if response.status_code == 200:
        logger.info(f"Key closed: {key_id}")
        return True
    else:
        logger.error(f"Failed to close key: {key_id}")
        return False
```

### Error Handling

```python
class QKDError(Exception):
    """Base exception for QKD errors"""
    pass

class QKDConnectionError(QKDError):
    """Raised when connection to KM fails"""
    pass

class QKDKeyError(QKDError):
    """Raised when key operation fails"""
    pass
```

---

## 5. Mock QKD Client

### Overview

**File:** `qmail/km_client/mock_km.py`

The Mock QKD Client simulates quantum key generation using cryptographically secure random number generation. Perfect for development and testing.

### Features

- ✅ **Cryptographically Secure:** Uses `secrets.token_bytes()`
- ✅ **Persistent Storage:** Keys saved to JSON file
- ✅ **Compatible Interface:** Same API as Real QKD
- ✅ **Fast:** No network latency
- ✅ **Survives Restarts:** Keys persist across app restarts

### Implementation

```python
class MockQKDClient:
    """
    Mock Quantum Key Distribution Client
    Simulates QKD using cryptographically secure random generation
    """
    
    def __init__(
        self,
        host: str = 'localhost',
        port: int = 8080,
        persist_keys: bool = True
    ):
        """
        Initialize Mock QKD Client
        
        Args:
            host: Ignored (for interface compatibility)
            port: Ignored (for interface compatibility)
            persist_keys: Save keys to disk for persistence
        """
        self.host = host
        self.port = port
        self.persist_keys = persist_keys
        
        # Key storage
        self.key_store = {}  # {key_id: key_bytes}
        self.keys_generated = 0
        
        # Persistent storage file
        self.key_store_file = Path('instance/mock_qkd_keys.json')
        
        # Load existing keys
        if persist_keys:
            self._load_keys()
        
        logger.info("Mock QKD Client initialized (simulation mode)")
    
    def get_key(
        self,
        key_size: int = 256,
        number_of_keys: int = 1,
        extension_mandatory: Optional[List[str]] = None
    ) -> List[QKDKey]:
        """
        Generate mock quantum keys
        
        Uses cryptographically secure random number generator
        to simulate quantum key generation
        
        Args:
            key_size: Size of key in bits
            number_of_keys: Number of keys to generate
            extension_mandatory: Ignored in mock
        
        Returns:
            List of QKDKey objects
        """
        import secrets
        
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
        
        # Save to persistent storage
        if self.persist_keys:
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
            
            # Update persistent storage
            if self.persist_keys:
                self._save_keys()
            
            logger.info(f"Mock key closed: {key_id}")
            return True
        
        logger.warning(f"Cannot close mock key (not found): {key_id}")
        return False
    
    def get_status(self) -> Dict:
        """
        Get mock Key Manager status
        
        Returns:
            Dictionary with simulated KM status
        """
        return {
            "status": "operational",
            "mode": "simulation",
            "keys_generated": self.keys_generated,
            "keys_stored": len(self.key_store),
            "timestamp": datetime.now().isoformat()
        }
```

---

## 6. Key Lifecycle

### Complete Lifecycle

```
1. GENERATION
   │
   ├─ User sends encrypted email
   ├─ MessageCipher requests key
   ├─ QKDClient.get_key() called
   ├─ Key Manager generates quantum key
   └─ Returns QKDKey object
   │
   ▼
2. STORAGE
   │
   ├─ Key stored in Key Manager database
   ├─ Key ID assigned (unique identifier)
   └─ Key associated with ciphertext
   │
   ▼
3. USE
   │
   ├─ EncryptionEngine uses key to encrypt
   ├─ Key ID saved in email metadata
   └─ Ciphertext sent to recipient
   │
   ▼
4. RETRIEVAL
   │
   ├─ Recipient receives encrypted email
   ├─ Extract key_id from metadata
   ├─ QKDClient.get_key_by_id() called
   └─ Key Manager returns key
   │
   ▼
5. DECRYPTION
   │
   ├─ EncryptionEngine uses key to decrypt
   └─ Plaintext recovered
   │
   ▼
6. DELETION (Optional)
   │
   ├─ QKDClient.close_key() called
   ├─ Key removed from Key Manager
   └─ Cannot be used again
```

### Key States

```python
class KeyState(Enum):
    GENERATED = "generated"       # Just created
    STORED = "stored"            # Saved in KM
    IN_USE = "in_use"            # Currently encrypting/decrypting
    USED = "used"                # Already used once
    CLOSED = "closed"            # Deleted from KM
```

---

## 7. Persistent Storage

### Mock QKD Persistence

**File:** `instance/mock_qkd_keys.json`

```python
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
```

### Storage Format

```json
{
  "keys": {
    "MOCK-KEY-00000001-20251012195640": "base64_encoded_key_bytes_here...",
    "MOCK-KEY-00000002-20251012195641": "base64_encoded_key_bytes_here...",
    "MOCK-KEY-00000003-20251012195642": "base64_encoded_key_bytes_here..."
  },
  "keys_generated": 3,
  "last_updated": "2025-10-12T19:56:42.123456"
}
```

---

## 8. Code Implementation

### Using QKD Client in Your Code

```python
# Initialize client
if os.getenv('QKD_USE_MOCK', 'true').lower() == 'true':
    qkd_client = MockQKDClient()
else:
    qkd_client = QKDClient(
        host=os.getenv('QKD_KM_HOST', 'localhost'),
        port=int(os.getenv('QKD_KM_PORT', 8080))
    )

# Request a quantum key
keys = qkd_client.get_key(key_size=256, number_of_keys=1)
qkd_key = keys[0]

print(f"Key ID: {qkd_key.key_id}")
print(f"Key Size: {qkd_key.key_size} bits")
print(f"Key: {qkd_key.key.hex()[:32]}...")  # Show first 16 bytes

# Use key for encryption
# ... encryption code ...

# Later: retrieve key for decryption
retrieved_key = qkd_client.get_key_by_id(qkd_key.key_id)

# Optional: delete key after use
qkd_client.close_key(qkd_key.key_id)
```

---

## Next Steps

Continue reading:
- **Part 4:** [Message Encryption Flow](04_MESSAGE_ENCRYPTION.md)
- **Part 5:** [Attachment Encryption](05_ATTACHMENT_ENCRYPTION.md)
- **Part 6:** [Code Reference](06_CODE_REFERENCE.md)

---

**Document:** Part 3 of 6  
**Last Updated:** October 12, 2025
