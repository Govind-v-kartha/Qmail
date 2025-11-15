"""
HTML Sanitization and Rendering Utilities
Safely render HTML emails with XSS protection
"""

import re
import logging
from typing import Optional, Dict, List
from bs4 import BeautifulSoup
import bleach

logger = logging.getLogger(__name__)


# Allowed HTML tags for email rendering
ALLOWED_TAGS = [
    'a', 'abbr', 'b', 'br', 'blockquote', 'code', 'div', 'em', 'font',
    'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'hr', 'i', 'img', 'li', 'ol',
    'p', 'pre', 'small', 'span', 'strong', 'sub', 'sup', 'table', 'tbody',
    'td', 'th', 'thead', 'tr', 'u', 'ul', 'center', 'strike', 's',
]

# Allowed attributes for HTML tags
ALLOWED_ATTRIBUTES = {
    '*': ['style', 'class', 'id'],
    'a': ['href', 'title', 'rel', 'target'],
    'img': ['src', 'alt', 'title', 'width', 'height', 'style'],
    'table': ['border', 'cellpadding', 'cellspacing', 'width', 'style'],
    'td': ['colspan', 'rowspan', 'align', 'valign', 'style'],
    'th': ['colspan', 'rowspan', 'align', 'valign', 'style'],
    'div': ['align', 'style'],
    'p': ['align', 'style'],
    'span': ['style'],
    'font': ['color', 'size', 'face', 'style'],
}

# Allowed CSS properties
ALLOWED_STYLES = [
    'color', 'background-color', 'font-size', 'font-family', 'font-weight',
    'text-align', 'text-decoration', 'padding', 'margin', 'border',
    'width', 'height', 'max-width', 'max-height', 'display', 'float',
    'line-height', 'letter-spacing'
]


def sanitize_html(html_content: str, strip_styles: bool = False) -> str:
    """
    Sanitize HTML content to prevent XSS attacks
    
    Args:
        html_content: Raw HTML content
        strip_styles: Remove all inline styles
    
    Returns:
        Sanitized HTML content
    """
    if not html_content:
        return ""
    
    try:
        # Remove dangerous content
        html_content = remove_dangerous_content(html_content)
        
        # Clean with bleach
        cleaned = bleach.clean(
            html_content,
            tags=ALLOWED_TAGS,
            attributes=ALLOWED_ATTRIBUTES,
            strip=True,
            strip_comments=True
        )
        
        if strip_styles:
            # Remove all style attributes
            soup = BeautifulSoup(cleaned, 'html.parser')
            for tag in soup.find_all(True):
                if 'style' in tag.attrs:
                    del tag['style']
            cleaned = str(soup)
        else:
            # Sanitize CSS in style attributes
            cleaned = sanitize_inline_styles(cleaned)
        
        # Make external links safe
        cleaned = make_links_safe(cleaned)
        
        # Add responsive wrapper
        cleaned = add_responsive_wrapper(cleaned)
        
        logger.debug(f"HTML sanitized successfully ({len(cleaned)} chars)")
        return cleaned
        
    except Exception as e:
        logger.error(f"Error sanitizing HTML: {e}")
        # Return plain text version on error
        return escape_html(strip_html_tags(html_content))


def remove_dangerous_content(html: str) -> str:
    """Remove potentially dangerous content"""
    # Remove script tags
    html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
    
    # Remove event handlers
    html = re.sub(r'\s*on\w+\s*=\s*["\'][^"\']*["\']', '', html, flags=re.IGNORECASE)
    html = re.sub(r'\s*on\w+\s*=\s*\S+', '', html, flags=re.IGNORECASE)
    
    # Remove javascript: links
    html = re.sub(r'href\s*=\s*["\']javascript:[^"\']*["\']', 'href="#"', html, flags=re.IGNORECASE)
    
    # Remove data: URIs (except images)
    html = re.sub(r'src\s*=\s*["\']data:(?!image)[^"\']*["\']', 'src="#"', html, flags=re.IGNORECASE)
    
    return html


def sanitize_inline_styles(html: str) -> str:
    """Sanitize inline CSS styles"""
    soup = BeautifulSoup(html, 'html.parser')
    
    for tag in soup.find_all(True):
        if 'style' in tag.attrs:
            style = tag['style']
            # Parse and filter CSS properties
            safe_styles = []
            for rule in style.split(';'):
                if ':' in rule:
                    prop, value = rule.split(':', 1)
                    prop = prop.strip().lower()
                    value = value.strip()
                    
                    # Only allow safe properties
                    if prop in ALLOWED_STYLES:
                        # Remove dangerous values
                        if 'expression' not in value.lower() and 'javascript' not in value.lower():
                            safe_styles.append(f"{prop}: {value}")
            
            tag['style'] = '; '.join(safe_styles)
    
    return str(soup)


