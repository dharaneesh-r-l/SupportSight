"""
SupportSight API Routes

REST API endpoints for system diagnostics.
"""

from flask import jsonify, request
from flask_login import login_required, current_user
from app.api import api_bp
from app.services.system_info import SystemInfoService
from app.services.cpu_service import CPUService
from app.services.ram_service import RAMService
from app.services.disk_service import DiskService
from app.services.network_service import NetworkService
from app.services.battery_service import BatteryService
from app.services.process_service import ProcessService
from app.services.health_score_service import HealthScoreService
from app.services.scan_service import ScanService
from app.services.root_cause_service import RootCauseAnalysisService
from app.models.scan import Scan


@api_bp.route('/system')
@login_required
def get_system_info():
    """Get comprehensive system information."""
    data = SystemInfoService.get_system_info()
    return jsonify(data)


@api_bp.route('/cpu')
@login_required
def get_cpu():
    """Get CPU diagnostics."""
    CPUService.record_usage()
    data = CPUService.get_cpu_info()
    return jsonify(data)


@api_bp.route('/cpu/history')
@login_required
def get_cpu_history():
    """Get CPU usage history."""
    points = request.args.get('points', 60, type=int)
    history = CPUService.get_usage_history(points)
    return jsonify({'history': history})


@api_bp.route('/ram')
@login_required
def get_ram():
    """Get RAM diagnostics."""
    RAMService.record_usage()
    data = RAMService.get_memory_info()
    return jsonify(data)


@api_bp.route('/ram/history')
@login_required
def get_ram_history():
    """Get RAM usage history."""
    points = request.args.get('points', 60, type=int)
    history = RAMService.get_usage_history(points)
    return jsonify({'history': history})


@api_bp.route('/disk')
@login_required
def get_disk():
    """Get disk diagnostics."""
    data = DiskService.get_disk_info()
    return jsonify(data)


@api_bp.route('/network')
@login_required
def get_network():
    """Get network diagnostics."""
    data = NetworkService.get_network_info()
    return jsonify(data)


@api_bp.route('/network/ping')
@login_required
def ping_host():
    """Ping a host."""
    host = request.args.get('host', '8.8.8.8')
    count = request.args.get('count', 4, type=int)
    result = NetworkService.ping_host(host, count)
    return jsonify(result)


@api_bp.route('/battery')
@login_required
def get_battery():
    """Get battery diagnostics."""
    data = BatteryService.get_battery_info()
    return jsonify(data)


@api_bp.route('/processes')
@login_required
def get_processes():
    """Get running processes."""
    limit = request.args.get('limit', 50, type=int)
    sort = request.args.get('sort', 'cpu')
    search = request.args.get('search', '')

    if search:
        processes = ProcessService.search_processes(search)
    elif sort == 'memory':
        processes = ProcessService.get_top_memory_processes(limit)
    else:
        processes = ProcessService.get_top_cpu_processes(limit)

    return jsonify({'processes': processes})


@api_bp.route('/health')
@login_required
def get_health():
    """Get overall health score."""
    data = HealthScoreService.get_overall_health()
    return jsonify(data)


@api_bp.route('/status')
@login_required
def get_quick_status():
    """Get quick system status."""
    data = ScanService.get_quick_status()
    return jsonify(data)


@api_bp.route('/root-cause')
@login_required
def get_root_cause_analysis():
    """Get AI root cause analysis for current live system diagnostics."""
    status_data = ScanService.get_quick_status()
    # Add top processes to snapshot
    status_data['processes'] = ProcessService.get_top_cpu_processes(10)
    analysis = RootCauseAnalysisService.analyze_system(status_data)
    return jsonify(analysis)


@api_bp.route('/scan/<int:scan_id>/root-cause')
@login_required
def get_scan_root_cause(scan_id):
    """Get AI root cause analysis for a specific saved scan snapshot."""
    scan = ScanService.get_scan_by_id(scan_id)
    if not scan or scan.user_id != current_user.id:
        return jsonify({'error': 'Scan not found'}), 404
        
    scan_dict = scan.to_dict()
    diagnostic_data = scan_dict.get('data', {})
    analysis = RootCauseAnalysisService.analyze_system(diagnostic_data)
    return jsonify(analysis)


@api_bp.route('/scan', methods=['POST'])
@login_required
def start_scan():
    """Start a new diagnostic scan."""
    scan = ScanService.run_full_scan(current_user.id)

    if scan:
        return jsonify({
            'success': True,
            'scan_id': scan.id,
            'health_score': scan.health_score,
            'status': scan.status
        })
    else:
        return jsonify({
            'success': False,
            'message': 'Scan failed'
        }), 500


@api_bp.route('/scan/<int:scan_id>')
@login_required
def get_scan(scan_id):
    """Get a specific scan."""
    scan = ScanService.get_scan_by_id(scan_id)

    if not scan or scan.user_id != current_user.id:
        return jsonify({'error': 'Scan not found'}), 404

    return jsonify(scan.to_dict())


@api_bp.route('/scan/<int:scan_id>/component/<string:component>')
@login_required
def get_scan_component(scan_id, component):
    """Get specific component data from a scan."""
    data = ScanService.get_component_data(scan_id, component)

    if data is None:
        return jsonify({'error': 'Component not found'}), 404

    return jsonify(data)


@api_bp.route('/scans')
@login_required
def get_scans():
    """Get scan history."""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    history = ScanService.get_scan_history(current_user.id, page, per_page)
    return jsonify(history)


@api_bp.route('/scans/latest')
@login_required
def get_latest_scan():
    """Get the most recent scan."""
    scan = ScanService.get_latest_scan(current_user.id)

    if scan:
        return jsonify(scan.to_dict())
    return jsonify({'error': 'No scans found'}), 404


@api_bp.route('/export/<int:scan_id>')
@login_required
def export_scan(scan_id):
    """Export scan as JSON."""
    data = ScanService.export_scan_to_dict(scan_id)

    if data is None:
        return jsonify({'error': 'Scan not found'}), 404

    return jsonify(data)
