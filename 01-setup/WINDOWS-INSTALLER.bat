@echo off
title Agent OS - Windows Installer (Node.js + Python)
echo ============================================
echo  FLIPKART AGENT OS - WINDOWS INSTALLER
echo  Installs: Node.js LTS + Python 3.12
echo ============================================
echo.

REM ---------- Check winget ----------
where winget >nul 2>&1
if errorlevel 1 (
    echo [ERROR] winget not found on this Windows version.
    echo.
    echo MANUAL INSTALL KARO:
    echo   1. Node.js : nodejs.org  ^> Download LTS  ^> installer run
    echo   2. Python  : python.org  ^> Download Python  ^>
    echo      installer mein "Add python.exe to PATH" TICK KARNA
    echo.
    pause
    exit /b 1
)

echo [1/3] Checking what is already installed...
where node >nul 2>&1
if not errorlevel 1 (echo       Node.js  : found) else (echo       Node.js  : missing - will install)
where python >nul 2>&1
if not errorlevel 1 (echo       Python   : found) else (echo       Python   : missing - will install)

echo.
echo [2/3] Installing Node.js LTS ^(winget^)...
winget install --id OpenJS.NodeJS.LTS --accept-source-agreements --accept-package-agreements
echo.

echo [3/3] Installing Python 3.12 ^(winget^)...
winget install --id Python.Python.3.12 --accept-source-agreements --accept-package-agreements
echo.

echo ============================================
echo  INSTALL DONE
echo  Ab yeh CMD window BAND karo.
echo  NAYA cmd kholo  ^(Win+R  -^>  cmd  -^>  Enter^)
echo  aur yeh 2 commands chalao:
echo       node -v
echo       python --version
echo  Dono ka version aaya toh:
echo  1. C:\agent-os\01-setup\VERIFY.bat double-click karo
echo  2. Phir C:\agent-os\01-setup\N8N-START.bat double-click karo
echo ============================================
pause
