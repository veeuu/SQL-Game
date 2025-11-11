# 🔄 Application Flow Diagram

## User Journey Map

```
┌─────────────────────────────────────────────────────────────────┐
│                         START HERE                               │
│                    http://localhost:3000                         │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │   Login Page     │
                    │   🔐             │
                    └──────────────────┘
                         │         │
                    New User?   Existing?
                         │         │
                         ▼         ▼
                  ┌──────────┐  ┌──────────┐
                  │ Register │  │  Login   │
                  └──────────┘  └──────────┘
                         │         │
                         └────┬────┘
                              ▼
                    ┌──────────────────┐
                    │   Dashboard      │
                    │   📊 Main Hub    │
                    └──────────────────┘
                              │
            ┌─────────────────┼─────────────────┐
            │                 │                 │
            ▼                 ▼                 ▼
    ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
    │ Dungeon Map  │  │  Mini Games  │  │   Profile    │
    │    🗺️        │  │     🎮       │  │     👤       │
    └──────────────┘  └──────────────┘  └──────────────┘
            │                 │                 │
            ▼                 ▼                 │
    ┌──────────────┐  ┌──────────────┐         │
    │ Select Level │  │ Choose Game  │         │
    │   (1-8)      │  │  • Match     │         │
    └──────────────┘  │  • Race      │         │
            │         │  • Puzzle    │         │
            ▼         └──────────────┘         │
    ┌──────────────┐         │                 │
    │  Game Play   │         ▼                 │
    │  Write SQL   │  ┌──────────────┐         │
    │  Get Hints   │  │  Play Game   │         │
    │  Submit      │  │  Earn Points │         │
    └──────────────┘  └──────────────┘         │
            │                 │                 │
            └─────────────────┴─────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │  Points Earned   │
                    │  Progress Saved  │
                    │  Heatmap Updated │
                    └──────────────────┘
```

## Component Interaction Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                        FRONTEND (React)                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐ │
│  │  Login   │───▶│Dashboard │───▶│   Map    │───▶│GamePlay  │ │
│  └──────────┘    └──────────┘    └──────────┘    └──────────┘ │
│       │               │                │               │        │
│       │               │                │               │        │
│       ▼               ▼                ▼               ▼        │
│  ┌────────────────────────────────────────────────────────┐    │
│  │              Axios HTTP Client                         │    │
│  └────────────────────────────────────────────────────────┘    │
└───────────────────────────────┬──────────────────────────────────┘
                                │
                                │ HTTP Requests
                                │
┌───────────────────────────────▼──────────────────────────────────┐
│                        BACKEND (FastAPI)                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐     │
│  │     Auth     │    │   Progress   │    │  Mini-Games  │     │
│  │  /register   │    │  /progress   │    │  /mini-game  │     │
│  │   /login     │    │  /activity   │    │              │     │
│  └──────────────┘    └──────────────┘    └──────────────┘     │
│         │                    │                    │             │
│         └────────────────────┼────────────────────┘             │
│                              │                                  │
│                              ▼                                  │
│                    ┌──────────────────┐                         │
│                    │  SQLite Database │                         │
│                    │   • users        │                         │
│                    │   • progress     │                         │
│                    │   • activity     │                         │
│                    │   • mini_games   │                         │
│                    └──────────────────┘                         │
│                                                                  │
│                    ┌──────────────────┐                         │
│                    │  Gemini AI API   │                         │
│                    │  • Hints         │                         │
│                    │  • Analysis      │                         │
│                    └──────────────────┘                         │
└─────────────────────────────────────────────────────────────────┘
```

## Data Flow: Solving a Query

```
┌──────────────┐
│   User       │
│  Types SQL   │
└──────┬───────┘
       │
       ▼
┌──────────────────────┐
│  GamePlay Component  │
│  • Validate input    │
│  • Show loading      │
└──────┬───────────────┘
       │
       │ POST /api/submit-query
       │ { query: "SELECT...", level: 1 }
       ▼
┌──────────────────────┐
│   FastAPI Backend    │
│  • Verify token      │
│  • Execute query     │
│  • Check correctness │
└──────┬───────────────┘
       │
       ├─────────────────┐
       │                 │
       ▼                 ▼
┌──────────────┐  ┌──────────────┐
│   SQLite     │  │  Gemini AI   │
│  Execute     │  │  Analyze     │
│  Query       │  │  Performance │
└──────┬───────┘  └──────┬───────┘
       │                 │
       └────────┬────────┘
                │
                ▼
       ┌──────────────────┐
       │  Update Database │
       │  • Add points    │
       │  • Update energy │
       │  • Log activity  │
       └────────┬─────────┘
                │
                │ JSON Response
                │ { success: true, points: 50 }
                ▼
       ┌──────────────────┐
       │  React Component │
       │  • Update state  │
       │  • Show feedback │
       │  • Animate       │
       └──────────────────┘
                │
                ▼
       ┌──────────────────┐
       │   User Sees      │
       │  ✅ Correct!     │
       │  +50 points      │
       └──────────────────┘
```

## Authentication Flow

```
┌──────────────┐
│ User Enters  │
│ Credentials  │
└──────┬───────┘
       │
       ▼
