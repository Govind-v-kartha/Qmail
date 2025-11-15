# HTML Email Rendering in QMail

## 🎨 Overview

QMail now supports **rich HTML email rendering** directly in the inbox, similar to Gmail. View styled emails, images, tables, and formatted content without leaving the inbox view.

---

## ✨ Key Features

### 1. Inbox HTML Previews
- ✅ Renders HTML emails directly in inbox list
- ✅ Shows images, styled text, and tables
- ✅ Max height preview with fade effect
- ✅ Safe HTML sanitization (XSS protection)

### 2. Full HTML Email View
- ✅ Complete HTML rendering in email view
- ✅ Responsive design
- ✅ External links open in new tab
- ✅ Inline images supported

### 3. Security Features
- ✅ **HTML Sanitization** - Removes dangerous scripts
- ✅ **XSS Protection** - Bleach + BeautifulSoup filtering
- ✅ **Safe CSS** - Only allowed style properties
- ✅ **Link Safety** - `rel="noopener noreferrer nofollow"`
- ✅ **Quantum Encryption** - HTML emails can be encrypted

---

## 🔒 Security Implementation

### HTML Sanitization Pipeline

```
Raw HTML Email
      ↓
Remove Scripts & Event Handlers
      ↓
Filter Allowed Tags & Attributes
      ↓
Sanitize Inline CSS
      ↓
Make Links Safe
      ↓
Add Responsive Wrapper
      ↓
Safe HTML Output
```

### Allowed HTML Tags

```python
ALLOWED_TAGS = [
    'a', 'abbr', 'b', 'br', 'blockquote', 'code', 'div', 'em', 'font',
    'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'hr', 'i', 'img', 'li', 'ol',
    'p', 'pre', 'small', 'span', 'strong', 'sub', 'sup', 'table', 'tbody',
    'td', 'th', 'thead', 'tr', 'u', 'ul', 'center', 'strike', 's',
]
```

### Allowed Attributes

```python
ALLOWED_ATTRIBUTES = {
    '*': ['style', 'class', 'id'],
    'a': ['href', 'title', 'rel', 'target'],
    'img': ['src', 'alt', 'title', 'width', 'height', 'style'],
    'table': ['border', 'cellpadding', 'cellspacing', 'width', 'style'],
    'td': ['colspan', 'rowspan', 'align', 'valign', 'style'],
    ...
}
```

### Blocked Content

❌ **Removed:**
- `<script>` tags
- Event handlers (`onclick`, `onload`, etc.)
- `javascript:` URLs
- `data:` URIs (except images)
- CSS `expression()`
- Dangerous CSS properties

---

## 📁 New Files Created

### 1. `qmail/utils/html_sanitizer.py`

**Functions:**
- `sanitize_html(html_content)` - Main sanitization
- `is_html_email(content)` - Detect HTML emails
- `render_html_preview(html, max_height)` - Create inbox preview
- `extract_preview_text(html, max_length)` - Extract plain text
- `extract_images_from_html(html)` - Find all images
- `strip_html_tags(html)` - Convert to plain text

**Usage:**
```python
from qmail.utils.html_sanitizer import sanitize_html, is_html_email

if is_html_email(email_body):
    safe_html = sanitize_html(email_body)
```

### 2. Database Updates

**Email Model - New Fields:**
```python
class Email(db.Model):
    # ... existing fields ...
    preview_text = db.Column(db.String(500))  # Plain text preview
    preview_html = db.Column(db.Text)  # Sanitized HTML preview
```

---

## 🎨 UI Components

### Inbox Preview

```html
<div class="email-preview">
    <div class="email-html-content">
        <!-- Sanitized HTML rendered here -->
        <p>Hello <b>John</b>!</p>
        <img src="logo.png" alt="Logo">
    </div>
</div>
```

**Styling:**
- Max height: 150px
- Overflow: hidden
- Fade effect at bottom
- Border-left: 3px accent

### Full Email View

```html
<div class="email-html-body">
    <div class="email-html-content">
        <!-- Complete sanitized HTML -->
    </div>
</div>
```

