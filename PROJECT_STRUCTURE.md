# 📁 Project Structure

```
sql-escape-dungeon/
│
├── 📂 backend/                    # FastAPI Backend
│   ├── main.py                    # Main API server
│   ├── requirements.txt           # Python dependencies
│   └── game.db                    # SQLite database (auto-generated)
│
├── 📂 frontend/                   # React Frontend
│   ├── 📂 public/
│   │   └── index.html            # HTML template
│   │
│   ├── 📂 src/
│   │   ├── 📂 components/
│   │   │   ├── Login.js          # Login/Register page
│   │   │   ├── Login.css
│   │   │   ├── Dashboard.js      # Main dashboard
│   │   │   ├── Dashboard.css
│   │   │   ├── DungeonMap.js     # Interactive map
│   │   │   ├── DungeonMap.css
│   │   │   ├── GamePlay.js       # Level gameplay
│   │   │   ├── GamePlay.css
│   │   │   ├── MiniGames.js      # Mini-games hub
│   │   │   ├── MiniGames.css
│   │   │   ├── Profile.js        # User profile
│   │   │   └── Profile.css
│   │   │
│   │   ├── App.js                # Main app component
│   │   ├── App.css               # Global styles
│   │   ├── index.js              # React entry point
│   │   └── index.css             # Base styles
│   │
│   └── package.json              # Node dependencies
│
├── 📂 venv/                       # Python virtual environment
│
├── app.py                         # Original Streamlit app (legacy)
├── requirements.txt               # Original requirements (legacy)
│
├── setup.bat                      # Automated setup script
├── start.bat                      # Start both servers
│
├── README.md                      # Project documentation
├── INSTALL.md                     # Installation guide
├── PROJECT_STRUCTURE.md           # This file
└── .gitignore                     # Git ignore rules
```

## 🎯 Key Components

### Backend (`backend/main.py`)
- **Authentication**: JWT-based user auth
- **Database**: SQLite with user progress tracking
- **AI Integration**: Gemini 2.0 Flash for hints
- **API Endpoints**: RESTful API for all game features

### Frontend Components

#### 🔐 Login (`Login.js`)
- User registration and login
- Animated glassmorphism design
- Form validation

#### 📊 Dashboard (`Dashboard.js`)
- User stats overview
- GitHub-style activity heatmap
- Quick navigation cards
- Progress tracking

#### 🗺️ Dungeon Map (`DungeonMap.js`)
- Interactive SVG map
- 8 levels with visual paths
- Level status indicators (completed/current/locked)
- Animated transitions

#### 🎮 Mini Games (`MiniGames.js`)
- **SQL Match**: Memory card game
- **Query Race**: Speed typing challenge
- **Index Puzzle**: Optimization quiz
- Point rewards system

#### 👤 Profile (`Profile.js`)
- User information
- Achievement badges
- Progress statistics

#### 🎯 GamePlay (`GamePlay.js`)
- Level-specific challenges
- SQL query editor
- Real-time validation
- AI-powered feedback

## 🔄 Data Flow

```
User Action → React Component → Axios Request → FastAPI Endpoint
                                                      ↓
                                                 SQLite DB
                                                      ↓
                                              Gemini AI (hints)
                                                      ↓
                                              JSON Response
                                                      ↓
                                              React State Update
                                                      ↓
                                              UI Re-render
```

## 🎨 Styling Architecture

- **Global Styles**: `App.css`, `index.css`
- **Component Styles**: Individual CSS files per component
- **Design System**:
  - Glassmorphism effects
  - Gradient backgrounds
  - Smooth animations (Framer Motion)
  - Responsive grid layouts

## 📦 Dependencies

### Backend
- FastAPI - Web framework
- Uvicorn - ASGI server
- SQLite3 - Database
- Google Generative AI - AI hints
- PyJWT - Authentication
- Bcrypt - Password hashing

### Frontend
- React - UI framework
- React Router - Navigation
- Axios - HTTP client
- Framer Motion - Animations
- React Hot Toast - Notifications
- Lucide React - Icons
- React Calendar Heatmap - Progress visualization

## 🚀 Deployment Ready

The project is structured for easy deployment:
- Backend: Deploy to Heroku, Railway, or AWS
- Frontend: Deploy to Vercel, Netlify, or AWS S3
- Database: Upgrade to PostgreSQL for production

## 🔧 Configuration

### Backend Config
- `SECRET_KEY`: JWT secret (in code or .env)
- `GEMINI_API_KEY`: AI API key (in code or .env)
- `DB_PATH`: Database location

### Frontend Config
- API URL: `http://localhost:8000` (development)
- Update in production to your backend URL

## 📈 Scalability

The architecture supports:
- Multiple concurrent users
- Real-time progress tracking
- Extensible level system
- Additional mini-games
- Leaderboard features (future)
- Multiplayer modes (future)
