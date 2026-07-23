"""
SupportSight Dashboard Blueprint

Main dashboard and homepage routes.
"""

from flask import Blueprint

dashboard_bp = Blueprint('dashboard', __name__)

from app.dashboard import routes
