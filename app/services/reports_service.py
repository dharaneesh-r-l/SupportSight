"""
SupportSight Reports Service

Generates enterprise-grade PDF diagnostic reports from scan data.
"""

import os
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

from app.utils.helpers import format_bytes, format_percentage, format_duration

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
    )
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
    from reportlab.pdfgen import canvas
    from reportlab.graphics.shapes import Drawing, Rect, String, Line, Group
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

from app.models.scan import Scan

logger = logging.getLogger(__name__)


if REPORTLAB_AVAILABLE:
    class NumberedCanvas(canvas.Canvas):
        """
        Two-pass canvas for dynamic 'Page X of Y' footers and running headers.
        """
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self._saved_page_states = []

        def showPage(self):
            self._saved_page_states.append(dict(self.__dict__))
            self._startPage()

        def save(self):
            num_pages = len(self._saved_page_states)
            for state in self._saved_page_states:
                self.__dict__.update(state)
                self.draw_page_decorations(num_pages)
                super().showPage()
            super().save()

        def draw_page_decorations(self, page_count):
            if self._pageNumber == 1:
                return  # Skip cover page

            self.saveState()
            self.setFont("Helvetica", 9)
            self.setFillColor(colors.HexColor('#64748B'))

            # Running Header
            self.drawString(54, 752, "SupportSight Enterprise System Diagnostics & Audit Report")
            self.drawRightString(612 - 54, 752, datetime.now().strftime('%B %d, %Y'))
            self.setStrokeColor(colors.HexColor('#E2E8F0'))
            self.setLineWidth(0.75)
            self.line(54, 744, 612 - 54, 744)

            # Running Footer
            self.line(54, 45, 612 - 54, 45)
            self.drawString(54, 30, "CONFIDENTIAL — FOR INTERNAL IT AUDIT & SYSTEM MAINTENANCE USE ONLY")
            self.drawRightString(612 - 54, 30, f"Page {self._pageNumber} of {page_count}")
            self.restoreState()


