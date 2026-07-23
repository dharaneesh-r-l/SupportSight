# SupportSight
## AI-Powered Windows Diagnostics & IT Support Platform

![SupportSight Banner](https://img.shields.io/badge/SupportSight-Windows%20Diagnostics-0078D4?style=for-the-badge&logo=microsoft&logoColor=white)

**SupportSight** is a professional Windows diagnostics and IT support platform that automatically analyzes Windows computers, collects system information, diagnoses common problems, calculates an overall system health score, and provides intelligent troubleshooting recommendations through a beautiful modern dashboard.

---

## 🎯 Features

### Core Diagnostics
- **CPU Monitoring** - Real-time CPU usage, frequency, core count, and process tracking
- **Memory Analysis** - RAM usage, swap memory, and memory-hungry process identification
- **Disk Diagnostics** - Storage usage, partition health, and SSD/HDD detection
- **Network Monitoring** - Connection status, latency, DNS, and gateway information
- **Battery Status** - Charge level, health, and time remaining (for laptops)
- **Process Management** - Running processes, CPU/RAM usage per process

### Intelligent Features
- **Health Score Engine** - Calculates 0-100 health score based on all components
- **Recommendation Engine** - Provides actionable recommendations based on diagnostic data
- **PDF Reports** - Generate comprehensive diagnostic reports
- **Scan History** - Track system health over time

### Modern UI
- Windows 11 inspired design
- Glassmorphism effects
- Smooth animations (AOS)
- Responsive layout
- Dark mode ready

---

## 🏗️ Architecture

```
SupportSight/
├── app/
│   ├── __init__.py          # Application factory
│   ├── auth/                 # Authentication module
│   ├── api/                  # REST API endpoints
│   ├── dashboard/            # Dashboard routes
│   ├── diagnostics/          # Diagnostic pages
│   ├── reports/              # Report generation
│   ├── models/               # Database models
│   ├── services/             # Business logic services
│   ├── utils/               # Helper functions
│   ├── templates/            # Jinja2 templates
│   └── static/               # CSS, JS, images
├── config.py                # Configuration
├── run.py                   # Entry point
├── requirements.txt         # Dependencies
└── README.md               # Documentation
```

---

## 🛠️ Tech Stack

### Backend
- **Python 3.12** - Core language
- **Flask 3.0** - Web framework
- **Flask-SQLAlchemy** - ORM
- **Flask-Login** - Authentication
- **Flask-Bcrypt** - Password hashing
- **SQLite** - Database (PostgreSQL-ready)

### Frontend
- **HTML5/CSS3** - Structure and styling
- **Bootstrap 5** - CSS framework
- **JavaScript** - Interactivity
- **Chart.js** - Data visualization
- **Boxicons** - Icon library
- **AOS** - Scroll animations

### Libraries
- **psutil** - System diagnostics
- **reportlab** - PDF generation
- **requests** - HTTP requests

---

## 📦 Installation

### Prerequisites
- Python 3.10 or higher
- pip (Python package manager)
- Git

### Clone the Repository
```bash
git clone https://github.com/yourusername/supportsight.git
cd supportsight
```

### Create Virtual Environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Run the Application
```bash
python run.py
```

The application will be available at `http://localhost:5000`

### Default Login
- **Username:** admin
- **Password:** Admin@123

---

## 🔧 Configuration

### Environment Variables
```bash
# Set Flask environment
export FLASK_ENV=development  # or production

# Set secret key (production)
export SECRET_KEY=your-secret-key-here

# Set database URL (production)
export DATABASE_URL=postgresql://user:password@localhost/supportsight
```

### Configuration File
Edit `config.py` to customize:
- Database settings
- Session configuration
- Health score thresholds
- Logging levels

---

## 📊 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/system` | GET | System information |
| `/api/cpu` | GET | CPU diagnostics |
| `/api/ram` | GET | RAM diagnostics |
| `/api/disk` | GET | Disk diagnostics |
| `/api/network` | GET | Network diagnostics |
| `/api/battery` | GET | Battery diagnostics |
| `/api/processes` | GET | Running processes |
| `/api/health` | GET | Health score |
| `/api/scan` | POST | Start new scan |

---

## 📁 Project Structure

```
SupportSight/
├── app/
│   ├── __init__.py           # Flask app factory
│   ├── auth/
│   │   ├── __init__.py
│   │   └── routes.py         # Login, register, logout
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py         # REST API endpoints
│   ├── dashboard/
│   │   ├── __init__.py
│   │   └── routes.py         # Dashboard routes
│   ├── diagnostics/
│   │   ├── __init__.py
│   │   └── routes.py         # Diagnostic pages
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py           # User model
│   │   ├── scan.py           # Scan model
│   │   └── recommendation.py # Recommendation model
│   ├── services/
│   │   ├── __init__.py
│   │   ├── system_info.py    # System info collector
│   │   ├── cpu_service.py    # CPU diagnostics
│   │   ├── ram_service.py    # RAM diagnostics
│   │   ├── disk_service.py   # Disk diagnostics
│   │   ├── network_service.py # Network diagnostics
│   │   ├── battery_service.py # Battery diagnostics
│   │   ├── process_service.py # Process monitoring
│   │   ├── health_score_service.py # Health calculation
│   │   ├── recommendation_service.py # Recommendations
│   │   ├── scan_service.py   # Scan orchestration
│   │   └── reports_service.py # PDF generation
│   ├── templates/
│   │   ├── base.html         # Base template
│   │   ├── auth/             # Auth templates
│   │   ├── components/       # Reusable components
│   │   ├── dashboard/        # Dashboard templates
│   │   └── errors/           # Error pages
│   └── static/
│       ├── css/              # Stylesheets
│       ├── js/                # JavaScript
│       └── images/           # Images
├── config.py                 # Configuration
├── run.py                    # Entry point
└── requirements.txt          # Dependencies
```

---

## 🎨 Screenshots

*Screenshots will be added here*

---

## 🔮 Future Scope

- [ ] Mobile app (React Native)
- [ ] Multi-device support
- [ ] Real-time WebSocket updates
- [ ] Cloud sync for scan history
- [ ] Malware detection integration
- [ ] Windows Security integration
- [ ] Remote support features
- [ ] Team/Enterprise features
- [ ] API rate limiting
- [ ] Dark mode toggle

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📧 Contact

- **Project Link:** https://github.com/yourusername/supportsight
- **Issues:** https://github.com/yourusername/supportsight/issues

---

## 🙏 Acknowledgments

- Microsoft for Windows design inspiration
- Flask community for the excellent framework
- Bootstrap team for the UI components
- All contributors who help improve this project

---

**Built with ❤️ for IT Support Professionals**
