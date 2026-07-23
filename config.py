"""
SupportSight Configuration Module

Production-grade configuration management with environment-specific settings.
Follows the twelve-factor app methodology for configuration.
"""

import os
from pathlib import Path

# Base Directory
BASE_DIR = Path(__file__).parent.absolute()


class Config:
    """Base configuration with sensible defaults."""

    # Security
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600

    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        f'sqlite:///{BASE_DIR}/instance/supportsight.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }

    # Session Configuration
    SESSION_TYPE = 'filesystem'
    SESSION_PERMANENT = False
    SESSION_USE_SIGNER = True
    SESSION_KEY_PREFIX = 'supportsight_'
    PERMANENT_SESSION_LIFETIME = 3600  # 1 hour

    # Application Settings
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max upload
    JSON_SORT_KEYS = False

    # Logging Configuration
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    LOG_FILE = BASE_DIR / 'logs' / 'supportsight.log'

    # Pagination
    ITEMS_PER_PAGE = 20
    MAX_ITEMS_PER_PAGE = 100

    # Diagnostics Settings
    SCAN_TIMEOUT = 300  # 5 minutes
    CPU_HISTORY_LENGTH = 60  # Store 60 data points
    RAM_HISTORY_LENGTH = 60
    DISK_CHECK_THRESHOLD = 90  # percentage
    RAM_CHECK_THRESHOLD = 90
    CPU_CHECK_THRESHOLD = 85

    # Health Score Thresholds
    HEALTH_SCORE_EXCELLENT = 80
    HEALTH_SCORE_GOOD = 60
    HEALTH_SCORE_FAIR = 40

    # Report Settings
    REPORT_OUTPUT_DIR = BASE_DIR / 'reports'
    MAX_REPORTS_STORED = 100


class DevelopmentConfig(Config):
    """Development environment configuration."""

    DEBUG = True
    TESTING = False
    LOG_LEVEL = 'DEBUG'


class ProductionConfig(Config):
    """Production environment configuration."""

    DEBUG = False
    TESTING = False

    # Force HTTPS in production
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

    # Use environment variable for secret key in production
    @property
    def SECRET_KEY(self):
        key = os.environ.get('SECRET_KEY')
        if not key:
            raise ValueError("SECRET_KEY environment variable must be set in production")
        return key


class TestingConfig(Config):
    """Testing environment configuration."""

    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False


# Configuration mapping
config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


def get_config(env_name: str = None) -> Config:
    """
    Get configuration object based on environment.

    Args:
        env_name: Environment name (development, production, testing)

    Returns:
        Configuration object
    """
    if env_name is None:
        env_name = os.environ.get('FLASK_ENV', 'development')

    return config_by_name.get(env_name, DevelopmentConfig)