**Styling:**
- Full content displayed
- Responsive images (max-width: 100%)
- Tables adapt to container
- Safe link styling

---

## 🚀 How It Works

### 1. Email Sync

```python
# When syncing emails from IMAP
emails = email_manager.fetch_and_decrypt_emails(limit=20)

for email_data in emails:
    # Detect if HTML
    if is_html_email(email_data['body']):
        # Generate preview
        preview_html = render_html_preview(email_data['body'])
        email.preview_html = preview_html
    else:
        # Plain text preview
        email.preview_text = extract_preview_text(email_data['body'])
```

### 2. Inbox Display

```python
@bp.route('/inbox')
def inbox():
    emails = Email.query.filter_by(user_id=current_user.id).all()
    
    for email in emails:
        # Generate preview if not exists
        if not email.preview_html and not email.preview_text:
            body = decrypt_if_needed(email.body)
            
            if is_html_email(body):
                email.preview_html = render_html_preview(body)
            else:
                email.preview_text = extract_preview_text(body)
    
    return render_template('inbox.html', emails=emails)
```

### 3. Email View

```python
@bp.route('/view/<int:email_id>')
def view(email_id):
    email = Email.query.get(email_id)
    body = decrypt_if_needed(email.body)
    
    is_html = is_html_email(body)
    if is_html:
        body = sanitize_html(body)  # Make safe
    
    return render_template('view.html', 
                         email=email, 
                         body=body,
                         is_html=is_html)
```

---

## 📋 Examples

### Example 1: LinkedIn Email

**Input (Raw HTML):**
```html
<html>
<head>
  <style>
    .text { font-size: 20px; font-weight: 400; line-height: 28px; }
    .footer a { text-decoration: none !important; color: #ffffff !important; }
  </style>
</head>
<body>
  <div class="text">
    <p>Hi <b>Afnan</b>,</p>
    <p>You have <b>5 new connections</b> waiting for you!</p>
    <a href="https://linkedin.com/...">View Connections</a>
  </div>
</body>
</html>
```

**Output (Sanitized):**
```html
<div class="email-html-content">
  <div class="text" style="font-size: 20px; font-weight: 400; line-height: 28px;">
    <p>Hi <b>Afnan</b>,</p>
    <p>You have <b>5 new connections</b> waiting for you!</p>
    <a href="https://linkedin.com/..." rel="noopener noreferrer nofollow" target="_blank">
      View Connections
    </a>
  </div>
</div>
```

### Example 2: IRCTC Email

**Input:**
```html
<HR/>
<B>This is a system generated mail. Please do not reply.</B><BR/>
Dear <B>afnan K,</B><BR/><BR/>
Your user id is <font color="red"><B>afnankanhirala</B></font>.<BR/>
Please <a href="www.irctc.co.in">Click Here</a> to login.<BR/>
```

**Output (Inbox Preview):**
```
Dear afnan K,
Your user id is afnankanhirala.
Please Click Here to login...
```

---

## 🎨 CSS Customization

### Inbox Preview Styling

```css
.email-preview {
    max-height: 150px;
    overflow: hidden;
    position: relative;
    border-left: 3px solid #e9ecef;
    padding-left: 10px;
}

.email-preview::after {
    content: '';
    position: absolute;
    bottom: 0;
    height: 30px;
    background: linear-gradient(to bottom, transparent, white);
}

.email-preview img {
    max-height: 120px;
    object-fit: contain;
    margin: 5px;
}
```

### Full Email Styling

```css
.email-html-body {
    padding: 20px;
    background: white;
    border: 1px solid #dee2e6;
    border-radius: 8px;
}

.email-html-body img {
    max-width: 100%;
    height: auto;
}

.email-html-body a {
    color: #0066cc;
    text-decoration: underline;
}
```

---

## 🔧 Configuration

### Install Dependencies

```bash
pip install bleach==6.1.0 beautifulsoup4==4.12.2 lxml==4.9.3
```

### Database Migration

