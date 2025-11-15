"""
Email Classifier - Automatically categorize emails
"""

import re


class EmailClassifier:
    """Classify emails into categories (promotional, social, updates, etc.)"""
    
    # Keywords for promotional emails
    PROMOTIONAL_KEYWORDS = [
        'sale', 'discount', 'offer', 'deal', 'coupon', 'promo', 'promotion',
        'limited time', 'exclusive', 'save', 'free shipping', 'buy now',
        'shop now', 'order now', 'special offer', 'clearance', 'bargain',
        'unsubscribe', 'click here', 'limited offer', 'act now', 'hurry',
        'don\'t miss', 'last chance', 'today only', 'flash sale', 'hot deal'
    ]
    
    # Keywords for social emails
    SOCIAL_KEYWORDS = [
        'liked your', 'commented on', 'tagged you', 'mentioned you',
        'friend request', 'connection request', 'follow', 'follower',
        'shared with you', 'invited you', 'message from', 'notification'
    ]
    
    # Keywords for updates/newsletters
    UPDATE_KEYWORDS = [
        'newsletter', 'weekly update', 'monthly update', 'digest',
        'summary', 'roundup', 'news', 'announcement', 'bulletin',
        'report', 'update', 'what\'s new', 'latest'
    ]
    
    # Keywords for forums/discussions
    FORUM_KEYWORDS = [
        'forum', 'discussion', 'thread', 'reply', 'comment',
        'post', 'topic', 'community', 'group'
    ]
    
    # Spam indicators
    SPAM_KEYWORDS = [
        'viagra', 'cialis', 'lottery', 'winner', 'prize', 'claim now',
        'congratulations', 'you won', 'free money', 'make money fast',
        'work from home', 'nigerian prince', 'inheritance', 'urgent',
        'verify your account', 'suspended account', 'unusual activity',
        'click immediately', 'act immediately'
    ]
    
    # Promotional sender domains
    PROMOTIONAL_DOMAINS = [
        'marketing', 'promo', 'offers', 'deals', 'newsletter',
        'noreply', 'no-reply', 'notifications', 'updates'
    ]
    
    def __init__(self, user_id=None):
        self.user_id = user_id
        self.learned_patterns = None
        
        # Load learned patterns if user_id provided
        if user_id:
            self._load_learned_patterns()
    
    def classify_email(self, subject, body, from_addr):
        """
        Classify email into category
        
        Args:
            subject: Email subject
            body: Email body (plain text or preview)
            from_addr: Sender email address
            
        Returns:
            tuple: (category, is_spam, confidence)
            category: 'promotional', 'social', 'updates', 'forums', 'primary', None
            is_spam: Boolean
            confidence: 0.0 to 1.0
        """
        # Combine subject and body for analysis
        text = f"{subject or ''} {body or ''}".lower()
        from_addr_lower = (from_addr or '').lower()
        
        # Check learned patterns first (highest priority)
        if self.learned_patterns:
            learned_result, learned_confidence = self._check_learned_patterns(from_addr)
            if learned_result == 'spam':
                return ('spam', True, learned_confidence)
            elif learned_result == 'not_spam':
                # Don't classify as spam even if it looks like spam
                pass
        
        # Check for spam
        spam_score = self._calculate_spam_score(text, from_addr_lower)
        if spam_score > 0.6:
            return ('spam', True, spam_score)
        
        # Calculate scores for each category
        scores = {
            'promotional': self._calculate_promotional_score(text, from_addr_lower),
            'social': self._calculate_social_score(text),
            'updates': self._calculate_update_score(text),
            'forums': self._calculate_forum_score(text)
        }
        
        # Get category with highest score
        max_category = max(scores, key=scores.get)
        max_score = scores[max_category]
        
        # Only classify if confidence is high enough
        if max_score > 0.3:
            return (max_category, False, max_score)
        
        # Default to primary if no clear category
        return ('primary', False, 0.0)
    
    def _calculate_spam_score(self, text, from_addr):
        """Calculate spam probability"""
        score = 0.0
        keyword_count = 0
        
        for keyword in self.SPAM_KEYWORDS:
            if keyword in text:
                keyword_count += 1
        
        # More spam keywords = higher score
        if keyword_count > 0:
            score = min(keyword_count / 5.0, 1.0)
        
        # Suspicious sender patterns
        if re.search(r'\d{5,}', from_addr):  # Many numbers in email
            score += 0.2
        
        if re.search(r'[A-Z]{10,}', text):  # Excessive caps
            score += 0.1
        
        if text.count('!') > 5:  # Excessive exclamation marks
            score += 0.1
        
        return min(score, 1.0)
    
    def _calculate_promotional_score(self, text, from_addr):
        """Calculate promotional probability"""
        score = 0.0
        keyword_count = 0
        
        for keyword in self.PROMOTIONAL_KEYWORDS:
            if keyword in text:
                keyword_count += 1
        
        # Keyword score
        score += min(keyword_count / 10.0, 0.6)
        
        # Check sender domain
        for domain in self.PROMOTIONAL_DOMAINS:
            if domain in from_addr:
                score += 0.3
                break
        
        # Unsubscribe link is strong indicator
        if 'unsubscribe' in text:
            score += 0.2
        
        return min(score, 1.0)
    
    def _calculate_social_score(self, text):
        """Calculate social probability"""
        score = 0.0
        keyword_count = 0
        
        for keyword in self.SOCIAL_KEYWORDS:
            if keyword in text:
                keyword_count += 1
        
        score = min(keyword_count / 5.0, 1.0)
        return score
    
    def _calculate_update_score(self, text):
        """Calculate update/newsletter probability"""
        score = 0.0
        keyword_count = 0
        
        for keyword in self.UPDATE_KEYWORDS:
            if keyword in text:
                keyword_count += 1
        
        score = min(keyword_count / 5.0, 1.0)
        return score
    
    def _calculate_forum_score(self, text):
        """Calculate forum/discussion probability"""
        score = 0.0
        keyword_count = 0
        
        for keyword in self.FORUM_KEYWORDS:
            if keyword in text:
                keyword_count += 1
        
        score = min(keyword_count / 5.0, 1.0)
        return score
    
    def is_promotional(self, subject, body, from_addr):
        """Quick check if email is promotional"""
        category, is_spam, confidence = self.classify_email(subject, body, from_addr)
        return category == 'promotional' and confidence > 0.3
    
    def is_spam(self, subject, body, from_addr):
        """Quick check if email is spam"""
        category, is_spam, confidence = self.classify_email(subject, body, from_addr)
        return is_spam and confidence > 0.6
    
    def _load_learned_patterns(self):
        """Load learned spam patterns from database"""
        try:
            from qmail.models.spam_pattern import SpamPattern
            patterns = SpamPattern.query.filter_by(user_id=self.user_id).all()
            self.learned_patterns = {
                'spam_domains': [p.sender_domain for p in patterns if p.pattern_type == 'spam' and p.get_confidence() > 0.7],
                'not_spam_domains': [p.sender_domain for p in patterns if p.pattern_type == 'not_spam' and p.get_confidence() > 0.7]
            }
        except Exception as e:
            print(f"Error loading learned patterns: {e}")
            self.learned_patterns = {'spam_domains': [], 'not_spam_domains': []}
    
    def _check_learned_patterns(self, from_addr):
        """Check if email matches learned patterns"""
        if not self.learned_patterns or not from_addr:
            return None, 0.0
        
        # Extract domain from email
        if '@' in from_addr:
            domain = from_addr.split('@')[1].lower()
            
            # Check spam patterns
            if domain in self.learned_patterns['spam_domains']:
                return 'spam', 0.9  # High confidence from user feedback
            
            # Check not-spam patterns
            if domain in self.learned_patterns['not_spam_domains']:
                return 'not_spam', 0.9
        
        return None, 0.0
