# ⚡ Quick Start Guide

Get SQL Escape running in 5 minutes!

## 🎯 Prerequisites Check

Before starting, verify you have:
- ✅ Python 3.11+ installed (`python --version`)
- ✅ Node.js 16+ installed (`node --version`)
- ✅ npm installed (`npm --version`)

## 🚀 Installation (Choose One)

### Option A: Automated Setup (Recommended)

```cmd
setup.bat
```

This will:
1. Install backend Python dependencies
2. Install frontend Node dependencies
3. Create the database
4. Verify installation

### Option B: Manual Setup

#### Backend
```cmd
cd backend
pip install -r requirements.txt
```

#### Frontend
```cmd
cd frontend
npm install
```

## ▶️ Running the App

### Option A: Automated Start (Recommended)

```cmd
start.bat
```

This opens two terminals:
- Backend server on `http://localhost:8000`
- Frontend server on `http://localhost:3000`

Press any key in the main terminal to stop both servers.

### Option B: Manual Start

**Terminal 1 - Backend:**
```cmd
cd backend
python main.py
```

**Terminal 2 - Frontend:**
```cmd
cd frontend
npm start
```

## 🎮 First Steps

1. **Open Browser**
   - Navigate to `http://localhost:3000`
   - You should see the login page

2. **Register Account**
   - Click "Don't have an account? Register"
   - Enter username, email, and password
   - Click "Begin Your Quest"

3. **Explore Dashboard**
   - View your stats (Level 1, Score 0, Energy 100)
   - See the empty activity heatmap
   - Check out the action cards

4. **Open Dungeon Map**
   - Click "Dungeon Map" card
   - See all 8 levels
   - Level 1 should be unlocked (glowing)

5. **Play Mini-Games**
   - Click "Mini Games" card
   - Try SQL Match, Query Race, or Index Puzzle
   - Earn bonus points!

6. **Start First Level**
   - Go back to map
   - Click on Level 1 (Gate of SELECT)
   - Solve your first SQL challenge!

## 🔍 Verify Installation

### Backend Health Check
Open `http://localhost:8000/docs` in browser
- You should see FastAPI Swagger documentation
- Try the `/api/register` endpoint

### Frontend Check
Open `http://localhost:3000`
- Login page should load
- No console errors
- Animations should be smooth

## 🐛 Troubleshooting

### Backend Won't Start

**Error: Port 8000 in use**
```cmd
netstat -ano | findstr :8000
taskkill /PID <process_id> /F
```

**Error: Module not found**
```cmd
cd backend
pip install --upgrade -r requirements.txt
```

### Frontend Won't Start

**Error: Port 3000 in use**
- Choose 'Y' when prompted to use port 3001
- Or kill the process using port 3000

**Error: npm install fails**
```cmd
cd frontend
npm cache clean --force
rmdir /s /q node_modules
del package-lock.json
npm install
```

**Error: Module not found**
```cmd
cd frontend
npm install react-router-dom axios framer-motion react-hot-toast lucide-react
```

### Database Issues

**Reset database:**
```cmd
cd backend
del game.db
python main.py
```

### Browser Issues

**Page won't load:**
1. Check both servers are running
2. Clear browser cache (Ctrl+Shift+Delete)
3. Try incognito mode
4. Check console for errors (F12)

**Animations not working:**
- Update browser to latest version
- Enable hardware acceleration
- Try different browser (Chrome recommended)

## 📊 Test the Features

### 1. Test Authentication
- Register new account ✅
- Logout ✅
- Login again ✅
- Token persists on refresh ✅

### 2. Test Dashboard
- Stats display correctly ✅
- Heatmap renders ✅
- Navigation works ✅

### 3. Test Dungeon Map
- Map displays 8 levels ✅
- Level 1 is unlocked ✅
- Hover shows tooltips ✅
- Click navigates to level ✅

### 4. Test Mini-Games
- SQL Match loads ✅
- Query Race works ✅
- Index Puzzle functions ✅
- Points are awarded ✅

### 5. Test Profile
- User info displays ✅
- Achievements show ✅
- Logout works ✅

## 🎯 Next Steps

1. **Complete Level 1**
   - Learn SELECT, WHERE, ORDER BY
   - Earn your first 50 points
   - Unlock Level 2

2. **Play Mini-Games**
   - Try all three games
   - Earn bonus points
   - Build your score

3. **Build a Streak**
   - Solve queries daily
   - Watch your heatmap fill up
   - Stay motivated!

4. **Progress Through Levels**
   - Master each SQL concept
   - Optimize your queries
   - Prepare for interviews

## 💡 Pro Tips

- **Use hints wisely** - They cost 20 points but save time
- **Play mini-games** - Easy way to boost your score
- **Check AI feedback** - Learn optimization techniques
- **Build streaks** - Daily practice is key
- **First-try bonus** - Get it right first time for +50 points

## 📚 Documentation

- `README.md` - Project overview
- `FEATURES.md` - Complete feature list
- `INSTALL.md` - Detailed installation
- `PROJECT_STRUCTURE.md` - Code organization
- `SUMMARY.md` - Complete project summary

## 🆘 Need Help?

1. Check the troubleshooting section above
2. Review the documentation files
3. Check console logs (F12 in browser)
4. Verify both servers are running
5. Try restarting the servers

## 🎉 You're Ready!

Everything set up? Great! Now:

1. Open `http://localhost:3000`
2. Register your account
3. Start your SQL adventure!

**Welcome to the dungeon, adventurer! 🗝️**
