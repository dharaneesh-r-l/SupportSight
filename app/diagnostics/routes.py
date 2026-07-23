"""
SupportSight Diagnostics Routes

Detailed diagnostic pages for each system component.
"""

from flask import render_template, jsonify
from app.diagnostics import diagnostics_bp
from app.services.cpu_service import CPUService
from app.services.ram_service import RAMService
from app.services.disk_service import DiskService
from app.services.network_service import NetworkService
from app.services.battery_service import BatteryService
from app.services.process_service import ProcessService


@diagnostics_bp.route('/cpu')
def cpu():
    """CPU diagnostics page."""
    CPUService.record_usage()
    cpu_data = CPUService.get_cpu_info()
    health = CPUService.get_cpu_health_status()
    top_processes = CPUService.get_top_processes(10)

    return render_template('dashboard/cpu.html',
                           cpu=cpu_data,
                           health=health,
                           top_processes=top_processes)


@diagnostics_bp.route('/ram')
def ram():
    """RAM diagnostics page."""
    RAMService.record_usage()
    ram_data = RAMService.get_memory_info()
    health = RAMService.get_memory_health_status()
    top_processes = RAMService.get_top_processes(10)

    return render_template('dashboard/ram.html',
                           ram=ram_data,
                           health=health,
                           top_processes=top_processes)


@diagnostics_bp.route('/disk')
def disk():
    """Disk diagnostics page."""
    disk_data = DiskService.get_disk_info()
    critical_partitions = DiskService.get_critical_partitions()

    return render_template('dashboard/disk.html',
                           disk=disk_data,
                           critical_partitions=critical_partitions)


@diagnostics_bp.route('/network')
def network():
    """Network diagnostics page."""
    network_data = NetworkService.get_network_info()
    quality = NetworkService.get_connection_quality()

    return render_template('dashboard/network.html',
                           network=network_data,
                           quality=quality)


@diagnostics_bp.route('/battery')
def battery():
    """Battery diagnostics page."""
    battery_data = BatteryService.get_battery_info()
    health = BatteryService.get_battery_health_status()

    return render_template('dashboard/battery.html',
                           battery=battery_data,
                           health=health)


@diagnostics_bp.route('/processes')
def processes():
    """Processes page."""
    process_data = ProcessService.get_process_info()
    counts = ProcessService.get_process_count()
    zombies = ProcessService.get_zombie_processes()

    return render_template('dashboard/processes.html',
                           processes=process_data,
                           counts=counts,
                           zombies=zombies)


@diagnostics_bp.route('/system')
def system():
    """System information page."""
    from app.services.system_info import SystemInfoService
    system_info = SystemInfoService.get_system_info()

    return render_template('dashboard/system.html', system=system_info)
