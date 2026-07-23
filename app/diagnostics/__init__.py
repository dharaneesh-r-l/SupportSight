"""
SupportSight Diagnostics Blueprint

Detailed diagnostic pages.
"""

from flask import Blueprint

diagnostics_bp = Blueprint('diagnostics', __name__)

from app.diagnostics import routes
