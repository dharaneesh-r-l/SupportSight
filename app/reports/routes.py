"""
SupportSight Reports Routes

PDF report generation and download.
"""

import os
from flask import render_template, redirect, url_for, flash, send_file, request
from flask_login import login_required, current_user
from app.reports import reports_bp
from app.services.reports_service import ReportsService
from app.services.scan_service import ScanService


@reports_bp.route('/report/<int:scan_id>')
@login_required
def view_report(scan_id):
    """View report details."""
    scan = ScanService.get_scan_by_id(scan_id)

    if not scan or scan.user_id != current_user.id:
        flash('Report not found.', 'warning')
        return redirect(url_for('dashboard.scan_history'))

    return render_template('dashboard/report.html', scan=scan)


@reports_bp.route('/report/<int:scan_id>/download')
@login_required
def download_report(scan_id):
    """Download PDF report."""
    scan = ScanService.get_scan_by_id(scan_id)

    if not scan or scan.user_id != current_user.id:
        flash('Report not found.', 'warning')
        return redirect(url_for('dashboard.scan_history'))

    if scan.status != 'completed':
        flash('Report not available. Scan may have failed.', 'warning')
        return redirect(url_for('dashboard.scan_result', scan_id=scan_id))

    # Generate PDF
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
@login_required
def all_reports():
    """List all downloadable reports."""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    history = ScanService.get_scan_history(current_user.id, page, per_page)

    return render_template('dashboard/reports.html', **history)
