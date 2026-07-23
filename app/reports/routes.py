"""
SupportSight Reports Routes

PDF report generation and download. No login required.
"""

import os
from flask import render_template, redirect, url_for, flash, send_file, request
from flask_login import current_user
from app.reports import reports_bp
from app.services.reports_service import ReportsService
from app.services.scan_service import ScanService

_GUEST_USER_ID = 0


@reports_bp.route('/report/<int:scan_id>')
def view_report(scan_id):
    """View report details."""
    scan = ScanService.get_scan_by_id(scan_id)

    if not scan:
        flash('Report not found.', 'warning')
        return redirect(url_for('dashboard.scan_history'))

    return render_template('dashboard/report.html', scan=scan)


@reports_bp.route('/report/<int:scan_id>/download')
def download_report(scan_id):
    """Download PDF report."""
    scan = ScanService.get_scan_by_id(scan_id)

    if not scan:
        flash('Report not found.', 'warning')
        return redirect(url_for('dashboard.scan_history'))

    if scan.status != 'completed':
        flash('Report not available. Scan may have failed.', 'warning')
        return redirect(url_for('dashboard.scan_result', scan_id=scan_id))

    filename = ReportsService.get_report_filename(scan)
    pdf_path = ReportsService.generate_pdf_report(scan)

    if pdf_path and os.path.exists(pdf_path):
        return send_file(
            pdf_path,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )
    else:
        flash('Failed to generate PDF report.', 'danger')
        return redirect(url_for('dashboard.scan_result', scan_id=scan_id))


@reports_bp.route('/reports')
def all_reports():
    """List all downloadable reports."""
    uid = current_user.id if current_user and current_user.is_authenticated else _GUEST_USER_ID
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    history = ScanService.get_scan_history(uid, page, per_page)
    return render_template('dashboard/reports.html', **history)
