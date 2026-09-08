@echo off
title Agent OS - System Verify
cd /d C:\agent-os
echo ============================================
echo  TEST 1: Node.js
echo ============================================
node -v
echo.
echo ============================================
echo  TEST 2: Python
echo ============================================
python --version
echo.
echo ============================================
echo  TEST 3: Finance Engine (aapka wallet)
echo ============================================
python 05-code\finance-agent\finance_engine.py --today
echo.
echo ============================================
echo  Agar upar ₹ numbers wali digest aayi =
echo  SYSTEM READY. Ab N8N-START.bat chalao.
echo ============================================
pause
