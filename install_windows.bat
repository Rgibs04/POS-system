@echo off
REM POS System Windows Installer
REM Automatically installs everything needed

echo POS System Windows Installer
echo =============================

REM Check for Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python not found. Installing Python...
    REM Try winget
    winget --version >nul 2>&1
    if %errorlevel% equ 0 (
        winget install --id Python.Python.3 --accept-source-agreements --accept-package-agreements
        if %errorlevel% neq 0 (
            echo Failed to install Python via winget. Please install Python manually from https://www.python.org/downloads/
            pause
            exit /b 1
        )
    ) else (
        echo winget not found. Please install Python manually from https://www.python.org/downloads/
        pause
        exit /b 1
    )
    echo Python installed. Please restart your computer and rerun this installer.
    pause
    exit /b 0
) else (
    echo Python found.
)

REM Check for Docker
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Docker not found. Installing Docker Desktop...
    REM Try winget
    winget --version >nul 2>&1
    if %errorlevel% equ 0 (
        winget install --id Docker.DockerDesktop --accept-source-agreements --accept-package-agreements
        if %errorlevel% neq 0 (
            echo Failed to install Docker via winget. Please install Docker Desktop manually from https://www.docker.com/products/docker-desktop
            pause
            exit /b 1
        )
    ) else (
        echo winget not found. Please install Docker Desktop manually from https://www.docker.com/products/docker-desktop
        pause
        exit /b 1
    )
    echo Docker installed. Please restart your computer if prompted, then rerun this installer.
    pause
    exit /b 0
) else (
    echo Docker found.
)

REM Check for git
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Git not found. Installing Git...
    winget --version >nul 2>&1
    if %errorlevel% equ 0 (
        winget install --id Git.Git --accept-source-agreements --accept-package-agreements
    ) else (
        echo Please install Git manually from https://git-scm.com/download/win
        pause
        exit /b 1
    )
) else (
    echo Git found.
)

REM Ask what to install
echo.
echo What to install:
echo 1. Server only
echo 2. Kiosk only
echo 3. Both
set /p install_choice="Choose (1, 2, or 3): "

if "%install_choice%"=="1" goto server_only
if "%install_choice%"=="2" goto kiosk_only
if "%install_choice%"=="3" goto both
echo Invalid choice.
pause
exit /b 1

:server_only
echo Building and starting server with Docker...
docker build -t pos-server server/ && docker run -d -p 5000:5000 --name pos-server pos-server
if %errorlevel% neq 0 (
    echo Installation failed.
    pause
    exit /b 1
)
echo.
echo Server installation complete!
echo Access server web UI at http://localhost:5000 (admin/admin)
goto end

:kiosk_only
echo Building and starting kiosk with Docker...
docker build -t pos-kiosk kiosk/ && docker run -d --name pos-kiosk pos-kiosk
if %errorlevel% neq 0 (
    echo Installation failed.
    pause
    exit /b 1
)
echo.
echo Kiosk installation complete!
goto end

:both
echo Building and starting with Docker...
docker-compose up --build -d
if %errorlevel% neq 0 (
    echo Installation failed.
    pause
    exit /b 1
)
echo.
echo Installation complete!
echo Access server web UI at http://localhost (admin/admin)
echo Kiosk is running in container.
goto end

:end
echo.
echo Installation complete!
pause