def make_links_safe(html: str) -> str:
    """Make external links safe"""
    soup = BeautifulSoup(html, 'html.parser')
    
    for link in soup.find_all('a'):
        if 'href' in link.attrs:
            href = link['href']
            # Add rel="noopener noreferrer" for external links
            if href.startswith('http'):
                link['rel'] = 'noopener noreferrer nofollow'
                link['target'] = '_blank'
    
    return str(soup)


def add_responsive_wrapper(html: str) -> str:
    """Add responsive wrapper for email content"""
    return f'<div class="email-html-content">{html}</div>'


def extract_preview_text(html: str, max_length: int = 150) -> str:
    """
    Extract plain text preview from HTML
    
    Args:
        html: HTML content
        max_length: Maximum length of preview
    
    Returns:
        Plain text preview
    """
    try:
        # Parse HTML
        soup = BeautifulSoup(html, 'html.parser')
        
        # Remove script and style tags
        for tag in soup(['script', 'style', 'head', 'meta']):
            tag.decompose()
        
        # Get text
        text = soup.get_text(separator=' ', strip=True)
        
        # Clean whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Truncate
        if len(text) > max_length:
            text = text[:max_length] + '...'
        
        return text
        
    except Exception as e:
        logger.error(f"Error extracting preview: {e}")
        return ""


def strip_html_tags(html: str) -> str:
    """Strip all HTML tags"""
    try:
        soup = BeautifulSoup(html, 'html.parser')
        return soup.get_text(separator=' ', strip=True)
    except:
        return re.sub(r'<[^>]+>', '', html)


def escape_html(text: str) -> str:
    """Escape HTML special characters"""
    return (text
            .replace('&', '&amp;')
            .replace('<', '&lt;')
            .replace('>', '&gt;')
            .replace('"', '&quot;')
            .replace("'", '&#39;'))


def is_html_email(content: str) -> bool:
    """
    Check if email content is HTML
    
    Args:
        content: Email content
    
    Returns:
        True if HTML, False if plain text
    """
    if not content:
        return False
    
    # Check for HTML tags
    html_pattern = r'<(html|body|div|p|table|br|img|a|span|font|h[1-6])[^>]*>'
    return bool(re.search(html_pattern, content, re.IGNORECASE))


def render_html_preview(html: str, max_height: int = 200) -> str:
    """
    Render HTML preview for inbox list
    
    Args:
        html: HTML content
        max_height: Maximum height in pixels
    
    Returns:
        HTML preview with wrapper
    """
    sanitized = sanitize_html(html)
    
    preview_html = f'''
    <div class="email-preview-html" style="max-height: {max_height}px; overflow: hidden; position: relative;">
        {sanitized}
        <div class="preview-fade"></div>
    </div>
    '''
    
    return preview_html


def extract_images_from_html(html: str) -> List[Dict]:
    """
    Extract image URLs from HTML
    
    Args:
        html: HTML content
    
    Returns:
        List of image info dicts
    """
    images = []
    
    try:
        soup = BeautifulSoup(html, 'html.parser')
        
        for img in soup.find_all('img'):
            src = img.get('src', '')
            alt = img.get('alt', '')
            
            if src:
                images.append({
                    'src': src,
                    'alt': alt,
                    'width': img.get('width'),
                    'height': img.get('height')
                })
        
    except Exception as e:
        logger.error(f"Error extracting images: {e}")
    
    return images


def convert_inline_images_to_attachments(html: str) -> tuple[str, List[Dict]]:
    """
    Convert inline base64 images to attachment references
    
    Args:
        html: HTML content with inline images
    
    Returns:
        Tuple of (modified_html, list of image data)
    """
    images = []
    soup = BeautifulSoup(html, 'html.parser')
    
    for idx, img in enumerate(soup.find_all('img')):
        src = img.get('src', '')
        
        # Check for base64 data URI
        if src.startswith('data:image/'):
            try:
                # Extract image data
                match = re.match(r'data:image/(\w+);base64,(.+)', src)
                if match:
                    img_format = match.group(1)
                    img_data = match.group(2)
                    
                    images.append({
                        'format': img_format,
                        'data': img_data,
                        'index': idx
                    })
                    
                    # Replace with placeholder
                    img['src'] = f'#inline-image-{idx}'
                    img['data-inline-image'] = str(idx)
                    
            except Exception as e:
                logger.error(f"Error processing inline image: {e}")
    
    return str(soup), images


def restore_inline_images(html: str, images: List[Dict]) -> str:
    """
    Restore inline images from attachment data
    
    Args:
        html: HTML content with placeholders
        images: List of image data dicts
    
    Returns:
        HTML with restored images
    """
    soup = BeautifulSoup(html, 'html.parser')
    
    for img_data in images:
        idx = img_data.get('index')
        img_tag = soup.find('img', {'data-inline-image': str(idx)})
        
        if img_tag and 'data' in img_data:
            # Restore data URI
            img_format = img_data.get('format', 'png')
            data = img_data.get('data')
            img_tag['src'] = f'data:image/{img_format};base64,{data}'
    
    return str(soup)
