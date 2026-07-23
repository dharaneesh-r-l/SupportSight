# SupportSight
## AI-Powered Windows Diagnostics & IT Support Platform

![SupportSight Banner](https://img.shields.io/badge/SupportSight-Windows%20Diagnostics-0078D4?style=for-the-badge&logo=microsoft&logoColor=white)
![Python Version](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/flask-3.0.0-000000?style=for-the-badge&logo=flask&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-green?style=for-the-badge)

**SupportSight** is a professional Windows diagnostics, local AI root cause inference, and IT support platform. It automatically scans Windows hardware subsystems, collects real-time system telemetry, isolates operational bottlenecks, computes a dynamic 0-100 system health index, and provides step-by-step troubleshooting recommendations through a modern Windows 11 Fluent and Microsoft Defender styled interface.

---

## 🎯 Key Features

### 🧠 Local AI Root Cause Analysis Engine
- **Deterministic AI Inference** - Analyzes live system telemetry without external cloud dependencies or third-party API costs.
- **Symptom Evidence Isolation** - Correlates CPU spikes, memory saturation, disk capacity thresholds, and network connectivity states.
- **Confidence Scoring** - Computes heuristic confidence ratings (e.g. `96% Confidence`) for every technical diagnosis.
- **Severity Matrix** - Ranks findings across `Critical`, `High`, `Medium`, and `Low` severity tiers.
- **Step-by-Step Resolution Checklists** - Provides clear, actionable technical resolution pathways.

### 🖥️ Core Hardware Diagnostics
- **Processor (CPU) Monitoring** - Real-time load, thread count, core frequency (MHz), and top CPU-consuming processes.
- **Physical Memory (RAM)** - Memory saturation, buffer allocation, swap usage, and memory-hungry process ranking.
- **Storage Subsystem** - Partition storage capacity, read/write usage, free space warnings, and SSD/HDD detection.
- **Network Interface** - Connection status, local/public IP routing, gateway ping latency, and DNS diagnostics.
- **Battery Health** - Charge level, AC power state, remaining discharge time, and battery degradation rating.
- **Process Management** - Complete active process enumeration with CPU % and RAM % resource ranking.

### 📊 Enterprise PDF Report Generator
- **Executive Cover Page** - Includes corporate header, audit metadata grid, machine hostname, and health status badge.
- **Subsystem Status Matrix** - High-level operational table with color-coded status pills (`HEALTHY`, `WARNING`, `CRITICAL`).
- **Visual Telemetry Progress Chart** - Rendered via ReportLab graphics shapes comparing CPU, RAM, and Storage loads.
- **Two-Pass `NumberedCanvas`** - Dynamic `Page X of Y` footers and confidential running headers on pages 2+.

### 💻 Modern Windows 11 Fluent UI
- **Microsoft Defender Security Theme** - Segoe UI typography, Defender green/blue/amber status palette, and dynamic shield badge pulse animations.
- **High-Precision OS Recognition** - Accurately identifies Windows 11 builds (Build `22000+` / `25H2`) and Windows Registry build numbers.
- **Accurate CPU Model Recognition** - Reads Central Processor Registry strings (e.g., `AMD Ryzen 5 5600H with Radeon Graphics` / `Intel Core i7-13700H`).
- **Responsive Layout** - Collapsible dark sidebar (80px vs 280px), off-canvas mobile drawer backdrop, custom dark scrollbars, and toast notifications.

---

## 🏗️ Architecture & Project Structure

```
SupportSight/
├── app/
│   ├── __init__.py                  # Flask app factory & auto DB schema migration
│   ├── auth/                        # User authentication & profile routes
│   ├── api/                         # REST API endpoints & AI inference
│   ├── dashboard/                   # Dashboard overview & scan result views
│   ├── diagnostics/                 # Subsystem diagnostic detail pages
│   ├── reports/                     # PDF report generation routes
│   ├── models/                      # SQLAlchemy ORM models (User, Scan, Recommendation)
│   ├── services/
│   │   ├── system_info.py           # Accurate OS & CPU brand name collector
│   │   ├── cpu_service.py           # CPU telemetry & process ranking
│   │   ├── ram_service.py           # RAM saturation & process ranking
│   │   ├── disk_service.py          # Storage partition diagnostics
│   │   ├── network_service.py       # Ping latency & network interface collector
│   │   ├── battery_service.py       # Power & battery health service
│   │   ├── process_service.py       # Active process enumeration
│   │   ├── health_score_service.py  # Overall health index score engine (0-100)
│   │   ├── recommendation_service.py# Diagnostic recommendations generator
│   │   ├── root_cause_service.py    # Local Rule-Based AI Root Cause Analysis engine
│   │   ├── scan_service.py          # Diagnostic scan orchestrator & history
│   │   └── reports_service.py       # Enterprise PDF report generator (ReportLab)
│   ├── utils/                       # Utility formatters & validators
│   ├── templates/                   # Jinja2 HTML templates
│   └── static/                      # Custom CSS design system, JS charts, & assets
├── config.py                        # Configuration settings
├── init_db.py                       # Database initialization script
├── run.py                           # Application entry point
├── requirements.txt                 # Python dependencies
└── README.md                        # Documentation
```

---

## 🛠️ Tech Stack

### Backend
- **Python 3.10+** - Core runtime
- **Flask 3.0** - Web framework
- **SQLAlchemy 2.0 / Flask-SQLAlchemy 3.1** - Database ORM
- **Flask-Login** - Session authentication
- **Flask-Bcrypt** - Password hashing
- **SQLite** - Embedded database

### Frontend
- **HTML5 / Vanilla CSS3** - Custom Windows 11 Fluent Design System
- **Bootstrap 5** - Responsive layout grids
- **JavaScript (ES6+)** - Dynamic DOM updates & AJAX polling
- **Chart.js** - Telemetry line/bar data visualization
- **Boxicons** - Icon library

### Libraries
- **psutil** - Cross-platform hardware diagnostics
- **ReportLab 4.0** - Enterprise PDF document creation

---

## 📦 Installation & Setup

### Prerequisites
- Python 3.10 or higher
- `pip` package manager

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/supportsight.git
cd supportsight
```

### 2. Create Virtual Environment
```bash
python -m venv venv

# Windows (PowerShell)
venv\Scripts\activate

# Linux / macOS
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Initialize Database & Create Admin User
```bash
python init_db.py
```

### 5. Run the Application
```bash
python run.py
```

Access the dashboard at `http://localhost:5000`

### 🔑 Default Credentials
- **Username:** `admin`
- **Password:** `password123` *(or `Admin@123`)*

---

## 📊 REST API Reference

| Endpoint | Method | Description |
|----------|:---:|-------------|
| `/api/system` | `GET` | System information, hostname, accurate OS & CPU model |
| `/api/cpu` | `GET` | CPU telemetry, core frequencies, and top processes |
| `/api/ram` | `GET` | Physical memory allocations and top RAM processes |
| `/api/disk` | `GET` | Storage partitions usage and capacity breakdown |
| `/api/network` | `GET` | Network interfaces, gateway latency, and IP routing |
| `/api/battery` | `GET` | Battery charge level, AC status, and health status |
| `/api/processes` | `GET` | Active process enumeration and resource usage |
| `/api/health` | `GET` | Overall health score index (0-100) |
| `/api/status` | `GET` | Quick subsystem status summary |
| `/api/root-cause` | `GET` | Live real-time AI Root Cause Analysis inference |
| `/api/scan/<scan_id>/root-cause` | `GET` | Historical scan snapshot AI Root Cause analysis |
| `/api/scan` | `POST` | Trigger and save a new complete diagnostic scan |

---

## 🧪 Testing & Verification

Run the full automated unit and integration test suite using `pytest`:

```bash
# Run pytest with code coverage
pytest -v --cov=app
```

*39 / 39 test suites pass with 100% success rate.*

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Built for Windows IT Professionals & System Administrators**
