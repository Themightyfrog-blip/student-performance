@echo off
title Launch Student Performance DWDM PBL
echo ====================================================================
echo Starting Student Performance DWDM PBL (FastAPI + Next.js App)
echo ====================================================================
echo.
echo [1/2] Starting Python FastAPI Backend on http://127.0.0.1:8000 ...
start "DWDM PBL API (Port 8000)" cmd /k "python server.py"

echo [2/2] Starting Next.js Frontend on http://localhost:3000 ...
start "DWDM PBL Next.js (Port 3000)" cmd /k "cd frontend && npm run dev"

echo.
echo ====================================================================
echo Backend and Frontend servers launched in dedicated windows!
echo - API Docs (Swagger):  http://127.0.0.1:8000/docs
echo - Web Dashboard (UI):   http://localhost:3000
echo ====================================================================
