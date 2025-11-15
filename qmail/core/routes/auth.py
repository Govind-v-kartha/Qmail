"""
Authentication routes
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from urllib.parse import urlparse
from datetime import datetime
import re

from qmail.models.database import db, User, Settings

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login page with account lockout protection"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = request.form.get('remember', False)
        
        user = User.query.filter_by(username=username).first()
        
        # Check if user exists
        if user is None:
            flash('Invalid username or password', 'error')
            return redirect(url_for('auth.login'))
        
        # Check if account is locked
        if user.is_account_locked():
            minutes_left = int((user.account_locked_until - datetime.utcnow()).total_seconds() / 60)
            flash(f'Account locked due to multiple failed login attempts. Try again in {minutes_left} minutes.', 'error')
            return redirect(url_for('auth.login'))
        
        # Check password
        if not user.check_password(password):
            user.record_failed_login()
            db.session.commit()
            
            attempts_left = 5 - user.failed_login_attempts
            if attempts_left > 0:
                flash(f'Invalid password. {attempts_left} attempts remaining.', 'error')
            else:
                flash('Account locked for 30 minutes due to multiple failed attempts.', 'error')
            return redirect(url_for('auth.login'))
        
        # Check if account is active
        if not user.is_active:
            flash('Your account has been deactivated', 'error')
            return redirect(url_for('auth.login'))
        
        # Successful login
        user.reset_failed_logins()
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        login_user(user, remember=remember)
        
        # Redirect to next page or index
        next_page = request.args.get('next')
        if not next_page or urlparse(next_page).netloc != '':
            next_page = url_for('main.index')
        
        flash(f'Welcome back, {user.username}!', 'success')
        return redirect(next_page)
    
    return render_template('auth/login.html')


def validate_password(password):
    """Validate password strength"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    if not re.search(r'\d', password):
        return False, "Password must contain at least one number"
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Password must contain at least one special character (!@#$%^&*)"
    return True, "Password is strong"


def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_username(username):
    """Validate username format"""
    if len(username) < 3:
        return False, "Username must be at least 3 characters long"
    if len(username) > 20:
        return False, "Username must be less than 20 characters"
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        return False, "Username can only contain letters, numbers, and underscores"
    return True, "Username is valid"


@bp.route('/register', methods=['GET', 'POST'])
def register():
    """Registration page with validation"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password')
        password_confirm = request.form.get('password_confirm')
        
        # Validation
        if not username or not email or not password:
            flash('All fields are required', 'error')
            return redirect(url_for('auth.register'))
        
        # Validate username
        is_valid, message = validate_username(username)
        if not is_valid:
            flash(message, 'error')
            return redirect(url_for('auth.register'))
        
        # Validate email
        if not validate_email(email):
            flash('Invalid email format', 'error')
            return redirect(url_for('auth.register'))
        
        # Validate password
        is_valid, message = validate_password(password)
        if not is_valid:
            flash(message, 'error')
            return redirect(url_for('auth.register'))
        
        # Check password confirmation
        if password != password_confirm:
            flash('Passwords do not match', 'error')
            return redirect(url_for('auth.register'))
        
        # Check if user already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'error')
            return redirect(url_for('auth.register'))
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'error')
            return redirect(url_for('auth.register'))
        
        # Create new user
        user = User(username=username, email=email)
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        # Create default settings
        settings = Settings(user_id=user.id)
        db.session.add(settings)
        db.session.commit()
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html')


@bp.route('/logout')
@login_required
def logout():
    """Logout"""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))


@bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Forgot password - request reset"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        
        if not email:
            flash('Please enter your email address', 'error')
            return redirect(url_for('auth.forgot_password'))
        
        user = User.query.filter_by(email=email).first()
        
        if user:
            # Generate reset token
            token = user.generate_reset_token()
            db.session.commit()
            
            # In production, send email with reset link
            # For now, just show the token (for testing)
            reset_url = url_for('auth.reset_password', token=token, _external=True)
            
            flash(f'Password reset link: {reset_url}', 'info')
            flash('In production, this link would be sent to your email.', 'info')
        else:
            # Don't reveal if email exists (security)
            flash('If that email is registered, you will receive a password reset link.', 'info')
        
        return redirect(url_for('auth.login'))
    
    return render_template('auth/forgot_password.html')


@bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """Reset password with token"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    # Find user with this token
    user = User.query.filter_by(reset_token=token).first()
    
    if not user or not user.verify_reset_token(token):
        flash('Invalid or expired reset link', 'error')
        return redirect(url_for('auth.forgot_password'))
    
    if request.method == 'POST':
        password = request.form.get('password')
        password_confirm = request.form.get('password_confirm')
        
        if not password:
            flash('Please enter a new password', 'error')
            return redirect(url_for('auth.reset_password', token=token))
        
        # Validate password
        is_valid, message = validate_password(password)
        if not is_valid:
            flash(message, 'error')
            return redirect(url_for('auth.reset_password', token=token))
        
        # Check password confirmation
        if password != password_confirm:
            flash('Passwords do not match', 'error')
            return redirect(url_for('auth.reset_password', token=token))
        
        # Update password
        user.set_password(password)
        user.clear_reset_token()
        user.reset_failed_logins()  # Clear any lockout
        db.session.commit()
        
        flash('Password reset successful! Please log in with your new password.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/reset_password.html', token=token)


@bp.route('/forgot-username', methods=['GET', 'POST'])
def forgot_username():
    """Forgot username - retrieve by email"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        
        if not email:
            flash('Please enter your email address', 'error')
            return redirect(url_for('auth.forgot_username'))
        
        user = User.query.filter_by(email=email).first()
        
        if user:
            # In production, send email with username
            # For now, just show it (for testing)
            flash(f'Your username is: {user.username}', 'info')
            flash('In production, this would be sent to your email.', 'info')
        else:
            # Don't reveal if email exists (security)
            flash('If that email is registered, you will receive your username.', 'info')
        
        return redirect(url_for('auth.login'))
    
    return render_template('auth/forgot_username.html')
