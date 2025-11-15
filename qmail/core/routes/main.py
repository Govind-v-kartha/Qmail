"""
Main application routes
"""

from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user

from qmail.models.database import db, Email, Contact

bp = Blueprint('main', __name__)


@bp.route('/')
def index():
    """Home page"""
    if current_user.is_authenticated:
        return redirect(url_for('email.inbox'))
    return redirect(url_for('auth.login'))


@bp.route('/dashboard')
@login_required
def dashboard():
    """Dashboard page"""
    # Get statistics
    inbox_count = Email.query.filter_by(
        user_id=current_user.id,
        folder='inbox',
        is_read=False
    ).count()
    
    sent_count = Email.query.filter_by(
        user_id=current_user.id,
        is_sent=True
    ).count()
    
    encrypted_count = Email.query.filter_by(
        user_id=current_user.id,
        is_encrypted=True
    ).count()
    
    contact_count = Contact.query.filter_by(user_id=current_user.id).count()
    
    # Get recent emails
    recent_emails = Email.query.filter_by(
        user_id=current_user.id
    ).order_by(Email.created_at.desc()).limit(5).all()
    
    stats = {
        'inbox_count': inbox_count,
        'sent_count': sent_count,
        'encrypted_count': encrypted_count,
        'contact_count': contact_count
    }
    
    return render_template('main/dashboard.html', stats=stats, recent_emails=recent_emails)


@bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    """Settings page"""
    from flask import request, flash
    from qmail.models.database import Settings
    
    user_settings = Settings.query.filter_by(user_id=current_user.id).first()
    if not user_settings:
        user_settings = Settings(user_id=current_user.id)
        db.session.add(user_settings)
        db.session.commit()
    
    if request.method == 'POST':
        # Update email configuration
        current_user.smtp_server = request.form.get('smtp_server')
        current_user.smtp_port = int(request.form.get('smtp_port', 587))
        current_user.smtp_username = request.form.get('smtp_username')
        
        current_user.imap_server = request.form.get('imap_server')
        current_user.imap_port = int(request.form.get('imap_port', 993))
        current_user.imap_username = request.form.get('imap_username')
        
        # Update passwords if provided
        smtp_password = request.form.get('smtp_password')
        if smtp_password:
            current_user.smtp_password = smtp_password  # Encrypt in production
        
        imap_password = request.form.get('imap_password')
        if imap_password:
            current_user.imap_password = imap_password  # Encrypt in production
        
        # Update preferences
        current_user.default_security_level = int(request.form.get('default_security_level', 2))
        
        # Update settings
        user_settings.emails_per_page = int(request.form.get('emails_per_page', 20))
        user_settings.theme = request.form.get('theme', 'light')
        user_settings.auto_encrypt = request.form.get('auto_encrypt') == 'on'
        
        db.session.commit()
        
        flash('Settings updated successfully', 'success')
        return redirect(url_for('main.settings'))
    
    return render_template('main/settings.html', settings=user_settings)


@bp.route('/about')
def about():
    """About page"""
    return render_template('main/about.html')


@bp.route('/support')
@login_required
def support():
    """Support page"""
    return render_template('main/support.html')
