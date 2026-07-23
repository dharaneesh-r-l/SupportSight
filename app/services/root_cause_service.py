"""
SupportSight Root Cause Analysis Service

Local, rule-based AI engine for analyzing system metrics and identifying root causes.
"""

from typing import Dict, List, Any, Optional
import math


class RootCauseAnalysisService:
    """
    Local AI Root Cause Analysis Engine.

    Evaluates system diagnostics using deterministic inference rules
    to derive technical root causes, severity levels, confidence scores,
    and step-by-step resolution pathways.
    """

    SEVERITY_CRITICAL = "Critical"
    SEVERITY_HIGH = "High"
    SEVERITY_MEDIUM = "Medium"
    SEVERITY_LOW = "Low"

    @classmethod
    def analyze_system(cls, diagnostic_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform local rule-based AI root cause analysis on diagnostic snapshot.

        Args:
            diagnostic_data: Full system scan or live metrics payload

        Returns:
            Dictionary containing overall summary, impact assessment, and detailed root cause findings.
        """
        findings = []

        # Analyze CPU
        cpu_finding = cls._analyze_cpu(diagnostic_data.get('cpu', {}), diagnostic_data.get('processes', []))
        if cpu_finding:
            findings.append(cpu_finding)

        # Analyze RAM
        ram_finding = cls._analyze_ram(diagnostic_data.get('ram', {}), diagnostic_data.get('processes', []))
        if ram_finding:
            findings.append(ram_finding)

        # Analyze Disk / Storage
        disk_finding = cls._analyze_disk(diagnostic_data.get('disk', {}))
        if disk_finding:
            findings.append(disk_finding)

        # Analyze Network
        network_finding = cls._analyze_network(diagnostic_data.get('network', {}))
        if network_finding:
            findings.append(network_finding)

        # Analyze Battery
        battery_finding = cls._analyze_battery(diagnostic_data.get('battery', {}))
        if battery_finding:
            findings.append(battery_finding)

        # Overall summary generation
        if not findings:
            summary = "AI Root Cause Engine detected zero system execution bottlenecks or resource constraints."
            impact = "Optimal System Performance"
            overall_confidence = 99
            findings.append({
                'id': 'rc_optimal',
                'component': 'System',
                'title': 'All Core Subsystems Operating Normally',
                'severity': cls.SEVERITY_LOW,
                'confidence_score': 99,
                'symptom_evidence': 'CPU, RAM, Storage, and Network parameters are well within nominal threshold limits.',
                'possible_causes': [
                    'Hardware resources are adequately scaled for current background processes.',
                    'No active software deadlocks or memory leaks detected.'
                ],
                'step_by_step_recommendations': [
                    '1. Maintain periodic diagnostic monitoring scans.',
                    '2. Ensure Windows Security definitions remain up-to-date.',
                    '3. Keep operating system patches current.'
                ]
            })
        else:
            critical_count = sum(1 for f in findings if f['severity'] == cls.SEVERITY_CRITICAL)
            high_count = sum(1 for f in findings if f['severity'] == cls.SEVERITY_HIGH)
            
            if critical_count > 0:
                summary = f"AI Analysis identified {critical_count} critical subsystem bottleneck(s) requiring immediate intervention."
                impact = "High Risk of System Instability & Unresponsiveness"
            elif high_count > 0:
                summary = f"AI Analysis detected {high_count} high-priority performance constraint(s) impacting system speed."
                impact = "Elevated Resource Saturation"
            else:
                summary = "AI Analysis identified minor component optimization opportunities."
                impact = "Sub-optimal Resource Allocation"
                
            avg_confidence = math.floor(sum(f['confidence_score'] for f in findings) / len(findings))
            overall_confidence = max(75, min(99, avg_confidence))

        return {
            'summary': summary,
            'health_impact': impact,
            'overall_confidence': overall_confidence,
            'total_findings': len(findings),
            'findings': findings
        }

    @classmethod
    def _analyze_cpu(cls, cpu_data: Dict[str, Any], processes: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        usage = cpu_data.get('usage', 0)
        cores = cpu_data.get('logical_cores', cpu_data.get('count', 4))
        top_processes = cpu_data.get('top_processes', processes)

        if usage < 65:
            return None

        if usage >= 90:
            severity = cls.SEVERITY_CRITICAL
            confidence = 96
        elif usage >= 80:
            severity = cls.SEVERITY_HIGH
            confidence = 91
        else:
            severity = cls.SEVERITY_MEDIUM
            confidence = 84

        top_proc_name = "Background Applications"
        top_proc_pct = 0
        if top_processes and isinstance(top_processes, list) and len(top_processes) > 0:
            first = top_processes[0]
            top_proc_name = first.get('name', 'Unknown Process')
            top_proc_pct = first.get('cpu_percent', first.get('cpu', 0))

        symptom = f"CPU utilization is at {usage:.1f}% across {cores} threads. "
        if top_proc_pct > 0:
            symptom += f"Process '{top_proc_name}' accounts for {top_proc_pct:.1f}% of total CPU cycles."

        possible_causes = [
            f"High CPU contention caused by '{top_proc_name}' or intensive active foreground tasks.",
            "Unoptimized background service or update downloader running infinite execution loop.",
            "Potential thermal throttling forcing processor clock down under heavy computational load."
        ]

        steps = [
            f"1. Open Task Manager and inspect CPU usage for '{top_proc_name}'.",
            "2. Terminate non-essential background processes or browser tabs with high CPU consumption.",
            "3. Run a Windows Security / Defender antimalware scan to check for unauthorized crypto-miners.",
            "4. Verify hardware ventilation ports are clear of dust to prevent thermal CPU throttling."
        ]

        return {
            'id': 'rc_cpu',
            'component': 'CPU',
            'title': 'High Processor Utilization & Thread Contention',
            'severity': severity,
            'confidence_score': confidence,
            'symptom_evidence': symptom,
            'possible_causes': possible_causes,
            'step_by_step_recommendations': steps
        }

    @classmethod
    def _analyze_ram(cls, ram_data: Dict[str, Any], processes: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        memory = ram_data.get('memory', ram_data)
        pct = memory.get('percent', 0)
        available_mb = memory.get('available_mb', memory.get('available', 0) / (1024 * 1024) if memory.get('available') else 0)
        total_gb = memory.get('total_gb', memory.get('total', 0) / (1024 * 1024 * 1024) if memory.get('total') else 0)

        if pct < 70:
            return None

        if pct >= 90:
            severity = cls.SEVERITY_CRITICAL
            confidence = 97
        elif pct >= 80:
            severity = cls.SEVERITY_HIGH
            confidence = 92
        else:
            severity = cls.SEVERITY_MEDIUM
            confidence = 85

        symptom = f"Physical Memory saturation at {pct:.1f}% ({available_mb:.0f} MB available of {total_gb:.1f} GB total)."

        possible_causes = [
            "Gradual memory leak in long-running desktop application or web browser instances.",
            "High concentration of resident memory applications loaded simultaneously.",
            "Virtual memory paging overflow forcing Windows swap file to disk, slowing system throughput."
        ]

        steps = [
            "1. Identify and close browser windows containing multiple heavy WebGL or media tabs.",
            "2. Restart applications that have been running continuously for several days to flush heap memory.",
            "3. Disable unnecessary startup applications in Windows Task Manager > Startup tab.",
            "4. Consider upgrading physical RAM capacity if memory usage regularly exceeds 85%."
        ]

        return {
            'id': 'rc_ram',
            'component': 'Memory',
            'title': 'Physical Memory Saturation & Heap Degradation',
            'severity': severity,
            'confidence_score': confidence,
            'symptom_evidence': symptom,
            'possible_causes': possible_causes,
            'step_by_step_recommendations': steps
        }

    @classmethod
    def _analyze_disk(cls, disk_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        overall_pct = disk_data.get('overall_percent', 0)
        partitions = disk_data.get('partitions', [])

        critical_part = None
        for p in partitions:
            if p.get('percent', 0) >= 85:
                critical_part = p
                break

        if overall_pct < 75 and not critical_part:
            return None

        pct = critical_part.get('percent', overall_pct) if critical_part else overall_pct
        part_name = critical_part.get('device', 'Primary Drive') if critical_part else 'Primary Drive'

        if pct >= 90:
            severity = cls.SEVERITY_CRITICAL
            confidence = 98
        elif pct >= 80:
            severity = cls.SEVERITY_HIGH
            confidence = 93
        else:
            severity = cls.SEVERITY_MEDIUM
            confidence = 86

        symptom = f"Storage partition '{part_name}' reached {pct:.1f}% capacity."

        possible_causes = [
            "Accumulation of temporary files, Windows Update cache, and system error log dumps.",
            "Large media downloads, un-emptied Recycle Bin, or oversized pagefile/hibernate files.",
            "Insufficient free disk space preventing Windows from allocating virtual memory paging files."
        ]

        steps = [
            "1. Launch Windows Storage Sense or Disk Cleanup utility to purge temporary system cache.",
            "2. Empty the desktop Recycle Bin to free up immediately recoverable space.",
            "3. Remove unneeded large applications or move large media files to secondary storage.",
            "4. Verify at least 15% free disk space is maintained for healthy Windows pagefile operation."
        ]

        return {
            'id': 'rc_disk',
            'component': 'Storage',
            'title': 'Storage Partition Capacity Exhaustion',
            'severity': severity,
            'confidence_score': confidence,
            'symptom_evidence': symptom,
            'possible_causes': possible_causes,
            'step_by_step_recommendations': steps
        }

    @classmethod
    def _analyze_network(cls, network_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        connected = network_data.get('connected', True)
        latency = network_data.get('latency', 0)

        if connected and (latency == 0 or latency < 120):
            return None

        if not connected:
            severity = cls.SEVERITY_CRITICAL
            confidence = 99
            symptom = "Network interface has lost internet connectivity to target gateway."
            causes = [
                "Local network adapter disabled or disconnected from Wi-Fi / Ethernet access point.",
                "DHCP IP configuration failure or local router DNS resolution failure.",
                "Upstream Internet Service Provider (ISP) outage."
            ]
            steps = [
                "1. Check physical Ethernet cable or verify Wi-Fi network connection state.",
                "2. Reset local TCP/IP stack via command prompt: 'ipconfig /flushdns' and 'netsh winsock reset'.",
                "3. Restart local Wi-Fi router / modem hardware.",
                "4. Run Windows Network Troubleshooting wizard."
            ]
        else:
            severity = cls.SEVERITY_HIGH
            confidence = 89
            symptom = f"Elevated network latency measured at {latency:.1f}ms to gateway."
            causes = [
                "Wi-Fi channel congestion or low signal strength to wireless access point.",
                "Background cloud backup or Windows Update downloading large bandwidth payloads.",
                "High latency or packet jitter along ISP routing nodes."
            ]
            steps = [
                "1. Move closer to the wireless access point or connect via direct Ethernet cable.",
                "2. Pause active cloud sync tasks (OneDrive, Google Drive, Dropbox) or large downloads.",
                "3. Flush local DNS cache using command prompt: 'ipconfig /flushdns'.",
                "4. Test connection speed and ping latency against alternative public DNS servers (8.8.8.8)."
            ]

        return {
            'id': 'rc_network',
            'component': 'Network',
            'title': 'Network Connectivity & Latency Degradation',
            'severity': severity,
            'confidence_score': confidence,
            'symptom_evidence': symptom,
            'possible_causes': causes,
            'step_by_step_recommendations': steps
        }

    @classmethod
    def _analyze_battery(cls, battery_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if not battery_data or not battery_data.get('has_battery', False):
            return None

        pct = battery_data.get('percent', 100)
        charging = battery_data.get('is_charging', False)

        if pct > 20 or charging:
            return None

        return {
            'id': 'rc_battery',
            'component': 'Battery',
            'title': 'Low Power Capacity & Battery Discharge',
            'severity': cls.SEVERITY_HIGH,
            'confidence_score': 94,
            'symptom_evidence': f"Battery level is at {pct}% while running on battery power.",
            'possible_causes': [
                "Discharging battery under active laptop usage without AC power adapter connected.",
                "High display brightness and high-performance battery power plan consuming elevated wattage."
            ],
            'step_by_step_recommendations': [
                "1. Connect laptop to AC main power adapter immediately.",
                "2. Lower display screen brightness to extend remaining battery life.",
                "3. Enable Windows Battery Saver mode until connected to wall power."
            ]
        }
