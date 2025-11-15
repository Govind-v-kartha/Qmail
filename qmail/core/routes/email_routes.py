"""
Email management routes
"""

import json
import logging
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, send_file
from flask_login import login_required, current_user
from datetime import datetime
from werkzeug.utils import secure_filename
import os
from io import BytesIO

from qmail.models.database import db, Email, Contact, EmailAttachment
from qmail.email_handler.email_manager import EmailManager
from qmail.email_handler.attachment_handler import AttachmentHandler, is_allowed_file, format_file_size
from qmail.crypto.encryption_engine import SecurityLevel

bp = Blueprint('email', __name__, url_prefix='/email')
logger = logging.getLogger(__name__)

# Get CSRF instance
from qmail.app import csrf


def get_email_manager():
    """Get email manager for current user"""
    smtp_config = {
        'smtp_server': current_user.smtp_server or 'smtp.gmail.com',
        'smtp_port': current_user.smtp_port or 587,
        'use_tls': True,
        'username': current_user.smtp_username or current_user.email,
        'password': current_user.smtp_password or ''
    }
    
    imap_config = {
        'imap_server': current_user.imap_server or 'imap.gmail.com',
        'imap_port': current_user.imap_port or 993,
        'use_ssl': True,
        'username': current_user.imap_username or current_user.email,
        'password': current_user.imap_password or ''
    }
    
    return EmailManager(smtp_config, imap_config, use_mock_qkd=True)


