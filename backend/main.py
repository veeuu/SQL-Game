from fastapi import FastAPI, HTTPException, Header, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict
import time
import jwt
import uuid
from datetime import datetime, timedelta
from passlib.hash import bcrypt
from database import get_conn, init_db, run_challenge_query

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://192.168.1.59:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SECRET_KEY = "sql-dungeon-secret-key-2024"

# Initialize PostgreSQL tables on startup
try:
    init_db()
except Exception as e:
    print(f"⚠️  DB init warning: {e}")

# ─── WebSocket Manager ────────────────────────────────────────────────────────

class ConnectionManager:
    def __init__(self):
        self.rooms: Dict[str, Dict[int, WebSocket]] = {}

    async def connect(self, ws: WebSocket, room_id: str, user_id: int):
        await ws.accept()
        self.rooms.setdefault(room_id, {})[user_id] = ws

    def disconnect(self, room_id: str, user_id: int):
        if room_id in self.rooms:
            self.rooms[room_id].pop(user_id, None)

    async def broadcast(self, room_id: str, msg: dict, exclude: int = None):
        for uid, ws in list(self.rooms.get(room_id, {}).items()):
            if uid != exclude:
                try:
                    await ws.send_json(msg)
                except:
                    pass

manager = ConnectionManager()

# ─── Pydantic Models ──────────────────────────────────────────────────────────

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
    solution_type: str = "simple"
    room_id: Optional[str] = None
    challenge_objective: Optional[str] = None
    solution_query: Optional[str] = None

class RoomCreate(BaseModel):
    mode: str
    level: int = 1

class RoomJoin(BaseModel):
    room_id: str

class MiniGameResult(BaseModel):
    game_type: str
    score: int

# ─── Auth Helpers ─────────────────────────────────────────────────────────────

def create_token(user_id: int, username: str):
    return jwt.encode(
        {"user_id": user_id, "username": username,
         "exp": datetime.utcnow() + timedelta(days=7)},
        SECRET_KEY, algorithm="HS256"
    )

def verify_token(token: str):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    except:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

def get_user(authorization: Optional[str]):
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    return verify_token(authorization.replace("Bearer ", ""))

# ─── Auth Routes ──────────────────────────────────────────────────────────────

@app.post("/api/register")
def register(user: UserRegister):
    conn = get_conn()
    c = conn.cursor()
    try:
        hashed = bcrypt.hash(user.password)
        c.execute(
            "INSERT INTO users (username, email, password, created_at) VALUES (%s,%s,%s,%s) RETURNING id",
            (user.username, user.email, hashed, datetime.now().isoformat())
        )
        uid = c.fetchone()[0]
        c.execute("INSERT INTO progress (user_id) VALUES (%s)", (uid,))
        conn.commit()
        return {"token": create_token(uid, user.username), "username": user.username}
    except Exception as e:
        conn.rollback()
        if "unique" in str(e).lower():
            raise HTTPException(status_code=400, detail="Username or email already exists")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        c.close(); conn.close()

@app.post("/api/login")
def login(user: UserLogin):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT id, username, password FROM users WHERE username=%s", (user.username,))
    row = c.fetchone()
    c.close(); conn.close()
    if not row or not bcrypt.verify(user.password, row[2]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"token": create_token(row[0], row[1]), "username": row[1]}

# ─── Progress Routes ──────────────────────────────────────────────────────────

@app.get("/api/progress/{username}")
def get_progress(username: str):
    conn = get_conn()
    c = conn.cursor()
    c.execute("""SELECT p.level, p.score, p.energy, u.id
                 FROM progress p JOIN users u ON p.user_id=u.id
                 WHERE u.username=%s""", (username,))
    row = c.fetchone()
    if not row:
        c.close(); conn.close()
        raise HTTPException(status_code=404, detail="User not found")
    c.execute("SELECT DISTINCT level FROM level_completions WHERE user_id=%s", (row[3],))
    completed = [r[0] for r in c.fetchall()]
    c.close(); conn.close()
    return {"level": row[0], "score": row[1], "energy": row[2], "completed_levels": completed}

@app.get("/api/activity/{username}")
def get_activity(username: str):
    conn = get_conn()
    c = conn.cursor()
    c.execute("""SELECT date, queries_solved, points_earned
                 FROM daily_activity da JOIN users u ON da.user_id=u.id
                 WHERE u.username=%s ORDER BY date DESC LIMIT 365""", (username,))
    rows = c.fetchall()
    c.close(); conn.close()
    return [{"date": r[0], "queries": r[1], "points": r[2]} for r in rows]