class ReportsService:
    """
    Service for generating enterprise PDF diagnostic reports.

    Produces executive-ready PDFs with cover page, summary matrix,
    visual telemetry charts, AI root cause analysis, and detailed component audits.
    """

    @classmethod
    def generate_pdf_report(cls, scan: Scan, output_path: str = None) -> Optional[str]:
        """
        Generate an enterprise PDF report for a scan.

        Args:
            scan: Scan object
            output_path: Optional output file path

        Returns:
            Path to generated PDF or None
        """
        if not REPORTLAB_AVAILABLE:
            logger.error("ReportLab library is missing. Cannot generate PDF.")
            return None

        if output_path is None:
            output_dir = Path(__file__).parent.parent.parent / 'reports'
            output_dir.mkdir(exist_ok=True)
            filename = f"supportsight_enterprise_audit_{scan.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            output_path = output_dir / filename

        try:
            doc = SimpleDocTemplate(
                str(output_path),
                pagesize=letter,
                rightMargin=54,
                leftMargin=54,
                topMargin=54,
                bottomMargin=54
            )

            story = []
            styles = getSampleStyleSheet()

            # Enterprise Typography & Styles
            style_cover_title = ParagraphStyle(
                'CoverTitle',
                fontName='Helvetica-Bold',
                fontSize=28,
                leading=34,
                textColor=colors.HexColor('#0F172A'),
                alignment=TA_LEFT,
                spaceAfter=8
            )

            style_cover_subtitle = ParagraphStyle(
                'CoverSubtitle',
                fontName='Helvetica',
                fontSize=14,
                leading=18,
                textColor=colors.HexColor('#0078D4'),
                alignment=TA_LEFT,
                spaceAfter=24
            )

            style_h1 = ParagraphStyle(
                'EnterpriseH1',
                fontName='Helvetica-Bold',
                fontSize=16,
                leading=20,
                textColor=colors.HexColor('#0F172A'),
                spaceBefore=16,
                spaceAfter=12,
                keepWithNext=True
            )

            style_h2 = ParagraphStyle(
                'EnterpriseH2',
                fontName='Helvetica-Bold',
                fontSize=12,
                leading=16,
                textColor=colors.HexColor('#0078D4'),
                spaceBefore=12,
                spaceAfter=8,
                keepWithNext=True
            )

            style_body = ParagraphStyle(
                'EnterpriseBody',
                fontName='Helvetica',
                fontSize=9.5,
                leading=14,
                textColor=colors.HexColor('#334155'),
                spaceAfter=8
            )

            style_body_bold = ParagraphStyle(
                'EnterpriseBodyBold',
                fontName='Helvetica-Bold',
                fontSize=9.5,
                leading=14,
                textColor=colors.HexColor('#0F172A'),
                spaceAfter=8
            )

            # Table Cell Styles
            style_th = ParagraphStyle(
                'PDFTableHeader',
                fontName='Helvetica-Bold',
                fontSize=9,
                leading=11,
                textColor=colors.white,
                alignment=TA_LEFT
            )

            style_th_center = ParagraphStyle(
                'PDFTableHeaderCenter',
                fontName='Helvetica-Bold',
                fontSize=9,
                leading=11,
                textColor=colors.white,
                alignment=TA_CENTER
            )

            style_th_sub = ParagraphStyle(
                'PDFTableHeaderSub',
                fontName='Helvetica-Bold',
                fontSize=8.5,
                leading=11,
                textColor=colors.HexColor('#0F172A'),
                alignment=TA_LEFT
            )

            style_td = ParagraphStyle(
                'PDFTableCell',
                fontName='Helvetica',
                fontSize=8.5,
                leading=11,
                textColor=colors.HexColor('#334155'),
                alignment=TA_LEFT
            )

            style_td_bold = ParagraphStyle(
                'PDFTableCellBold',
                fontName='Helvetica-Bold',
                fontSize=8.5,
                leading=11,
                textColor=colors.HexColor('#0F172A'),
                alignment=TA_LEFT
            )

            style_td_center = ParagraphStyle(
                'PDFTableCellCenter',
                fontName='Helvetica',
                fontSize=8.5,
                leading=11,
                textColor=colors.HexColor('#334155'),
                alignment=TA_CENTER
            )

            # =========================================================================
            # SECTION 1: COVER PAGE
            # =========================================================================
            header_bar = Table([['']], colWidths=[504], rowHeights=[6])
            header_bar.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#0078D4')),
            ]))
            story.append(header_bar)
            story.append(Spacer(1, 24))

            story.append(Paragraph("SUPPORTSIGHT ENTERPRISE", ParagraphStyle('Brand', fontName='Helvetica-Bold', fontSize=10, textColor=colors.HexColor('#0078D4'), spaceAfter=6)))
            story.append(Paragraph("System Health & Diagnostic Audit Report", style_cover_title))
            story.append(Paragraph("Comprehensive Hardware Telemetry, Performance Analytics & Local AI Root Cause Analysis", style_cover_subtitle))

            story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#E2E8F0'), spaceBefore=0, spaceAfter=20))

            score_bg = cls._get_score_color_hex(scan.health_score)
            score_box_data = [
                [
                    Paragraph(f"<font color='white' size=32><b>{scan.health_score}</b></font><font color='#E2E8F0' size=14>/100</font>", ParagraphStyle('ScoreVal', alignment=TA_CENTER)),
                    Paragraph(f"<font color='white' size=16><b>OVERALL STATUS: {scan.health_category.upper()}</b></font><br/><font color='#E2E8F0' size=10>SupportSight System Health Audit Engine completed analysis.</font>", ParagraphStyle('ScoreDesc', alignment=TA_LEFT))
                ]
            ]
            score_table = Table(score_box_data, colWidths=[140, 364])
            score_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor(score_bg)),
                ('TOPPADDING', (0, 0), (-1, -1), 16),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 16),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('LEFTPADDING', (0, 0), (0, 0), 12),
                ('RIGHTPADDING', (1, 0), (1, 0), 16),
            ]))
            story.append(score_table)
            story.append(Spacer(1, 28))

            system_info = scan.get_data('system_info') or {}
            platform_info = system_info.get('platform', {})

            meta_data = [
                [Paragraph("<b>Audit Report ID:</b>", style_body), Paragraph(f"#{scan.id}", style_body), Paragraph("<b>Target Hostname:</b>", style_body), Paragraph(system_info.get('computer_name', 'N/A'), style_body)],
                [Paragraph("<b>Execution Date:</b>", style_body), Paragraph(scan.started_at.strftime('%Y-%m-%d %H:%M:%S') if scan.started_at else 'N/A', style_body), Paragraph("<b>Operating System:</b>", style_body), Paragraph(f"{platform_info.get('system', 'Windows')} {platform_info.get('release', '')}", style_body)],
                [Paragraph("<b>Audit Scan Type:</b>", style_body), Paragraph(scan.scan_type.upper(), style_body), Paragraph("<b>Architecture:</b>", style_body), Paragraph(platform_info.get('architecture', 'x64'), style_body)],
                [Paragraph("<b>Scan Duration:</b>", style_body), Paragraph(format_duration(scan.duration) if scan.duration else 'N/A', style_body), Paragraph("<b>Processor Specs:</b>", style_body), Paragraph(platform_info.get('processor', 'N/A')[:32], style_body)],
                [Paragraph("<b>Scan Status:</b>", style_body), Paragraph(f"<font color='#107C41'><b>{scan.status.upper()}</b></font>", style_body), Paragraph("<b>Total Memory:</b>", style_body), Paragraph(format_bytes(system_info.get('memory', {}).get('total', 0)), style_body)],
            ]

            meta_table = Table(meta_data, colWidths=[110, 142, 110, 142])
            meta_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F8FAFC')),
                ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#E2E8F0')),
                ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#F1F5F9')),
                ('TOPPADDING', (0, 0), (-1, -1), 7),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
                ('LEFTPADDING', (0, 0), (-1, -1), 8),
                ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ]))
            story.append(meta_table)
            story.append(Spacer(1, 40))

            signoff_data = [
                [Paragraph("<b>Report Generated For:</b> Authorized IT Administrator", style_body), Paragraph("<b>Inspection Engine:</b> SupportSight v2.0 Local AI", style_body)]
            ]
            signoff_table = Table(signoff_data, colWidths=[252, 252])
            signoff_table.setStyle(TableStyle([
                ('LINEABOVE', (0, 0), (-1, -1), 1, colors.HexColor('#CBD5E1')),
                ('TOPPADDING', (0, 0), (-1, -1), 10),
            ]))
            story.append(signoff_table)

            story.append(PageBreak())

            # =========================================================================
            # SECTION 2: EXECUTIVE SUMMARY & TELEMETRY CHARTS
            # =========================================================================
            story.append(Paragraph("1. Executive Summary & Subsystem Matrix", style_h1))
            story.append(Paragraph("This executive summary presents a high-level operational assessment of core hardware components based on diagnostic telemetry collected during the system audit scan.", style_body))

            cpu_data = scan.get_data('cpu_data') or {}
            ram_data = scan.get_data('ram_data') or {}
            disk_data = scan.get_data('disk_data') or {}
            network_data = scan.get_data('network_data') or {}
            battery_data = scan.get_data('battery_data') or {}

            cpu_val = cpu_data.get('usage', 0)
            ram_val = ram_data.get('memory', {}).get('percent', 0)
            disk_val = disk_data.get('overall_percent', 0)
            net_conn = network_data.get('internet_connectivity', {}).get('connected', True)

            matrix_rows = [
                [
                    Paragraph("Subsystem", style_th),
                    Paragraph("Metric Load / Value", style_th),
                    Paragraph("Status Level", style_th_center),
                    Paragraph("Operational Assessment", style_th)
                ],
                [
                    Paragraph("Processor (CPU)", style_td_bold),
                    Paragraph(f"{cpu_val:.1f}% Load", style_td),
                    Paragraph(cls._get_status_pill(cpu_val, 70, 88), style_td_center),
                    Paragraph("Normal core processing" if cpu_val < 70 else "Elevated CPU contention", style_td)
                ],
                [
                    Paragraph("Physical Memory (RAM)", style_td_bold),
                    Paragraph(f"{ram_val:.1f}% Saturation", style_td),
                    Paragraph(cls._get_status_pill(ram_val, 75, 90), style_td_center),
                    Paragraph("Optimal heap buffer" if ram_val < 75 else "High memory allocation", style_td)
                ],
                [
                    Paragraph("Storage Capacity", style_td_bold),
                    Paragraph(f"{disk_val:.1f}% Capacity Used", style_td),
                    Paragraph(cls._get_status_pill(disk_val, 80, 92), style_td_center),
                    Paragraph("Sufficient storage space" if disk_val < 80 else "Storage threshold warning", style_td)
                ],
                [
                    Paragraph("Network Interface", style_td_bold),
                    Paragraph("Connected" if net_conn else "Offline", style_td),
                    Paragraph("<font color='#107C41'><b>HEALTHY</b></font>" if net_conn else "<font color='#D13438'><b>CRITICAL</b></font>", style_td_center),
                    Paragraph("Active internet access" if net_conn else "Interface disconnected", style_td)
                ],
            ]

            if battery_data and battery_data.get('has_battery'):
                bat_pct = battery_data.get('percent', 100)
                matrix_rows.append([
                    Paragraph("Battery Subsystem", style_td_bold),
                    Paragraph(f"{bat_pct}% Charge", style_td),
                    Paragraph(cls._get_status_pill(100 - bat_pct, 70, 85), style_td_center),
                    Paragraph("AC/Battery normal" if bat_pct > 20 else "Low battery state", style_td)
                ])

            matrix_table = Table(matrix_rows, colWidths=[120, 110, 94, 180])
            matrix_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0F172A')),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('LEFTPADDING', (0, 0), (-1, -1), 6),
                ('RIGHTPADDING', (0, 0), (-1, -1), 6),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8FAFC')]),
            ]))
            story.append(matrix_table)
            story.append(Spacer(1, 18))

            story.append(Paragraph("Subsystem Load Telemetry Breakdown", style_h2))
            story.append(cls._draw_telemetry_chart(cpu_val, ram_val, disk_val))
            story.append(Spacer(1, 20))

            # =========================================================================
            # SECTION 3: AI ROOT CAUSE ANALYSIS REPORT
            # =========================================================================
            root_cause = scan.get_data('root_cause_analysis') or {}
            findings = root_cause.get('findings', [])

            story.append(Paragraph("2. Local AI Root Cause Analysis Report", style_h1))
            story.append(Paragraph("The SupportSight Local Rule-Based AI Engine evaluated system diagnostics to isolate potential operational bottlenecks, technical root causes, and resolution steps.", style_body))

            if findings:
                summary_text = root_cause.get('summary', 'AI Root Cause Engine completed analysis.')
                confidence = root_cause.get('overall_confidence', 95)

                ai_summary_box = [
                    [Paragraph(f"<b>AI Diagnosis Summary:</b> {summary_text}", style_body), Paragraph(f"<b>Confidence:</b> {confidence}%", ParagraphStyle('Right', parent=style_body_bold, alignment=TA_RIGHT))]
                ]
                ai_table = Table(ai_summary_box, colWidths=[380, 124])
                ai_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#EFF6FF')),
                    ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#93C5FD')),
                    ('TOPPADDING', (0, 0), (-1, -1), 8),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                    ('LEFTPADDING', (0, 0), (-1, -1), 10),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 10),
                ]))
                story.append(ai_table)
                story.append(Spacer(1, 14))

                for finding in findings:
                    sev = finding.get('severity', 'Medium')
                    sev_color = cls._get_severity_color_hex(sev)

                    f_title = finding.get('title', 'Diagnostic Finding')
                    f_comp = finding.get('component', 'System')
                    f_conf = finding.get('confidence_score', 90)
                    f_evidence = finding.get('symptom_evidence', 'No symptom recorded.')
                    f_causes = finding.get('possible_causes', [])
                    f_steps = finding.get('step_by_step_recommendations', [])

                    f_header_table = Table([[
                        Paragraph(f"<b>{f_title}</b> ({f_comp})", ParagraphStyle('FTitle', fontName='Helvetica-Bold', fontSize=10, textColor=colors.HexColor('#0F172A'))),
                        Paragraph(f"<font color='{sev_color}'><b>[{sev.upper()} SEVERITY]</b></font> &nbsp;|&nbsp; {f_conf}% Confidence", ParagraphStyle('FConf', fontName='Helvetica', fontSize=9, alignment=TA_RIGHT))
                    ]], colWidths=[330, 174])
                    f_header_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F1F5F9')),
                        ('LINEBELOW', (0, 0), (-1, -1), 1, colors.HexColor(sev_color)),
                        ('TOPPADDING', (0, 0), (-1, -1), 6),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                        ('LEFTPADDING', (0, 0), (-1, -1), 8),
                        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
                    ]))

                    finding_content = [f_header_table, Spacer(1, 6)]

                    finding_content.append(Paragraph(f"<b>Symptom Evidence:</b> {f_evidence}", style_body))

                    if f_causes:
                        finding_content.append(Paragraph("<b>Possible Technical Root Causes:</b>", style_body_bold))
                        for c in f_causes:
                            finding_content.append(Paragraph(f"• {c}", style_body))

                    if f_steps:
                        finding_content.append(Paragraph("<b>Step-by-Step Resolution Recommendations:</b>", ParagraphStyle('GreenH', parent=style_body_bold, textColor=colors.HexColor('#107C41'))))
                        for s in f_steps:
                            finding_content.append(Paragraph(f"  {s}", style_body))

                    finding_content.append(Spacer(1, 14))
                    story.append(KeepTogether(finding_content))

            story.append(Spacer(1, 10))

            # =========================================================================
            # SECTION 4: DETAILED COMPONENT AUDIT ANNEX
            # =========================================================================
            story.append(KeepTogether([
                Paragraph("3. Detailed Component Telemetry Annex", style_h1),
                Paragraph("Detailed diagnostic specifications gathered per hardware domain during scan execution.", style_body)
            ]))

            # CPU Details
            if cpu_data:
                cpu_details = [
                    [Paragraph('Parameter', style_th_sub), Paragraph('Diagnostic Value', style_th_sub), Paragraph('Parameter', style_th_sub), Paragraph('Diagnostic Value', style_th_sub)],
                    [Paragraph('Current Load:', style_td_bold), Paragraph(f"{cpu_data.get('usage', 0):.1f}%", style_td), Paragraph('Physical Cores:', style_td_bold), Paragraph(str(cpu_data.get('core_count', {}).get('physical', 'N/A')), style_td)],
                    [Paragraph('Average Load:', style_td_bold), Paragraph(f"{cpu_data.get('average_usage', 0):.1f}%", style_td), Paragraph('Logical Cores:', style_td_bold), Paragraph(str(cpu_data.get('core_count', {}).get('logical', 'N/A')), style_td)],
                    [Paragraph('Frequency:', style_td_bold), Paragraph(f"{cpu_data.get('frequency', {}).get('current', 0):.0f} MHz" if cpu_data.get('frequency') else 'N/A', style_td), Paragraph('Architecture:', style_td_bold), Paragraph(platform_info.get('architecture', 'N/A'), style_td)],
                ]
                cpu_tbl = Table(cpu_details, colWidths=[120, 132, 120, 132])
                cpu_tbl.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E2E8F0')),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
                    ('TOPPADDING', (0, 0), (-1, -1), 5),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                ]))
                story.append(KeepTogether([
                    Paragraph("Processor (CPU) Specifications", style_h2),
                    cpu_tbl,
                    Spacer(1, 12)
                ]))

            # RAM Details
            if ram_data:
                mem = ram_data.get('memory', {})
                ram_details = [
                    [Paragraph('Parameter', style_th_sub), Paragraph('Diagnostic Value', style_th_sub), Paragraph('Parameter', style_th_sub), Paragraph('Diagnostic Value', style_th_sub)],
                    [Paragraph('Memory Saturation:', style_td_bold), Paragraph(f"{mem.get('percent', 0):.1f}%", style_td), Paragraph('Total Installed RAM:', style_td_bold), Paragraph(format_bytes(mem.get('total', 0)), style_td)],
                    [Paragraph('Used Memory:', style_td_bold), Paragraph(format_bytes(mem.get('used', 0)), style_td), Paragraph('Available Memory:', style_td_bold), Paragraph(format_bytes(mem.get('available', 0)), style_td)],
                ]
                ram_tbl = Table(ram_details, colWidths=[120, 132, 120, 132])
                ram_tbl.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E2E8F0')),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
                    ('TOPPADDING', (0, 0), (-1, -1), 5),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                ]))
                story.append(KeepTogether([
                    Paragraph("Physical Memory (RAM) Specifications", style_h2),
                    ram_tbl,
                    Spacer(1, 12)
                ]))

            # Storage Partitions
            if disk_data and disk_data.get('partitions'):
                p_rows = [[
                    Paragraph('Drive Partition', style_th),
                    Paragraph('Total Capacity', style_th_center),
                    Paragraph('Used Space', style_th_center),
                    Paragraph('Free Space', style_th_center),
                    Paragraph('Usage %', style_th_center)
                ]]
                for p in disk_data.get('partitions', [])[:6]:
                    p_rows.append([
                        Paragraph(p.get('mountpoint', 'N/A'), style_td_bold),
                        Paragraph(format_bytes(p.get('total', 0)), style_td_center),
                        Paragraph(format_bytes(p.get('used', 0)), style_td_center),
                        Paragraph(format_bytes(p.get('free', 0)), style_td_center),
                        Paragraph(f"{p.get('percent', 0):.1f}%", style_td_center)
                    ])

                p_tbl = Table(p_rows, colWidths=[100, 100, 100, 104, 100])
                p_tbl.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0078D4')),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
                    ('TOPPADDING', (0, 0), (-1, -1), 5),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                ]))
                story.append(KeepTogether([
                    Paragraph("Storage Partition Breakdown", style_h2),
                    p_tbl,
                    Spacer(1, 12)
                ]))

            # Actionable Recommendations
            recommendations = scan.get_data('recommendations') or []
            if recommendations:
                story.append(KeepTogether([
                    Paragraph("4. Actionable Maintenance Recommendations", style_h1),
                    Paragraph("Specific maintenance actions recommended by SupportSight diagnostic rules engine:", style_body)
                ]))

                for i, rec in enumerate(recommendations[:8], 1):
                    sev = rec.get('severity', 'info')
                    sev_col = cls._get_severity_color_hex(sev)

                    r_block = [
                        Paragraph(f"<b>{i}. {rec.get('title', 'Recommendation')}</b> <font color='{sev_col}'>[{sev.upper()}]</font>", style_body_bold),
                        Paragraph(rec.get('description', ''), style_body)
                    ]

                    action_items = rec.get('action_items', [])
                    if action_items:
                        for act in action_items[:4]:
                            r_block.append(Paragraph(f"  • {act}", style_body))

                    r_block.append(Spacer(1, 8))
                    story.append(KeepTogether(r_block))

            # Build Document with Two-Pass Numbered Canvas
            doc.build(story, canvasmaker=NumberedCanvas)
            logger.info(f"Enterprise PDF report successfully generated: {output_path}")

            return str(output_path)

        except Exception as e:
            logger.error(f"Failed to generate PDF report: {str(e)}", exc_info=True)
            return None

    @classmethod
    def _draw_telemetry_chart(cls, cpu: float, ram: float, disk: float) -> Drawing:
        """
        Draw a visual horizontal bar chart using ReportLab shapes.
        """
        d = Drawing(504, 110)

        # Outer Background Box
        d.add(Rect(0, 0, 504, 110, fillColor=colors.HexColor('#F8FAFC'), strokeColor=colors.HexColor('#E2E8F0'), strokeWidth=1, rx=6, ry=6))

        # Bar Data
        metrics = [
            ('Processor Load (CPU)', cpu, colors.HexColor('#0078D4')),
            ('Memory Saturation (RAM)', ram, colors.HexColor('#107C41')),
            ('Storage Usage (Disk)', disk, colors.HexColor('#D97706'))
        ]

        y_pos = 75
        for label, val, bar_color in metrics:
            val_clamped = max(0, min(100, val))

            # Label
            d.add(String(14, y_pos + 4, label, fontName='Helvetica-Bold', fontSize=9, fillColor=colors.HexColor('#334155')))
            d.add(String(160, y_pos + 4, f"{val:.1f}%", fontName='Helvetica-Bold', fontSize=9, fillColor=colors.HexColor('#0F172A')))

            # Progress Bar Track
            track_w = 300
            d.add(Rect(190, y_pos + 2, track_w, 10, fillColor=colors.HexColor('#E2E8F0'), strokeColor=None, rx=3, ry=3))

            # Progress Bar Fill
            fill_w = max(4, (val_clamped / 100.0) * track_w)
            d.add(Rect(190, y_pos + 2, fill_w, 10, fillColor=bar_color, strokeColor=None, rx=3, ry=3))

            y_pos -= 28

        return d

    @classmethod
    def _get_status_pill(cls, val: float, warn_thresh: float, crit_thresh: float) -> str:
        """Get HTML text status pill."""
        if val >= crit_thresh:
            return "<font color='#D13438'><b>CRITICAL</b></font>"
        elif val >= warn_thresh:
            return "<font color='#D97706'><b>WARNING</b></font>"
        return "<font color='#107C41'><b>HEALTHY</b></font>"

    @classmethod
    def _get_score_color_hex(cls, score: int) -> str:
        """Get Hex background color for overall health score."""
        if score >= 80:
            return '#107C41'  # Defender Green
        elif score >= 60:
            return '#D97706'  # Amber
        elif score >= 40:
            return '#EA580C'  # Orange
        return '#D13438'      # Red

    @classmethod
    def _get_severity_color_hex(cls, severity: str) -> str:
        """Get Hex color for severity string."""
        sev = str(severity).lower()
        if sev == 'critical':
            return '#D13438'
        elif sev in ['high', 'warning']:
            return '#D97706'
        elif sev in ['medium', 'info']:
            return '#0078D4'
        return '#107C41'

    @classmethod
    def get_report_filename(cls, scan: Scan) -> str:
        """Get formatted filename for a report."""
        date_str = scan.started_at.strftime('%Y%m%d') if scan.started_at else 'unknown'
        return f"supportsight_enterprise_audit_{scan.id}_{date_str}.pdf"
