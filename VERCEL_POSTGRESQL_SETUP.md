# Vercel Deployment - PostgreSQL Setup

## 🔴 CRITICAL: Use PostgreSQL, NOT SQLite

SQLite doesn't work on Vercel serverless because:
- File system is ephemeral (temporary)
- Database file disappears after each function call
- Each invocation starts fresh

## ✅ Solution: Use PostgreSQL

### Option 1: Railway.app (Recommended - Easiest)
1. Go to https://railway.app
2. Sign up with GitHub
3. Create new project → PostgreSQL
4. Copy the connection string from Railway dashboard
5. Use it in your DATABASE_URL

**Connection String Format:**
```
postgresql://user:password@containers-us-west-xxx.railway.app:5432/railway
```

### Option 2: Render.com
1. Go to https://render.com
2. Sign up
3. Create new PostgreSQL database
4. Copy connection string

**Connection String Format:**
```
postgresql://qmail_user:qmail_password@dpg-xxx.render.com:5432/qmail
```

### Option 3: AWS RDS
1. Create PostgreSQL database on AWS
2. Get connection string from RDS dashboard

---

## 📝 Update Your Vercel Environment Variables

In Vercel Dashboard → Settings → Environment Variables:

Replace this line:
```
DATABASE_URL=sqlite:///qmail.db
```

With your PostgreSQL URL from Railway/Render/AWS:
```
DATABASE_URL=postgresql://user:password@host:5432/dbname
```

---

## Complete .env for Vercel (Copy This)

```
FLASK_APP=app.py
FLASK_ENV=production
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
SECRET_KEY=a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2
DATABASE_URL=postgresql://user:password@host:5432/qmail
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USE_TLS=true
IMAP_SERVER=imap.gmail.com
IMAP_PORT=993
IMAP_USE_SSL=true
QKD_USE_MOCK=true
DEFAULT_SECURITY_LEVEL=2
SESSION_TIMEOUT=30
MAX_EMAIL_SIZE=25
LOG_LEVEL=INFO
LOG_FILE=qmail.log
```

⚠️ **Replace `postgresql://user:password@host:5432/qmail` with your actual PostgreSQL URL**

---

## Testing

After updating DATABASE_URL:
1. Redeploy on Vercel
2. Check logs: Vercel → Deployments → Logs
3. Visit `/health` endpoint to test
