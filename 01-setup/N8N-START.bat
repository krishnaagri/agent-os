@echo off
title Agent OS - n8n Server [DO NOT CLOSE]
cd /d C:\agent-os
echo ============================================
echo  n8n STARTING...
echo  Open in browser: http://localhost:5678
echo.
echo  WARNING: Is window ko BAND mat karna.
echo  Window band = system band (laptop phase).
echo  Minimize kar sakte ho, band nahi.
echo ============================================
call npx -y n8n
