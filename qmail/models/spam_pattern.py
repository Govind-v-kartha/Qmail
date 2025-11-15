"""
Spam Pattern Learning Model
"""

from datetime import datetime
from qmail.models.database import db


class SpamPattern(db.Model):
    """Store learned spam patterns from user feedback"""
    __tablename__ = 'spam_patterns'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Pattern details
    sender_domain = db.Column(db.String(255))  # e.g., "marketing.com"
    sender_pattern = db.Column(db.String(255))  # e.g., "noreply@%"
    subject_keywords = db.Column(db.Text)  # JSON list of keywords
    
    # Pattern type
    pattern_type = db.Column(db.String(50))  # 'spam', 'not_spam', 'promotional'
    
    # Confidence
    match_count = db.Column(db.Integer, default=1)  # How many times this pattern matched
    correct_count = db.Column(db.Integer, default=1)  # How many times user confirmed
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<SpamPattern {self.pattern_type}: {self.sender_domain}>'
    
    def get_confidence(self):
        """Calculate confidence score (0.0 to 1.0)"""
        if self.match_count == 0:
            return 0.0
        return self.correct_count / self.match_count
