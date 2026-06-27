@echo off
echo ============================================
echo   SentinelAI Development Server Launcher
echo ============================================
echo.

echo Starting Backend (FastAPI) on port 8000...
start "SentinelAI Backend" cmd /k "cd backend && python -m uvicorn app.main:app --reload --port 8000"

echo Waiting 5 seconds for backend to initialize...
timeout /t 5 /nobreak > nul

echo Starting Frontend (Next.js) on port 3000...
start "SentinelAI Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo ============================================
echo   Both servers starting...
echo   Backend:  http://localhost:8000/docs
echo   Frontend: http://localhost:3000
echo   Login:    admin / Admin@123
echo ============================================
echo.
pause
