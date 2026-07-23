"""
WSGI entry point for Gunicorn (Render, production deployment).
Exposes a module-level `app` variable that Gunicorn can discover.
"""

import os
from pathlib import Path

# Ensure required directories exist before app starts
for d in ['instance', 'logs', 'reports']:
    Path(d).mkdir(parents=True, exist_ok=True)

from app import create_app, db

env = os.environ.get('FLASK_ENV', 'production')
app = create_app(env)

# Initialize database on startup
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run()
