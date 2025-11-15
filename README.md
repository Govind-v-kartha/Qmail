# QMail - Quantum-Secure Email Client

A quantum-secure email client that integrates Quantum Key Distribution (QKD) with existing email protocols to provide next-generation security.

## 🚀 Quick Start

### Prerequisites

- Python 3.10 or higher
- Access to a Quantum Key Manager (QKD) service (or use simulation mode)
- Email account (Gmail, Yahoo, Outlook, etc.)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Qmail
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On Unix/macOS
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

5. **Initialize database**
   ```bash
   python -m qmail.core.init_db
   ```

6. **Run the application**
   ```bash
   flask run
   ```

7. **Access the application**
   ```
   Open your browser and navigate to: http://localhost:5000
   ```

## 📁 Project Structure

```
Qmail/
├── qmail/                  # Main application package
│   ├── core/              # Core application logic
│   ├── crypto/            # Encryption engine
│   ├── email_handler/     # SMTP/IMAP/POP3 handlers
│   ├── km_client/         # Quantum Key Manager client
│   ├── models/            # Database models
│   ├── static/            # CSS, JS, images
│   └── templates/         # HTML templates
├── tests/                 # Test suite
├── config/                # Configuration files
├── docs/                  # Documentation
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
└── README.md             # This file
```

## 🔐 Security Levels

QMail supports four encryption security levels:

| Level | Name | Description |
|-------|------|-------------|
| 1 | Quantum Secure (OTP) | Perfect secrecy using quantum one-time pads |
| 2 | Quantum-Aided AES | Hybrid security with quantum key seeding |
| 3 | Post-Quantum Crypto | PQC algorithms (Kyber/Dilithium) |
| 4 | Classical Encryption | Standard AES/RSA encryption |

## 🛠️ Configuration

Edit `.env` file to configure:

- **QKD Key Manager**: Connection details for your Key Manager
- **Email Servers**: SMTP/IMAP server settings
- **Security**: Default encryption level and preferences
- **Database**: Database connection string

## 📖 Usage

### Sending a Quantum-Secure Email

1. Log in to QMail
2. Click "Compose New Email"
3. Fill in recipient, subject, and message
4. Select encryption level (1-4)
5. Click "Send Securely"

### Receiving Encrypted Emails

1. Navigate to "Inbox"
2. Click on an encrypted email
3. QMail automatically retrieves the quantum key
4. Message is decrypted and displayed

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=qmail

# Run specific test file
pytest tests/test_encryption.py
```

## 📚 Documentation

For detailed documentation, see the [docs](./docs) directory:

- [CONTEXT.md](./docs/CONTEXT.md) - Project overview and architecture
- API documentation (coming soon)
- Deployment guide (coming soon)

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## ⚠️ Security Notice

This is a research prototype. For production use:
- Use a certified Quantum Key Manager
- Enable all security features
- Conduct security audit
- Follow ETSI QKD standards

## 📞 Support

For issues and questions:
- Open an issue on GitHub
- Check the documentation
- Contact the development team

---

**Version**: 1.0.0  
**Last Updated**: November 2025
