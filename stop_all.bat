@echo off
chcp 65001 >nul
title NexusDoc AI - Dung toan bo he thong
color 0C

echo ===============================================================================
echo                DANG DUNG TOAN BO HE THONG NEXUSDOC AI...
echo ===============================================================================
echo.

:: 1. Tat Port 8000 (Backend FastAPI)
echo [*] Dang tat Backend FastAPI (Port 8000)...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8000" ^| findstr "LISTENING"') do (
    taskkill /F /PID %%a >nul 2>&1
)

:: 2. Tat Port 3000 (Frontend Next.js)
echo [*] Dang tat Frontend Next.js (Port 3000)...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":3000" ^| findstr "LISTENING"') do (
    taskkill /F /PID %%a >nul 2>&1
)

:: 3. Tat cac process Celery Worker
echo [*] Dang tat Celery Worker...
taskkill /F /IM celery.exe >nul 2>&1

echo.
echo ===============================================================================
echo [OK] DA DUNG THANH CONG TOAN BO DICH VU BACKEND VA FRONTEND!
echo ===============================================================================
echo.
pause
