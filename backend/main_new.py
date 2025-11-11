from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import jwt
from datetime import datetime, timedelta
import google.generativeai as genai
from passlib.hash import bcrypt
from bson import ObjectId
import uuid

from database import (
    users_collection, progress_collection, challenges_collection,
    level_completions_collection, rooms_collection, daily_activity_collection
)

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://192.168.1.59:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Configure Gemini
genai.configure(api_key="")
gemini_model = genai.GenerativeModel('gemini-2.0-flash')

SECRET_KEY = "sql-dungeon-secret-key-2024"

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
    solution_type: str
    room_id: Optional[str] = None

class RoomCreate(BaseModel):
    mode: str
    level: int

class RoomJoin(BaseModel):
    room_id: str

# Helper functions
def create_token(user_id: str, username: str):
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
    # Check if user exists
    if users_collection.find_one({"$or": [{"username": user.username}, {"email": user.email}]}):
        raise HTTPException(status_code=400, detail="Username or email already exists")
    
    # Create user
    hashed_pw = bcrypt.hash(user.password)
    user_doc = {
        "username": user.username,
        "email": user.email,
        "password": hashed_pw,
        "created_at": datetime.utcnow()
    }
    result = users_collection.insert_one(user_doc)
    user_id = str(result.inserted_id)
    
    # Initialize progress
    progress_collection.insert_one({
        "user_id": user_id,
        "current_level": 1,
        "completed_levels": [],
        "score": 0,
        "coins": 0,
        "energy": 100,
        "updated_at": datetime.utcnow()
    })
    
    token = create_token(user_id, user.username)
    return {"token": token, "username": user.username}

@app.post("/api/login")
def login(user: UserLogin):
    user_doc = users_collection.find_one({"username": user.username})
    if not user_doc or not bcrypt.verify(user.password, user_doc["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_token(str(user_doc["_id"]), user_doc["username"])
    return {"token": token, "username": user_doc["username"]}

@app.get("/api/progress/{username}")
def get_progress(username: str):
    user = users_collection.find_one({"username": username})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    progress = progress_collection.find_one({"user_id": str(user["_id"])})
    if not progress:
        return {"level": 1, "score": 0, "coins": 0, "energy": 100, "completed_levels": []}
    
    return {
        "level": progress.get("current_level", 1),
        "score": progress.get("score", 0),
        "coins": progress.get("coins", 0),
        "energy": progress.get("energy", 100),
        "completed_levels": progress.get("completed_levels", [])
    }

@app.get("/api/challenges")
def get_challenges():
    challenges = list(challenges_collection.find({}, {"_id": 0}))
    return {"challenges": challenges}

@app.get("/api/challenge/{level}")
def get_challenge(level: int):
    challenge = challenges_collection.find_one({"level": level}, {"_id": 0})
    if not challenge:
        raise HTTPException(status_code=404, detail="Challenge not found")
    return challenge

@app.post("/api/submit-query")
async def submit_query(data: QuerySubmit, authorization: Optional[str] = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    
    token = authorization.replace("Bearer ", "")
    user = verify_token(token)
    
    # Get challenge
    challenge = challenges_collection.find_one({"level": data.level})
    if not challenge:
        raise HTTPException(status_code=404, detail="Challenge not found")
    
    # Use Gemini to validate the query
    try:
        validation_prompt = f"""
        You are a SQL validator. Check if this query solves the challenge correctly.
        
        Challenge: {challenge['objective']}
        User's Query: {data.query}
        
        Respond with ONLY a JSON object:
        {{
            "is_correct": true/false,
            "feedback": "brief feedback message",
            "explanation": "why it's correct or what's wrong"
        }}
        """
        
        response = gemini_model.generate_content(validation_prompt)
        # Parse Gemini response (simplified - you'd want better parsing)
        is_correct = "true" in response.text.lower() and "is_correct" in response.text.lower()
        
        if is_correct:
            # Update progress
            progress = progress_collection.find_one({"user_id": user["user_id"]})
            completed_levels = progress.get("completed_levels", [])
            
            if data.level not in completed_levels:
                completed_levels.append(data.level)
                next_level = data.level + 1
            else:
                next_level = progress.get("current_level", data.level)
            
            # Update progress
            progress_collection.update_one(
                {"user_id": user["user_id"]},
                {
                    "$set": {
                        "current_level": next_level,
                        "completed_levels": completed_levels,
                        "updated_at": datetime.utcnow()
                    },
                    "$inc": {
                        "score": challenge["points"],
                        "coins": challenge["coins"],
                        "energy": 5
                    }
                }
            )
            
            # Save completion
            level_completions_collection.insert_one({
                "user_id": user["user_id"],
                "level": data.level,
                "solution_type": data.solution_type,
                "query": data.query,
                "completed_at": datetime.utcnow()
            })
            
            # Update daily activity
            today = datetime.utcnow().date().isoformat()
            daily_activity_collection.update_one(
                {"user_id": user["user_id"], "date": today},
                {
                    "$inc": {
                        "queries_solved": 1,
                        "points_earned": challenge["points"]
                    },
                    "$setOnInsert": {"user_id": user["user_id"], "date": today}
                },
                upsert=True
            )
            
            return {
                "success": True,
                "correct": True,
                "points_earned": challenge["points"],
                "coins_earned": challenge["coins"],
                "next_level": next_level,
                "message": "Perfect! Level completed!",
                "feedback": response.text
            }
        else:
            return {
                "success": True,
                "correct": False,
                "message": "Query executed but doesn't solve the challenge",
                "feedback": response.text
            }
            
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/api/room/create")
def create_room(data: RoomCreate, authorization: Optional[str] = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    
    token = authorization.replace("Bearer ", "")
    user = verify_token(token)
    
    room_id = str(uuid.uuid4())[:8]
    
    rooms_collection.insert_one({
        "room_id": room_id,
        "mode": data.mode,
        "level": data.level,
        "creator_id": user["user_id"],
        "opponent_id": None,
        "status": "waiting",
        "created_at": datetime.utcnow()
    })
    
    return {"room_id": room_id, "mode": data.mode, "level": data.level}

@app.post("/api/room/join")
def join_room(data: RoomJoin, authorization: Optional[str] = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    
    token = authorization.replace("Bearer ", "")
    user = verify_token(token)
    
    room = rooms_collection.find_one({"room_id": data.room_id, "status": "waiting"})
    if not room:
        raise HTTPException(status_code=404, detail="Room not found or already started")
    
    rooms_collection.update_one(
        {"room_id": data.room_id},
        {"$set": {"opponent_id": user["user_id"], "status": "active"}}
    )
    
    return {"success": True, "room_id": data.room_id}

@app.get("/api/activity/{username}")
def get_activity(username: str):
    user = users_collection.find_one({"username": username})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    activities = list(daily_activity_collection.find(
        {"user_id": str(user["_id"])},
        {"_id": 0}
    ).sort("date", -1).limit(365))
    
    return [{"date": a["date"], "queries": a.get("queries_solved", 0), "points": a.get("points_earned", 0)} for a in activities]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
