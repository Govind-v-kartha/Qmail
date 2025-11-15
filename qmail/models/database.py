"""
Database models for QMail
"""

from datetime import datetime, timedelta
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(UserMixin, db.Model):
    """User model for authentication"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    is_verified = db.Column(db.Boolean, default=False)
    
    # Password reset
    reset_token = db.Column(db.String(100))
    reset_token_expiry = db.Column(db.DateTime)
    
    # Account security
    failed_login_attempts = db.Column(db.Integer, default=0)
    account_locked_until = db.Column(db.DateTime)
    
    # Email configuration
    smtp_server = db.Column(db.String(255))
    smtp_port = db.Column(db.Integer, default=587)
    smtp_username = db.Column(db.String(120))
    smtp_password = db.Column(db.String(255))  # Encrypted in production
    
    imap_server = db.Column(db.String(255))
    imap_port = db.Column(db.Integer, default=993)
    imap_username = db.Column(db.String(120))
    imap_password = db.Column(db.String(255))  # Encrypted in production
    
    # QKD preferences
    default_security_level = db.Column(db.Integer, default=2)
    
    # Relationships
    emails = db.relationship('Email', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    contacts = db.relationship('Contact', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verify password"""
        return check_password_hash(self.password_hash, password)
    
    def generate_reset_token(self):
        """Generate password reset token"""
        import secrets
        self.reset_token = secrets.token_urlsafe(32)
        self.reset_token_expiry = datetime.utcnow() + timedelta(hours=1)
        return self.reset_token
    
    def verify_reset_token(self, token):
        """Verify reset token is valid and not expired"""
        if not self.reset_token or not self.reset_token_expiry:
            return False
        if self.reset_token != token:
            return False
        if datetime.utcnow() > self.reset_token_expiry:
            return False
        return True
    
    def clear_reset_token(self):
        """Clear reset token after use"""
        self.reset_token = None
        self.reset_token_expiry = None
    
    def is_account_locked(self):
        """Check if account is locked"""
        if not self.account_locked_until:
            return False
        if datetime.utcnow() > self.account_locked_until:
            # Lock expired, clear it
            self.account_locked_until = None
            self.failed_login_attempts = 0
            return False
        return True
    
    def record_failed_login(self):
        """Record failed login attempt"""
        self.failed_login_attempts += 1
        if self.failed_login_attempts >= 5:
            # Lock account for 30 minutes
            self.account_locked_until = datetime.utcnow() + timedelta(minutes=30)
    
    def reset_failed_logins(self):
        """Reset failed login counter on successful login"""
        self.failed_login_attempts = 0
        self.account_locked_until = None
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'is_active': self.is_active
        }
    
    def __repr__(self):
        return f'<User {self.username}>'


class Email(db.Model):
    """Email message model"""
    __tablename__ = 'emails'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Email metadata
    message_id = db.Column(db.String(255), unique=True)
    from_addr = db.Column(db.String(255), nullable=False)
    to_addr = db.Column(db.Text, nullable=False)  # JSON list
    cc_addr = db.Column(db.Text)  # JSON list
    subject = db.Column(db.String(500))
    
    # Email content
    body = db.Column(db.Text)  # Encrypted JSON or plain text
    preview_text = db.Column(db.String(500))  # Plain text preview for inbox
    preview_html = db.Column(db.Text)  # Sanitized HTML preview for inbox
    
    # Encryption metadata
    is_encrypted = db.Column(db.Boolean, default=False)
    security_level = db.Column(db.Integer)
    security_level_name = db.Column(db.String(50))
    qkd_key_id = db.Column(db.String(255))
    
    # Status
    is_read = db.Column(db.Boolean, default=False)
    is_sent = db.Column(db.Boolean, default=False)
    is_draft = db.Column(db.Boolean, default=False)
    is_starred = db.Column(db.Boolean, default=False)
    is_important = db.Column(db.Boolean, default=False)
    is_spam = db.Column(db.Boolean, default=False)
    is_deleted = db.Column(db.Boolean, default=False)
    
    # Timestamps
    received_at = db.Column(db.DateTime)
    sent_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Folder and Category
    folder = db.Column(db.String(50), default='inbox')
    category = db.Column(db.String(50))  # 'promotional', 'social', 'updates', 'forums', etc.
    
    # Relationships
    attachments = db.relationship('EmailAttachment', backref='email', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'message_id': self.message_id,
            'from': self.from_addr,
            'to': self.to_addr,
            'cc': self.cc_addr,
            'subject': self.subject,
            'body': self.body,
            'preview_text': self.preview_text,
            'preview_html': self.preview_html,
            'is_encrypted': self.is_encrypted,
            'security_level': self.security_level,
            'security_level_name': self.security_level_name,
            'qkd_key_id': self.qkd_key_id,
            'is_read': self.is_read,
            'is_sent': self.is_sent,
            'is_draft': self.is_draft,
            'is_starred': self.is_starred,
            'is_important': self.is_important,
            'is_spam': self.is_spam,
            'received_at': self.received_at.isoformat() if self.received_at else None,
            'sent_at': self.sent_at.isoformat() if self.sent_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'folder': self.folder,
            'category': self.category
        }
    
    def __repr__(self):
        return f'<Email {self.subject}>'


