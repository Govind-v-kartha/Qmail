"""
API routes for QMail
"""

from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from datetime import datetime
import logging

from qmail.models.database import db, Email, Contact
from qmail.crypto.message_cipher import MessageCipher
from qmail.crypto.encryption_engine import SecurityLevel

bp = Blueprint('api', __name__, url_prefix='/api')
logger = logging.getLogger(__name__)


@bp.route('/status')
@login_required
def status():
    """Get QMail system status"""
    cipher = MessageCipher(use_mock_qkd=True)
    km_status = cipher.get_key_manager_status()
    
    return jsonify({
        'status': 'operational',
        'user': current_user.username,
        'qkd_status': km_status,
        'timestamp': km_status.get('timestamp')
    })


@bp.route('/encrypt', methods=['POST'])
@login_required
def encrypt_text():
    """Encrypt text via API"""
    data = request.get_json()
    
    if not data or 'message' not in data:
        return jsonify({'error': 'Message is required'}), 400
    
    message = data['message']
    security_level = SecurityLevel(data.get('security_level', 2))
    
    try:
        cipher = MessageCipher(use_mock_qkd=True)
        encrypted_package = cipher.encrypt_message(message, security_level)
        
        return jsonify({
            'success': True,
            'encrypted_package': encrypted_package
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/decrypt', methods=['POST'])
@login_required
def decrypt_text():
    """Decrypt text via API"""
    data = request.get_json()
    
    if not data or 'encrypted_package' not in data:
        return jsonify({'error': 'Encrypted package is required'}), 400
    
    try:
        cipher = MessageCipher(use_mock_qkd=True)
        decrypted_message = cipher.decrypt_message(data['encrypted_package'])
        
        return jsonify({
            'success': True,
            'message': decrypted_message
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/emails')
@login_required
def get_emails():
    """Get emails via API"""
    folder = request.args.get('folder', 'inbox')
    limit = request.args.get('limit', 20, type=int)
    
    emails = Email.query.filter_by(
        user_id=current_user.id,
        folder=folder
    ).order_by(Email.received_at.desc()).limit(limit).all()
    
    return jsonify({
        'success': True,
        'emails': [email.to_dict() for email in emails]
    })


@bp.route('/emails/<int:email_id>')
@login_required
def get_email(email_id):
    """Get specific email via API"""
    email = Email.query.filter_by(id=email_id, user_id=current_user.id).first_or_404()
    
    return jsonify({
        'success': True,
        'email': email.to_dict()
    })


@bp.route('/contacts')
@login_required
def get_contacts():
    """Get contacts via API"""
    contacts = Contact.query.filter_by(user_id=current_user.id).all()
    
    return jsonify({
        'success': True,
        'contacts': [contact.to_dict() for contact in contacts]
    })


@bp.route('/security-levels')
def get_security_levels():
    """Get available security levels"""
    levels = [
        {
            'value': SecurityLevel.QUANTUM_OTP,
            'name': 'QUANTUM_OTP',
            'description': 'Quantum Secure (One-Time Pad) - Perfect Secrecy'
        },
        {
            'value': SecurityLevel.QUANTUM_AES,
            'name': 'QUANTUM_AES',
            'description': 'Quantum-Aided AES - Strong Hybrid Security'
        },
        {
            'value': SecurityLevel.POST_QUANTUM,
            'name': 'POST_QUANTUM',
            'description': 'Post-Quantum Cryptography - Quantum Resistant'
        },
        {
            'value': SecurityLevel.CLASSICAL,
            'name': 'CLASSICAL',
            'description': 'Classical Encryption - Standard AES/RSA'
        }
    ]
    
    return jsonify({
        'success': True,
        'security_levels': levels
    })


@bp.route('/security/log', methods=['POST'])
@login_required
def log_security_event():
    """Log security events from client-side"""
    try:
        data = request.get_json()
        
        if not data or 'type' not in data:
            return jsonify({'error': 'Event type is required'}), 400
        
        # Log the security event
        event_type = data.get('type')
        details = data.get('details', '')
        timestamp = data.get('timestamp', datetime.utcnow().isoformat())
        user_agent = data.get('userAgent', request.headers.get('User-Agent'))
        session_id = data.get('sessionId', '')
        url = data.get('url', '')
        
        # Log to application logger
        logger.warning(
            f"SECURITY EVENT: {event_type} | "
            f"User: {current_user.username} ({current_user.email}) | "
            f"Details: {details} | "
            f"Session: {session_id} | "
            f"URL: {url} | "
            f"Timestamp: {timestamp} | "
            f"User-Agent: {user_agent}"
        )
        
        # TODO: Store in database for audit trail
        # You can create a SecurityLog model to persist these events
        
        return jsonify({
            'success': True,
            'message': 'Security event logged'
        })
        
    except Exception as e:
        logger.error(f"Error logging security event: {e}")
        return jsonify({'error': 'Failed to log event'}), 500
