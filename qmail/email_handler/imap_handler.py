"""
IMAP Handler for receiving emails
"""

import imaplib
import email
import logging
import json
from email.header import decode_header
from typing import List, Dict, Optional, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)


class IMAPHandler:
    """Handler for receiving emails via IMAP"""
    
    def __init__(
        self,
        imap_server: str,
        imap_port: int = 993,
        use_ssl: bool = True,
        username: Optional[str] = None,
        password: Optional[str] = None
    ):
        """
        Initialize IMAP handler
        
        Args:
            imap_server: IMAP server hostname
            imap_port: IMAP port (default: 993 for SSL)
            use_ssl: Use SSL encryption (default: True)
            username: IMAP username
            password: IMAP password
        """
        self.imap_server = imap_server
        self.imap_port = imap_port
        self.use_ssl = use_ssl
        self.username = username
        self.password = password
        self.connection = None
        
        logger.info(f"IMAP handler initialized: {imap_server}:{imap_port}")
    
    def connect(self) -> bool:
        """
        Connect to IMAP server
        
        Returns:
            True if successful, False otherwise
        """
        try:
            if self.use_ssl:
                self.connection = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
            else:
                self.connection = imaplib.IMAP4(self.imap_server, self.imap_port)
            
            if self.username and self.password:
                self.connection.login(self.username, self.password)
            
            logger.info("IMAP connection established")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to IMAP server: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from IMAP server"""
        try:
            if self.connection:
                self.connection.logout()
                logger.info("IMAP connection closed")
        except Exception as e:
            logger.error(f"Error disconnecting from IMAP: {e}")
    
    def list_folders(self) -> List[str]:
        """
        List all available folders/mailboxes
        
        Returns:
            List of folder names
        """
        try:
            if not self.connection:
                self.connect()
            
            status, folders = self.connection.list()
            folder_names = []
            
            if status == 'OK':
                for folder in folders:
                    # Parse folder name from IMAP response
                    folder_str = folder.decode()
                    folder_name = folder_str.split('"')[-2]
                    folder_names.append(folder_name)
            
            return folder_names
            
        except Exception as e:
            logger.error(f"Failed to list folders: {e}")
            return []
    
    def select_folder(self, folder: str = 'INBOX') -> bool:
        """
        Select a folder to read messages from
        
        Args:
            folder: Folder name (default: INBOX)
        
        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.connection:
                self.connect()
            
            status, messages = self.connection.select(folder)
            if status == 'OK':
                logger.info(f"Selected folder: {folder}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Failed to select folder: {e}")
            return False
    
    def get_email_count(self, folder: str = 'INBOX') -> int:
        """
        Get number of emails in a folder
        
        Args:
            folder: Folder name (default: INBOX)
        
        Returns:
            Number of emails
        """
        try:
            self.select_folder(folder)
            status, messages = self.connection.search(None, 'ALL')
            
            if status == 'OK':
                email_ids = messages[0].split()
                return len(email_ids)
            return 0
            
        except Exception as e:
            logger.error(f"Failed to get email count: {e}")
            return 0
    
    def fetch_emails(
        self,
        folder: str = 'INBOX',
        limit: int = 10,
        unread_only: bool = False
    ) -> List[Dict]:
        """
        Fetch emails from a folder
        
        Args:
            folder: Folder name (default: INBOX)
            limit: Maximum number of emails to fetch
            unread_only: Fetch only unread emails
        
        Returns:
            List of email dictionaries
        """
        try:
            if not self.connection:
                self.connect()
            
            self.select_folder(folder)
            
            # Search for emails
            search_criteria = 'UNSEEN' if unread_only else 'ALL'
            status, messages = self.connection.search(None, search_criteria)
            
            if status != 'OK':
                return []
            
            email_ids = messages[0].split()
            emails = []
            
            # Fetch most recent emails (up to limit)
            for email_id in reversed(email_ids[-limit:]):
                email_data = self.fetch_email_by_id(email_id)
                if email_data:
                    emails.append(email_data)
            
            logger.info(f"Fetched {len(emails)} email(s) from {folder}")
            return emails
            
        except Exception as e:
            logger.error(f"Failed to fetch emails: {e}")
            return []
    
    def fetch_email_by_id(self, email_id: bytes) -> Optional[Dict]:
        """
        Fetch a single email by ID
        
        Args:
            email_id: Email ID (from IMAP search)
        
        Returns:
            Email dictionary or None
        """
        try:
            status, msg_data = self.connection.fetch(email_id, '(RFC822)')
            
            if status != 'OK':
                return None
            
            # Parse email message
            raw_email = msg_data[0][1]
            msg = email.message_from_bytes(raw_email)
            
            # Extract email data
            email_data = {
                'id': email_id.decode(),
                'subject': self._decode_header(msg.get('Subject', '')),
                'from': self._decode_header(msg.get('From', '')),
                'to': self._decode_header(msg.get('To', '')),
                'date': msg.get('Date', ''),
                'body': self._get_email_body(msg),
                'is_encrypted': msg.get('X-QKD-Encrypted', 'false') == 'true',
                'qkd_key_id': msg.get('X-QKD-KeyID', ''),
                'qkd_security_level': msg.get('X-QKD-Security-Level', ''),
                'qkd_security_level_name': msg.get('X-QKD-Security-Level-Name', ''),
                'has_attachments': msg.get('X-QKD-Has-Attachments', 'false') == 'true',
                'attachment_count': int(msg.get('X-QKD-Attachment-Count', '0')),
                'headers': dict(msg.items())
            }
            
            # Extract attachments (including encrypted .qmail_enc files)
            email_data['attachments'] = self._extract_attachments(msg)
            
            # If encrypted, extract encrypted package
            if email_data['is_encrypted']:
                email_data['encrypted_package'] = self._extract_encrypted_package(
                    email_data['body']
                )
            
            return email_data
            
        except Exception as e:
            logger.error(f"Failed to fetch email by ID: {e}")
            return None
    
    def _decode_header(self, header: str) -> str:
        """Decode email header"""
        try:
            decoded_parts = decode_header(header)
            decoded_header = ''
            
            for part, encoding in decoded_parts:
                if isinstance(part, bytes):
                    decoded_header += part.decode(encoding or 'utf-8', errors='ignore')
                else:
                    decoded_header += str(part)
            
            return decoded_header
        except Exception as e:
            logger.error(f"Failed to decode header: {e}")
            return header
    
    def _get_email_body(self, msg: email.message.Message) -> str:
        """Extract email body"""
        try:
            body = ''
            
            if msg.is_multipart():
                for part in msg.walk():
                    content_type = part.get_content_type()
                    content_disposition = str(part.get('Content-Disposition', ''))
                    
                    if content_type == 'text/plain' and 'attachment' not in content_disposition:
                        payload = part.get_payload(decode=True)
                        if payload:
                            body += payload.decode('utf-8', errors='ignore')
            else:
                payload = msg.get_payload(decode=True)
                if payload:
                    body = payload.decode('utf-8', errors='ignore')
            
            return body
            
        except Exception as e:
            logger.error(f"Failed to extract email body: {e}")
            return ''
    
    def _extract_attachments(self, msg: email.message.Message) -> List[Dict]:
        """Extract attachments from email message"""
        attachments = []
        
        try:
            if msg.is_multipart():
                for part in msg.walk():
                    content_disposition = str(part.get('Content-Disposition', ''))
                    
                    # Check if this part is an attachment
                    if 'attachment' in content_disposition:
                        filename = part.get_filename()
                        if filename:
                            filename = self._decode_header(filename)
                            
                            # Get attachment data
                            payload = part.get_payload(decode=True)
                            
                            if payload:
                                attachment_data = {
                                    'filename': filename,
                                    'content_type': part.get_content_type(),
                                    'size': len(payload),
                                    'data': payload
                                }
                                
                                # Check if it's an encrypted QMail attachment (.qmail_enc)
                                if filename.endswith('.qmail_enc'):
                                    try:
                                        # Parse JSON content
                                        encrypted_package = json.loads(payload.decode('utf-8'))
                                        attachment_data['is_encrypted'] = True
                                        attachment_data['encrypted_package'] = encrypted_package
                                        attachment_data['original_filename'] = encrypted_package.get('filename', filename)
                                        attachment_data['key_id'] = encrypted_package.get('key_id', '')
                                        attachment_data['security_level_name'] = encrypted_package.get('security_level_name', '')
                                        attachment_data['original_size'] = encrypted_package.get('original_size', 0)
                                    except:
                                        # Not a valid QMail encrypted attachment
                                        attachment_data['is_encrypted'] = False
                                else:
                                    attachment_data['is_encrypted'] = False
                                
                                attachments.append(attachment_data)
            
            logger.debug(f"Extracted {len(attachments)} attachment(s)")
            return attachments
            
        except Exception as e:
            logger.error(f"Failed to extract attachments: {e}")
            return []
    
    def _extract_encrypted_package(self, body: str) -> Optional[Dict]:
        """Extract encrypted package from email body"""
        try:
            # Look for JSON content in body
            start_idx = body.find('{')
            end_idx = body.rfind('}') + 1
            
            if start_idx >= 0 and end_idx > start_idx:
                json_str = body[start_idx:end_idx]
                encrypted_package = json.loads(json_str)
                return encrypted_package
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to extract encrypted package: {e}")
            return None
    
    def mark_as_read(self, email_id: bytes) -> bool:
        """Mark an email as read"""
        try:
            self.connection.store(email_id, '+FLAGS', '\\Seen')
            return True
        except Exception as e:
            logger.error(f"Failed to mark email as read: {e}")
            return False
    
    def mark_as_unread(self, email_id: bytes) -> bool:
        """Mark an email as unread"""
        try:
            self.connection.store(email_id, '-FLAGS', '\\Seen')
            return True
        except Exception as e:
            logger.error(f"Failed to mark email as unread: {e}")
            return False
    
    def delete_email(self, email_id: bytes) -> bool:
        """Delete an email"""
        try:
            self.connection.store(email_id, '+FLAGS', '\\Deleted')
            self.connection.expunge()
            return True
        except Exception as e:
            logger.error(f"Failed to delete email: {e}")
            return False
