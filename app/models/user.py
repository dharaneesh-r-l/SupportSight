"""
SupportSight User Model

Authentication and user management.
"""

from datetime import datetime
from flask_login import UserMixin
from app import db, bcrypt


class User(UserMixin, db.Model):
    """
    User model for authentication and authorization.

    Attributes:
        id: Unique identifier
        username: User's username
        email: User's email address
        password_hash: Bcrypt hashed password
        first_name: User's first name
        last_name: User's last name
        role: User role (admin, user, guest)
        is_active: Account status
        created_at: Account creation timestamp
        last_login: Last login timestamp
    """

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    role = db.Column(db.String(20), default='user')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)

    # Relationships
    scans = db.relationship('Scan', backref='user', lazy='dynamic', cascade='all, delete-orphan')

    def __init__(self, **kwargs):
        """Initialize user with hashed password."""
        super(User, self).__init__(**kwargs)
        if 'password' in kwargs:
            self.set_password(kwargs['password'])

    def set_password(self, password: str) -> None:
        """
        Hash and set the user's password.

        Args:
            password: Plain text password
        """
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password: str) -> bool:
        """
        Verify password against hash.

        Args:
            password: Plain text password to verify

        Returns:
            True if password matches, False otherwise
        """
        return bcrypt.check_password_hash(self.password_hash, password)

    @property
    def full_name(self) -> str:
        """Return user's full name."""
        if self.first_name and self.last_name:
            return f'{self.first_name} {self.last_name}'
        return self.username

    @property
    def initials(self) -> str:
        """Return user's initials."""
        if self.first_name and self.last_name:
            return f'{self.first_name[0]}{self.last_name[0]}'.upper()
        return self.username[:2].upper()

    def update_last_login(self) -> None:
        """Update the last login timestamp."""
        self.last_login = datetime.utcnow()
        db.session.commit()

    def is_admin(self) -> bool:
        """Check if user has admin role."""
        return self.role == 'admin'

    def to_dict(self) -> dict:
        """Convert user to dictionary."""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': self.full_name,
            'role': self.role,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }

    def __repr__(self) -> str:
        return f'<User {self.username}>'
