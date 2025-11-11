@echo off
echo Starting SQL Escape: The Optimization Dungeon...
echo.

start "Backend Server" cmd /k "cd backend && python main.py"
timeout /t 3 /nobreak > nul

start "Frontend Server" cmd /k "cd frontend && npm start"

echo.
echo Servers starting...
echo Backend: http://localhost:8000
echo Frontend: http://localhost:3000
echo.
echo Press any key to stop all servers...
pause > nul

taskkill /FI "WindowTitle eq Backend Server*" /T /F
taskkill /FI "WindowTitle eq Frontend Server*" /T /F
