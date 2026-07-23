import pytest
import os
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app import create_app, db
from app.models.user import User
from app.models.scan import Scan
from app.models.recommendation import Recommendation


@pytest.fixture
def app():
    """Create and configure a Flask app for testing."""
    app = create_app('testing')
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """A test runner for the app's CLI commands."""
    return app.test_cli_runner()


@pytest.fixture
def test_user(app):
    """Create a test user."""
    with app.app_context():
        user = User(
            username='testuser',
            email='test@example.com',
            first_name='Test',
            last_name='User',
            role='user'
        )
        user.set_password('TestPassword123!')
        db.session.add(user)
        db.session.commit()
        
        # Re-query user to attach to session
        user = User.query.filter_by(username='testuser').first()
        yield user


@pytest.fixture
def auth_client(client, test_user):
    """A test client logged in as testuser."""
    client.post('/auth/login', data={
        'username': 'testuser',
        'password': 'TestPassword123!'
    })
    return client
