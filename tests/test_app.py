"""
Tests for Flask application
"""

import pytest
from qmail.app import create_app
from qmail.models.database import db, User


@pytest.fixture
def app():
    """Create application for testing"""
    app = create_app('testing')
    
    with app.app_context():
        db.create_all()
        
        # Create test user
        user = User(username='testuser', email='test@example.com')
        user.set_password('testpass123')
        db.session.add(user)
        db.session.commit()
    
    yield app
    
    with app.app_context():
        db.drop_all()


@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()


class TestAuthentication:
    """Test authentication routes"""
    
    def test_login_page(self, client):
        """Test login page loads"""
        response = client.get('/auth/login')
        assert response.status_code == 200
        assert b'QMail' in response.data
    
    def test_register_page(self, client):
        """Test register page loads"""
        response = client.get('/auth/register')
        assert response.status_code == 200
        assert b'Create Account' in response.data
    
    def test_login_success(self, client):
        """Test successful login"""
        response = client.post('/auth/login', data={
            'username': 'testuser',
            'password': 'testpass123'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Welcome back' in response.data or b'Inbox' in response.data
    
    def test_login_failure(self, client):
        """Test failed login"""
        response = client.post('/auth/login', data={
            'username': 'testuser',
            'password': 'wrongpassword'
        }, follow_redirects=True)
        
        assert b'Invalid username or password' in response.data
    
    def test_register_new_user(self, client):
        """Test user registration"""
        response = client.post('/auth/register', data={
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'newpass123',
            'password_confirm': 'newpass123'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Registration successful' in response.data


class TestAPIEndpoints:
    """Test API endpoints"""
    
    def test_security_levels(self, client):
        """Test security levels API"""
        response = client.get('/api/security-levels')
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['success'] is True
        assert 'security_levels' in data
        assert len(data['security_levels']) == 4


class TestMainRoutes:
    """Test main application routes"""
    
    def test_index_redirect(self, client):
        """Test index redirects to login"""
        response = client.get('/')
        assert response.status_code == 302  # Redirect
    
    def test_about_page(self, client):
        """Test about page"""
        response = client.get('/about')
        assert response.status_code == 200
