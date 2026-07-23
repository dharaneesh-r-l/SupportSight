#!/usr/bin/env python3
"""
SupportSight - Application Entry Point

AI-Powered Windows Diagnostics & IT Support Platform
"""

import os
import sys
import logging
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

from app import create_app, db
from config import get_config


def setup_logging(app):
    """Configure application logging."""
    log_dir = Path(__file__).parent / 'logs'
    log_dir.mkdir(exist_ok=True)

    log_level = getattr(logging, app.config.get('LOG_LEVEL', 'INFO'))
    log_format = app.config.get('LOG_FORMAT', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    logging.basicConfig(
        level=log_level,
        format=log_format,
        handlers=[
            logging.FileHandler(log_dir / 'supportsight.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )

    app.logger.setLevel(log_level)


def ensure_directories(app):
    """Ensure required directories exist."""
    directories = [
        app.config.get('REPORT_OUTPUT_DIR', Path(__file__).parent / 'reports'),
        Path(__file__).parent / 'logs',
        Path(__file__).parent / 'instance',
    ]

    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)


def init_database(app):
    """Initialize database tables."""
    with app.app_context():
        db.create_all()
        app.logger.info("Database tables created successfully")


def main():
    """Main entry point for the application."""
    env_name = os.environ.get('FLASK_ENV', 'development')
    app = create_app(env_name)

    setup_logging(app)
    ensure_directories(app)

    app.logger.info("=" * 60)
    app.logger.info("SupportSight - AI-Powered Windows Diagnostics Platform")
    app.logger.info(f"Environment: {env_name}")
    app.logger.info("=" * 60)

    init_database(app)

    host = os.environ.get('FLASK_HOST', '0.0.0.0')
    port = int(os.environ.get('FLASK_PORT', 5000))
    debug = app.config.get('DEBUG', False)

    app.logger.info(f"Starting server on {host}:{port}")
    app.run(host=host, port=port, debug=debug)


if __name__ == '__main__':
    main()
