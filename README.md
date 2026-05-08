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

5. **Run the application** (database tables are auto-created on first run)
   ```bash
   python run.py
   ```

6. **Access the application**
   ```
   Open your browser and navigate to: http://localhost:5000
   ```

7. **Log in with the default admin account**
   ```
   Username: admin
   Password: admin
   ```
   ⚠️ **Change this password immediately.** Override via the
   `DEFAULT_ADMIN_USERNAME` / `DEFAULT_ADMIN_PASSWORD` env vars, or set
   `DEFAULT_ADMIN_DISABLE=true` to skip auto-seeding entirely.

## ☁️ Deploy to Vercel (https://quantmail.vercel.app)

The repo is already wired for Vercel via [vercel.json](vercel.json) and
[app.py](app.py). To deploy to `quantmail.vercel.app`:

1. **Install the Vercel CLI** (one-time):
   ```bash
   npm i -g vercel
   ```
2. **Log in and link the project**:
   ```bash
   vercel login
   vercel link --project quantmail
   ```
3. **Set required environment variables** (only need to do this once):
   ```bash
   vercel env add SECRET_KEY production
   vercel env add DATABASE_URL production           # PostgreSQL URL
   vercel env add DEFAULT_ADMIN_USERNAME production # e.g. admin
   vercel env add DEFAULT_ADMIN_PASSWORD production # use a strong password!
   vercel env add DEFAULT_ADMIN_EMAIL production
   ```
4. **Deploy**:
   ```bash
   vercel --prod
   ```

After the first successful deploy, the site will be available at
<https://quantmail.vercel.app>. The default admin account is auto-seeded on
first request — log in, change the password, and consider setting
`DEFAULT_ADMIN_DISABLE=true` afterwards.

## 📁 Project Structure

```
Qmail/
├── qmail/                  # Main application package
│   ├── core/              # Core application logic + routes
│   ├── crypto/            # Encryption engine
│   ├── email_handler/     # SMTP/IMAP handlers + attachments
│   ├── km_client/         # Quantum Key Manager client
│   ├── models/            # Database models
│   ├── static/            # CSS, JS, images
│   ├── templates/         # HTML templates
│   └── utils/             # Sanitizers and classifiers
├── tests/                 # Automated test suite (pytest)
├── scripts/               # One-off helper scripts
│   ├── db/                # Database migration helpers
│   ├── dev/               # Setup, demo, diagnostic helpers
│   └── manual_tests/      # Ad-hoc/manual exploration scripts
├── docs/                  # Documentation
├── run.py                 # Local development entry point
├── app.py                 # Vercel / serverless entry point
├── wsgi.py                # WSGI entry point (gunicorn)
├── requirements.txt       # Python dependencies
├── requirements-vercel.txt # Vercel-only minimal dependencies
├── .env.example           # Environment variables template
└── README.md              # This file
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
- [API.md](./docs/API.md) - HTTP API reference
- [ENV_SETUP.md](./docs/ENV_SETUP.md) - Environment configuration
- [VERCEL_POSTGRESQL_SETUP.md](./docs/VERCEL_POSTGRESQL_SETUP.md) - Vercel deployment with Postgres
- [ATTACHMENTS.md](./docs/ATTACHMENTS.md) - Encrypted attachments
- [HTML_EMAIL_RENDERING.md](./docs/HTML_EMAIL_RENDERING.md) - HTML email rendering
- [explain/](./docs/explain/) - In-depth crypto/architecture walkthrough

## 🛠️ Helper Scripts

Utility scripts live under `scripts/`:

- `scripts/db/` - SQLite migrations and schema fixers (e.g. `recreate_database.py`).
- `scripts/dev/` - Developer utilities (`create_admin.py`, `demo.py`, `diagnostic.py`, `setup.py`).
- `scripts/manual_tests/` - Manual / ad-hoc verification scripts.

Run from the project root, for example:
```bash
python scripts/dev/create_admin.py
python scripts/db/recreate_database.py
```

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
**Last Updated**: December 2025
