#!/usr/bin/env python3
"""
Interactive Installer for POS System
Pulls from GitHub and sets up the system.
"""

import os
import subprocess
import sys

def run_command(cmd, cwd=None):
    """Run a shell command and return success."""
    try:
        subprocess.run(cmd, shell=True, check=True, cwd=cwd)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {e}")
        return False

def main():
    print("POS System Interactive Installer")
    print("================================")

    # Install Python if needed
    print("Checking for Python3 and pip...")
    if not run_command("python3 --version"):
        print("Installing Python3...")
        if not run_command("sudo apt update && sudo apt install -y python3 python3-pip"):
            sys.exit(1)
    else:
        print("Python3 found.")

    # Ask for repo URL
    repo_url = input("Enter the GitHub repository URL (default: https://github.com/Rgibs04/POS-system.git): ").strip()
    if not repo_url:
        repo_url = "https://github.com/Rgibs04/POS-system.git"

    # Ask what to install
    print("\nWhat to install:")
    print("1. Server only")
    print("2. Kiosk only")
    print("3. Both (forces Docker)")
    install_choice = input("Choose (1, 2, or 3): ").strip()

    if install_choice not in ['1', '2', '3']:
        print("Invalid choice.")
        sys.exit(1)

    if install_choice == '3':
        # Both: force Docker
        install_type = 'docker'
    else:
        # Ask for installation type
        print("\nInstallation Options:")
        print("1. Docker (recommended for cross-platform)")
        print("2. Native (Ubuntu only)")
        choice = input("Choose installation type (1 or 2): ").strip()
        if choice == '1':
            install_type = 'docker'
        elif choice == '2':
            install_type = 'native'
        else:
            print("Invalid choice.")
            sys.exit(1)

    # Clone repo
    print("\nCloning repository...")
    if not run_command(f"git clone {repo_url} pos_system"):
        sys.exit(1)

    os.chdir("pos_system")

    if install_type == 'docker':
        # Docker install
        print("Installing Docker and Docker Compose...")
        if not run_command("sudo apt update && sudo apt install -y docker.io docker-compose"):
            sys.exit(1)
        if install_choice == '1':
            # Server only
            print("Building and starting server with Docker...")
            if not run_command("docker build -t pos-server server/ && docker run -d -p 5000:5000 --name pos-server pos-server"):
                sys.exit(1)
            print("\nServer installation complete!")
            print("Access server web UI at http://localhost:5000 (admin/admin)")
        elif install_choice == '2':
            # Kiosk only
            print("Building and starting kiosk with Docker...")
            if not run_command("docker build -t pos-kiosk kiosk/ && docker run -d --name pos-kiosk pos-kiosk"):
                sys.exit(1)
            print("\nKiosk installation complete!")
        else:
            # Both
            print("Building and starting with Docker...")
            if not run_command("docker-compose up --build -d"):
                sys.exit(1)
            print("\nInstallation complete!")
            print("Access server web UI at http://localhost (admin/admin)")
            print("Kiosk is running in container.")

    elif install_type == 'native':
        # Native install
        print("Installing Python and dependencies...")
        if not run_command("sudo apt update && sudo apt install -y python3 python3-pip"):
            sys.exit(1)

        if install_choice == '1' or install_choice == '3':
            # Server setup
            print("Setting up server...")
            os.chdir("server")
            if not run_command("pip3 install -r requirements.txt"):
                sys.exit(1)
            # Create systemd service for auto-start
            service_content = """[Unit]
Description=POS Server
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/pos_system/server
ExecStart=/usr/bin/python3 /root/pos_system/server/app.py
Restart=always

[Install]
WantedBy=multi-user.target
"""
            with open('/etc/systemd/system/pos-server.service', 'w') as f:
                f.write(service_content)
            run_command("systemctl enable pos-server")
            run_command("systemctl start pos-server")
            os.chdir("..")

        if install_choice == '2' or install_choice == '3':
            # Kiosk setup
            print("Setting up kiosk...")
            os.chdir("kiosk")
            if not run_command("pip3 install -r requirements.txt"):
                sys.exit(1)
            # Create systemd service for auto-start
            service_content = """[Unit]
Description=POS Kiosk
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/pos_system/kiosk
ExecStart=/usr/bin/python3 /root/pos_system/kiosk/kiosk.py
Restart=always

[Install]
WantedBy=multi-user.target
"""
            with open('/etc/systemd/system/pos-kiosk.service', 'w') as f:
                f.write(service_content)
            run_command("systemctl enable pos-kiosk")
            run_command("systemctl start pos-kiosk")
            # Create desktop shortcut
            desktop_content = """[Desktop Entry]
Name=POS Kiosk
Exec=/usr/bin/python3 /root/pos_system/kiosk/kiosk.py
Type=Application
Terminal=false
"""
            with open('/usr/share/applications/pos-kiosk.desktop', 'w') as f:
                f.write(desktop_content)
            os.chdir("..")

        print("\nInstallation complete!")
        if install_choice == '1' or install_choice == '3':
            print("Server is running and will start on boot.")
            print("Access server web UI at http://localhost:5000 (admin/admin)")
        if install_choice == '2' or install_choice == '3':
            print("Kiosk is running and will start on boot.")
            print("Shortcut created in applications menu.")

if __name__ == "__main__":
    main()
