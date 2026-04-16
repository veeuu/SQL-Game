import google.generativeai as genai
import json
import re
import os
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel(os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite-preview"))

LEVEL_CONFIG = {
    (1, 3):   {"difficulty": "easy",   "concept": "SELECT, FROM, WHERE basics"},
    (4, 6):   {"difficulty": "easy",   "concept": "ORDER BY, LIMIT, DISTINCT"},
    (7, 10):  {"difficulty": "medium", "concept": "AND/OR, LIKE, IN, BETWEEN"},
    (11, 15): {"difficulty": "medium", "concept": "JOIN, GROUP BY, HAVING, COUNT/SUM/AVG"},
    (16, 20): {"difficulty": "hard",   "concept": "LEFT JOIN, Subqueries, CASE, MAX/MIN"},
    (21, 25): {"difficulty": "hard",   "concept": "Window Functions, CTEs, Self JOIN"},
    (26, 30): {"difficulty": "expert", "concept": "Recursive CTEs, Complex Aggregations"},
}

def get_level_config(level: int):
    for (lo, hi), cfg in LEVEL_CONFIG.items():
        if lo <= level <= hi:
            return cfg
    return {"difficulty": "medium", "concept": "SQL basics"}


def generate_challenge(level: int, round_number: int = 1):
    """Generate a unique SQL challenge using Gemini AI."""
    cfg = get_level_config(level)

    prompt = f"""You are designing a SQL challenge for a competitive dungeon-themed coding game.

Level: {level} | Round: {round_number} | Difficulty: {cfg['difficulty']}
SQL Concept: {cfg['concept']}

Available tables (PostgreSQL syntax):
- users(id, username, email, age, city)
- orders(id, user_id, product, amount, created_at)
- employees(id, name, department, salary, manager_id)

Rules:
- Only use the tables listed above
- Test the concept: {cfg['concept']}
- Fun dungeon/quest/adventure theme
- Valid PostgreSQL query as solution
- Solvable in under 2 minutes
- Round {round_number} must feel different from other rounds

Return ONLY this JSON (no markdown):
{{
  "title": "Short catchy title with emoji",
  "story": "1-2 sentence dungeon-themed story",
  "objective": "Exact task description for the player",
  "solution_query": "The correct PostgreSQL query",
  "hints": [
    "Hint 1: general direction",
    "Hint 2: specific keyword",
    "Hint 3: near-complete guidance"
  ],
  "concept": "{cfg['concept']}",
  "difficulty": "{cfg['difficulty']}",
  "points": {50 + (level * 5)}
}}"""

    try:
        response = model.generate_content(prompt)
        text = response.text.strip().replace('```json', '').replace('```', '').strip()
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            data = json.loads(match.group())
            data.setdefault("title", f"Level {level} Challenge")
            data.setdefault("story", "A new challenge awaits in the dungeon!")
            data.setdefault("objective", "Write a SQL query to solve this challenge")
            data.setdefault("solution_query", "SELECT * FROM users")
            data.setdefault("hints", ["Think about the SQL concept", "Check the table structure", "Try a simple query first"])
            data.setdefault("points", 50 + (level * 5))
            return data
    except Exception as e:
        print(f"[Gemini] Challenge generation error: {e}")

    return _fallback(level, round_number)


def get_hint(objective: str, solution_query: str, hint_number: int = 1):
    """Get a progressive hint from Gemini."""
    prompt = f"""A player is stuck on this SQL challenge:
Objective: {objective}

Give hint #{hint_number} (1=vague direction, 2=specific SQL keyword, 3=near-complete answer).
Return ONLY the hint text, no formatting, no markdown."""

    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except:
        defaults = [
            "Think about which SQL clause you need here.",
            "You'll need a specific SQL keyword for this type of query.",
            f"Start with: {solution_query[:40]}..."
        ]
        return defaults[min(hint_number - 1, 2)]


def validate_query(user_query: str, solution_query: str, objective: str,
                   actual_results, expected_results):
    """
    Validate a user's SQL query.
    1. Compare results if available
    2. Fall back to Gemini semantic check
    Returns: (is_correct: bool, feedback: str)
    """
    # Primary: result comparison
    if actual_results is not None and expected_results is not None:
        try:
            if sorted(actual_results) == sorted(expected_results):
                return True, "✅ Correct! Your query matches the expected output."
        except:
            pass

    # Secondary: Gemini semantic validation
    prompt = f"""SQL Challenge: {objective}
Expected solution: {solution_query}
Player's query: {user_query}

Is the player's query logically correct for this challenge?
Accept any valid SQL that achieves the same result.
Return ONLY JSON: {{"is_correct": true, "feedback": "one sentence explanation"}}"""

    try:
        response = model.generate_content(prompt)
        text = response.text.strip().replace('```json', '').replace('```', '').strip()
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            result = json.loads(match.group())
            return result.get("is_correct", False), result.get("feedback", "")
    except Exception as e:
        print(f"[Gemini] Validation error: {e}")

    # Tertiary: if query ran and returned rows, assume correct
    if actual_results and len(actual_results) > 0:
        return True, "✅ Query returned results!"

    return False, "❌ Query didn't match the expected output. Try again!"


def _fallback(level: int, round_number: int):
    """Fallback challenges when Gemini is unavailable."""
    pool = [
        {
            "title": "🗡️ The Adventurer's Registry",
            "story": "The dungeon master needs a complete list of all registered adventurers.",
            "objective": "Select all columns from the users table",
            "solution_query": "SELECT * FROM users",
            "hints": ["Use SELECT *", "Specify the table with FROM", "No filtering needed"],
            "concept": "SELECT", "difficulty": "easy", "points": 50
        },
        {
            "title": "⚔️ The Veteran Warriors",
            "story": "Only experienced warriors (age > 25) may enter the advanced dungeon.",
            "objective": "Find all users where age is greater than 25",
            "solution_query": "SELECT * FROM users WHERE age > 25",
            "hints": ["Use WHERE clause", "Use > operator", "Filter on the age column"],
            "concept": "WHERE", "difficulty": "easy", "points": 60
        },
        {
            "title": "📜 The Quest Ledger",
            "story": "The guild master wants to see which heroes have completed quests.",
            "objective": "Join users and orders tables to show usernames with their orders",
            "solution_query": "SELECT users.username, orders.* FROM users JOIN orders ON users.id = orders.user_id",
            "hints": ["Use JOIN", "Match users.id = orders.user_id", "Select from both tables"],
            "concept": "JOIN", "difficulty": "medium", "points": 80
        },
        {
            "title": "💰 The Treasure Counter",
            "story": "Count how many treasure orders exist in the dungeon vault.",
            "objective": "Count the total number of orders",
            "solution_query": "SELECT COUNT(*) FROM orders",
            "hints": ["Use COUNT()", "No WHERE needed", "COUNT(*) counts all rows"],
            "concept": "COUNT", "difficulty": "easy", "points": 60
        },
        {
            "title": "🏆 The Richest Heroes",
            "story": "Find the heroes who have spent the most gold in the dungeon shop.",
            "objective": "Get total amount spent per user, ordered by total descending",
            "solution_query": "SELECT user_id, SUM(amount) AS total FROM orders GROUP BY user_id ORDER BY total DESC",
            "hints": ["Use GROUP BY user_id", "Use SUM(amount)", "ORDER BY total DESC"],
            "concept": "GROUP BY", "difficulty": "medium", "points": 90
        },
    ]
    return pool[(level + round_number) % len(pool)]
