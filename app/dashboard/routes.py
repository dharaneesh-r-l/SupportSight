"""
SupportSight Dashboard Routes

Main dashboard and overview pages.
"""

from flask import render_template, redirect, url_for, flash, jsonify, request
from flask_login import login_required, current_user
from app.dashboard import dashboard_bp
from app.services.scan_service import ScanService
from app.services.health_score_service import HealthScoreService


@dashboard_bp.route('/')
def index():
    """Main landing page - redirects to dashboard."""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.home'))
    return redirect(url_for('auth.login'))


@dashboard_bp.route('/dashboard')
@dashboard_bp.route('/home')
@login_required
def home():
    """Main dashboard page."""
    # Get latest scan for quick status
    latest_scan = ScanService.get_latest_scan(current_user.id)

    # Get quick status
    quick_status = ScanService.get_quick_status()

    # Get recent scans
    recent_scans = ScanService.get_user_scans(current_user.id, limit=5)

    context = {
        'latest_scan': latest_scan,
        'quick_status': quick_status,
        'recent_scans': recent_scans
    }

    return render_template('dashboard/home.html', **context)


@dashboard_bp.route('/diagnostics')
@login_required
def diagnostics():
    """Comprehensive diagnostics page."""
    quick_status = ScanService.get_quick_status()

    return render_template('dashboard/diagnostics.html', status=quick_status)


@dashboard_bp.route('/scan-history')
@login_required
def scan_history():
    """Scan history page."""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    history = ScanService.get_scan_history(current_user.id, page=page, per_page=per_page)

    return render_template('dashboard/scan_history.html', **history)


@dashboard_bp.route('/quick-scan')
@login_required
def quick_scan():
    """Trigger a quick scan."""
    scan = ScanService.run_full_scan(current_user.id)

    if scan:
        flash('Scan completed successfully!', 'success')
        return redirect(url_for('dashboard.scan_result', scan_id=scan.id))
    else:
        flash('Scan failed. Please try again.', 'danger')
        return redirect(url_for('dashboard.home'))


@dashboard_bp.route('/scan/<int:scan_id>')
@login_required
def scan_result(scan_id):
    """View a specific scan result."""
    scan = ScanService.get_scan_by_id(scan_id)

    if not scan or scan.user_id != current_user.id:
        flash('Scan not found.', 'warning')
        return redirect(url_for('dashboard.scan_history'))

    return render_template('dashboard/scan_result.html', scan=scan)


@dashboard_bp.route('/api/quick-status')
@login_required
def api_quick_status():
    """API endpoint for quick status."""
    status = ScanService.get_quick_status()
    return jsonify(status)


@dashboard_bp.route('/api/health-score')
@login_required
def api_health_score():
    """API endpoint for current health score."""
    health = HealthScoreService.get_overall_health()
    return jsonify(health)
