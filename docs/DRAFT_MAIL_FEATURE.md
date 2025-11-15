# Draft Mail Feature in QMail

## 📝 Overview

QMail now includes a **complete draft mail system** that allows users to save, edit, and manage email drafts with auto-save functionality.

---

## ✨ Key Features

### 1. Manual Save as Draft
- ✅ "Save as Draft" button in compose form
- ✅ Saves recipient, subject, body, and security level
- ✅ Redirects to Drafts page after saving

### 2. Auto-Save Functionality
- ✅ Automatically saves every 3 seconds of inactivity
- ✅ Visual indicator shows save status
- ✅ Works in background via AJAX
- ✅ No page refresh required

### 3. Draft Management
- ✅ Dedicated Drafts page
- ✅ List all saved drafts
- ✅ Edit existing drafts
- ✅ Delete drafts
- ✅ Preview draft content

### 4. Edit & Send
- ✅ Open draft for editing
- ✅ Continue composing
- ✅ Send email (draft auto-deleted)
- ✅ Save again to update draft

---

## 🎯 User Flow

### Creating a Draft

```
1. User clicks "Compose"
   ↓
2. Starts typing email
   ↓
3. After 3 seconds → Auto-save triggers
   ↓
4. "Draft saved" notification appears
   ↓
5. User can continue or leave
   ↓
6. Draft saved in database
```

### Editing a Draft

```
1. User navigates to "Drafts"
   ↓
2. Clicks "Edit" on a draft
   ↓
3. Compose form opens with draft data
   ↓
4. User edits content
   ↓
5. Auto-save updates the draft
   ↓
6. User sends or saves manually
```

### Sending from Draft

```
1. User opens draft
   ↓
2. Completes email
   ↓
3. Clicks "Send Encrypted"
   ↓
4. Email sent successfully
   ↓
5. Draft automatically deleted
   ↓
6. Redirected to Sent folder
```

---

## 🎨 UI Components

### Compose Form with Draft Controls

```html
┌────────────────────────────────────────┐
│  Compose New Email                     │
├────────────────────────────────────────┤
│  To: recipient@example.com             │
│  CC: (Optional)                        │
│  Subject: Meeting Tomorrow             │
│  Security Level: Quantum-AES ⭐        │
│                                        │
│  Message:                              │
│  ┌────────────────────────────────┐   │
│  │ Let's meet at 3 PM...          │   │
│  │                                 │   │
│  └────────────────────────────────┘   │
│                                        │
│  [Send Encrypted] [Save as Draft]     │
│                                        │
│  ● Auto-save enabled                   │
└────────────────────────────────────────┘
```

### Drafts List Page

```html
┌────────────────────────────────────────┐
│  Drafts                  [New Draft]   │
├────────────────────────────────────────┤
│  📄 Meeting Tomorrow                   │
│  To: bob@example.com                   │
│  Let's meet at 3 PM...                 │
│  📎 2 attachments                      │
│  2025-10-13 10:30    [Edit] [Delete]  │
├────────────────────────────────────────┤
│  📄 Project Update                     │
│  To: team@example.com                  │
│  Here's the latest progress...         │
│  2025-10-12 15:45    [Edit] [Delete]  │
└────────────────────────────────────────┘
```

### Auto-Save Status Indicators

```
● Auto-save enabled        (Gray - Ready)
● Pending changes...       (Yellow - Waiting)
● Saving draft...          (Blue - Spinning)
● Draft saved             (Green - Success)
● Auto-save failed        (Red - Error)
```

---

## 🔧 Implementation Details

### Database Schema

**Email Model - Draft Fields:**
```python
class Email(db.Model):
    # ... existing fields ...
    is_draft = db.Column(db.Boolean, default=False)
    folder = db.Column(db.String(50), default='inbox')
    
    # For drafts:
    # is_draft = True
    # is_sent = False
    # is_encrypted = False (draft not encrypted until sent)
    # folder = 'drafts'
```

### Routes

**1. Drafts List**
```python
@bp.route('/drafts')
@login_required
def drafts():
    """Show all drafts"""
    drafts = Email.query.filter_by(
        user_id=current_user.id,
        is_draft=True
    ).order_by(Email.created_at.desc()).paginate()
    
    return render_template('email/drafts.html', drafts=drafts)
```

**2. Save Draft (Manual)**
```python
@bp.route('/compose', methods=['POST'])
def compose():
    action = request.form.get('action')
    
    if action == 'draft':
        # Save as draft
        draft = Email(
            user_id=current_user.id,
            to_addr=to_addr,
            subject=subject,
            body=body,
            is_draft=True,
            folder='drafts'
        )
        db.session.add(draft)
        db.session.commit()
        
        return redirect(url_for('email.drafts'))
```

