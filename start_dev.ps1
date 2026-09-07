# NexusDoc AI - Development Runner (PowerShell)
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "=================================================================" -ForegroundColor Cyan
Write-Host "           NEXUSDOC AI - DEVELOPMENT SYSTEM RUNNER              " -ForegroundColor Cyan
Write-Host "=================================================================" -ForegroundColor Cyan
Write-Host ""

$rootDir = $PSScriptRoot

# 1. Kiem tra Ollama
Write-Host "[1/4] Kiểm tra Ollama Local LLM..." -ForegroundColor Yellow
try {
    $ollamaCheck = Invoke-RestMethod -Uri "http://localhost:11434/api/tags" -Method Get -TimeoutSec 2 -ErrorAction Stop
    Write-Host "  -> [OK] Ollama đang hoạt động (Model: qwen2.5:7b)" -ForegroundColor Green
} catch {
    Write-Host "  -> [!] Đang kích hoạt Ollama serve..." -ForegroundColor DarkYellow
    Start-Process "ollama" -ArgumentList "serve" -WindowStyle Hidden
    Start-Sleep -Seconds 2
}

# 2. Kiem tra Docker Infrastructure
Write-Host "[2/4] Kiểm tra cơ sở dữ liệu Vector & Cache..." -ForegroundColor Yellow
try {
    $qdrantCheck = Invoke-RestMethod -Uri "http://localhost:6333/dashboard" -Method Get -TimeoutSec 2 -ErrorAction Stop
    Write-Host "  -> [OK] Qdrant Vector Store sẵn sàng trên cổng 6333" -ForegroundColor Green
} catch {
    Write-Host "  -> [!] Qdrant chưa sẵn sàng, đang thử khởi động Docker containers..." -ForegroundColor DarkYellow
    docker compose up -d qdrant redis postgres minio | Out-Null
}

# 3. Khoi chay Celery Worker
Write-Host "[3/4] Khởi động Celery Worker..." -ForegroundColor Yellow
$celeryCmd = "cd '$rootDir\src\backend'; & '..\..\venv\Scripts\celery.exe' -A core.celery_app.celery_app worker --loglevel=info --pool=solo"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $celeryCmd

# 4. Khoi chay Backend FastAPI
Write-Host "[4/4] Khởi động FastAPI Backend (Port 8000)..." -ForegroundColor Yellow
$backendCmd = "cd '$rootDir\src\backend'; & '..\..\venv\Scripts\python.exe' -m uvicorn main:app --reload --host 127.0.0.1 --port 8000"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendCmd

# 5. Khoi chay Frontend Next.js
Write-Host "[5/5] Khởi động Next.js Frontend (Port 3000)..." -ForegroundColor Yellow
$frontendCmd = "cd '$rootDir\src\frontend'; npm run dev"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $frontendCmd

Write-Host ""
Write-Host "=================================================================" -ForegroundColor Green
Write-Host "         TẤT CẢ DỊCH VỤ ĐÃ KHỞI CHẠY THÀNH CÔNG!                " -ForegroundColor Green
Write-Host "=================================================================" -ForegroundColor Green
Write-Host " -> Dashboard:      http://localhost:3000" -ForegroundColor Cyan
Write-Host " -> Backend Docs:   http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host " -> Qdrant Vector:  http://localhost:6333/dashboard" -ForegroundColor Cyan
Write-Host ""

Start-Sleep -Seconds 3
Start-Process "http://localhost:3000"
