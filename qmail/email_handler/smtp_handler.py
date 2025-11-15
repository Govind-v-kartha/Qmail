"""
SMTP Handler for sending emails
"""

import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import List, Optional, Dict
import json

logger = logging.getLogger(__name__)


class SMTPHandler:
    """Handler for sending emails via SMTP"""
    
    def __init__(
        self,
        smtp_server: str,
        smtp_port: int = 587,
        use_tls: bool = True,
        username: Optional[str] = None,
        password: Optional[str] = None
    ):
        """
        Initialize SMTP handler
        
        Args:
            smtp_server: SMTP server hostname
            smtp_port: SMTP port (default: 587 for TLS)
            use_tls: Use TLS encryption (default: True)
            username: SMTP username
            password: SMTP password
        """
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.use_tls = use_tls
        self.username = username
        self.password = password
        
        logger.info(f"SMTP handler initialized: {smtp_server}:{smtp_port}")
    
    def send_email(
        self,
        from_addr: str,
        to_addrs: List[str],
        subject: str,
        body: str,
        html_body: Optional[str] = None,
        cc_addrs: Optional[List[str]] = None,
        bcc_addrs: Optional[List[str]] = None,
        attachments: Optional[List[Dict]] = None,
        custom_headers: Optional[Dict[str, str]] = None
    ) -> bool:
        """
        Send an email via SMTP
        
        Args:
            from_addr: Sender email address
            to_addrs: List of recipient email addresses
            subject: Email subject
            body: Plain text email body
            html_body: Optional HTML email body
            cc_addrs: Optional list of CC recipients
            bcc_addrs: Optional list of BCC recipients
            attachments: Optional list of attachments
            custom_headers: Optional custom headers (e.g., X-QKD-KeyID)
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = from_addr
            msg['To'] = ', '.join(to_addrs)
            msg['Subject'] = subject
            
            if cc_addrs:
                msg['Cc'] = ', '.join(cc_addrs)
            
            # Add custom headers (for QKD metadata)
            if custom_headers:
                for key, value in custom_headers.items():
                    msg[key] = value
            
            # Add body parts
            if body:
                msg.attach(MIMEText(body, 'plain', 'utf-8'))
            
            if html_body:
                msg.attach(MIMEText(html_body, 'html', 'utf-8'))
            
            # Add attachments
            if attachments:
                for attachment in attachments:
                    self._add_attachment(msg, attachment)
            
            # Prepare recipient list
            all_recipients = to_addrs.copy()
            if cc_addrs:
                all_recipients.extend(cc_addrs)
            if bcc_addrs:
                all_recipients.extend(bcc_addrs)
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                if self.use_tls:
                    server.starttls()
                
                if self.username and self.password:
                    server.login(self.username, self.password)
                
                server.send_message(msg, from_addr, all_recipients)
            
            logger.info(f"Email sent successfully to {len(all_recipients)} recipient(s)")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False
    
    def send_encrypted_email(
        self,
        from_addr: str,
        to_addrs: List[str],
        subject: str,
        encrypted_package: Dict,
        cc_addrs: Optional[List[str]] = None,
        encrypted_attachments: Optional[List[Dict]] = None
    ) -> bool:
        """
        Send an encrypted email with QKD metadata and encrypted attachments
        
        Args:
            from_addr: Sender email address
            to_addrs: List of recipient email addresses
            subject: Email subject (will be prefixed with [ENCRYPTED])
            encrypted_package: Encrypted message package from MessageCipher
            cc_addrs: Optional list of CC recipients
            encrypted_attachments: Optional list of encrypted attachments
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Prepare encrypted body as JSON
            encrypted_body = json.dumps(encrypted_package, indent=2)
            
            # Add custom headers for QKD metadata
            custom_headers = {
                'X-QKD-KeyID': encrypted_package.get('key_id', ''),
                'X-QKD-Security-Level': str(encrypted_package.get('security_level', 2)),
                'X-QKD-Security-Level-Name': encrypted_package.get('security_level_name', 'QUANTUM_AES'),
                'X-QKD-Encrypted': 'true'
            }
            
            # If there are attachments, add metadata
            if encrypted_attachments:
                custom_headers['X-QKD-Has-Attachments'] = 'true'
                custom_headers['X-QKD-Attachment-Count'] = str(len(encrypted_attachments))
            
            # Prefix subject
            encrypted_subject = f"[QMail Encrypted] {subject}"
            if encrypted_attachments:
                encrypted_subject += f" ({len(encrypted_attachments)} attachment{'s' if len(encrypted_attachments) > 1 else ''})"
            
            # Plain text notice for non-QMail clients
            attachment_notice = ""
            if encrypted_attachments:
                attachment_notice = f"\n\nEncrypted Attachments: {len(encrypted_attachments)}"
                for att in encrypted_attachments:
                    attachment_notice += f"\n  • {att.get('filename', 'Unknown')} ({att.get('security_level_name', 'N/A')} encryption)"
            
            plain_notice = (
                "🔒 QUANTUM-ENCRYPTED EMAIL\n"
                "=" * 60 + "\n\n"
                "This email was sent using QMail - Quantum-Secure Email Client.\n"
                "The message content is encrypted and cannot be read in regular email clients.\n\n"
                "To read this message, you need:\n"
                "  1. QMail client installed (https://github.com/yourusername/qmail)\n"
                "  2. Access to the same Quantum Key Manager\n"
                "  3. The Key ID shown below\n\n"
                "ENCRYPTION DETAILS:\n"
                f"  • Key ID: {encrypted_package.get('key_id', 'N/A')}\n"
                f"  • Security Level: {encrypted_package.get('security_level_name', 'N/A')}\n"
                f"  • Algorithm: {encrypted_package.get('metadata', {}).get('algorithm', 'N/A')}"
                f"{attachment_notice}\n\n"
                "=" * 60 + "\n"
                "For more information about QMail, visit: https://github.com/yourusername/qmail\n"
                "=" * 60 + "\n\n"
                "--- ENCRYPTED PAYLOAD (For QMail Client Only) ---\n"
                f"{encrypted_body}"
            )
            
            # HTML notice for better presentation in email clients
            attachment_html = ""
            if encrypted_attachments:
                attachment_html = f"<p><strong>Encrypted Attachments:</strong> {len(encrypted_attachments)}</p><ul>"
                for att in encrypted_attachments:
                    attachment_html += f"<li>{att.get('filename', 'Unknown')} ({att.get('security_level_name', 'N/A')} encryption)</li>"
                attachment_html += "</ul>"
            
            html_notice = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                    .header h1 {{ margin: 0; font-size: 24px; }}
                    .header p {{ margin: 10px 0 0 0; opacity: 0.9; }}
                    .content {{ background: #f8f9fa; padding: 30px; border-radius: 0 0 10px 10px; }}
                    .info-box {{ background: white; border-left: 4px solid #667eea; padding: 15px; margin: 20px 0; border-radius: 5px; }}
                    .info-box h3 {{ margin-top: 0; color: #667eea; }}
                    .info-item {{ margin: 8px 0; }}
                    .info-item strong {{ color: #555; }}
                    .steps {{ background: white; padding: 20px; margin: 20px 0; border-radius: 5px; }}
                    .steps ol {{ margin: 10px 0; padding-left: 20px; }}
                    .steps li {{ margin: 10px 0; }}
                    .footer {{ text-align: center; margin-top: 30px; padding-top: 20px; border-top: 2px solid #e0e0e0; color: #666; font-size: 14px; }}
                    .button {{ display: inline-block; background: #667eea; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                    .encrypted-data {{ display: none; }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>🔒 Quantum-Encrypted Email</h1>
                    <p>Secured with QMail - Quantum-Secure Email Client</p>
                </div>
                
                <div class="content">
                    <p>This email was sent using <strong>QMail</strong>, a quantum-secure email client. The message content is encrypted and cannot be read in regular email clients like Gmail, Outlook, or Apple Mail.</p>
                    
                    <div class="info-box">
                        <h3>📋 Encryption Details</h3>
                        <div class="info-item"><strong>Key ID:</strong> {encrypted_package.get('key_id', 'N/A')}</div>
                        <div class="info-item"><strong>Security Level:</strong> {encrypted_package.get('security_level_name', 'N/A')}</div>
                        <div class="info-item"><strong>Algorithm:</strong> {encrypted_package.get('metadata', {}).get('algorithm', 'N/A')}</div>
                    </div>
                    
                    {attachment_html}
                    
                    <div class="steps">
                        <h3>📖 How to Read This Email</h3>
                        <ol>
                            <li><strong>Install QMail Client</strong> - Download from the official repository</li>
                            <li><strong>Configure Quantum Key Manager</strong> - Connect to the same QKD system</li>
                            <li><strong>Use the Key ID</strong> - The encrypted content will be automatically decrypted</li>
                        </ol>
                    </div>
                    
                    <div style="text-align: center;">
                        <a href="https://github.com/yourusername/qmail" class="button">Get QMail Client</a>
                    </div>
                    
                    <div class="footer">
                        <p><strong>QMail</strong> - Quantum-Secure Email Communication</p>
                        <p>For more information, visit our documentation</p>
                    </div>
                </div>
                
                <!-- Encrypted payload hidden from view but available for QMail client -->
                <div class="encrypted-data" style="display:none;">
                    {encrypted_body}
                </div>
            </body>
            </html>
            """
            
            # Prepare attachments for SMTP (convert encrypted attachments to MIME format)
            smtp_attachments = []
            if encrypted_attachments:
                for att in encrypted_attachments:
                    # Create JSON package for each encrypted attachment
                    att_package = {
                        'filename': att.get('filename'),
                        'encrypted_content': att.get('encrypted_content'),
                        'key_id': att.get('key_id'),
                        'security_level': att.get('security_level'),
                        'security_level_name': att.get('security_level_name'),
                        'content_type': att.get('content_type'),
                        'original_size': att.get('original_size'),
                        'metadata': att.get('metadata')
                    }
                    
                    # Encode as JSON and convert to bytes for attachment
                    att_data = json.dumps(att_package, indent=2).encode('utf-8')
                    
                    # Add encrypted extension to show it's encrypted
                    filename = f"{att.get('filename', 'attachment')}.qmail_enc"
                    
                    smtp_attachments.append({
                        'filename': filename,
                        'data': att_data
                    })
            
            # Send email with attachments and HTML body
            return self.send_email(
                from_addr=from_addr,
                to_addrs=to_addrs,
                subject=encrypted_subject,
                body=plain_notice,
                html_body=html_notice,
                cc_addrs=cc_addrs,
                custom_headers=custom_headers,
                attachments=smtp_attachments if smtp_attachments else None
            )
            
        except Exception as e:
            logger.error(f"Failed to send encrypted email: {e}")
            return False
    
    def _add_attachment(self, msg: MIMEMultipart, attachment: Dict):
        """Add an attachment to the email message"""
        try:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment['data'])
            encoders.encode_base64(part)
            part.add_header(
                'Content-Disposition',
                f"attachment; filename= {attachment['filename']}"
            )
            msg.attach(part)
            logger.debug(f"Added attachment: {attachment['filename']}")
        except Exception as e:
            logger.error(f"Failed to add attachment: {e}")
