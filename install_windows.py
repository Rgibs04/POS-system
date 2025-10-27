#!/usr/bin/env python3
"""
Interactive Installer for POS System (Windows)
Forces Docker usage. Pulls from GitHub and sets up the system.
"""

import os
import subprocess
import sys
import platform

def run_command(cmd, cwd=None):
    """Run a shell command and return success."""
    try:
        subprocess.run(cmd, shell=True, check=True, cwd=cwd)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {e}")
        return False

def main():
    if platform.system() != 'Windows':
        print("This installer is for Windows only. Use install.py for Linux.")
        sys.exit(1)

    print("POS System Interactive Installer (Windows - Docker Only)")
    print("=======================================================")

    # Check for Docker
    print("Checking for Docker...")
    if not run_command("docker --version"):
        print("Docker not found. Installing Docker Desktop...")
        # Try winget
        if run_command("winget --version"):
            if not run_command("winget install --id Docker.DockerDesktop --accept-source-agreements --accept-package-agreements"):
                print("Failed to install Docker via winget. Please install Docker Desktop manually from https://www.docker.com/products/docker-desktop")
                print("Then rerun this installer.")
                sys.exit(1)
        else:
            print("winget not found. Please install Docker Desktop manually from https://www.docker.com/products/docker-desktop")
            print("Then rerun this installer.")
            sys.exit(1)
        print("Docker installed. Please restart your computer if prompted, then rerun this installer.")
        sys.exit(0)

    # Check for git
    if not run_command("git --version"):
        print("Git not found. Installing Git...")
        if run_command("winget --version"):
            run_command("winget install --id Git.Git --accept-source-agreements --accept-package-agreements")
        else:
            print("Please install Git manually from https://git-scm.com/download/win")
            sys.exit(1)

    # Ask for repo URL
    repo_url = input("Enter the GitHub repository URL (default: https://github.com/Rgibs04/POS-system.git): ").strip()
    if not repo_url:
        repo_url = "https://github.com/Rgibs04/POS-system.git"

    # Clone repo
    print("\nCloning repository...")
    if not run_command(f"git clone {repo_url} pos_system"):
        sys.exit(1)

    os.chdir("pos_system")

    # Docker setup
    print("Building and starting with Docker...")
    if not run_command("docker-compose up --build -d"):
        sys.exit(1)

    print("\nInstallation complete!")
    print("Access server web UI at http://localhost (admin/admin)")
    print("Kiosk is running in container.")

if __name__ == "__main__":
    main()