**3. Auto-Save Draft (AJAX)**
```python
@bp.route('/save-draft', methods=['POST'])
@login_required
def save_draft():
    """Auto-save draft via AJAX"""
    draft_id = request.form.get('draft_id')
    
    if draft_id:
        # Update existing
        draft = Email.query.get(draft_id)
        draft.to_addr = request.form.get('to')
        draft.subject = request.form.get('subject')
        draft.body = request.form.get('body')
    else:
        # Create new
        draft = Email(...)
        db.session.add(draft)
    
    db.session.commit()
    return jsonify({'success': True, 'draft_id': draft.id})
```

**4. Edit Draft**
```python
@bp.route('/compose?draft_id=<id>')
def compose():
    draft_id = request.args.get('draft_id')
    
    if draft_id:
        draft = Email.query.filter_by(
            id=draft_id,
            is_draft=True
        ).first_or_404()
        
        return render_template('compose.html', draft=draft)
```

**5. Delete Draft**
```python
@bp.route('/draft/<int:draft_id>/delete')
@login_required
def delete_draft(draft_id):
    """Delete a draft"""
    draft = Email.query.filter_by(
        id=draft_id,
        is_draft=True
    ).first_or_404()
    
    db.session.delete(draft)
    db.session.commit()
    
    return redirect(url_for('email.drafts'))
```

---

## 📋 Auto-Save Implementation

### JavaScript Auto-Save Logic

```javascript
let autosaveTimeout;
let isDirty = false;

// Track changes
['to', 'cc', 'subject', 'body'].forEach(fieldId => {
    document.getElementById(fieldId).addEventListener('input', () => {
        isDirty = true;
        scheduleAutosave();
    });
});

function scheduleAutosave() {
    clearTimeout(autosaveTimeout);
    updateStatus('pending');
    
    // Wait 3 seconds after last change
    autosaveTimeout = setTimeout(() => {
        if (isDirty) {
            autosaveDraft();
        }
    }, 3000);
}

function autosaveDraft() {
    const formData = new FormData(document.getElementById('compose-form'));
    formData.set('action', 'autosave');
    
    updateStatus('saving');
    
    fetch('/email/save-draft', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            isDirty = false;
            updateStatus('saved');
            
            // Update draft_id for future saves
            if (data.draft_id && !document.querySelector('[name="draft_id"]')) {
                const input = document.createElement('input');
                input.type = 'hidden';
                input.name = 'draft_id';
                input.value = data.draft_id;
                form.appendChild(input);
            }
        } else {
            updateStatus('error');
        }
    })
    .catch(error => {
        console.error('Auto-save error:', error);
        updateStatus('error');
    });
}

function updateStatus(state) {
    const statusElement = document.getElementById('autosave-status');
    
    switch(state) {
        case 'pending':
            statusElement.innerHTML = '<i class="fas fa-circle text-warning"></i> Pending changes...';
            break;
        case 'saving':
            statusElement.innerHTML = '<i class="fas fa-spinner fa-spin text-primary"></i> Saving draft...';
            break;
        case 'saved':
            statusElement.innerHTML = '<i class="fas fa-check-circle text-success"></i> Draft saved';
            setTimeout(() => {
                statusElement.innerHTML = '<i class="fas fa-circle text-secondary"></i> Auto-save enabled';
            }, 2000);
            break;
        case 'error':
            statusElement.innerHTML = '<i class="fas fa-exclamation-circle text-danger"></i> Auto-save failed';
            break;
    }
}
```

---

## 🔒 Security Considerations

### Draft Storage

**Not Encrypted in Database:**
- Drafts stored as plain text in database
- Only encrypted when sent as email
- Reduces complexity for editing
- User controls when encryption happens

**Why Not Encrypt Drafts?**
1. User needs to edit repeatedly
2. Decryption required for every edit
3. Performance impact
4. Drafts are personal (not transmitted)

**Security Measures:**
- Database access restricted to user
- User authentication required
- No external access to drafts
- SSL/TLS for database connections

---

## 📊 Features Comparison

| Feature | Traditional Email | QMail Drafts |
|---------|------------------|--------------|
| Manual Save | ✅ Yes | ✅ Yes |
| Auto-Save | ❌ No | ✅ Yes (3 sec) |
| Visual Status | ❌ No | ✅ Yes |
| Edit Existing | ✅ Yes | ✅ Yes |
| Delete Draft | ✅ Yes | ✅ Yes |
| Auto-Delete on Send | ✅ Yes | ✅ Yes |
| Quantum Encryption | ❌ No | ✅ Yes (on send) |
| Attachments Support | ✅ Yes | 🔄 Future |

---

## 🚀 Usage Examples

### Example 1: Basic Draft Save

