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
    repo_url = input("Enter the GitHub repository URL (e.g., https://github.com/username/pos-system): ").strip()
    if not repo_url:
        print("Repository URL is required.")
        sys.exit(1)

    # Ask for installation type
    print("\nInstallation Options:")
    print("1. Docker (recommended for cross-platform)")
    print("2. Native (Ubuntu only)")
    choice = input("Choose installation type (1 or 2): ").strip()

    if choice not in ['1', '2']:
        print("Invalid choice.")
        sys.exit(1)

    # Clone repo
    print("\nCloning repository...")
    if not run_command(f"git clone {repo_url} pos_system"):
        sys.exit(1)

    os.chdir("pos_system")

    if choice == '1':
        # Docker install
        print("Installing Docker and Docker Compose...")
        if not run_command("sudo apt update && sudo apt install -y docker.io docker-compose"):
            sys.exit(1)
        print("Building and starting with Docker...")
        if not run_command("docker-compose up --build -d"):
            sys.exit(1)
        print("\nInstallation complete!")
        print("Access server web UI at http://localhost (admin/admin)")
        print("Kiosk is running in container.")

    elif choice == '2':
        # Native install
        print("Installing Python and dependencies...")
        if not run_command("sudo apt update && sudo apt install -y python3 python3-pip"):
            sys.exit(1)

        # Server setup
        print("Setting up server...")
        os.chdir("server")
        if not run_command("pip3 install -r requirements.txt"):
            sys.exit(1)
        os.chdir("..")

        # Kiosk setup
        print("Setting up kiosk...")
        os.chdir("kiosk")
        if not run_command("pip3 install -r requirements.txt"):
            sys.exit(1)
        os.chdir("..")

        print("\nInstallation complete!")
        print("To start server: cd server && python3 app.py & python3 discovery_server.py &")
        print("To start kiosk: cd kiosk && python3 kiosk.py")
        print("Access server web UI at http://localhost:5000 (admin/admin)")

if __name__ == "__main__":
    main()
