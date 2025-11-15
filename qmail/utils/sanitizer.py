"""
HTML Sanitization Utility
Prevents XSS attacks in email content
"""

import bleach
from bleach.css_sanitizer import CSSSanitizer

# Allowed HTML tags
ALLOWED_TAGS = [
    'p', 'br', 'strong', 'em', 'u', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    'blockquote', 'code', 'pre', 'hr', 'div', 'span',
    'ul', 'ol', 'li', 'a', 'img', 'table', 'thead', 'tbody', 'tr', 'th', 'td'
]

# Allowed attributes
ALLOWED_ATTRIBUTES = {
    'a': ['href', 'title', 'target'],
    'img': ['src', 'alt', 'title', 'width', 'height'],
    'div': ['class'],
    'span': ['class'],
    'table': ['class'],
    'td': ['colspan', 'rowspan'],
    'th': ['colspan', 'rowspan'],
}

# Allowed CSS properties
css_sanitizer = CSSSanitizer(allowed_css_properties=['color', 'background-color', 'font-weight'])


def sanitize_html(html_content):
    """
    Sanitize HTML content to prevent XSS attacks
    
    Args:
        html_content: Raw HTML string
        
    Returns:
        Sanitized HTML string
    """
    if not html_content:
        return ''
    
    # Clean HTML
    clean_html = bleach.clean(
        html_content,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        css_sanitizer=css_sanitizer,
        strip=True,
        strip_comments=True
    )
    
    # Linkify URLs (make them clickable)
    clean_html = bleach.linkify(clean_html)
    
    return clean_html


def sanitize_text(text_content):
    """
    Sanitize plain text (escape HTML)
    
    Args:
        text_content: Plain text string
        
    Returns:
        HTML-escaped string
    """
    if not text_content:
        return ''
    
    return bleach.clean(text_content, tags=[], strip=True)
