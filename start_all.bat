@echo off
chcp 65001 >nul
title NexusDoc AI - Khoi dong he thong
color 0B

echo ===============================================================================
echo                NEXUSDOC AI - KHOI DONG TOAN BO HE THONG
echo ===============================================================================
echo.

set ROOT_DIR=%~dp0
cd /d "%ROOT_DIR%"

:: 1. Kiem tra va khoi chay Ollama
echo [1/5] Kiem tra Engine AI Local (Ollama)...
curl -s http://localhost:11434/api/tags >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] Ollama chua bat. Dang khoi chay Ollama...
    start "" ollama serve
    timeout /t 3 /nobreak >nul
) else (
    echo [OK] Ollama dang hoat dong san sang.
)

:: 2. Kiem tra Docker ha tang (Qdrant, Redis, Postgres)
echo [2/5] Kiem tra he thong Ha tang Docker (Qdrant, Redis, Postgres)...
docker info >nul 2>&1
if %errorlevel% equ 0 (
    docker ps | findstr /i "qdrant" >nul 2>&1
    if %errorlevel% neq 0 (
        echo [!] Dang khoi dong cac Container Ha tang (Qdrant, Redis, Postgres)...
        docker compose up -d qdrant redis postgres minio >nul 2>&1
    ) else (
        echo [OK] Cac container Docker (Qdrant, Redis, Postgres) dang chay.
    )
) else (
    echo [WARN] Docker Desktop chua bat hoac khong chay. Neu da chay Qdrant rieng le, he thong se tiep tuc.
)

:: 3. Khoi chay Celery Background Worker
echo [3/5] Khoi chay Celery Background Worker (Boc tach & Vector hoa)...
start "NexusDoc - Celery Worker" cmd /k "cd /d %ROOT_DIR%src\backend && ..\..\venv\Scripts\celery.exe -A core.celery_app.celery_app worker --loglevel=info --pool=solo"

:: 4. Khoi chay Backend FastAPI (Port 8000)
echo [4/5] Khoi chay Backend FastAPI (Port 8000)...
start "NexusDoc - Backend API" cmd /k "cd /d %ROOT_DIR%src\backend && ..\..\venv\Scripts\python.exe -m uvicorn main:app --reload --host 127.0.0.1 --port 8000"

:: 5. Khoi chay Frontend Next.js (Port 3000)
echo [5/5] Khoi chay Frontend Next.js (Port 3000)...
start "NexusDoc - Frontend Dashboard" cmd /k "cd /d %ROOT_DIR%src\frontend && npm run dev"

echo.
echo ===============================================================================
echo    TAT CA DICH VU DA DUOC KHOI CHAY THANH CONG!
echo ===============================================================================
echo.
echo - Web Dashboard:  http://localhost:3000
echo - API Docs:       http://localhost:8000/docs
echo - Qdrant Vector:  http://localhost:6333/dashboard
echo.
echo Dang mo trinh duyet den http://localhost:3000 trong 4 giay...
timeout /t 4 /nobreak >nul
start http://localhost:3000

echo Ban co the thu nho cua so nay. Chuc ban lam viec hieu qua!
pause
