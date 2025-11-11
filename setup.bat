@echo off
echo ========================================
echo SQL Escape: The Optimization Dungeon
echo Setup Script
echo ========================================
echo.

echo [1/4] Setting up Backend...
cd backend
pip install -r requirements.txt
cd ..
echo Backend setup complete!
echo.

echo [2/4] Setting up Frontend...
cd frontend
call npm install
cd ..
echo Frontend setup complete!
echo.

echo [3/4] Creating database...
python -c "import sqlite3; conn = sqlite3.connect('backend/game.db'); conn.close()"
echo Database created!
echo.

echo [4/4] Setup complete!
echo.
echo ========================================
echo To start the application:
echo.
echo 1. Backend:  cd backend ^&^& python main.py
echo 2. Frontend: cd frontend ^&^& npm start
echo.
echo Backend will run on: http://localhost:8000
echo Frontend will run on: http://localhost:3000
echo ========================================
pause