@bp.route('/inbox')
@login_required
def inbox():
    """Inbox page with HTML preview support"""
    from qmail.utils.html_sanitizer import is_html_email, render_html_preview, extract_preview_text
    from qmail.crypto.message_cipher import MessageCipher
    
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    emails = Email.query.filter_by(
        user_id=current_user.id,
        folder='inbox',
        is_deleted=False
    ).order_by(Email.received_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    # Generate previews for emails that don't have them
    cipher = MessageCipher(use_mock_qkd=True)
    
    for email in emails.items:
        # Skip if preview already exists
        if email.preview_html or email.preview_text:
            continue
            
        try:
            # Get email body
            body = email.body
            
            # Decrypt if encrypted
            if email.is_encrypted and body:
                try:
                    encrypted_package = json.loads(body)
                    body = cipher.decrypt_message(encrypted_package)
                except Exception as e:
                    logger.warning(f"Could not decrypt email {email.id} for preview: {e}")
                    continue
            
            # Generate preview
            if body and is_html_email(body):
                # HTML email - render preview
                email.preview_html = render_html_preview(body, max_height=150)
            elif body:
                # Plain text - extract preview
                email.preview_text = extract_preview_text(body, max_length=200)
            
            # Save preview to database
            db.session.add(email)
            
        except Exception as e:
            logger.error(f"Error generating preview for email {email.id}: {e}")
    
    try:
        db.session.commit()
    except Exception as e:
        logger.error(f"Error saving previews: {e}")
        db.session.rollback()
    
    return render_template('email/inbox.html', emails=emails)


@bp.route('/sent')
@login_required
def sent():
    """Sent emails page"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    emails = Email.query.filter_by(
        user_id=current_user.id,
        is_sent=True
    ).order_by(Email.sent_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return render_template('email/sent.html', emails=emails)


@bp.route('/drafts')
@login_required
def drafts():
    """Drafts page"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    drafts = Email.query.filter_by(
        user_id=current_user.id,
        is_draft=True
    ).order_by(Email.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return render_template('email/drafts.html', drafts=drafts)


@bp.route('/starred')
@login_required
def starred():
    """Starred emails page"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    emails = Email.query.filter_by(
        user_id=current_user.id,
        is_starred=True
    ).order_by(Email.received_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return render_template('email/starred.html', emails=emails)


@bp.route('/important')
@login_required
def important():
    """Important emails page"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    emails = Email.query.filter_by(
        user_id=current_user.id,
        is_important=True
    ).order_by(Email.received_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return render_template('email/important.html', emails=emails)


@bp.route('/spam')
@login_required
def spam():
    """Spam emails page"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    emails = Email.query.filter_by(
        user_id=current_user.id,
        is_spam=True
    ).order_by(Email.received_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return render_template('email/spam.html', emails=emails)


@bp.route('/promotional')
@login_required
def promotional():
    """Promotional emails page"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    emails = Email.query.filter_by(
        user_id=current_user.id,
        category='promotional'
    ).order_by(Email.received_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return render_template('email/promotional.html', emails=emails)


@bp.route('/trash')
@login_required
def trash():
    """Trash emails page"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    emails = Email.query.filter_by(
        user_id=current_user.id,
        is_deleted=True
    ).order_by(Email.received_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return render_template('email/trash.html', emails=emails)


@bp.route('/sync-emails', methods=['POST'])
@csrf.exempt  # AJAX endpoint - protected by login_required
@login_required
def sync_emails():
    """Sync new emails from IMAP server"""
    try:
        # Check if user has configured email settings
        if not current_user.imap_server or not current_user.imap_username:
            return jsonify({
                'success': False,
                'error': 'Please configure your email settings first'
            }), 400
        
        # Get email manager
        email_manager = get_email_manager()
        
        # Fetch new emails
        new_count = email_manager.fetch_emails(limit=50)
        
        return jsonify({
            'success': True,
            'new_emails': new_count if new_count else 0,
            'message': f'Synced {new_count if new_count else 0} new email(s)'
        })
    except AttributeError as e:
        logger.error(f"Email sync configuration error: {e}")
        return jsonify({
            'success': False,
            'error': 'Email settings not configured. Please update your settings.'
        }), 400
    except Exception as e:
        logger.error(f"Email sync error: {e}", exc_info=True)
        # Sanitize error message - don't expose sensitive details
        error_msg = 'Failed to sync emails. Please check your email settings.'
        if 'authentication' in str(e).lower():
            error_msg = 'Authentication failed. Please check your email password.'
        elif 'connection' in str(e).lower():
            error_msg = 'Connection failed. Please check your internet connection.'
        
        return jsonify({
            'success': False,
            'error': error_msg
        }), 500


@bp.route('/compose', methods=['GET', 'POST'])
@login_required
def compose():
    """Compose new email with attachments or edit draft"""
    # Check if editing a draft
    draft_id = request.args.get('draft_id', type=int)
    draft = None
    
    if draft_id:
        draft = Email.query.filter_by(
            id=draft_id,
            user_id=current_user.id,
            is_draft=True
        ).first_or_404()
    
    if request.method == 'POST':
        action = request.form.get('action', 'send')
        to_addr = request.form.get('to', '')
        cc_addr = request.form.get('cc', '')
        subject = request.form.get('subject', '')
        body = request.form.get('body', '')
        security_level = int(request.form.get('security_level', current_user.default_security_level))
        form_draft_id = request.form.get('draft_id', type=int)
        
        # Handle draft save
        if action == 'draft':
            return save_draft_handler(form_draft_id, to_addr, cc_addr, subject, body, security_level)
        
        # Validation for sending
        if not to_addr or not subject or not body:
            flash('Recipient, subject, and message are required', 'error')
            return redirect(url_for('email.compose', draft_id=draft_id))
        
        try:
            # Get email manager
            email_manager = get_email_manager()
            
            # Prepare recipient list
            to_list = [addr.strip() for addr in to_addr.split(',')]
            cc_list = [addr.strip() for addr in cc_addr.split(',')] if cc_addr else None
            
            # Handle file attachments - encrypt them first
            encrypted_attachments_list = []
            attachment_handler = None
            if 'attachments' in request.files:
                attachment_handler = AttachmentHandler(use_mock_qkd=True)
                files = request.files.getlist('attachments')
                
                for file in files:
                    if file and file.filename:
                        # Validate file
                        if not is_allowed_file(file.filename):
                            flash(f'File type not allowed: {file.filename}', 'warning')
                            continue
                        
                        filename = secure_filename(file.filename)
                        file_content = file.read()
                        
                        # Encrypt attachment
                        encrypted_attachment = attachment_handler.encrypt_attachment(
                            filename=filename,
                            content=file_content,
                            security_level=SecurityLevel(security_level)
                        )
                        
                        # Convert to dict for email manager
                        encrypted_attachments_list.append({
                            'filename': encrypted_attachment.filename,
                            'encrypted_content': encrypted_attachment.encrypted_content,
                            'key_id': encrypted_attachment.key_id,
                            'security_level': security_level,
                            'security_level_name': encrypted_attachment.security_level,
                            'content_type': encrypted_attachment.content_type,
                            'original_size': encrypted_attachment.original_size,
                            'metadata': encrypted_attachment.metadata
                        })
            
            # Send encrypted email with attachments
            success = email_manager.send_encrypted_email(
                from_addr=current_user.email,
                to_addrs=to_list,
                subject=subject,
                message=body,
                security_level=SecurityLevel(security_level),
                cc_addrs=cc_list,
                encrypted_attachments=encrypted_attachments_list if encrypted_attachments_list else None
            )
            
            if success:
                # Save to database
                email = Email(
                    user_id=current_user.id,
                    from_addr=current_user.email,
                    to_addr=json.dumps(to_list),
                    cc_addr=json.dumps(cc_list) if cc_list else None,
                    subject=subject,
                    body=body,
                    is_encrypted=True,
                    security_level=security_level,
                    security_level_name=SecurityLevel(security_level).name,
                    is_sent=True,
                    sent_at=datetime.utcnow()
                )
                db.session.add(email)
                db.session.flush()  # Get email ID
                
                # Save attachments to database or disk (they were already encrypted and sent)
                if encrypted_attachments_list:
                    # Create attachments directory if it doesn't exist
                    attachments_dir = os.path.join('instance', 'attachments', f'user_{current_user.id}')
                    os.makedirs(attachments_dir, exist_ok=True)
                    
                    for att_dict in encrypted_attachments_list:
                        encrypted_content = att_dict['encrypted_content']
                        encrypted_size = len(encrypted_content)
                        
                        # Smart storage: small files in DB, large files on disk
                        file_path = None
                        db_content = None
                        
                        # Threshold: 1MB
                        if encrypted_size < 1048576:  # < 1MB
                            # Store in database
                            db_content = encrypted_content
                        else:
                            # Store on disk
                            file_name = f"email_{email.id}_{secure_filename(att_dict['filename'])}.enc"
                            file_path = os.path.join(attachments_dir, file_name)
                            
                            # Write encrypted content to file
                            with open(file_path, 'w') as f:
                                f.write(encrypted_content)
                        
                        db_attachment = EmailAttachment(
                            email_id=email.id,
                            filename=att_dict['filename'],
                            content_type=att_dict['content_type'],
                            original_size=att_dict['original_size'],
                            encrypted_size=encrypted_size,
                            encrypted_content=db_content,  # None for large files
                            file_path=file_path,  # None for small files
                            key_id=att_dict['key_id'],
                            security_level=att_dict['security_level'],
                            security_level_name=att_dict['security_level_name'],
                            encryption_metadata=json.dumps(att_dict['metadata'])
                        )
                        db.session.add(db_attachment)
                    
                db.session.commit()
                
                # Delete draft if this was sent from a draft
                if form_draft_id:
                    try:
                        draft_to_delete = Email.query.filter_by(
                            id=form_draft_id,
                            user_id=current_user.id,
                            is_draft=True
                        ).first()
                        if draft_to_delete:
                            db.session.delete(draft_to_delete)
                            db.session.commit()
                    except Exception as e:
                        logger.warning(f"Could not delete draft after sending: {e}")
                
                # Success message with attachment info
                success_msg = f'Email sent successfully with {SecurityLevel(security_level).name} encryption!'
                if encrypted_attachments_list:
                    success_msg += f' ({len(encrypted_attachments_list)} encrypted attachment{"s" if len(encrypted_attachments_list) > 1 else ""})'
                flash(success_msg, 'success')
                return redirect(url_for('email.sent'))
            else:
                flash('Failed to send email. Please check your email configuration.', 'error')
                
        except Exception as e:
            db.session.rollback()
            flash(f'Error sending email: {str(e)}', 'error')
            return redirect(url_for('email.compose'))
    
    # Get contacts for auto-complete
    contacts = Contact.query.filter_by(user_id=current_user.id).all()
    
    return render_template('email/compose.html', contacts=contacts, draft=draft)


def save_draft_handler(draft_id, to_addr, cc_addr, subject, body, security_level):
    """Helper function to save draft"""
    try:
        if draft_id:
            # Update existing draft
            draft = Email.query.filter_by(
                id=draft_id,
                user_id=current_user.id,
                is_draft=True
            ).first()
            
            if draft:
                draft.to_addr = to_addr  # Store as plain text for drafts
                draft.cc_addr = cc_addr if cc_addr else None
                draft.subject = subject
                draft.body = body
                draft.security_level = security_level
                draft.security_level_name = SecurityLevel(security_level).name
            else:
                flash('Draft not found', 'error')
                return redirect(url_for('email.compose'))
        else:
            # Create new draft
            draft = Email(
                user_id=current_user.id,
                from_addr=current_user.email,
                to_addr=to_addr,
                cc_addr=cc_addr,
                subject=subject,
                body=body,
                is_draft=True,
                is_encrypted=False,
                security_level=security_level,
                security_level_name=SecurityLevel(security_level).name,
                folder='drafts'
            )
            db.session.add(draft)
        
        db.session.commit()
        flash('Draft saved successfully', 'success')
        return redirect(url_for('email.drafts'))
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error saving draft: {e}")
        flash(f'Error saving draft: {str(e)}', 'error')
        return redirect(url_for('email.compose'))


@bp.route('/save-draft', methods=['POST'])
@login_required
def save_draft():
    """Auto-save draft via AJAX"""
    try:
        draft_id = request.form.get('draft_id', type=int)
        to_addr = request.form.get('to', '')
        cc_addr = request.form.get('cc', '')
        subject = request.form.get('subject', '')
        body = request.form.get('body', '')
        security_level = int(request.form.get('security_level', current_user.default_security_level))
        
        if draft_id:
            # Update existing draft
            draft = Email.query.filter_by(
                id=draft_id,
                user_id=current_user.id,
                is_draft=True
            ).first()
            
            if draft:
                draft.to_addr = to_addr  # Store as plain text for drafts
                draft.cc_addr = cc_addr if cc_addr else None
                draft.subject = subject
                draft.body = body
                draft.security_level = security_level
                draft.security_level_name = SecurityLevel(security_level).name
            else:
                return jsonify({'success': False, 'error': 'Draft not found'})
        else:
            # Create new draft
            draft = Email(
                user_id=current_user.id,
                from_addr=current_user.email,
                to_addr=to_addr,  # Store as plain text for drafts
                cc_addr=cc_addr if cc_addr else None,
                subject=subject,
                body=body,
                is_draft=True,
                is_encrypted=False,
                security_level=security_level,
                security_level_name=SecurityLevel(security_level).name,
                folder='drafts'
            )
            db.session.add(draft)
        
        db.session.commit()
        return jsonify({'success': True, 'draft_id': draft.id})
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error auto-saving draft: {e}")
        return jsonify({'success': False, 'error': str(e)})


@bp.route('/draft/<int:draft_id>/delete')
@login_required
def delete_draft(draft_id):
    """Delete a draft"""
    draft = Email.query.filter_by(
        id=draft_id,
        user_id=current_user.id,
        is_draft=True
    ).first_or_404()
    
    try:
        db.session.delete(draft)
        db.session.commit()
        flash('Draft deleted successfully', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting draft: {str(e)}', 'error')
    
    return redirect(url_for('email.drafts'))


@bp.route('/view/<int:email_id>')
@login_required
def view(email_id):
    """View email details with HTML rendering support"""
    from qmail.utils.sanitizer import sanitize_html, sanitize_text
    from qmail.utils.html_sanitizer import is_html_email
    
    email = Email.query.filter_by(id=email_id, user_id=current_user.id).first_or_404()
    
    # Mark as read
    if not email.is_read:
        email.is_read = True
        db.session.commit()
    
    # If encrypted, try to decrypt
    decrypted_body = None
    decryption_error = None
    is_html_content = False
    
    if email.is_encrypted and email.body:
        try:
            from qmail.crypto.message_cipher import MessageCipher
            cipher = MessageCipher(use_mock_qkd=True)
            
            # Try to parse email body as JSON (encrypted package)
            try:
                encrypted_package = json.loads(email.body)
            except json.JSONDecodeError:
                # Body might contain the encrypted package within text
                # Look for JSON content
                body_text = email.body
                start_idx = body_text.find('{')
                end_idx = body_text.rfind('}') + 1
                
                if start_idx >= 0 and end_idx > start_idx:
                    json_str = body_text[start_idx:end_idx]
                    encrypted_package = json.loads(json_str)
                else:
                    raise ValueError("Could not find encrypted package in email body")
            
            # Decrypt the message
            decrypted_body = cipher.decrypt_message(encrypted_package)
            
            # Check if HTML and sanitize
            if is_html_email(decrypted_body):
                is_html_content = True
                decrypted_body = sanitize_html(decrypted_body)
            
        except Exception as e:
            decryption_error = f"Decryption failed: {str(e)}"
            logger.error(f"Failed to decrypt email {email_id}: {e}")
    else:
        # Not encrypted - check if HTML
        if email.body and is_html_email(email.body):
            is_html_content = True
            email.body = sanitize_html(email.body)
    
    return render_template(
        'email/view.html',
        email=email,
        decrypted_body=decrypted_body,
        decryption_error=decryption_error,
        is_html_content=is_html_content
    )


@bp.route('/sync')
@login_required
def sync():
    """Sync emails from server"""
    try:
        from qmail.utils.email_classifier import EmailClassifier
        
        email_manager = get_email_manager()
        classifier = EmailClassifier(user_id=current_user.id)
        
        # Fetch recent emails
        emails = email_manager.fetch_and_decrypt_emails(limit=20)
        
        # Save to database
        new_count = 0
        for email_data in emails:
            # Check if email already exists
            existing = Email.query.filter_by(
                user_id=current_user.id,
                message_id=email_data.get('id')
            ).first()
            
            if not existing:
                # Classify email
                subject = email_data.get('subject', '')
                body = email_data.get('body', '')
                from_addr = email_data.get('from', '')
                
                category, is_spam, confidence = classifier.classify_email(subject, body, from_addr)
                
                email = Email(
                    user_id=current_user.id,
                    message_id=email_data.get('id'),
                    from_addr=from_addr,
                    to_addr=json.dumps([email_data.get('to', '')]),
                    subject=subject,
                    body=json.dumps(email_data.get('encrypted_package')) if email_data.get('is_encrypted') else body,
                    is_encrypted=email_data.get('is_encrypted', False),
                    security_level=int(email_data.get('qkd_security_level', 0)) if email_data.get('qkd_security_level') else None,
                    qkd_key_id=email_data.get('qkd_key_id', ''),
                    received_at=datetime.utcnow(),
                    folder='spam' if is_spam else 'inbox',
                    is_spam=is_spam,
                    category=category if category != 'primary' else None
                )
                db.session.add(email)
                db.session.flush()  # Get email ID
                
                # Save attachments if present
                attachments = email_data.get('attachments', [])
                if attachments:
                    for att_data in attachments:
                        # Only save encrypted QMail attachments
                        if att_data.get('is_encrypted') and att_data.get('encrypted_package'):
                            enc_pkg = att_data['encrypted_package']
                            db_attachment = EmailAttachment(
                                email_id=email.id,
                                filename=enc_pkg.get('filename', att_data['filename']),
                                content_type=enc_pkg.get('content_type', att_data['content_type']),
                                original_size=enc_pkg.get('original_size', att_data['size']),
                                encrypted_size=att_data['size'],
                                encrypted_content=enc_pkg.get('encrypted_content', ''),
                                key_id=enc_pkg.get('key_id', ''),
                                security_level=enc_pkg.get('security_level', 2),
                                security_level_name=enc_pkg.get('security_level_name', 'QUANTUM_AES'),
                                encryption_metadata=json.dumps(enc_pkg.get('metadata', {}))
                            )
                            db.session.add(db_attachment)
                
                new_count += 1
        
        if new_count > 0:
            db.session.commit()
            flash(f'Synced {new_count} new email(s)', 'success')
        else:
            flash('No new emails', 'info')
            
    except Exception as e:
        flash(f'Sync failed: {str(e)}', 'error')
    
    return redirect(url_for('email.inbox'))


@bp.route('/delete/<int:email_id>')
@login_required
def delete(email_id):
    """Move email to trash (soft delete)"""
    email = Email.query.filter_by(id=email_id, user_id=current_user.id).first_or_404()
    
    # Soft delete - move to trash
    email.is_deleted = True
    email.folder = 'trash'
    db.session.commit()
    
    flash('Email moved to trash', 'info')
    return redirect(url_for('email.inbox'))


@bp.route('/attachment/<int:attachment_id>/download')
@login_required
def download_attachment(attachment_id):
    """Download and decrypt an attachment"""
    # Get attachment
    attachment = EmailAttachment.query.get_or_404(attachment_id)
    
    # Verify user owns the email
    email = Email.query.filter_by(id=attachment.email_id, user_id=current_user.id).first_or_404()
    
    try:
        # Initialize attachment handler
        attachment_handler = AttachmentHandler(use_mock_qkd=True)
        
        # Load encrypted content from database or disk
        encrypted_content = attachment.encrypted_content
        if not encrypted_content and attachment.file_path:
            # Load from disk
            if os.path.exists(attachment.file_path):
                with open(attachment.file_path, 'r') as f:
                    encrypted_content = f.read()
            else:
                flash('Attachment file not found on disk', 'error')
                return redirect(url_for('email.view', email_id=email.id))
        
        # Create EncryptedAttachment object
        from qmail.email_handler.attachment_handler import EncryptedAttachment
        encrypted_attachment = EncryptedAttachment(
            filename=attachment.filename,
            encrypted_content=encrypted_content,
            content_type=attachment.content_type,
            original_size=attachment.original_size,
            encrypted_size=attachment.encrypted_size,
            key_id=attachment.key_id,
            security_level=attachment.security_level_name,
            metadata=json.loads(attachment.encryption_metadata)
        )
        
        # Decrypt attachment
        decrypted_attachment = attachment_handler.decrypt_attachment(encrypted_attachment)
        
        # Send file to user
        return send_file(
            BytesIO(decrypted_attachment.content),
            as_attachment=True,
            download_name=decrypted_attachment.filename,
            mimetype=decrypted_attachment.content_type
        )
        
    except Exception as e:
        flash(f'Error downloading attachment: {str(e)}', 'error')
        return redirect(url_for('email.view', email_id=email.id))


@bp.route('/attachment/<int:attachment_id>/inline')
@login_required
def view_attachment_inline(attachment_id):
    """View attachment inline (for images)"""
    # Get attachment
    attachment = EmailAttachment.query.get_or_404(attachment_id)
    
    # Verify user owns the email
    email = Email.query.filter_by(id=attachment.email_id, user_id=current_user.id).first_or_404()
    
    try:
        # Initialize attachment handler
        attachment_handler = AttachmentHandler(use_mock_qkd=True)
        
        # Load encrypted content from database or disk
        encrypted_content = attachment.encrypted_content
        if not encrypted_content and attachment.file_path:
            # Load from disk
            if os.path.exists(attachment.file_path):
                with open(attachment.file_path, 'r') as f:
                    encrypted_content = f.read()
            else:
                from flask import abort
                abort(404)
        
        # Create EncryptedAttachment object
        from qmail.email_handler.attachment_handler import EncryptedAttachment
        encrypted_attachment = EncryptedAttachment(
            filename=attachment.filename,
            encrypted_content=encrypted_content,
            content_type=attachment.content_type,
            original_size=attachment.original_size,
            encrypted_size=attachment.encrypted_size,
            key_id=attachment.key_id,
            security_level=attachment.security_level_name,
            metadata=json.loads(attachment.encryption_metadata)
        )
        
        # Decrypt attachment
        decrypted_attachment = attachment_handler.decrypt_attachment(encrypted_attachment)
        
        # Send file inline (not as download)
        return send_file(
            BytesIO(decrypted_attachment.content),
            mimetype=decrypted_attachment.content_type,
            as_attachment=False,
            download_name=decrypted_attachment.filename
        )
        
    except Exception as e:
        # Return error image or placeholder
        from flask import abort
        abort(404)


@bp.route('/attachment/<int:attachment_id>/view')
@login_required
def view_attachment(attachment_id):
    """View attachment info"""
    attachment = EmailAttachment.query.get_or_404(attachment_id)
    
    # Verify user owns the email
    email = Email.query.filter_by(id=attachment.email_id, user_id=current_user.id).first_or_404()
    
    return jsonify({
        'success': True,
        'attachment': {
            'id': attachment.id,
            'filename': attachment.filename,
            'content_type': attachment.content_type,
            'original_size': attachment.original_size,
            'original_size_formatted': format_file_size(attachment.original_size),
            'encrypted_size': attachment.encrypted_size,
            'encrypted_size_formatted': format_file_size(attachment.encrypted_size),
            'key_id': attachment.key_id,
            'security_level': attachment.security_level_name,
            'created_at': attachment.created_at.isoformat() if attachment.created_at else None
        }
    })


@bp.route('/contacts')
@login_required
def contacts():
    """Contacts page"""
    contacts = Contact.query.filter_by(user_id=current_user.id).all()
    return render_template('email/contacts.html', contacts=contacts)


@bp.route('/contacts/add', methods=['GET', 'POST'])
@login_required
def add_contact():
    """Add new contact"""
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone', '')
        has_qkd = request.form.get('has_qkd') == 'on'
        preferred_security_level = int(request.form.get('preferred_security_level', 2))
        
        if not name or not email:
            flash('Name and email are required', 'error')
            return redirect(url_for('email.add_contact'))
        
        contact = Contact(
            user_id=current_user.id,
            name=name,
            email=email,
            phone=phone,
            has_qkd=has_qkd,
            preferred_security_level=preferred_security_level
        )
        
        db.session.add(contact)
        db.session.commit()
        
        flash(f'Contact {name} added successfully', 'success')
        return redirect(url_for('email.contacts'))
    
    return render_template('email/add_contact.html')


@bp.route('/action/<int:email_id>/toggle_star', methods=['POST'])
@csrf.exempt  # AJAX endpoint - uses JSON
@login_required
def toggle_star(email_id):
    """Toggle starred status"""
    try:
        email = Email.query.filter_by(id=email_id, user_id=current_user.id).first_or_404()
        email.is_starred = not email.is_starred
        db.session.commit()
        
        return jsonify({
            'success': True,
            'is_starred': email.is_starred
        })
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error toggling star: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to update star status. Please try again.'
        }), 500


@bp.route('/action/<int:email_id>/toggle_important', methods=['POST'])
@csrf.exempt  # AJAX endpoint - uses JSON
@login_required
def toggle_important(email_id):
    """Toggle important status"""
    try:
        email = Email.query.filter_by(id=email_id, user_id=current_user.id).first_or_404()
        email.is_important = not email.is_important
        db.session.commit()
        
        return jsonify({
            'success': True,
            'is_important': email.is_important
        })
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error toggling important: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to update important status. Please try again.'
        }), 500


@bp.route('/action/<int:email_id>/mark_spam', methods=['POST'])
@csrf.exempt  # AJAX endpoint - uses JSON
@login_required
def mark_spam(email_id):
    """Mark email as spam and learn pattern"""
    try:
        email = Email.query.filter_by(id=email_id, user_id=current_user.id).first_or_404()
        email.is_spam = True
        email.folder = 'spam'
        db.session.commit()
        
        # Try to learn pattern (non-blocking)
        try:
            from qmail.models.spam_pattern import SpamPattern
            
            sender_email = email.from_addr
            if sender_email and '@' in sender_email:
                domain = sender_email.split('@')[1].lower()
                
                # Check if pattern exists
                existing_pattern = SpamPattern.query.filter_by(
                    user_id=current_user.id,
                    sender_domain=domain,
                    pattern_type='spam'
                ).first()
                
                if existing_pattern:
                    existing_pattern.match_count += 1
                    existing_pattern.correct_count += 1
                    existing_pattern.updated_at = datetime.utcnow()
                else:
                    new_pattern = SpamPattern(
                        user_id=current_user.id,
                        sender_domain=domain,
                        pattern_type='spam',
                        match_count=1,
                        correct_count=1
                    )
                    db.session.add(new_pattern)
                
                db.session.commit()
                logger.info(f"Learned spam pattern: {domain}")
        except Exception as learn_error:
            logger.warning(f"Could not learn spam pattern: {learn_error}")
            # Don't fail the whole operation if learning fails
        
        return jsonify({
            'success': True,
            'message': 'Email marked as spam'
        })
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error marking spam: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to mark as spam. Please try again.'
        }), 500


@bp.route('/action/<int:email_id>/not_spam', methods=['POST'])
@csrf.exempt  # AJAX endpoint - uses JSON
@login_required
def not_spam(email_id):
    """Mark email as not spam"""
    try:
        email = Email.query.filter_by(id=email_id, user_id=current_user.id).first_or_404()
        email.is_spam = False
        email.folder = 'inbox'
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Email moved to inbox'
        })
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error marking not spam: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to move email. Please try again.'
        }), 500


@bp.route('/restore/<int:email_id>', methods=['POST'])
@csrf.exempt  # AJAX endpoint
@login_required
def restore_email(email_id):
    """Restore email from trash"""
    try:
        email = Email.query.filter_by(id=email_id, user_id=current_user.id).first_or_404()
        email.is_deleted = False
        email.folder = 'inbox'
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Error restoring email: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/permanent-delete/<int:email_id>', methods=['POST'])
@csrf.exempt  # AJAX endpoint
@login_required
def permanent_delete(email_id):
    """Permanently delete email"""
    try:
        email = Email.query.filter_by(id=email_id, user_id=current_user.id).first_or_404()
        db.session.delete(email)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Error permanently deleting email: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/empty-trash', methods=['POST'])
@csrf.exempt  # AJAX endpoint
@login_required
def empty_trash():
    """Empty all emails from trash"""
    try:
        deleted_count = Email.query.filter_by(
            user_id=current_user.id,
            is_deleted=True
        ).delete()
        db.session.commit()
        return jsonify({'success': True, 'deleted_count': deleted_count})
    except Exception as e:
        logger.error(f"Error emptying trash: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
