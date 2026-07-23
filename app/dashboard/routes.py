"""
SupportSight Dashboard Routes

Main dashboard and overview pages.
"""

from flask import render_template, redirect, url_for, flash, jsonify, request
from flask_login import current_user
from app.dashboard import dashboard_bp
from app.services.scan_service import ScanService
from app.services.health_score_service import HealthScoreService

# Use a guest user ID (0) when no one is logged in
_GUEST_USER_ID = 0


def _active_user_id():
    """Return the logged-in user ID or a guest placeholder."""
    if current_user and current_user.is_authenticated:
        return current_user.id
    return _GUEST_USER_ID


@dashboard_bp.route('/')
def index():
    """Main landing page - goes straight to dashboard (no login required)."""
    return redirect(url_for('dashboard.home'))


@dashboard_bp.route('/dashboard')
@dashboard_bp.route('/home')
def home():
    """Main dashboard page."""
    uid = _active_user_id()
    latest_scan = ScanService.get_latest_scan(uid) if uid else None
    quick_status = ScanService.get_quick_status()
    recent_scans = ScanService.get_user_scans(uid, limit=5) if uid else []

    context = {
        'latest_scan': latest_scan,
        'quick_status': quick_status,
        'recent_scans': recent_scans
    }

    return render_template('dashboard/home.html', **context)


@dashboard_bp.route('/diagnostics')
def diagnostics():
    """Comprehensive diagnostics page."""
    quick_status = ScanService.get_quick_status()
    return render_template('dashboard/diagnostics.html', status=quick_status)


@dashboard_bp.route('/scan-history')
def scan_history():
    """Scan history page."""
    uid = _active_user_id()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    history = ScanService.get_scan_history(uid, page=page, per_page=per_page)
    return render_template('dashboard/scan_history.html', **history)


@dashboard_bp.route('/quick-scan')
def quick_scan():
    """Trigger a quick scan."""
    uid = _active_user_id()
    scan = ScanService.run_full_scan(uid)

    if scan:
        flash('Scan completed successfully!', 'success')
        return redirect(url_for('dashboard.scan_result', scan_id=scan.id))
    else:
        flash('Scan failed. Please try again.', 'danger')
        return redirect(url_for('dashboard.home'))


@dashboard_bp.route('/scan/<int:scan_id>')
def scan_result(scan_id):
    """View a specific scan result."""
    scan = ScanService.get_scan_by_id(scan_id)

    if not scan:
        flash('Scan not found.', 'warning')
        return redirect(url_for('dashboard.scan_history'))

    return render_template('dashboard/scan_result.html', scan=scan)


@dashboard_bp.route('/api/quick-status')
def api_quick_status():
    """API endpoint for quick status."""
    status = ScanService.get_quick_status()
    return jsonify(status)


@dashboard_bp.route('/api/health-score')
def api_health_score():
    """API endpoint for current health score."""
    health = HealthScoreService.get_overall_health()
    return jsonify(health)
