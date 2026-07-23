"""
SupportSight Recommendation Model

Stores diagnostic recommendations and rules.
"""

import json
from datetime import datetime
from app import db


class Recommendation(db.Model):
    """
    Recommendation model for storing diagnostic recommendations.

    Attributes:
        id: Unique recommendation identifier
        scan_id: Reference to associated scan
        component: System component (cpu, ram, disk, network, etc.)
        severity: Issue severity (critical, warning, info)
        title: Recommendation title
        description: Detailed description
        action_items: JSON list of actionable steps
        resources: JSON list of helpful resources
        is_resolved: Whether recommendation was addressed
        created_at: Recommendation creation timestamp
        resolved_at: Resolution timestamp
    """

    __tablename__ = 'recommendations'

    # Severity levels
    SEVERITY_CRITICAL = 'critical'
    SEVERITY_WARNING = 'warning'
    SEVERITY_INFO = 'info'

    # Component types
    COMPONENT_CPU = 'cpu'
    COMPONENT_RAM = 'ram'
    COMPONENT_DISK = 'disk'
    COMPONENT_NETWORK = 'network'
    COMPONENT_BATTERY = 'battery'
    COMPONENT_GPU = 'gpu'
    COMPONENT_GENERAL = 'general'

    id = db.Column(db.Integer, primary_key=True)
    scan_id = db.Column(db.Integer, db.ForeignKey('scans.id'), nullable=False, index=True)
    component = db.Column(db.String(50), nullable=False, index=True)
    severity = db.Column(db.String(20), default=SEVERITY_INFO)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    action_items = db.Column(db.Text)  # JSON list
    resources = db.Column(db.Text)  # JSON list
    is_resolved = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    resolved_at = db.Column(db.DateTime)

    # Relationship
    scan = db.relationship('Scan', backref=db.backref('rec_list', lazy='dynamic'))

    def __init__(self, **kwargs):
        """Initialize recommendation."""
        super(Recommendation, self).__init__(**kwargs)
        # Convert action_items and resources to JSON if list
        if 'action_items' in kwargs and isinstance(kwargs['action_items'], list):
            self.action_items = json.dumps(kwargs['action_items'])
        if 'resources' in kwargs and isinstance(kwargs['resources'], list):
            self.resources = json.dumps(kwargs['resources'])

    def set_action_items(self, items: list) -> None:
        """Set action items as JSON."""
        self.action_items = json.dumps(items)

    def get_action_items(self) -> list:
        """Get action items from JSON."""
        if self.action_items:
            try:
                return json.loads(self.action_items)
            except json.JSONDecodeError:
                return []
        return []

    def set_resources(self, resources: list) -> None:
        """Set resources as JSON."""
        self.resources = json.dumps(resources)

    def get_resources(self) -> list:
        """Get resources from JSON."""
        if self.resources:
            try:
                return json.loads(self.resources)
            except json.JSONDecodeError:
                return []
        return []

    def mark_resolved(self) -> None:
        """Mark recommendation as resolved."""
        self.is_resolved = True
        self.resolved_at = datetime.utcnow()

    @property
    def severity_color(self) -> str:
        """Get Bootstrap color for severity."""
        colors = {
            self.SEVERITY_CRITICAL: 'danger',
            self.SEVERITY_WARNING: 'warning',
            self.SEVERITY_INFO: 'info'
        }
        return colors.get(self.severity, 'info')

    @property
    def severity_icon(self) -> str:
        """Get icon class for severity."""
        icons = {
            self.SEVERITY_CRITICAL: 'exclamation-triangle-fill',
            self.SEVERITY_WARNING: 'exclamation-circle',
            self.SEVERITY_INFO: 'info-circle'
        }
        return icons.get(self.severity, 'info-circle')

    def to_dict(self) -> dict:
        """Convert recommendation to dictionary."""
        return {
            'id': self.id,
            'scan_id': self.scan_id,
            'component': self.component,
            'severity': self.severity,
            'title': self.title,
            'description': self.description,
            'action_items': self.get_action_items(),
            'resources': self.get_resources(),
            'is_resolved': self.is_resolved,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None
        }

    def __repr__(self) -> str:
        return f'<Recommendation {self.id}: {self.title}>'


class RecommendationRule(db.Model):
    """
    Rule model for defining recommendation generation rules.

    Allows configuration of threshold-based recommendations.
    """

    __tablename__ = 'recommendation_rules'

    id = db.Column(db.Integer, primary_key=True)
    component = db.Column(db.String(50), nullable=False, index=True)
    metric_name = db.Column(db.String(100), nullable=False)
    operator = db.Column(db.String(10), nullable=False)  # gt, lt, eq, gte, lte
    threshold = db.Column(db.Float, nullable=False)
    severity = db.Column(db.String(20), default=Recommendation.SEVERITY_WARNING)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    action_items = db.Column(db.Text)  # JSON list
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __init__(self, **kwargs):
        """Initialize recommendation rule."""
        super(RecommendationRule, self).__init__(**kwargs)
        if 'action_items' in kwargs and isinstance(kwargs['action_items'], list):
            self.action_items = json.dumps(kwargs['action_items'])

    def evaluate(self, value: float) -> bool:
        """
        Evaluate if the rule should trigger for a given value.

        Args:
            value: Metric value to evaluate

        Returns:
            True if rule triggers, False otherwise
        """
        operators = {
            'gt': lambda v, t: v > t,
            'lt': lambda v, t: v < t,
            'eq': lambda v, t: v == t,
            'gte': lambda v, t: v >= t,
            'lte': lambda v, t: v <= t,
        }
        func = operators.get(self.operator)
        if func:
            return func(value, self.threshold)
        return False

    def create_recommendation(self, scan_id: int, current_value: float) -> Recommendation:
        """
        Create a recommendation from this rule.

        Args:
            scan_id: Associated scan ID
            current_value: Current metric value

        Returns:
            New Recommendation instance
        """
        return Recommendation(
            scan_id=scan_id,
            component=self.component,
            severity=self.severity,
            title=self.title,
            description=self.description,
            action_items=self.get_action_items()
        )

    def get_action_items(self) -> list:
        """Get action items from JSON."""
        if self.action_items:
            try:
                return json.loads(self.action_items)
            except json.JSONDecodeError:
                return []
        return []

    def __repr__(self) -> str:
        return f'<RecommendationRule {self.component}:{self.metric_name} {self.operator} {self.threshold}>'
