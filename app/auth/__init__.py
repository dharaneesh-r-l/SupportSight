"""
SupportSight Authentication Blueprint

User authentication and registration routes.
"""

from flask import Blueprint

auth_bp = Blueprint('auth', __name__)

from app.auth import routes