# ─── Challenge Routes (Gemini-powered) ───────────────────────────────────────

@app.get("/api/challenge/{level}")
def get_challenge(level: int):
    """Gemini-generated challenge for solo mode."""
    from gemini_challenge_generator import generate_challenge
    ch = generate_challenge(level, round_number=1)
    return {
        "level": level,
        "title": ch.get("title", f"Level {level}"),
        "story": ch.get("story", ""),
        "objective": ch.get("objective", ""),
        "hints": ch.get("hints", []),
        "difficulty": ch.get("difficulty", "medium"),
        "points": ch.get("points", 50),
        "concept": ch.get("concept", "SQL"),
        "solution_query": ch.get("solution_query", "")
    }

@app.get("/api/room/{room_id}/challenge")
def get_room_challenge(room_id: str):
    """Gemini-generated challenge for the current duo round."""
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT level, current_round FROM rooms WHERE id=%s", (room_id,))
    row = c.fetchone()
    c.close(); conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Room not found")

    level, current_round = row
    from gemini_challenge_generator import generate_challenge
    ch = generate_challenge(level, current_round)
    return {
        "level": level,
        "round": current_round,
        "title": ch.get("title", f"Round {current_round}"),
        "story": ch.get("story", ""),
        "objective": ch.get("objective", ""),
        "hints": ch.get("hints", []),
        "difficulty": ch.get("difficulty", "medium"),
        "points": ch.get("points", 50),
        "concept": ch.get("concept", "SQL"),
        "solution_query": ch.get("solution_query", "")
    }

@app.get("/api/hint")
def get_hint_api(objective: str, solution_query: str, hint_number: int = 1):
    """Progressive hint from Gemini."""
    from gemini_challenge_generator import get_hint
    return {"hint": get_hint(objective, solution_query, hint_number)}

# ─── Solo Query Submit ────────────────────────────────────────────────────────

@app.post("/api/submit-query")
def submit_query(data: QuerySubmit, authorization: Optional[str] = Header(None)):
    user = get_user(authorization)

    sandbox = setup_sandbox()
    try:
        c = sandbox.cursor()
        start = time.time()
        c.execute(data.query)
        results = c.fetchall()
        exec_time = (time.time() - start) * 1000
    except Exception as e:
        sandbox.close()
        return {"success": False, "error": str(e)}
    finally:
        sandbox.close()

    from gemini_challenge_generator import validate_query
    is_correct, feedback = validate_query(
        data.query, data.solution_query or "",
        data.challenge_objective or "", results, None
    )

    if is_correct:
        points = data.level * 10 + 40
        conn = get_conn()
        dc = conn.cursor()
        dc.execute("""INSERT INTO level_completions (user_id, level, query, execution_time, completed_at)
                      VALUES (%s,%s,%s,%s,%s)""",
                   (user['user_id'], data.level, data.query, exec_time, datetime.now().isoformat()))
        dc.execute("UPDATE progress SET score=score+%s, energy=LEAST(energy+5,100) WHERE user_id=%s",
                   (points, user['user_id']))
        today = datetime.now().date().isoformat()
        dc.execute("""INSERT INTO daily_activity (user_id, date, queries_solved, points_earned)
                      VALUES (%s,%s,1,%s)
                      ON CONFLICT(user_id,date) DO UPDATE SET
                      queries_solved=daily_activity.queries_solved+1,
                      points_earned=daily_activity.points_earned+%s""",
                   (user['user_id'], today, points, points))
        conn.commit()
        dc.close(); conn.close()
        return {"success": True, "correct": True, "results": results,
                "execution_time": exec_time, "points_earned": points, "feedback": feedback}

    return {"success": True, "correct": False, "results": results,
            "execution_time": exec_time, "feedback": feedback}

# ─── Duo Submit ───────────────────────────────────────────────────────────────

