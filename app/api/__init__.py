"""
SupportSight API Blueprint

REST API endpoints for diagnostics and scan data.
"""

from flask import Blueprint

api_bp = Blueprint('api', __name__)

from app.api import routes
