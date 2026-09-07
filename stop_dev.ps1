# NexusDoc AI - Stop All Services (PowerShell)
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "Đang dừng toàn bộ dịch vụ NexusDoc AI..." -ForegroundColor Yellow

# Dung port 8000
$p8000 = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -Unique
if ($p8000) {
    Stop-Process -Id $p8000 -Force -ErrorAction SilentlyContinue
    Write-Host "  -> Đã tắt Backend (Port 8000)" -ForegroundColor Green
}

# Dung port 3000
$p3000 = Get-NetTCPConnection -LocalPort 3000 -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -Unique
if ($p3000) {
    Stop-Process -Id $p3000 -Force -ErrorAction SilentlyContinue
    Write-Host "  -> Đã tắt Frontend (Port 3000)" -ForegroundColor Green
}

# Dung Celery
Get-Process "celery" -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue

Write-Host "Hoàn tất dừng hệ thống!" -ForegroundColor Green
