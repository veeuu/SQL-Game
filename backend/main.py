from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
import sqlite3
import time
import jwt
from datetime import datetime, timedelta
import google.generativeai as genai
from passlib.hash import bcrypt

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure Gemini
genai.configure(api_key="AIzaSyAM1qA3ayBq4pO7yXH-wDe1f_imx1MNmvQ")
gemini_model = genai.GenerativeModel('gemini-2.5-flash')

SECRET_KEY = "sql-dungeon-secret-key-2024"
DB_PATH = "game.db"

# Models
class UserRegister(BaseModel):
    username: str
    email: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class QuerySubmit(BaseModel):
    query: str
    level: int

class MiniGameResult(BaseModel):
    game_type: str
    score: int

# Database setup
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute("""CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        username TEXT UNIQUE,
        email TEXT UNIQUE,
        password TEXT,
        created_at TEXT
    )""")
    
    c.execute("""CREATE TABLE IF NOT EXISTS progress (
        id INTEGER PRIMARY KEY,
        user_id INTEGER,
        level INTEGER,
        score INTEGER,
        energy INTEGER,
        completed_at TEXT,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )""")
    
    c.execute("""CREATE TABLE IF NOT EXISTS daily_activity (
        id INTEGER PRIMARY KEY,
        user_id INTEGER,
        date TEXT,
        queries_solved INTEGER,
        points_earned INTEGER,
        UNIQUE(user_id, date),
        FOREIGN KEY(user_id) REFERENCES users(id)
    )""")
    
    c.execute("""CREATE TABLE IF NOT EXISTS mini_game_scores (
        id INTEGER PRIMARY KEY,
        user_id INTEGER,
        game_type TEXT,
        score INTEGER,
        played_at TEXT,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )""")
    
    conn.commit()
    conn.close()

init_db()

# Auth helpers
def create_token(user_id: int, username: str):
    payload = {
        "user_id": user_id,
        "username": username,
        "exp": datetime.utcnow() + timedelta(days=7)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload
    except:
        raise HTTPException(status_code=401, detail="Invalid token")

# Routes
@app.post("/api/register")
def register(user: UserRegister):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    try:
        hashed_pw = bcrypt.hash(user.password)
        c.execute("INSERT INTO users (username, email, password, created_at) VALUES (?, ?, ?, ?)",
                  (user.username, user.email, hashed_pw, datetime.now().isoformat()))
        conn.commit()
        user_id = c.lastrowid
        
        # Initialize progress
        c.execute("INSERT INTO progress (user_id, level, score, energy) VALUES (?, 1, 0, 100)",
                  (user_id,))
        conn.commit()
        
        token = create_token(user_id, user.username)
        return {"token": token, "username": user.username}
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Username or email already exists")
    finally:
        conn.close()

@app.post("/api/login")
def login(user: UserLogin):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute("SELECT id, username, password FROM users WHERE username = ?", (user.username,))
    result = c.fetchone()
    conn.close()
    
    if not result or not bcrypt.verify(user.password, result[2]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_token(result[0], result[1])
    return {"token": token, "username": result[1]}

@app.get("/api/progress/{username}")
def get_progress(username: str):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute("""SELECT p.level, p.score, p.energy 
                 FROM progress p 
                 JOIN users u ON p.user_id = u.id 
                 WHERE u.username = ?""", (username,))
    result = c.fetchone()
    conn.close()
    
    if not result:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {"level": result[0], "score": result[1], "energy": result[2]}

@app.get("/api/activity/{username}")
def get_activity(username: str):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute("""SELECT date, queries_solved, points_earned 
                 FROM daily_activity da
                 JOIN users u ON da.user_id = u.id 
                 WHERE u.username = ?
                 ORDER BY date DESC LIMIT 365""", (username,))
    results = c.fetchall()
    conn.close()
    
    return [{"date": r[0], "queries": r[1], "points": r[2]} for r in results]

@app.post("/api/submit-query")
def submit_query(data: QuerySubmit, authorization: str = ""):
    token = authorization.replace("Bearer ", "")
    user = verify_token(token)
    
    # Execute query logic here
    conn = sqlite3.connect(':memory:')
    c = conn.cursor()
    
    try:
        start = time.time()
        c.execute(data.query)
        results = c.fetchall()
        exec_time = (time.time() - start) * 1000
        
        # Update progress
        db_conn = sqlite3.connect(DB_PATH)
        db_c = db_conn.cursor()
        
        # Update daily activity
        today = datetime.now().date().isoformat()
        db_c.execute("""INSERT INTO daily_activity (user_id, date, queries_solved, points_earned)
                        VALUES (?, ?, 1, 50)
                        ON CONFLICT(user_id, date) DO UPDATE SET
                        queries_solved = queries_solved + 1,
                        points_earned = points_earned + 50""",
                     (user['user_id'], today))
        db_conn.commit()
        db_conn.close()
        
        return {
            "success": True,
            "results": results,
            "execution_time": exec_time,
            "points_earned": 50
        }
    except Exception as e:
        return {"success": False, "error": str(e)}
    finally:
        conn.close()

@app.post("/api/mini-game")
def submit_mini_game(data: MiniGameResult, authorization: str = ""):
    token = authorization.replace("Bearer ", "")
    user = verify_token(token)
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute("""INSERT INTO mini_game_scores (user_id, game_type, score, played_at)
                 VALUES (?, ?, ?, ?)""",
              (user['user_id'], data.game_type, data.score, datetime.now().isoformat()))
    
    # Award points
    points = data.score * 10
    c.execute("""UPDATE progress SET score = score + ? 
                 WHERE user_id = ?""", (points, user['user_id']))
    
    conn.commit()
    conn.close()
    
    return {"points_earned": points}

@app.get("/api/ai-hint")
def get_ai_hint(level: int, concept: str):
    prompt = f"Give a brief SQL optimization hint for level {level} focusing on {concept}. One sentence only."
    try:
        response = gemini_model.generate_content(prompt)
        return {"hint": response.text}
    except:
        return {"hint": "Try optimizing your query with proper indexes and joins."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
