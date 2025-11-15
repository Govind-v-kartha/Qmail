"""
Email Manager - High-level interface for email operations
Combines SMTP and IMAP handlers with encryption
"""

import logging
from typing import List, Dict, Optional
from qmail.email_handler.smtp_handler import SMTPHandler
from qmail.email_handler.imap_handler import IMAPHandler
from qmail.crypto.message_cipher import MessageCipher
from qmail.crypto.encryption_engine import SecurityLevel

logger = logging.getLogger(__name__)


class EmailManager:
    """
    High-level manager for sending and receiving quantum-encrypted emails
    """
    
    def __init__(
        self,
        smtp_config: Dict,
        imap_config: Dict,
        use_mock_qkd: bool = True
    ):
        """
        Initialize email manager
        
        Args:
            smtp_config: SMTP configuration dictionary
            imap_config: IMAP configuration dictionary
            use_mock_qkd: Use mock QKD client (default: True for development)
        """
        self.smtp_handler = SMTPHandler(**smtp_config)
        self.imap_handler = IMAPHandler(**imap_config)
        self.message_cipher = MessageCipher(use_mock_qkd=use_mock_qkd)
        
        logger.info("Email manager initialized")
    
    def send_encrypted_email(
        self,
        from_addr: str,
        to_addrs: List[str],
        subject: str,
        message: str,
        security_level: SecurityLevel = SecurityLevel.QUANTUM_AES,
        cc_addrs: Optional[List[str]] = None,
        encrypted_attachments: Optional[List[Dict]] = None
    ) -> bool:
        """
        Send an encrypted email with optional encrypted attachments
        
        Args:
            from_addr: Sender email address
            to_addrs: List of recipient email addresses
            subject: Email subject
            message: Plain text message to encrypt and send
            security_level: Security level to use for encryption
            cc_addrs: Optional list of CC recipients
            encrypted_attachments: Optional list of encrypted attachments (from AttachmentHandler)
        
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"Sending encrypted email to {len(to_addrs)} recipient(s)")
            
            # Encrypt message
            encrypted_package = self.message_cipher.encrypt_message(
                message=message,
                security_level=security_level
            )
            
            # Send encrypted email with attachments
            success = self.smtp_handler.send_encrypted_email(
                from_addr=from_addr,
                to_addrs=to_addrs,
                subject=subject,
                encrypted_package=encrypted_package,
                cc_addrs=cc_addrs,
                encrypted_attachments=encrypted_attachments
            )
            
            if success:
                logger.info("Encrypted email sent successfully")
            else:
                logger.error("Failed to send encrypted email")
            
            return success
            
        except Exception as e:
            logger.error(f"Error sending encrypted email: {e}")
            return False
    
    def send_plain_email(
        self,
        from_addr: str,
        to_addrs: List[str],
        subject: str,
        body: str,
        html_body: Optional[str] = None,
        cc_addrs: Optional[List[str]] = None
    ) -> bool:
        """
        Send a plain (unencrypted) email
        
        Args:
            from_addr: Sender email address
            to_addrs: List of recipient email addresses
            subject: Email subject
            body: Plain text email body
            html_body: Optional HTML email body
            cc_addrs: Optional list of CC recipients
        
        Returns:
            True if successful, False otherwise
        """
        return self.smtp_handler.send_email(
            from_addr=from_addr,
            to_addrs=to_addrs,
            subject=subject,
            body=body,
            html_body=html_body,
            cc_addrs=cc_addrs
        )
    
    def fetch_emails(
        self,
        folder: str = 'INBOX',
        limit: int = 10,
        unread_only: bool = False
    ) -> List[Dict]:
        """
        Fetch emails from mailbox
        
        Args:
            folder: Folder name (default: INBOX)
            limit: Maximum number of emails to fetch
            unread_only: Fetch only unread emails
        
        Returns:
            List of email dictionaries
        """
        try:
            emails = self.imap_handler.fetch_emails(
                folder=folder,
                limit=limit,
                unread_only=unread_only
            )
            
            logger.info(f"Fetched {len(emails)} email(s)")
            return emails
            
        except Exception as e:
            logger.error(f"Error fetching emails: {e}")
            return []
    
    def fetch_and_decrypt_emails(
        self,
        folder: str = 'INBOX',
        limit: int = 10,
        encrypted_only: bool = False
    ) -> List[Dict]:
        """
        Fetch emails and decrypt quantum-encrypted ones
        
        Args:
            folder: Folder name (default: INBOX)
            limit: Maximum number of emails to fetch
            encrypted_only: Fetch only encrypted emails
        
        Returns:
            List of email dictionaries with decrypted content
        """
        try:
            # Fetch emails
            emails = self.fetch_emails(folder=folder, limit=limit)
            
            # Filter if needed
            if encrypted_only:
                emails = [e for e in emails if e.get('is_encrypted')]
            
            # Decrypt encrypted emails
            for email_data in emails:
                if email_data.get('is_encrypted') and email_data.get('encrypted_package'):
                    try:
                        decrypted_message = self.message_cipher.decrypt_message(
                            email_data['encrypted_package']
                        )
                        email_data['decrypted_body'] = decrypted_message
                        email_data['decryption_success'] = True
                        logger.info(f"Decrypted email: {email_data['id']}")
                    except Exception as e:
                        logger.error(f"Failed to decrypt email {email_data['id']}: {e}")
                        email_data['decryption_success'] = False
                        email_data['decryption_error'] = str(e)
            
            return emails
            
        except Exception as e:
            logger.error(f"Error fetching and decrypting emails: {e}")
            return []
    
    def get_email_count(self, folder: str = 'INBOX') -> int:
        """Get number of emails in a folder"""
        return self.imap_handler.get_email_count(folder)
    
    def list_folders(self) -> List[str]:
        """List all available folders/mailboxes"""
        return self.imap_handler.list_folders()
    
    def mark_as_read(self, email_id: str) -> bool:
        """Mark an email as read"""
        return self.imap_handler.mark_as_read(email_id.encode())
    
    def mark_as_unread(self, email_id: str) -> bool:
        """Mark an email as unread"""
        return self.imap_handler.mark_as_unread(email_id.encode())
    
    def delete_email(self, email_id: str) -> bool:
        """Delete an email"""
        return self.imap_handler.delete_email(email_id.encode())
    
    def get_key_manager_status(self) -> Dict:
        """Get status of the Quantum Key Manager"""
        return self.message_cipher.get_key_manager_status()
    
    def disconnect(self):
        """Disconnect from email servers"""
        self.imap_handler.disconnect()
        logger.info("Email manager disconnected")