@app.post("/api/duo/submit")
async def duo_submit(data: QuerySubmit, authorization: Optional[str] = Header(None)):
    user = get_user(authorization)
    if not data.room_id:
        raise HTTPException(status_code=400, detail="room_id required")

    conn = get_conn()
    dc = conn.cursor()
    dc.execute("""SELECT level, current_round, creator_id, opponent_id,
                         player1_score, player2_score, total_rounds
                  FROM rooms WHERE id=%s""", (data.room_id,))
    room = dc.fetchone()
    if not room:
        dc.close(); conn.close()
        raise HTTPException(status_code=404, detail="Room not found")

    level, current_round, creator_id, opponent_id, p1_score, p2_score, total_rounds = room

    # Execute in sandbox
    sandbox = setup_sandbox()
    try:
        sc = sandbox.cursor()
        start = time.time()
        sc.execute(data.query)
        results = sc.fetchall()
        exec_time = (time.time() - start) * 1000
    except Exception as e:
        sandbox.close()
        dc.close(); conn.close()
        return {"success": False, "error": str(e)}
    finally:
        sandbox.close()

    from gemini_challenge_generator import validate_query
    is_correct, feedback = validate_query(
        data.query, data.solution_query or "",
        data.challenge_objective or "", results, None
    )

    # Save submission
    dc.execute("""INSERT INTO duo_submissions
                  (room_id, user_id, round_number, query, is_correct, execution_time, submitted_at)
                  VALUES (%s,%s,%s,%s,%s,%s,%s)""",
               (data.room_id, user['user_id'], current_round, data.query,
                is_correct, exec_time, datetime.now().isoformat()))
    conn.commit()

    round_winner_id = None
    match_winner_id = None
    points_earned = 0

    if is_correct:
        # Check if first correct this round
        dc.execute("""SELECT user_id FROM duo_submissions
                      WHERE room_id=%s AND round_number=%s AND is_correct=TRUE
                      ORDER BY submitted_at ASC""", (data.room_id, current_round))
        correct_subs = dc.fetchall()

        if len(correct_subs) == 1:
            # First correct → wins round, double points
            round_winner_id = user['user_id']
            points_earned = 100

            if user['user_id'] == creator_id:
                p1_score += 1
            else:
                p2_score += 1

            dc.execute("UPDATE rooms SET player1_score=%s, player2_score=%s WHERE id=%s",
                       (p1_score, p2_score, data.room_id))
            conn.commit()

            # Check match winner
            rounds_to_win = (total_rounds // 2) + 1
            if p1_score >= rounds_to_win:
                match_winner_id = creator_id
            elif p2_score >= rounds_to_win:
                match_winner_id = opponent_id

            if match_winner_id:
                dc.execute("UPDATE rooms SET status='completed', winner_id=%s WHERE id=%s",
                           (match_winner_id, data.room_id))
                conn.commit()
                await manager.broadcast(data.room_id, {
                    "type": "match_over",
                    "winner_id": match_winner_id,
                    "player1_score": p1_score,
                    "player2_score": p2_score
                })
            else:
                await manager.broadcast(data.room_id, {
                    "type": "round_won",
                    "round_number": current_round,
                    "winner_id": round_winner_id,
                    "player1_score": p1_score,
                    "player2_score": p2_score
                })
        else:
            points_earned = 50  # consolation for second correct

        # Award points
        dc.execute("UPDATE progress SET score=score+%s WHERE user_id=%s",
                   (points_earned, user['user_id']))
        today = datetime.now().date().isoformat()
        dc.execute("""INSERT INTO daily_activity (user_id, date, queries_solved, points_earned)
                      VALUES (%s,%s,1,%s)
                      ON CONFLICT(user_id,date) DO UPDATE SET
                      queries_solved=daily_activity.queries_solved+1,
                      points_earned=daily_activity.points_earned+%s""",
                   (user['user_id'], today, points_earned, points_earned))
        conn.commit()

    dc.close(); conn.close()

    return {
        "success": True,
        "correct": is_correct,
        "feedback": feedback,
        "results": results,
        "execution_time": exec_time,
        "points_earned": points_earned,
        "is_round_winner": round_winner_id == user['user_id'],
        "is_match_winner": match_winner_id == user['user_id'] if match_winner_id else False,
        "player1_score": p1_score,
        "player2_score": p2_score
    }

# ─── Room Routes ──────────────────────────────────────────────────────────────

@app.post("/api/room/create")
def create_room(data: RoomCreate, authorization: Optional[str] = Header(None)):
    user = get_user(authorization)
    room_id = str(uuid.uuid4())[:8]
    conn = get_conn()
    c = conn.cursor()
    c.execute("""INSERT INTO rooms (id, mode, level, creator_id, status, created_at)
                 VALUES (%s,%s,%s,%s,'waiting',%s)""",
              (room_id, data.mode, data.level, user['user_id'], datetime.now().isoformat()))
    conn.commit()
    c.close(); conn.close()
    return {"room_id": room_id, "mode": data.mode, "level": data.level}

@app.post("/api/room/join")
def join_room(data: RoomJoin, authorization: Optional[str] = Header(None)):
    user = get_user(authorization)
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT id FROM rooms WHERE id=%s AND status='waiting'", (data.room_id,))
    if not c.fetchone():
        c.close(); conn.close()
        raise HTTPException(status_code=404, detail="Room not found or already started")
    c.execute("UPDATE rooms SET opponent_id=%s, status='active' WHERE id=%s",
              (user['user_id'], data.room_id))
    conn.commit()
    c.close(); conn.close()
    return {"success": True, "room_id": data.room_id}

@app.get("/api/room/{room_id}")
def get_room(room_id: str):
    conn = get_conn()
    c = conn.cursor()
    c.execute("""SELECT r.id, r.mode, r.level, r.creator_id, r.opponent_id, r.status,
                        r.winner_id, r.total_rounds, r.current_round,
                        r.player1_score, r.player2_score,
                        u1.username, u2.username
                 FROM rooms r
                 JOIN users u1 ON r.creator_id=u1.id
                 LEFT JOIN users u2 ON r.opponent_id=u2.id
                 WHERE r.id=%s""", (room_id,))
    row = c.fetchone()
    c.close(); conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Room not found")
    return {
        "room_id": row[0], "mode": row[1], "level": row[2],
        "creator_id": row[3], "opponent_id": row[4], "status": row[5],
        "winner_id": row[6], "total_rounds": row[7], "current_round": row[8],
        "player1_score": row[9], "player2_score": row[10],
        "creator_name": row[11], "opponent_name": row[12]
    }

@app.post("/api/room/{room_id}/next-round")
async def next_round(room_id: str, authorization: Optional[str] = Header(None)):
    get_user(authorization)
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT current_round, total_rounds FROM rooms WHERE id=%s", (room_id,))
    row = c.fetchone()
    if not row:
        c.close(); conn.close()
        raise HTTPException(status_code=404, detail="Room not found")
    current, total = row
    if current >= total:
        c.close(); conn.close()
        raise HTTPException(status_code=400, detail="All rounds completed")
    c.execute("UPDATE rooms SET current_round=current_round+1 WHERE id=%s", (room_id,))
    conn.commit()
    c.close(); conn.close()
    await manager.broadcast(room_id, {"type": "next_round", "round_number": current + 1})
    return {"success": True, "next_round": current + 1}

# ─── WebSocket ────────────────────────────────────────────────────────────────

@app.websocket("/ws/{room_id}/{user_id}")
async def websocket_endpoint(ws: WebSocket, room_id: str, user_id: int):
    await manager.connect(ws, room_id, user_id)
    try:
        await manager.broadcast(room_id, {"type": "player_connected", "user_id": user_id}, exclude=user_id)
        while True:
            data = await ws.receive_json()
            if data.get("type") == "typing":
                await manager.broadcast(room_id, {
                    "type": "typing_indicator",
                    "user_id": user_id,
                    "is_typing": data.get("is_typing", True)
                }, exclude=user_id)
            elif data.get("type") == "query_submitted":
                await manager.broadcast(room_id, {
                    "type": "opponent_submitted", "user_id": user_id
                }, exclude=user_id)
    except WebSocketDisconnect:
        manager.disconnect(room_id, user_id)
        await manager.broadcast(room_id, {"type": "player_disconnected", "user_id": user_id})

# ─── Mini Games ───────────────────────────────────────────────────────────────

@app.post("/api/mini-game")
def mini_game(data: MiniGameResult, authorization: Optional[str] = Header(None)):
    user = get_user(authorization)
    points = data.score * 10
    conn = get_conn()
    c = conn.cursor()
    c.execute("INSERT INTO mini_game_scores (user_id, game_type, score, played_at) VALUES (%s,%s,%s,%s)",
              (user['user_id'], data.game_type, data.score, datetime.now().isoformat()))
    c.execute("UPDATE progress SET score=score+%s WHERE user_id=%s", (points, user['user_id']))
    conn.commit()
    c.close(); conn.close()
    return {"points_earned": points}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
