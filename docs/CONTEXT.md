# QMail - Quantum-Secure Email Client

## 📋 Overview

**QMail** is an advanced email client designed to deliver **quantum-secure communication** over existing email infrastructures such as Gmail, Yahoo Mail, or Outlook.

It combines **Quantum Key Distribution (QKD)** with traditional email protocols (SMTP, IMAP, and POP3) to achieve next-generation confidentiality, integrity, and authenticity in electronic communication.

The system is built to protect email exchanges from:
- **Classical threats**: eavesdropping and man-in-the-middle attacks
- **Future post-quantum computing threats**: quantum computer-based cryptanalysis

---

## 🎯 Objective

The main objective of QMail is to develop a **secure and user-friendly email client** that integrates Quantum Key Distribution (QKD) with existing email protocols while maintaining interoperability with popular mail servers.

### Key Goals

- **Client Application**: QMail communicates with a Key Manager (KM) service to fetch quantum keys using **ETSI GS QKD 014 REST-based APIs**
- **Encryption**: These keys are used to encrypt email messages before transmission through untrusted networks
- **Non-Invasive Integration**: Enhance security without altering the existing infrastructure of email servers

---

## ❗ Problem Statement

### Current Vulnerability

Traditional encryption systems such as **RSA** and **ECC** rely on computational hardness, which can be broken by powerful quantum computers in the near future.

Conventional email encryption methods are susceptible to:
- **Interception**
- **Man-in-the-middle (MITM) attacks**
- **Eavesdropping**
- **Data breaches**

### Quantum Solution

**Quantum Key Distribution (QKD)** provides an unconditional level of security by leveraging the laws of quantum mechanics to exchange symmetric keys between two endpoints.

> **Key Advantage**: Any interception attempt during key exchange alters the quantum state, thereby alerting both users of potential intrusion.

Integrating QKD into an email system ensures **future-proof, quantum-resistant communication**.

---

## 💡 Use Case Scenario

### The Alice and Bob Example

1. **Setup**: Alice and Bob each have access to a local **Key Manager (KM)** connected to a quantum network
2. **Key Synchronization**: The Key Managers have already exchanged and synchronized symmetric quantum keys using QKD
3. **Sending**:
   - Alice composes an email
   - QMail retrieves a quantum key from the KM
   - Message is encrypted before sending via Gmail/Yahoo Mail
4. **Receiving**:
   - Bob receives the encrypted email
   - His QMail client retrieves the corresponding key from his KM
   - Message is decrypted and displayed

**Result**: Even if the email is transmitted over an untrusted network, only authorized users can read it.

---

## ✨ Core Features

### 🔐 Integration with QKD Services
QMail communicates with a Quantum Key Manager using the **ETSI GS QKD 014 REST API** to securely obtain quantum keys.

### 📧 Standard Email Compatibility
Maintains compatibility with existing **SMTP**, **IMAP**, and **POP3** email servers, ensuring seamless integration with popular providers.

### 🖥️ User-Friendly Graphical Interface
The email client provides a GUI built with **Flask** or **Django** for:
- Composing emails
- Managing inbox
- Configuring security settings

### 🔒 Application-Layer Encryption
Encryption is performed at the application layer before sending messages through the network, ensuring that **even the mail server cannot access message contents**.

### ⚙️ Multi-Level Security Configuration
Users can choose between different encryption levels depending on their security needs, ranging from fully quantum-secure one-time pads to classical encryption.

### 🧩 Modular Architecture
The system is designed to be extensible, allowing future upgrades such as:
- Quantum-secure chat
- Voice communication
- Video communication

---

## 🔐 Security Levels

QMail provides **four levels** of encryption security to accommodate different performance and protection requirements:

| Level | Name | Description | Security |
|-------|------|-------------|----------|
| **Level 1** | **Quantum Secure (One-Time Pad)** | Uses quantum-generated keys as one-time pads, achieving theoretically perfect secrecy. Each key is used only once and then discarded. | ⭐⭐⭐⭐⭐ |
| **Level 2** | **Quantum-Aided AES** | Quantum keys are used as seeds to generate AES session keys. Provides strong hybrid security while maintaining efficiency and speed. | ⭐⭐⭐⭐ |
| **Level 3** | **Post-Quantum Cryptography (PQC)** | Employs post-quantum algorithms such as Kyber or Dilithium to resist quantum attacks. Optional layer for users without access to QKD. | ⭐⭐⭐ |
| **Level 4** | **Classical Encryption** | Fallback mode using standard AES or RSA encryption without quantum security features. | ⭐⭐ |

---

## 🏗️ System Architecture

### High-Level Design

The system architecture is divided into multiple layers:

