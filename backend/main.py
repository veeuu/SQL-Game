from fastapi import FastAPI, HTTPException, Depends, Header
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
    allow_origins=[
        "http://localhost:3000", 
        "http://127.0.0.1:3000",
        "http://192.168.1.59:3000"  # Your network IP
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Configure Gemini
genai.configure(api_key="")
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
    solution_type: str  # "simple" or "optimized"
    room_id: Optional[str] = None

class MiniGameResult(BaseModel):
    game_type: str
    score: int

class RoomCreate(BaseModel):
    mode: str  # "solo" or "duo"
    level: int

class RoomJoin(BaseModel):
    room_id: str

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
    
    c.execute("""CREATE TABLE IF NOT EXISTS rooms (
        id TEXT PRIMARY KEY,
        mode TEXT,
        level INTEGER,
        creator_id INTEGER,
        opponent_id INTEGER,
        status TEXT,
        created_at TEXT,
        FOREIGN KEY(creator_id) REFERENCES users(id),
        FOREIGN KEY(opponent_id) REFERENCES users(id)
    )""")
    
    c.execute("""CREATE TABLE IF NOT EXISTS level_completions (
        id INTEGER PRIMARY KEY,
        user_id INTEGER,
        level INTEGER,
        solution_type TEXT,
        query TEXT,
        execution_time REAL,
        completed_at TEXT,
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
def submit_query(data: QuerySubmit, authorization: Optional[str] = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    token = authorization.replace("Bearer ", "")
    user = verify_token(token)
    
    # Execute query logic here
    conn = sqlite3.connect(':memory:')
    c = conn.cursor()
    
    try:
        # Setup challenge data
        from challenge_data import setup_challenge_data, get_expected_result
        setup_challenge_data(conn, data.level)
        
        # Execute user's query
        start = time.time()
        c.execute(data.query)
        results = c.fetchall()
        exec_time = (time.time() - start) * 1000
        
        # Get expected results
        expected = get_expected_result(data.level)
        
        # Check if results match (for levels with validation)
        is_correct = True
        if expected:
            # Sort both for comparison
            sorted_results = sorted(results) if results else []
            sorted_expected = sorted(expected) if expected else []
            is_correct = sorted_results == sorted_expected
        
        if is_correct:
            # Get challenge points
            from challenges import CHALLENGES
            challenge = next((c for c in CHALLENGES if c['level'] == data.level), None)
            points = challenge['points'] if challenge else 50
            coins = challenge['coins'] if challenge else 10
            
            # Update progress
            db_conn = sqlite3.connect(DB_PATH)
            db_c = db_conn.cursor()
            
            # Save level completion
            db_c.execute("""INSERT INTO level_completions 
                           (user_id, level, solution_type, query, execution_time, completed_at)
                           VALUES (?, ?, ?, ?, ?, ?)""",
                        (user['user_id'], data.level, data.solution_type, data.query, 
                         exec_time, datetime.now().isoformat()))
            
            # Update score and coins
            db_c.execute("""UPDATE progress SET score = score + ?, energy = energy + 5
                           WHERE user_id = ?""", (points, user['user_id']))
            
            # Update daily activity
            today = datetime.now().date().isoformat()
            db_c.execute("""INSERT INTO daily_activity (user_id, date, queries_solved, points_earned)
                            VALUES (?, ?, 1, ?)
                            ON CONFLICT(user_id, date) DO UPDATE SET
                            queries_solved = queries_solved + 1,
                            points_earned = points_earned + ?""",
                         (user['user_id'], today, points, points))
            
            db_conn.commit()
            db_conn.close()
            
            return {
                "success": True,
                "correct": True,
                "results": results,
                "execution_time": exec_time,
                "points_earned": points,
                "coins_earned": coins,
                "message": "Perfect! Query executed successfully!"
            }
        else:
            return {
                "success": True,
                "correct": False,
                "results": results,
                "expected": expected,
                "execution_time": exec_time,
                "message": "Query executed but results don't match expected output"
            }
            
    except Exception as e:
        return {"success": False, "error": str(e)}
    finally:
        conn.close()

@app.post("/api/mini-game")
def submit_mini_game(data: MiniGameResult, authorization: Optional[str] = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")
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

@app.post("/api/room/create")
def create_room(data: RoomCreate, authorization: Optional[str] = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    token = authorization.replace("Bearer ", "")
    user = verify_token(token)
    
    import uuid
    room_id = str(uuid.uuid4())[:8]
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute("""INSERT INTO rooms (id, mode, level, creator_id, status, created_at)
                 VALUES (?, ?, ?, ?, 'waiting', ?)""",
              (room_id, data.mode, data.level, user['user_id'], datetime.now().isoformat()))
    conn.commit()
    conn.close()
    
    return {"room_id": room_id, "mode": data.mode, "level": data.level}

@app.post("/api/room/join")
def join_room(data: RoomJoin, authorization: Optional[str] = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    token = authorization.replace("Bearer ", "")
    user = verify_token(token)
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute("SELECT * FROM rooms WHERE id = ? AND status = 'waiting'", (data.room_id,))
    room = c.fetchone()
    
    if not room:
        raise HTTPException(status_code=404, detail="Room not found or already started")
    
    c.execute("UPDATE rooms SET opponent_id = ?, status = 'active' WHERE id = ?",
              (user['user_id'], data.room_id))
    conn.commit()
    conn.close()
    
    return {"success": True, "room_id": data.room_id}

@app.get("/api/room/{room_id}")
def get_room(room_id: str):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute("""SELECT r.*, u1.username as creator_name, u2.username as opponent_name
                 FROM rooms r
                 JOIN users u1 ON r.creator_id = u1.id
                 LEFT JOIN users u2 ON r.opponent_id = u2.id
                 WHERE r.id = ?""", (room_id,))
    room = c.fetchone()
    conn.close()
    
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    
    return {
        "room_id": room[0],
        "mode": room[1],
        "level": room[2],
        "creator": room[7],
        "opponent": room[8] if room[8] else None,
        "status": room[5]
    }

@app.get("/api/challenges")
def get_challenges():
    from challenges import CHALLENGES
    return {"challenges": CHALLENGES}

@app.get("/api/test-auth")
def test_auth(authorization: Optional[str] = Header(None)):
    if not authorization:
        return {"error": "No authorization header", "received": None}
    
    try:
        token = authorization.replace("Bearer ", "")
        user = verify_token(token)
        return {"success": True, "user": user}
    except Exception as e:
        return {"error": str(e), "token_received": authorization[:20] + "..."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
