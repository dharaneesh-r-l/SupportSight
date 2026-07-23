"""
SupportSight Scan Model

Stores system scan history and results.
"""

import json
from datetime import datetime
from app import db


class Scan(db.Model):
    """
    Scan model for storing diagnostic scan history.

    Attributes:
        id: Unique scan identifier
        user_id: Reference to user who initiated scan
        scan_type: Type of scan performed
        health_score: Overall health score (0-100)
        status: Scan status (completed, failed, in_progress)
        system_info: JSON containing system information
        cpu_data: JSON containing CPU diagnostics
        ram_data: JSON containing RAM diagnostics
        disk_data: JSON containing disk diagnostics
        network_data: JSON containing network diagnostics
        battery_data: JSON containing battery diagnostics
        process_data: JSON containing process information
        recommendations: JSON containing recommendations
        error_message: Error message if scan failed
        started_at: Scan start timestamp
        completed_at: Scan completion timestamp
        duration: Scan duration in seconds
    """

    __tablename__ = 'scans'

    # Scan status constants
    STATUS_COMPLETED = 'completed'
    STATUS_FAILED = 'failed'
    STATUS_IN_PROGRESS = 'in_progress'

    # Scan type constants
    TYPE_FULL = 'full'
    TYPE_QUICK = 'quick'
    TYPE_CUSTOM = 'custom'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    scan_type = db.Column(db.String(20), default=TYPE_FULL)
    health_score = db.Column(db.Integer, default=0)
    status = db.Column(db.String(20), default=STATUS_IN_PROGRESS)

    # Diagnostic data as JSON
    system_info = db.Column(db.Text)
    cpu_data = db.Column(db.Text)
    ram_data = db.Column(db.Text)
    disk_data = db.Column(db.Text)
    network_data = db.Column(db.Text)
    battery_data = db.Column(db.Text)
    process_data = db.Column(db.Text)
    recommendations = db.Column(db.Text)

    # Error handling
    error_message = db.Column(db.Text)

    # Timestamps
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    duration = db.Column(db.Float)

    # Relationships
    scan_user = db.relationship('User', backref=db.backref('scan_history', lazy='dynamic', overlaps="scans,user"), overlaps="scans,user")

    def __init__(self, **kwargs):
        """Initialize scan with default values."""
        super(Scan, self).__init__(**kwargs)
        self.started_at = datetime.utcnow()

    def set_data(self, key: str, data: dict) -> None:
        """
        Set diagnostic data as JSON.

        Args:
            key: Data type (system_info, cpu_data, etc.)
            data: Dictionary to store as JSON
        """
        setattr(self, key, json.dumps(data))

    def get_data(self, key: str) -> dict:
        """
        Get diagnostic data from JSON.

        Args:
            key: Data type (system_info, cpu_data, etc.)

        Returns:
            Parsed dictionary or empty dict
        """
        data = getattr(self, key)
        if data:
            try:
                return json.loads(data)
            except json.JSONDecodeError:
                return {}
        return {}

    def mark_completed(self, health_score: int) -> None:
        """
        Mark scan as completed.

        Args:
            health_score: Calculated health score
        """
        self.status = self.STATUS_COMPLETED
        self.health_score = health_score
        self.completed_at = datetime.utcnow()
        self.duration = (self.completed_at - self.started_at).total_seconds()

    def mark_failed(self, error_message: str) -> None:
        """
        Mark scan as failed.

        Args:
            error_message: Error description
        """
        self.status = self.STATUS_FAILED
        self.error_message = error_message
        self.completed_at = datetime.utcnow()
        if self.started_at:
            self.duration = (self.completed_at - self.started_at).total_seconds()

    @property
    def health_category(self) -> str:
        """Get health score category."""
        if self.health_score >= 80:
            return 'Excellent'
        elif self.health_score >= 60:
            return 'Good'
        elif self.health_score >= 40:
            return 'Fair'
        return 'Poor'

    @property
    def problems_count(self) -> int:
        """Count number of problems found."""
        recommendations = self.get_data('recommendations')
        if isinstance(recommendations, list):
            return len(recommendations)
        return 0

    def to_dict(self) -> dict:
        """Convert scan to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'scan_type': self.scan_type,
            'health_score': self.health_score,
            'health_category': self.health_category,
            'status': self.status,
            'system_info': self.get_data('system_info'),
            'cpu_data': self.get_data('cpu_data'),
            'ram_data': self.get_data('ram_data'),
            'disk_data': self.get_data('disk_data'),
            'network_data': self.get_data('network_data'),
            'battery_data': self.get_data('battery_data'),
            'process_data': self.get_data('process_data'),
            'recommendations': self.get_data('recommendations'),
            'error_message': self.error_message,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'duration': self.duration
        }

    def __repr__(self) -> str:
        return f'<Scan {self.id} - {self.status}>'


class ScanResult(db.Model):
    """
    Individual scan result for detailed tracking.

    Used for time-series data and historical analysis.
    """

    __tablename__ = 'scan_results'

    id = db.Column(db.Integer, primary_key=True)
    scan_id = db.Column(db.Integer, db.ForeignKey('scans.id'), nullable=False, index=True)
    component = db.Column(db.String(50), nullable=False)  # cpu, ram, disk, etc.
    metric_name = db.Column(db.String(100), nullable=False)
    metric_value = db.Column(db.Float)
    unit = db.Column(db.String(20))
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship
    scan = db.relationship('Scan', backref=db.backref('results', lazy='dynamic'))

    def __repr__(self) -> str:
        return f'<ScanResult {self.component}:{self.metric_name}={self.metric_value}>'
