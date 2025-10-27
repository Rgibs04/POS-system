# POS System

## Uploading to GitHub
1. Create a new repository on GitHub (e.g., https://github.com/username/pos-system).
2. In your local terminal, navigate to the pos_system folder.
3. Run: `git remote add origin https://github.com/username/pos-system.git`
4. Run: `git push -u origin master`

## Quick Install (Interactive)
### Linux (Ubuntu/Debian)
1. Ensure Python3 and pip are installed: `sudo apt update && sudo apt install -y python3 python3-pip`.
2. Download the installer: `curl -O https://raw.githubusercontent.com/Rgibs04/POS-system/master/install.py`
3. Run `python3 install.py` (installer will check and install additional dependencies if needed).
4. Follow the prompts to choose Docker or native install (default: native).
5. The installer will clone the repo, install dependencies, and set up the system.

### Windows
1. Download the installer: `curl -O https://raw.githubusercontent.com/Rgibs04/POS-system/master/install_windows.bat`
2. Run `install_windows.bat` (installer will automatically install Python, Docker, and Git if needed).
3. Follow the prompts (Docker only).
4. The installer will clone the repo and set up the system via Docker.

## Manual Server Setup (Ubuntu 22.04 Server)
1. Install Python and pip.
2. Clone or copy the server folder.
3. cd server
4. pip install -r requirements.txt
5. python app.py &
6. python discovery_server.py &

## Manual Docker Setup (Cross-platform)
1. Install Docker and Docker Compose.
2. Clone or copy the entire project.
3. docker-compose up --build

## Kiosk Setup (Ubuntu 24.04 Desktop)
1. Install Python and pip.
2. Clone or copy the kiosk folder.
3. cd kiosk
4. pip install -r requirements.txt
5. python kiosk.py

## Features
- Server: Web UI for management, API for kiosk interaction, database for users/items/sales/kiosks.
- Kiosk: Touch-screen GUI app with modes, RFID reader support (wired/wireless), cart, error handling.
- Modes: kiosk_staff (default), teacher, admin.
- RFID: Associate cards to users for auto-unlock, supports hardware readers with fallback to simulation.
- Error handling: Kiosk enters error mode on server disconnect, can retry.
- Kiosk management: Change passwords, set status remotely, monitor kiosks.
- Auto-discovery: Kiosks find server via UDP broadcast.
- Multiple kiosks supported.

## Database
- All data stored on server: users (with RFID), items, sales, kiosks.
- Kiosks authenticate against server database.
- No duplicate RFID associations allowed.

Default passwords:
- Server: 'admin'
- Kiosk kiosk_staff: 'kiosk'
- Kiosk teacher: 'teacher'
- Kiosk admin: 'admin'
