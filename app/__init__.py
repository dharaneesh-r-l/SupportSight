"""
SupportSight Application Package

AI-Powered Windows Diagnostics & IT Support Platform
Flask application factory with blueprint architecture.
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate

from config import get_config

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
bcrypt = Bcrypt()
migrate = Migrate()


def create_app(config_name: str = 'development') -> Flask:
    """
    Application factory for creating Flask app instances.

    Args:
        config_name: Configuration environment (development, production, testing)

    Returns:
        Configured Flask application instance
    """
    app = Flask(__name__,
                template_folder='templates',
                static_folder='static',
                static_url_path='/static')

    # Load configuration
    config_class = get_config(config_name)
    app.config.from_object(config_class)

    # Initialize extensions with app
    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    migrate.init_app(app, db)

    # Ensure database schema is up-to-date
    ensure_database_schema(app)

    # Login manager configuration
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'

    # User loader for Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        from app.models.user import User
        return db.session.get(User, int(user_id))

    # Register blueprints
    register_blueprints(app)

    # Register error handlers
    register_error_handlers(app)

    # Register Jinja2 filters
    register_jinja_filters(app)

    return app


def ensure_database_schema(app: Flask) -> None:
    """Ensure all required database tables and columns exist."""
    with app.app_context():
        try:
            db.create_all()
            with db.engine.connect() as conn:
                result = conn.execute(db.text("PRAGMA table_info(scans)")).fetchall()
                columns = [row[1] for row in result]
                if columns and 'root_cause_analysis' not in columns:
                    conn.execute(db.text("ALTER TABLE scans ADD COLUMN root_cause_analysis TEXT"))
                    conn.commit()
                    app.logger.info("Migrated SQLite database: Added scans.root_cause_analysis column")
        except Exception as e:
            app.logger.warning(f"Database schema check notice: {str(e)}")


def register_blueprints(app: Flask) -> None:
    """Register all application blueprints."""
    from app.dashboard import dashboard_bp
    from app.auth import auth_bp
    from app.api import api_bp
    from app.diagnostics import diagnostics_bp
    from app.reports import reports_bp

    app.register_blueprint(dashboard_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(diagnostics_bp, url_prefix='/diagnostics')
    app.register_blueprint(reports_bp, url_prefix='/reports')


def register_error_handlers(app: Flask) -> None:
    """Register custom error handlers."""
    from flask import render_template

    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('errors/500.html'), 500

    @app.errorhandler(403)
    def forbidden_error(error):
        return render_template('errors/403.html'), 403


def register_jinja_filters(app: Flask) -> None:
    """Register custom Jinja2 filters and context processors."""
    from datetime import datetime
    from app.utils.helpers import format_bytes, format_percentage, format_datetime, format_duration

    @app.template_filter('datetime')
    @app.template_filter('format_datetime')
    def filter_format_datetime(value, format_str='%Y-%m-%d %H:%M:%S'):
        return format_datetime(value, format_str)

    @app.template_filter('percentage')
    @app.template_filter('format_percentage')
    def filter_format_percentage(value):
        return format_percentage(value)

    @app.template_filter('bytes_to_human')
    @app.template_filter('format_bytes')
    def filter_format_bytes(value):
        return format_bytes(value)

    @app.template_filter('duration')
    @app.template_filter('format_duration')
    def filter_format_duration(value):
        return format_duration(value)

    @app.context_processor
    def inject_helpers():
        return dict(
            format_bytes=format_bytes,
            format_percentage=format_percentage,
            format_datetime=format_datetime,
            format_duration=format_duration
        )

