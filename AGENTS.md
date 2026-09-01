# AGENTS.md — WebDiag GPON Portal

Web portal for remote GPON terminal diagnostics.

## Project Structure
```
webdiag/
├── webdiag.py             # Flask app: routes, telnet diagnostics, auth
├── switches.py            # Huawei OLT switch configuration / telnet commands
├── templates/             # HTML templates (Jinja2)
├── static/                # CSS, JS, images
├── requirements.txt       # Dependencies (Flask, Paramiko, Telnetlib3, python-dotenv)
├── .env                   # Credentials (USERNAME, PASSWORD for OLT access)
├── Dockerfile             # Gunicorn deployment
└── run_server.sh          # Quick launch script
```

## Quick Start
```bash
pip install -r requirements.txt
cp .env.example .env  # configure OLT credentials
python webdiag.py     # Flask dev server on http://0.0.0.0:5000
# or via gunicorn:
gunicorn app:app -w 4 -b 0.0.0.0:8000
```

## Functionality
- Level 1 support: terminal diagnostics (ping, telnet to serial)
- Level 2 support: configuration changes, remote assistance
- Level 3 support: reserved for future escalation workflows
- Authentication via `.env`-configured credentials
- GPON OLT control via Telnet (Huawei OLT switches)

## Environment
- Python 3.12+
- Flask, Paramiko, Telnetlib3, Gunicorn
- Docker deployment supported

## Notes for Agents
- Network diagnostic tooling — this project intentionally uses Telnet/SSH for telecom infrastructure management.
- Credentials are stored in `.env` (not committed). The example file `.env.example` shows required variables.
- The `switches.py` module defines the Huawei OLT command set — changes here affect live network operations.
- No test suite; visual testing via browser-based UI.
- TODO list in `webdiag.py` top comments defines pending feature work.