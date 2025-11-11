# 🚀 Installation Guide

## Prerequisites

- Python 3.11+ installed
- Node.js 16+ and npm installed
- Git (optional)

## Quick Setup (Windows)

### Option 1: Automated Setup

1. Run the setup script:
```cmd
setup.bat
```

2. Start both servers:
```cmd
start.bat
```

### Option 2: Manual Setup

#### Backend Setup

1. Navigate to backend folder:
```cmd
cd backend
```

2. Install Python dependencies:
```cmd
pip install -r requirements.txt
```

3. Start the backend server:
```cmd
python main.py
```

Backend will run on `http://localhost:8000`

#### Frontend Setup

1. Open a new terminal and navigate to frontend folder:
```cmd
cd frontend
```

2. Install Node dependencies:
```cmd
npm install
```

3. Start the frontend development server:
```cmd
npm start
```

Frontend will run on `http://localhost:3000`

## First Time Usage

1. Open your browser to `http://localhost:3000`
2. Click "Register" to create a new account
3. Enter username, email, and password
4. Login and start your SQL adventure!

## Troubleshooting

### Backend Issues

**Port 8000 already in use:**
```cmd
# Find and kill the process
netstat -ano | findstr :8000
taskkill /PID <process_id> /F
```

**Missing dependencies:**
```cmd
cd backend
pip install --upgrade -r requirements.txt
```

### Frontend Issues

**Port 3000 already in use:**
- The app will prompt to use a different port (usually 3001)
- Or kill the process using port 3000

**npm install fails:**
```cmd
# Clear npm cache
npm cache clean --force
# Delete node_modules and package-lock.json
rmdir /s /q node_modules
del package-lock.json
# Reinstall
npm install
```

**Module not found errors:**
```cmd
cd frontend
npm install react-router-dom axios framer-motion react-hot-toast lucide-react recharts react-calendar-heatmap
```

## Database

The SQLite database (`game.db`) is automatically created in the `backend` folder on first run.

To reset the database:
```cmd
cd backend
del game.db
python main.py
```

## Environment Configuration

### Backend (Optional)

Create `backend/.env` file:
```
GEMINI_API_KEY=your_api_key_here
SECRET_KEY=your_custom_secret_key
```

Note: The app includes a default Gemini API key for testing.

## Verifying Installation

1. Backend health check:
   - Open `http://localhost:8000/docs` in browser
   - You should see FastAPI Swagger documentation

2. Frontend check:
   - Open `http://localhost:3000`
   - You should see the login page

## Next Steps

1. Register a new account
2. Explore the dashboard
3. Check out the dungeon map
4. Play mini-games to earn points
5. Start solving SQL challenges!

## Support

If you encounter issues:
1. Check that both servers are running
2. Verify Python and Node.js versions
3. Check console logs for errors
4. Ensure ports 3000 and 8000 are available

Happy SQL adventuring! 🗝️