```python
# User composes email
to = "alice@example.com"
subject = "Project Update"
body = "Here's the latest progress..."

# User clicks "Save as Draft"
# System creates:
draft = Email(
    user_id=1,
    from_addr="user@example.com",
    to_addr="alice@example.com",
    subject="Project Update",
    body="Here's the latest progress...",
    is_draft=True,
    is_encrypted=False,
    folder='drafts',
    created_at=datetime.utcnow()
)
```

### Example 2: Auto-Save Scenario

```
Time 0:00 - User types "Hello Alice,"
Time 0:03 - Auto-save triggers → Draft created (ID: 123)
Time 0:10 - User types more text
Time 0:13 - Auto-save triggers → Draft 123 updated
Time 0:20 - User closes browser
Time 1:00 - User returns → Opens draft 123
Time 1:05 - User completes email
Time 1:10 - User sends → Draft 123 deleted
```

### Example 3: API Usage

**Create Draft:**
```bash
curl -X POST http://localhost:5000/email/save-draft \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "to=alice@example.com" \
  -d "subject=Test" \
  -d "body=Hello" \
  -d "security_level=2"
```

**Response:**
```json
{
  "success": true,
  "draft_id": 123
}
```

**Update Draft:**
```bash
curl -X POST http://localhost:5000/email/save-draft \
  -d "draft_id=123" \
  -d "body=Updated content"
```

---

## 🐛 Troubleshooting

### Issue 1: Auto-save not working

**Symptoms:** Status stays at "Auto-save disabled"

**Causes:**
- JavaScript not loaded
- Form ID mismatch
- Route not configured

**Solution:**
```javascript
// Check if form exists
const form = document.getElementById('compose-form');
if (!form) {
    console.error('Compose form not found!');
}

// Check route
fetch('/email/save-draft', {method: 'POST'})
  .then(r => console.log('Route OK'))
  .catch(e => console.error('Route error:', e));
```

### Issue 2: Draft not saving

**Symptoms:** "Auto-save failed" message

**Causes:**
- Database error
- User not authenticated
- Missing fields

**Solution:**
```python
# Check server logs
logger.error(f"Error saving draft: {e}")

# Verify user auth
if not current_user.is_authenticated:
    return jsonify({'success': False, 'error': 'Not authenticated'})

# Check database
try:
    db.session.commit()
except Exception as e:
    db.session.rollback()
    logger.error(f"DB error: {e}")
```

### Issue 3: Draft not loading

**Symptoms:** Empty compose form when editing

**Causes:**
- Draft_id not passed correctly
- Query filter wrong
- Template not updated

**Solution:**
```python
# Debug draft loading
draft = Email.query.filter_by(
    id=draft_id,
    user_id=current_user.id,
    is_draft=True
).first()

if not draft:
    logger.error(f"Draft {draft_id} not found for user {current_user.id}")
    
# Check template
{{ draft.subject if draft else '' }}
```

---

## 🔮 Future Enhancements

### Planned Features
- [ ] Draft attachments support
- [ ] Multiple draft versions (history)
- [ ] Draft templates
- [ ] Scheduled send from draft
- [ ] Draft sharing/collaboration
- [ ] Draft folders/categories
- [ ] Draft search functionality
- [ ] Export drafts

### Advanced Features
- [ ] Offline draft editing
- [ ] Real-time collaborative drafts
- [ ] AI-powered draft suggestions
- [ ] Draft analytics (time spent, edits)
- [ ] Version control for drafts
- [ ] Draft backup/restore

---

## 📚 Related Documentation

- **Email Routes:** [qmail/core/routes/email_routes.py](../qmail/core/routes/email_routes.py)
- **Database Models:** [qmail/models/database.py](../qmail/models/database.py)
- **Compose Template:** [qmail/templates/email/compose.html](../qmail/templates/email/compose.html)
- **Drafts Template:** [qmail/templates/email/drafts.html](../qmail/templates/email/drafts.html)

---

## 🎉 Summary

**What's New:**
- ✅ Manual draft saving
- ✅ Auto-save every 3 seconds
- ✅ Draft management page
- ✅ Edit existing drafts
- ✅ Delete drafts
- ✅ Visual status indicators
- ✅ Navigation menu link

**Benefits:**
- 📧 Never lose email progress
- 💾 Automatic background saving
- ✏️ Continue composing later
- 🔒 Quantum encryption when sent
- 📱 Works on all devices
- ⚡ Fast and responsive

**Try it now!**
1. Click "Compose"
2. Start typing an email
3. Wait 3 seconds - see "Draft saved"
4. Close browser and return
5. Go to "Drafts" - your work is saved!

---

**Last Updated:** October 13, 2025  
**Feature Version:** 1.0  
**Status:** ✅ Complete