```
┌─────────────────────────────────────┐
│     User Interface Layer            │
│  (Email Composition, Inbox, Config) │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│      Email Manager Layer            │
│    (SMTP, IMAP, POP3 Handlers)     │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│    Encryption Engine Layer          │
│   (OTP, AES, PQC Implementation)    │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│  Quantum Key Manager Interface      │
│   (ETSI GS QKD 014 REST API)       │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│      Email Server Layer             │
│   (Gmail, Yahoo, Outlook, etc.)     │
└─────────────────────────────────────┘
```

This layered structure ensures both **modularity** and **security**.

### Component Description

#### 1. QMail Client
The main application developed using **Flask** or **Django**, managing user interaction and mail processing.

#### 2. Key Manager (KM)
A local or remote service providing quantum keys through **ETSI-compliant REST APIs**.

#### 3. Encryption Engine
Responsible for performing encryption and decryption operations based on user-selected security levels.

#### 4. Email Handler
Handles communication with existing email servers via standard protocols.

#### 5. Database Module
Stores user preferences, email metadata, and key references *(but not the actual keys for security reasons)*.

---

## 🔄 Integration Flow

### 📤 Sending an Email

1. User composes an email in the QMail interface
2. User selects a desired encryption level from the available options
3. QMail requests a new quantum key from the Key Manager via the **ETSI GS QKD 014 API**
4. Key Manager returns a response containing:
   - `key_id`
   - `key_material`
5. QMail encrypts the message using the selected algorithm and embeds headers:
   - `X-QKD-KeyID`
   - `X-QKD-Security-Level`
6. Encrypted message is sent via **SMTP** to the recipient's mail server

### 📥 Receiving an Email

1. Recipient's QMail client retrieves the encrypted message via **IMAP** or **POP3**
2. Reads the message headers to identify:
   - Key ID
   - Encryption level
3. QMail requests the corresponding key from its Key Manager
4. Encryption engine decrypts the message using the retrieved key
5. Decrypted message is displayed in the GUI

---

## 🛠️ Technologies and Tools

### Core Technologies

| Category | Technology |
|----------|------------|
| **Programming Language** | Python 3.10 or higher |
| **Web Framework** | Flask or Django |
| **Cryptography Libraries** | `cryptography`, `pycryptodome`, `pqcrypto` |
| **Quantum Key Interface** | ETSI-compliant client library for QKD API |
| **Quantum Simulation** | SimulaQron or QuKayDee |
| **Email Libraries** | `smtplib`, `imaplib`, `email` |
| **Networking** | `requests`, `Flask-RESTful` |
| **Database** | SQLite |
| **Testing** | `pytest`, Postman, MailHog |
| **Version Control** | Git, GitHub |
| **Security Tools** | OpenSSL |

### Development Stack

```python
# Key Dependencies
- cryptography>=41.0.0      # Modern cryptographic primitives
- pycryptodome>=3.18.0      # AES and RSA implementations
- pqcrypto>=0.3.0           # Post-quantum algorithms
- Flask>=2.3.0              # Web framework
- requests>=2.31.0          # HTTP client for QKD API
- pytest>=7.4.0             # Testing framework
```

---

## 🎯 Expected Outcome

The expected outcome is a **working prototype of QMail**, a quantum-secure email client that allows users to send and receive encrypted emails using QKD-based keys.

### Key Deliverables

✅ **Modular Design**: Extensible architecture for future enhancements  
✅ **User-Friendly Interface**: Intuitive GUI for all user interactions  
✅ **Multiple Security Levels**: Flexible encryption options (OTP, AES, PQC, Classical)  
✅ **Seamless Integration**: Works with existing email infrastructure  
✅ **Proof of Concept**: Demonstrates quantum-secured communication without disrupting existing services

### Success Criteria

- ✔️ Successfully send and receive quantum-encrypted emails
- ✔️ Integrate with at least one major email provider (Gmail/Yahoo/Outlook)
- ✔️ Retrieve quantum keys via ETSI GS QKD 014 API
- ✔️ Support all four security levels
- ✔️ Provide comprehensive testing and documentation

---

## 📚 References

- **ETSI GS QKD 014**: Quantum Key Distribution (QKD); Protocol and data format of REST-based key delivery API
- **BB84 Protocol**: First quantum key distribution scheme
- **Post-Quantum Cryptography**: NIST PQC standardization process
- **RFC 5321**: Simple Mail Transfer Protocol (SMTP)
- **RFC 3501**: Internet Message Access Protocol (IMAP)
- **RFC 1939**: Post Office Protocol - Version 3 (POP3)

---

*Last Updated: October 2025*
