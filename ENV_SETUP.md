# QMail Environment Setup Guide

## Quick Start - Copy & Paste Values

### Step 1: Create your `.env` file
Copy the values below and create a `.env` file in the project root.

### Step 2: Minimum Configuration (Copy This)
```
FLASK_APP=app.py
FLASK_ENV=development
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
SECRET_KEY=abcdef123456789012345678901234567890abcd
DATABASE_URL=sqlite:///qmail.db
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USE_TLS=true
IMAP_SERVER=imap.gmail.com
IMAP_PORT=993
IMAP_USE_SSL=true
DEFAULT_SECURITY_LEVEL=2
SESSION_TIMEOUT=30
MAX_EMAIL_SIZE=25
LOG_LEVEL=INFO
LOG_FILE=qmail.log
QKD_USE_MOCK=true
```

---

## For Vercel Deployment - Copy These Variables

Go to **Vercel Dashboard** → Your Project → **Settings** → **Environment Variables**

Add these exact values:

| Name | Value | Copy Paste |
|------|-------|-----------|
| `FLASK_APP` | `app.py` | `app.py` |
| `FLASK_ENV` | `production` | `production` |
| `SECRET_KEY` | Random secure key | `a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6` |
| `DATABASE_URL` | PostgreSQL URL | `postgresql://user:password@host.railway.app:5432/qmail` |

---

## Generate a Secure SECRET_KEY

Run this command in PowerShell:
```powershell
python -c "import secrets; print(secrets.token_hex(32))"
```

Example output: `7f8e9d0c1b2a3f4e5d6c7b8a9f0e1d2c3b4a5f6e7d8c9b0a1f2e3d4c5b6a`

Use this value for `SECRET_KEY`

---

## PostgreSQL Connection String (for Production)

If using Railway.app (recommended for Vercel):
```
postgresql://postgres:PASSWORD@containers-us-west-XXX.railway.app:5432/railway
```

If using Render.com:
```
postgresql://qmail_user:qmail_password@dpg-example.render.com:5432/qmail_db
```

---

## Checking Your Configuration

After setting `.env`, run this to verify:
```powershell
cd c:\Users\acer\Downloads\Qmail\Qmail
python diagnostic.py
```

You should see:
```
✓ Flask app created successfully
✓ Config name: development
```

---

## Need Help?

1. **Local Development**: Use `FLASK_ENV=development` and `DATABASE_URL=sqlite:///qmail.db`
2. **Vercel Deployment**: Use `FLASK_ENV=production` and PostgreSQL URL
3. **Email Issues**: Make sure SMTP/IMAP settings match your email provider
4. **Database Issues**: Check PostgreSQL URL format and credentials