class Contact(db.Model):
    """Contact model"""
    __tablename__ = 'contacts'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(50))
    notes = db.Column(db.Text)
    
    # QKD information
    has_qkd = db.Column(db.Boolean, default=False)
    preferred_security_level = db.Column(db.Integer, default=2)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'notes': self.notes,
            'has_qkd': self.has_qkd,
            'preferred_security_level': self.preferred_security_level,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<Contact {self.name} ({self.email})>'


class KeyUsageLog(db.Model):
    """Log of quantum key usage"""
    __tablename__ = 'key_usage_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    key_id = db.Column(db.String(255), nullable=False)
    security_level = db.Column(db.Integer, nullable=False)
    operation = db.Column(db.String(20), nullable=False)  # 'encrypt' or 'decrypt'
    
    email_id = db.Column(db.Integer, db.ForeignKey('emails.id'))
    
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'key_id': self.key_id,
            'security_level': self.security_level,
            'operation': self.operation,
            'email_id': self.email_id,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }
    
    def __repr__(self):
        return f'<KeyUsageLog {self.key_id} ({self.operation})>'


class Settings(db.Model):
    """Application settings"""
    __tablename__ = 'settings'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Display settings
    emails_per_page = db.Column(db.Integer, default=20)
    theme = db.Column(db.String(20), default='light')
    
    # Security settings
    auto_encrypt = db.Column(db.Boolean, default=True)
    require_encryption = db.Column(db.Boolean, default=False)
    
    # Notification settings
    email_notifications = db.Column(db.Boolean, default=True)
    
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'emails_per_page': self.emails_per_page,
            'theme': self.theme,
            'auto_encrypt': self.auto_encrypt,
            'require_encryption': self.require_encryption,
            'email_notifications': self.email_notifications
        }
    
    def __repr__(self):
        return f'<Settings for User {self.user_id}>'


class EmailAttachment(db.Model):
    """Email attachment model with quantum encryption"""
    __tablename__ = 'email_attachments'
    
    id = db.Column(db.Integer, primary_key=True)
    email_id = db.Column(db.Integer, db.ForeignKey('emails.id'), nullable=False)
    
    # File information
    filename = db.Column(db.String(255), nullable=False)
    content_type = db.Column(db.String(100))
    original_size = db.Column(db.Integer)  # Size before encryption
    encrypted_size = db.Column(db.Integer)  # Size after encryption
    
    # File storage path (instead of storing in database)
    file_path = db.Column(db.String(500))  # Path to encrypted file on disk
    
    # Encrypted content (only for small files < 1MB, otherwise use file_path)
    encrypted_content = db.Column(db.Text)
    
    # Encryption metadata
    key_id = db.Column(db.String(255), nullable=False)
    security_level = db.Column(db.Integer)
    security_level_name = db.Column(db.String(50))
    encryption_metadata = db.Column(db.Text)  # JSON metadata
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'email_id': self.email_id,
            'filename': self.filename,
            'content_type': self.content_type,
            'original_size': self.original_size,
            'encrypted_size': self.encrypted_size,
            'key_id': self.key_id,
            'security_level': self.security_level,
            'security_level_name': self.security_level_name,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<EmailAttachment {self.filename} for Email {self.email_id}>'