```bash
# Add new fields to Email model
flask db migrate -m "Add HTML preview fields"
flask db upgrade
```

---

## 🐛 Troubleshooting

### Issue 1: HTML not rendering

**Symptoms:** Emails show as plain text

**Cause:** `is_html_email()` not detecting HTML

**Solution:**
```python
# Check if email contains HTML tags
if '<html' in email_body.lower() or '<div' in email_body.lower():
    # Force HTML rendering
    email.preview_html = render_html_preview(email_body)
```

### Issue 2: Images not displaying

**Symptoms:** Broken image icons

**Causes:**
- External images blocked
- Base64 images stripped
- Image URL invalid

**Solutions:**
```python
# Allow data: URIs for images
html = re.sub(r'src\s*=\s*["\']data:(?!image)[^"\']*["\']', 'src="#"', html)
# ↑ This keeps image data URIs

# For external images, ensure they're allowed
ALLOWED_ATTRIBUTES = {
    'img': ['src', 'alt', 'width', 'height', 'style']
}
```

### Issue 3: XSS warning in console

**Symptoms:** Browser console shows security warnings

**Cause:** Unsafe HTML passed to template

**Solution:**
```python
# Always sanitize before rendering
body = sanitize_html(raw_html)

# In template, use |safe filter ONLY after sanitization
{{ body|safe }}
```

### Issue 4: Preview not saving

**Symptoms:** Previews regenerate every time

**Cause:** Database not committing

**Solution:**
```python
email.preview_html = render_html_preview(body)
db.session.add(email)
db.session.commit()  # ← Don't forget!
```

---

## 📊 Performance

### Optimization Strategies

**1. Cache Previews**
```python
if email.preview_html:  # Use cached
    return email.preview_html
else:  # Generate and cache
    preview = render_html_preview(body)
    email.preview_html = preview
    db.session.commit()
```

**2. Lazy Loading**
```python
# Generate previews only for visible emails
for email in emails[:20]:  # First 20 only
    if not email.preview_html:
        generate_preview(email)
```

**3. Background Processing**
```python
# Generate previews async (future enhancement)
@celery.task
def generate_email_previews(email_id):
    email = Email.query.get(email_id)
    email.preview_html = render_html_preview(email.body)
    db.session.commit()
```

---

## 🔮 Future Enhancements

### Planned Features
- [ ] Dark mode support for HTML emails
- [ ] Better table responsive handling
- [ ] Inline style to CSS extraction
- [ ] Email template detection (newsletters, etc.)
- [ ] "View Original" button
- [ ] Print-friendly version
- [ ] Email archiving with HTML preservation

### Advanced Features
- [ ] Spam detection using HTML analysis
- [ ] Phishing link detection
- [ ] Automatic image proxying
- [ ] Email categorization by HTML structure
- [ ] Custom CSS themes for emails

---

## 📚 Related Documentation

- **HTML Sanitizer API:** [qmail/utils/html_sanitizer.py](../qmail/utils/html_sanitizer.py)
- **Email Model:** [qmail/models/database.py](../qmail/models/database.py)
- **Email Routes:** [qmail/core/routes/email_routes.py](../qmail/core/routes/email_routes.py)
- **Inbox Template:** [qmail/templates/email/inbox.html](../qmail/templates/email/inbox.html)

---

## 🎉 Summary

**What's New:**
- ✅ HTML email rendering in inbox
- ✅ Safe HTML sanitization (XSS protected)
- ✅ Inline images in previews
- ✅ Responsive design
- ✅ Quantum-encrypted HTML support

**Benefits:**
- 📧 Better email viewing experience
- 🎨 See styled emails as intended
- 🔒 Maintains security
- 📱 Works on all devices
- ⚡ Fast preview generation

**Try it now!**
1. Sync emails with HTML content
2. Open inbox - see rich previews
3. Click email - see full HTML rendering
4. Send HTML emails - they render beautifully!

---

**Last Updated:** October 13, 2025  
**Feature Version:** 1.0  
**Status:** ✅ Complete
