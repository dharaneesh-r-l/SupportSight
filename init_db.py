#!/usr/bin/env python3
"""
SupportSight Database Initialization Script

Creates default admin user and initializes the database.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from app import create_app, db
from app.models.user import User


def init_database():
    """Initialize database and create default admin user."""
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')

    app = create_app('development')

    with app.app_context():
        # Create all tables
        db.create_all()
        print("[OK] Database tables created")

        # Check if admin exists
        admin = User.query.filter_by(username='admin').first()

        if not admin:
            # Create admin user
            admin = User(
                username='admin',
                email='admin@supportsight.local',
                first_name='Admin',
                last_name='User',
                role='admin'
            )
            admin.set_password('password123')
            db.session.add(admin)
            db.session.commit()
            print("[OK] Admin user created")
            print("  Username: admin")
            print("  Password: password123")
        else:
            if not admin.check_password('password123') and not admin.check_password('Admin@123'):
                admin.set_password('password123')
                db.session.commit()
                print("[OK] Admin user password reset to: password123")
            else:
                print("[OK] Admin user already exists")

        # Create logs directory
        logs_dir = Path(__file__).parent / 'logs'
        logs_dir.mkdir(exist_ok=True)
        print("[OK] Logs directory created")

        # Create reports directory
        reports_dir = Path(__file__).parent / 'reports'
        reports_dir.mkdir(exist_ok=True)
        print("[OK] Reports directory created")

        print("\n[OK] Database initialization complete!")


if __name__ == '__main__':
    init_database()
