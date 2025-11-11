# 🗝️ SQL Escape: The Optimization Dungeon

An immersive gamified SQL learning platform with React frontend and FastAPI backend.

## ✨ Features

- 🎮 **8 Progressive Levels** - From basic SELECT to complex multi-table queries
- 🗺️ **Interactive Dungeon Map** - Visual progress tracking
- 🤖 **AI-Powered Hints** - Gemini 2.0 Flash integration
- 🎯 **Mini Games** - Earn bonus points through SQL challenges
- 📊 **GitHub-Style Heatmap** - Track your daily progress
- 🏆 **Achievement System** - Unlock badges as you progress
- 👤 **User Authentication** - Secure login and progress saving

## 🚀 Quick Start

### Backend Setup

```bash
cd backend
pip install -r requirements.txt
python main.py
```

Backend runs on `http://localhost:8000`

### Frontend Setup

```bash
cd frontend
npm install
npm start
```

Frontend runs on `http://localhost:3000`

## 🎯 Game Modes

### Main Quest
- Progress through 8 dungeon levels
- Each level teaches SQL optimization concepts
- Earn points and unlock achievements

### Mini Games
1. **SQL Match** - Match keywords with functions
2. **Query Race** - Type queries as fast as possible
3. **Index Puzzle** - Solve optimization challenges

## 📊 Progress Tracking

- **Daily Activity Heatmap** - GitHub-style visualization
- **Score System** - Earn points for correct queries
- **Energy System** - Manage your attempts wisely
- **Achievements** - Unlock badges for milestones

## 🛠️ Tech Stack

### Frontend
- React 18
- Framer Motion (animations)
- React Router (navigation)
- Axios (API calls)
- React Calendar Heatmap
- Lucide React (icons)

### Backend
- FastAPI
- SQLite (database)
- Google Gemini AI
- JWT Authentication
- Bcrypt (password hashing)

## 🎨 UI/UX Features

- Glassmorphism design
- Smooth animations
- Responsive layout
- Dark theme optimized
- Interactive map visualization
- Real-time feedback

## 📝 API Endpoints

- `POST /api/register` - User registration
- `POST /api/login` - User login
- `GET /api/progress/{username}` - Get user progress
- `GET /api/activity/{username}` - Get activity heatmap data
- `POST /api/submit-query` - Submit SQL query
- `POST /api/mini-game` - Submit mini-game score
- `GET /api/ai-hint` - Get AI-powered hint

## 🎓 Learning Path

1. **Gate of SELECT** - Basic filtering and sorting
2. **Joins of Doom** - Multi-table queries
3. **Subquery Swamp** - IN vs EXISTS optimization
4. **Aggregation Tower** - GROUP BY and HAVING
5. **Window Cave** - Window functions and ranking
6. **Index Labyrinth** - Index optimization
7. **Recursive Depths** - Self-joins and hierarchies
8. **Query Dragon** - Final boss challenge

## 🔐 Environment Variables

Create `.env` file in backend:
```
GEMINI_API_KEY=your_api_key_here
SECRET_KEY=your_secret_key_here
```

## 📱 Screenshots

(Add screenshots of your app here)

## 🤝 Contributing

Contributions welcome! Please open an issue or submit a PR.

## 📄 License

MIT License

## 🎮 Start Your Adventure!

Register, login, and begin your journey through the SQL Optimization Dungeon!
