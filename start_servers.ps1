Write-Host "====================================================================" -ForegroundColor Cyan
Write-Host "Starting Student Performance DWDM PBL (FastAPI + Next.js App)" -ForegroundColor Cyan
Write-Host "====================================================================" -ForegroundColor Cyan

Write-Host "`n[1/2] Starting Python FastAPI Backend on http://127.0.0.1:8000 ..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "python server.py"

Write-Host "[2/2] Starting Next.js Frontend on http://localhost:3000 ..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location frontend; npm run dev"

Write-Host "`n====================================================================" -ForegroundColor Green
Write-Host "Backend and Frontend launched!" -ForegroundColor Green
Write-Host "• Swagger API Documentation: http://127.0.0.1:8000/docs" -ForegroundColor White
Write-Host "• Modern Next.js Dashboard:  http://localhost:3000" -ForegroundColor White
Write-Host "====================================================================" -ForegroundColor Green