┌──────────────────────┐
│  Login Component     │
│  • Validate form     │
│  • Submit            │
└──────┬───────────────┘
       │
       │ POST /api/login
       │ { username, password }
       ▼
┌──────────────────────┐
│   FastAPI Backend    │
│  • Find user         │
│  • Verify password   │
│  • Generate JWT      │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│   Database Query     │
│  SELECT * FROM users │
│  WHERE username=?    │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│  Bcrypt Verify       │
│  Compare hashed pwd  │
└──────┬───────────────┘
       │
       │ Success!
       ▼
┌──────────────────────┐
│  Create JWT Token    │
│  { user_id, exp }    │
└──────┬───────────────┘
       │
       │ Return token
       ▼
┌──────────────────────┐
│  React App           │
│  • Store in state    │
│  • Save to localStorage │
│  • Redirect to dashboard │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│  All Future Requests │
│  Include token in    │
│  Authorization header│
└──────────────────────┘
```

## Heatmap Update Flow

```
┌──────────────┐
│ User Solves  │
│    Query     │
└──────┬───────┘
       │
       ▼
┌──────────────────────┐
│  Backend Receives    │
│  Query Submission    │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│  Get Today's Date    │
│  YYYY-MM-DD          │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│  Update/Insert       │
│  daily_activity      │
│  • user_id           │
│  • date              │
│  • queries_solved++  │
│  • points_earned++   │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│  Dashboard Fetches   │
│  GET /api/activity   │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│  React Calendar      │
│  Heatmap Component   │
│  • Map dates to data │
│  • Color by count    │
│  • Render 365 days   │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│  User Sees Updated   │
│  Green Squares! 🟩   │
└──────────────────────┘
```

## Mini-Game Flow

```
┌──────────────┐
│ User Clicks  │
│  Mini-Game   │
└──────┬───────┘
       │
       ▼
┌──────────────────────┐
│  MiniGames Component │
│  • Show game list    │
└──────┬───────────────┘
       │
       │ Select game
       ▼
┌──────────────────────┐
│  Initialize Game     │
│  • SQL Match         │
│  • Query Race        │
│  • Index Puzzle      │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│  User Plays          │
│  • Interactive UI    │
│  • Real-time scoring │
└──────┬───────────────┘
       │
       │ Game Complete
       ▼
┌──────────────────────┐
│  POST /api/mini-game │
│  { type, score }     │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│  Backend             │
│  • Save score        │
│  • Award points      │
│  • Update progress   │
└──────┬───────────────┘
       │
       │ Return points earned
       ▼
┌──────────────────────┐
│  Show Success        │
│  🎉 +150 points!     │
└──────────────────────┘
```

## State Management

```
┌─────────────────────────────────────────┐
│         React App State                 │
├─────────────────────────────────────────┤
│                                         │
│  ┌────────────────────────────────┐    │
│  │  App.js (Root)                 │    │
│  │  • user: { token, username }   │    │
│  │  • isAuthenticated             │    │
│  └────────────────────────────────┘    │
│                │                        │
│                ▼                        │
│  ┌────────────────────────────────┐    │
│  │  Dashboard                     │    │
│  │  • progress: { level, score }  │    │
│  │  • activity: [...]             │    │
│  └────────────────────────────────┘    │
│                │                        │
│                ▼                        │
│  ┌────────────────────────────────┐    │
│  │  GamePlay                      │    │
│  │  • currentQuery                │    │
│  │  • results                     │    │
│  │  • feedback                    │    │
│  └────────────────────────────────┘    │
│                                         │
└─────────────────────────────────────────┘
```

## Technology Stack Flow

```
┌─────────────────────────────────────────┐
│           User's Browser                │
│  ┌───────────────────────────────────┐  │
│  │         React 18                  │  │
│  │  • Components                     │  │
│  │  • Hooks (useState, useEffect)    │  │
│  │  • React Router                   │  │
│  └───────────────────────────────────┘  │
│  ┌───────────────────────────────────┐  │
│  │      Framer Motion                │  │
│  │  • Animations                     │  │
│  │  • Transitions                    │  │
│  └───────────────────────────────────┘  │
│  ┌───────────────────────────────────┐  │
│  │         Axios                     │  │
│  │  • HTTP Requests                  │  │
│  │  • Token Management               │  │
│  └───────────────────────────────────┘  │
└─────────────────────────────────────────┘
                    │
                    │ HTTP/HTTPS
                    ▼
┌─────────────────────────────────────────┐
│           Server                        │
│  ┌───────────────────────────────────┐  │
│  │         FastAPI                   │  │
│  │  • REST Endpoints                 │  │
│  │  • Request Validation             │  │
│  │  • Response Formatting            │  │
│  └───────────────────────────────────┘  │
│  ┌───────────────────────────────────┐  │
│  │         SQLite                    │  │
│  │  • User Data                      │  │
│  │  • Progress Tracking              │  │
│  │  • Activity Logs                  │  │
│  └───────────────────────────────────┘  │
│  ┌───────────────────────────────────┐  │
│  │      Google Gemini AI             │  │
│  │  • Hints Generation               │  │
│  │  • Query Analysis                 │  │
│  └───────────────────────────────────┘  │
└─────────────────────────────────────────┘
```

This visual guide shows how all components interact in the SQL Escape application!
