import pytest
import os
from app.services.system_info import SystemInfoService
from app.services.cpu_service import CPUService
from app.services.ram_service import RAMService
from app.services.disk_service import DiskService
from app.services.network_service import NetworkService
from app.services.battery_service import BatteryService
from app.services.process_service import ProcessService
from app.services.health_score_service import HealthScoreService
from app.services.recommendation_service import RecommendationService
from app.services.scan_service import ScanService
from app.services.reports_service import ReportsService
from app.services.root_cause_service import RootCauseAnalysisService
from app.models.scan import Scan
from app import db


def test_system_info_service():
    info = SystemInfoService.get_system_info()
    assert isinstance(info, dict)
    assert 'computer_name' in info
    assert 'platform' in info
    assert 'cpu' in info
    assert 'memory' in info


def test_cpu_service():
    CPUService.record_usage()
    cpu_info = CPUService.get_cpu_info()
    assert isinstance(cpu_info, dict)
    assert 'usage' in cpu_info
    assert 'core_count' in cpu_info

    history = CPUService.get_usage_history(10)
    assert isinstance(history, list)

    health = CPUService.get_cpu_health_status()
    assert 'status' in health

    top_proc = CPUService.get_top_processes(5)
    assert isinstance(top_proc, list)


def test_ram_service():
    RAMService.record_usage()
    ram_info = RAMService.get_memory_info()
    assert isinstance(ram_info, dict)
    assert 'memory' in ram_info
    assert 'percent' in ram_info['memory']

    history = RAMService.get_usage_history(10)
    assert isinstance(history, list)

    health = RAMService.get_memory_health_status()
    assert 'status' in health

    top_proc = RAMService.get_top_processes(5)
    assert isinstance(top_proc, list)


def test_disk_service():
    disk_info = DiskService.get_disk_info()
    assert isinstance(disk_info, dict)
    assert 'partitions' in disk_info

    crit = DiskService.get_critical_partitions()
    assert isinstance(crit, list)


def test_network_service():
    net_info = NetworkService.get_network_info()
    assert isinstance(net_info, dict)
    assert 'interfaces' in net_info

    quality = NetworkService.get_connection_quality()
    assert 'quality' in quality
    assert 'severity' in quality

    ping_res = NetworkService.ping_host('127.0.0.1', count=1)
    assert isinstance(ping_res, dict)


def test_battery_service():
    bat_info = BatteryService.get_battery_info()
    assert isinstance(bat_info, dict)

    health = BatteryService.get_battery_health_status()
    assert isinstance(health, dict)


def test_process_service():
    proc_info = ProcessService.get_process_info()
    assert isinstance(proc_info, dict)

    top_cpu = ProcessService.get_top_cpu_processes(5)
    assert isinstance(top_cpu, list)

    top_mem = ProcessService.get_top_memory_processes(5)
    assert isinstance(top_mem, list)

    counts = ProcessService.get_process_count()
    assert isinstance(counts, dict)

    zombies = ProcessService.get_zombie_processes()
    assert isinstance(zombies, list)


def test_health_score_service():
    health = HealthScoreService.get_overall_health()
    assert isinstance(health, dict)
    assert 'category' in health
    assert 'components' in health


def test_scan_and_recommendation_and_report_services(app, test_user):
    with app.app_context():
        scan = ScanService.run_full_scan(test_user.id)
        assert scan is not None
        assert scan.status == 'completed'
        assert scan.health_score is not None

        # Test scan retrieval
        fetched_scan = ScanService.get_scan_by_id(scan.id)
        assert fetched_scan.id == scan.id

        latest = ScanService.get_latest_scan(test_user.id)
        assert latest.id == scan.id

        history = ScanService.get_scan_history(test_user.id)
        assert history['total'] >= 1

        quick_stat = ScanService.get_quick_status()
        assert isinstance(quick_stat, dict)

        # Test Report service PDF generation
        filename = ReportsService.get_report_filename(scan)
        assert filename.endswith('.pdf')

        pdf_path = ReportsService.generate_pdf_report(scan)
        assert pdf_path is not None
        assert os.path.exists(pdf_path)

        # Cleanup created pdf file
        if os.path.exists(pdf_path):
            os.remove(pdf_path)


def test_root_cause_service():
    # Test with critical high usage metrics
    mock_data = {
        'cpu': {'usage': 94.5, 'count': 8, 'top_processes': [{'name': 'chrome.exe', 'cpu_percent': 45.2}]},
        'ram': {'memory': {'percent': 88.0, 'available_mb': 1024, 'total_gb': 16.0}},
        'disk': {'overall_percent': 92.0, 'partitions': [{'device': 'C:', 'percent': 95.0}]},
        'network': {'connected': False, 'latency': 0},
        'battery': {'has_battery': True, 'percent': 15, 'is_charging': False}
    }

    result = RootCauseAnalysisService.analyze_system(mock_data)
    assert isinstance(result, dict)
    assert 'summary' in result
    assert 'findings' in result
    assert result['overall_confidence'] >= 75
    assert len(result['findings']) == 5

    first_finding = result['findings'][0]
    assert 'possible_causes' in first_finding
    assert 'severity' in first_finding
    assert 'confidence_score' in first_finding
    assert 'step_by_step_recommendations' in first_finding
    assert len(first_finding['step_by_step_recommendations']) > 0

    # Test with healthy metrics
    healthy_data = {
        'cpu': {'usage': 25.0},
        'ram': {'memory': {'percent': 40.0}},
        'disk': {'overall_percent': 50.0},
        'network': {'connected': True, 'latency': 25.0}
    }
    healthy_result = RootCauseAnalysisService.analyze_system(healthy_data)
    assert healthy_result['overall_confidence'] == 99
    assert len(healthy_result['findings']) == 1
    assert healthy_result['findings'][0]['severity'] == 'Low'
