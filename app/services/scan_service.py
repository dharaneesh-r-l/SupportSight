"""
SupportSight Scan Service

Orchestrates comprehensive system diagnostic scans.
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

from app import db
from app.models.scan import Scan
from app.models.recommendation import Recommendation
from app.services.system_info import SystemInfoService
from app.services.cpu_service import CPUService
from app.services.ram_service import RAMService
from app.services.disk_service import DiskService
from app.services.battery_service import BatteryService
from app.services.network_service import NetworkService
from app.services.process_service import ProcessService
from app.services.health_score_service import HealthScoreService
from app.services.recommendation_service import RecommendationService

logger = logging.getLogger(__name__)


class ScanService:
    """
    Service for orchestrating diagnostic scans.

    Coordinates collection of system data, health scoring,
    and recommendation generation.
    """

    @classmethod
    def run_full_scan(cls, user_id: int) -> Optional[Scan]:
        """
        Run a complete diagnostic scan.

        Args:
            user_id: ID of user initiating the scan

        Returns:
            Scan object or None if scan failed
        """
        scan = Scan(user_id=user_id, scan_type=Scan.TYPE_FULL)
        db.session.add(scan)
        db.session.commit()

        try:
            # Collect all diagnostic data
            diagnostic_data = cls._collect_diagnostic_data()

            # Store system info
            scan.set_data('system_info', diagnostic_data.get('system_info', {}))
            scan.set_data('cpu_data', diagnostic_data.get('cpu', {}))
            scan.set_data('ram_data', diagnostic_data.get('ram', {}))
            scan.set_data('disk_data', diagnostic_data.get('disk', {}))
            scan.set_data('network_data', diagnostic_data.get('network', {}))
            scan.set_data('battery_data', diagnostic_data.get('battery', {}))
            scan.set_data('process_data', diagnostic_data.get('processes', {}))

            # Calculate health score
            health_data = HealthScoreService.get_overall_health()
            health_score = health_data.get('overall_score', 0)

            # Generate recommendations
            recommendations = RecommendationService.generate_recommendations(diagnostic_data)
            scan.set_data('recommendations', recommendations)

            # Mark scan as completed
            scan.mark_completed(health_score)

            # Create recommendation records
            cls._create_recommendation_records(scan.id, recommendations)

            db.session.commit()
            logger.info(f"Full scan completed for user {user_id}. Health score: {health_score}")

            return scan

        except Exception as e:
            logger.error(f"Scan failed: {str(e)}")
            scan.mark_failed(str(e))
            db.session.commit()
            return None

    @classmethod
    def _collect_diagnostic_data(cls) -> Dict[str, Any]:
        """
        Collect all diagnostic data from services.

        Returns:
            Dictionary with all diagnostic information
        """
        # Collect data in parallel would be ideal, but we'll do sequential
        data = {}

        # System info
        data['system_info'] = SystemInfoService.get_system_info()

        # CPU data
        CPUService.record_usage()
        data['cpu'] = CPUService.get_cpu_info()

        # RAM data
        RAMService.record_usage()
        data['ram'] = RAMService.get_memory_info()

        # Disk data
        data['disk'] = DiskService.get_disk_info()

        # Network data
        data['network'] = NetworkService.get_network_info()

        # Battery data
        data['battery'] = BatteryService.get_battery_info()

        # Process data
        data['processes'] = ProcessService.get_process_info()

        return data

    @classmethod
    def _create_recommendation_records(cls, scan_id: int,
                                         recommendations: List[Dict[str, Any]]) -> None:
        """
        Create Recommendation records in database.

        Args:
            scan_id: Scan ID
            recommendations: List of recommendation dictionaries
        """
        for rec in recommendations:
            recommendation = Recommendation(
                scan_id=scan_id,
                component=rec.get('component', 'general'),
                severity=rec.get('severity', 'info'),
                title=rec.get('title', ''),
                description=rec.get('description', ''),
                action_items=rec.get('action_items', [])
            )
            db.session.add(recommendation)

    @classmethod
    def get_scan_by_id(cls, scan_id: int) -> Optional[Scan]:
        """
        Get a scan by ID.

        Args:
            scan_id: Scan ID

        Returns:
            Scan object or None
        """
        return Scan.query.get(scan_id)

    @classmethod
    def get_user_scans(cls, user_id: int, limit: int = 20) -> List[Scan]:
        """
        Get scans for a user.

        Args:
            user_id: User ID
            limit: Maximum number of scans to return

        Returns:
            List of Scan objects
        """
        return Scan.query.filter_by(user_id=user_id)\
                        .order_by(Scan.started_at.desc())\
                        .limit(limit)\
                        .all()

    @classmethod
    def get_latest_scan(cls, user_id: int) -> Optional[Scan]:
        """
        Get the most recent scan for a user.

        Args:
            user_id: User ID

        Returns:
            Latest Scan object or None
        """
        return Scan.query.filter_by(user_id=user_id)\
                        .filter_by(status=Scan.STATUS_COMPLETED)\
                        .order_by(Scan.started_at.desc())\
                        .first()

    @classmethod
    def delete_scan(cls, scan_id: int) -> bool:
        """
        Delete a scan.

        Args:
            scan_id: Scan ID

        Returns:
            True if deleted, False otherwise
        """
        scan = Scan.query.get(scan_id)
        if scan:
            db.session.delete(scan)
            db.session.commit()
            return True
        return False

    @classmethod
    def get_quick_status(cls) -> Dict[str, Any]:
        """
        Get a quick system status without creating a scan.

        Returns:
            Dictionary with quick status information
        """
        # Record current CPU usage
        CPUService.record_usage()
        RAMService.record_usage()

        return {
            'timestamp': datetime.utcnow().isoformat(),
            'cpu': {
                'usage': CPUService.get_usage(),
                'average': CPUService.get_average_usage()
            },
            'ram': {
                'percent': RAMService.get_percent(),
                'average': RAMService.get_average_usage()
            },
            'battery': BatteryService.get_battery_health_status(),
            'network': NetworkService.check_internet_connectivity()
        }

    @classmethod
    def get_scan_history(cls, user_id: int, page: int = 1,
                          per_page: int = 20) -> Dict[str, Any]:
        """
        Get paginated scan history for a user.

        Args:
            user_id: User ID
            page: Page number
            per_page: Items per page

        Returns:
            Dictionary with paginated results
        """
        pagination = Scan.query.filter_by(user_id=user_id)\
                               .order_by(Scan.started_at.desc())\
                               .paginate(page=page, per_page=per_page, error_out=False)

        return {
            'scans': [scan.to_dict() for scan in pagination.items],
            'total': pagination.total,
            'page': pagination.page,
            'pages': pagination.pages,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev
        }

    @classmethod
    def export_scan_to_dict(cls, scan_id: int) -> Optional[Dict[str, Any]]:
        """
        Export a scan to a dictionary for JSON export.

        Args:
            scan_id: Scan ID

        Returns:
            Dictionary representation of scan or None
        """
        scan = Scan.query.get(scan_id)
        if scan:
            return scan.to_dict()
        return None

    @classmethod
    def get_component_data(cls, scan_id: int, component: str) -> Optional[Dict[str, Any]]:
        """
        Get specific component data from a scan.

        Args:
            scan_id: Scan ID
            component: Component name (cpu, ram, disk, etc.)

        Returns:
            Component data dictionary or None
        """
        scan = Scan.query.get(scan_id)
        if not scan:
            return None

        component_map = {
            'cpu': 'cpu_data',
            'ram': 'ram_data',
            'disk': 'disk_data',
            'network': 'network_data',
            'battery': 'battery_data',
            'processes': 'process_data',
            'system': 'system_info'
        }

        data_key = component_map.get(component.lower())
        if not data_key:
            return None

        return scan.get_data(data_key)
