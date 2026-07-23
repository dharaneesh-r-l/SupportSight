"""
SupportSight Reports Service

Generates PDF reports from scan data.
"""

import os
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

from app.utils.helpers import format_bytes, format_percentage, format_duration

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch, cm
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

from app.models.scan import Scan

logger = logging.getLogger(__name__)


class ReportsService:
    """
    Service for generating diagnostic reports.

    Creates professional PDF reports from scan data.
    """

    @classmethod
    def generate_pdf_report(cls, scan: Scan, output_path: str = None) -> Optional[str]:
        """
        Generate a PDF report for a scan.

        Args:
            scan: Scan object
            output_path: Optional output file path

        Returns:
            Path to generated PDF or None
        """
        if not REPORTLAB_AVAILABLE:
            logger.error("ReportLab is not installed. Cannot generate PDF.")
            return None

        if output_path is None:
            output_dir = Path(__file__).parent.parent.parent / 'reports'
            output_dir.mkdir(exist_ok=True)
            filename = f"supportsight_report_{scan.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            output_path = output_dir / filename

        try:
            doc = SimpleDocTemplate(
                str(output_path),
                pagesize=letter,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=72
            )

            # Build report content
            story = []
            styles = getSampleStyleSheet()

            # Custom styles
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                spaceAfter=30,
                alignment=TA_CENTER,
                textColor=colors.HexColor('#0078D4')
            )

            heading_style = ParagraphStyle(
                'CustomHeading',
                parent=styles['Heading2'],
                fontSize=14,
                spaceBefore=20,
                spaceAfter=10,
                textColor=colors.HexColor('#323130')
            )

            # Title
            story.append(Paragraph("SupportSight", title_style))
            story.append(Paragraph("Diagnostic Report", styles['Heading2']))
            story.append(Spacer(1, 20))

            # Report info
            info_data = [
                ['Report ID:', str(scan.id)],
                ['Scan Date:', scan.started_at.strftime('%Y-%m-%d %H:%M:%S') if scan.started_at else 'N/A'],
                ['Health Score:', f"{scan.health_score}/100 ({scan.health_category})"],
                ['Scan Duration:', format_duration(scan.duration) if scan.duration else 'N/A'],
                ['Status:', scan.status.capitalize()]
            ]

            info_table = Table(info_data, colWidths=[1.5*inch, 4*inch])
            info_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#323130')),
            ]))
            story.append(info_table)
            story.append(Spacer(1, 30))

            # System Information
            story.append(Paragraph("System Information", heading_style))
            system_info = scan.get_data('system_info')
            if system_info:
                sys_data = [
                    ['Computer Name:', system_info.get('computer_name', 'N/A')],
                    ['Platform:', system_info.get('platform', {}).get('system', 'N/A')],
                    ['OS:', system_info.get('platform', {}).get('release', 'N/A')],
                    ['Architecture:', system_info.get('platform', {}).get('architecture', 'N/A')],
                    ['Processor:', system_info.get('platform', {}).get('processor', 'N/A')],
                ]

                sys_table = Table(sys_data, colWidths=[2*inch, 4*inch])
                sys_table.setStyle(TableStyle([
                    ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ]))
                story.append(sys_table)

            story.append(Spacer(1, 20))

            # Health Score Summary
            story.append(Paragraph("Health Score Summary", heading_style))
            score_color = cls._get_score_color(scan.health_score)
            score_text = f"<font color='{score_color}'><b>{scan.health_score}/100</b></font> - {scan.health_category}"
            story.append(Paragraph(f"Overall Score: {score_text}", styles['Normal']))
            story.append(Spacer(1, 20))

            # CPU Information
            cpu_data = scan.get_data('cpu_data')
            if cpu_data:
                story.append(Paragraph("CPU Diagnostics", heading_style))
                cpu_info = [
                    ['Usage:', f"{cpu_data.get('usage', 0):.1f}%"],
                    ['Average:', f"{cpu_data.get('average_usage', 0):.1f}%"],
                    ['Physical Cores:', str(cpu_data.get('core_count', {}).get('physical', 'N/A'))],
                    ['Logical Cores:', str(cpu_data.get('core_count', {}).get('logical', 'N/A'))],
                ]
                cpu_table = Table(cpu_info, colWidths=[2*inch, 4*inch])
                cpu_table.setStyle(TableStyle([
                    ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ]))
                story.append(cpu_table)
                story.append(Spacer(1, 15))

            # RAM Information
            ram_data = scan.get_data('ram_data')
            if ram_data:
                story.append(Paragraph("Memory (RAM) Diagnostics", heading_style))
                memory = ram_data.get('memory', {})
                ram_info = [
                    ['Usage:', f"{memory.get('percent', 0):.1f}%"],
                    ['Total:', format_bytes(memory.get('total', 0))],
                    ['Used:', format_bytes(memory.get('used', 0))],
                    ['Available:', format_bytes(memory.get('available', 0))],
                ]
                ram_table = Table(ram_info, colWidths=[2*inch, 4*inch])
                ram_table.setStyle(TableStyle([
                    ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ]))
                story.append(ram_table)
                story.append(Spacer(1, 15))

            # Disk Information
            disk_data = scan.get_data('disk_data')
            if disk_data:
                story.append(Paragraph("Disk Diagnostics", heading_style))
                partitions = disk_data.get('partitions', [])
                if partitions:
                    disk_table_data = [['Drive', 'Total', 'Used', 'Free', 'Usage']]

                    for partition in partitions[:5]:  # Limit to 5 partitions
                        disk_table_data.append([
                            partition.get('mountpoint', 'N/A'),
                            format_bytes(partition.get('total', 0)),
                            format_bytes(partition.get('used', 0)),
                            format_bytes(partition.get('free', 0)),
                            f"{partition.get('percent', 0):.1f}%"
                        ])

                    disk_table = Table(disk_table_data, colWidths=[0.8*inch, 1.2*inch, 1.2*inch, 1.2*inch, 0.8*inch])
                    disk_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0078D4')),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, -1), 9),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                        ('TOPPADDING', (0, 0), (-1, -1), 6),
                        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#E1DFDD')),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ]))
                    story.append(disk_table)
                story.append(Spacer(1, 15))

            # Network Information
            network_data = scan.get_data('network_data')
            if network_data:
                story.append(Paragraph("Network Diagnostics", heading_style))
                connectivity = network_data.get('internet_connectivity', {})
                network_info = [
                    ['Hostname:', network_data.get('hostname', 'N/A')],
                    ['Local IP:', network_data.get('local_ip', 'N/A')],
                    ['Internet:', 'Connected' if connectivity.get('connected') else 'Disconnected'],
                    ['Latency:', f"{connectivity.get('latency', 'N/A')} ms" if connectivity.get('latency') else 'N/A'],
                ]
                network_table = Table(network_info, colWidths=[2*inch, 4*inch])
                network_table.setStyle(TableStyle([
                    ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ]))
                story.append(network_table)
                story.append(Spacer(1, 15))

            # Battery Information
            battery_data = scan.get_data('battery_data')
            if battery_data and battery_data.get('has_battery'):
                story.append(Paragraph("Battery Diagnostics", heading_style))
                battery_info = [
                    ['Status:', battery_data.get('status', 'N/A')],
                    ['Charge:', f"{battery_data.get('percent', 0)}%"],
                    ['Plugged In:', 'Yes' if battery_data.get('is_plugged_in') else 'No'],
                ]
                battery_table = Table(battery_info, colWidths=[2*inch, 4*inch])
                battery_table.setStyle(TableStyle([
                    ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ]))
                story.append(battery_table)
                story.append(Spacer(1, 15))

            # Recommendations
            recommendations = scan.get_data('recommendations')
            if recommendations:
                story.append(PageBreak())
                story.append(Paragraph("Recommendations", heading_style))

                for i, rec in enumerate(recommendations[:10], 1):  # Limit to 10
                    severity = rec.get('severity', 'info')
                    severity_color = cls._get_severity_color(severity)

                    story.append(Paragraph(
                        f"<font color='{severity_color}'><b>{i}. {rec.get('title', 'Recommendation')}</b></font>",
                        styles['Normal']
                    ))
                    story.append(Paragraph(rec.get('description', ''), styles['Normal']))

                    action_items = rec.get('action_items', [])
                    if action_items:
                        story.append(Spacer(1, 5))
                        for item in action_items[:5]:
                            story.append(Paragraph(f"• {item}", styles['Normal']))

                    story.append(Spacer(1, 15))

            # Footer
            story.append(Spacer(1, 30))
            footer_text = f"<i>Generated by SupportSight on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</i>"
            story.append(Paragraph(footer_text, styles['Normal']))

            # Build PDF
            doc.build(story)
            logger.info(f"PDF report generated: {output_path}")

            return str(output_path)

        except Exception as e:
            logger.error(f"Failed to generate PDF report: {str(e)}")
            return None

    @classmethod
    def _get_score_color(cls, score: int) -> str:
        """Get color for health score."""
        if score >= 80:
            return '#28a745'  # Green
        elif score >= 60:
            return '#ffc107'  # Yellow
        elif score >= 40:
            return '#fd7e14'  # Orange
        return '#dc3545'  # Red

    @classmethod
    def _get_severity_color(cls, severity: str) -> str:
        """Get color for severity level."""
        colors = {
            'critical': '#dc3545',
            'warning': '#fd7e14',
            'info': '#0078D4'
        }
        return colors.get(severity, '#6c757d')

    @classmethod
    def get_report_filename(cls, scan: Scan) -> str:
        """Get a formatted filename for a report."""
        date_str = scan.started_at.strftime('%Y%m%d') if scan.started_at else 'unknown'
        return f"supportsight_report_{scan.id}_{date_str}.pdf"
