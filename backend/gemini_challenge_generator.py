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

EXACT table schemas (use ONLY these column names, no others):

challenge.customers  → customers(id, name, email, city, age, joined_date)
challenge.orders     → orders(id, customer_id, product, category, amount, quantity, order_date)
challenge.employees  → employees(id, name, department, salary, manager_id, hire_date)
challenge.products   → products(id, name, category, price, stock)

Rules:
- Use ONLY the column names listed above — do not invent column names
- Use ONLY the table names listed above
- Test the concept: {cfg['concept']}
- Fun dungeon/quest/adventure theme
- Valid PostgreSQL query using the exact schema above
- Solvable in under 2 minutes
- Round {round_number} must feel different from other rounds

Return ONLY this JSON (no markdown):
{{
  "title": "Short catchy title with emoji",
  "story": "1-2 sentence dungeon-themed story",
  "objective": "Exact task description using the real column names",
  "solution_query": "The correct PostgreSQL query using exact column names from schema",
  "hints": [
    "Hint 1: general direction",
    "Hint 2: specific keyword or column name",
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
    Validate a player's SQL query by logic/syntax using Gemini.
    We do NOT compare result rows — the DB may be empty so that's irrelevant.
    Returns: (is_correct: bool, feedback: str)
    """
    # If query threw an error (actual_results is None), it's wrong
    if actual_results is None:
        return False, "❌ Your query has a syntax error."

    # Gemini checks structure and logic, not result data
    prompt = f"""You are a SQL teacher validating a student's query.

Objective: {objective}
Reference solution: {solution_query}
Student's query: {user_query}

Available schema:
- customers(id, name, email, city, age, joined_date)
- orders(id, customer_id, product, category, amount, quantity, order_date)
- employees(id, name, department, salary, manager_id, hire_date)
- products(id, name, category, price, stock)

Important rules:
- Validate the LOGIC and STRUCTURE only — NOT the result rows
- The database may be empty so empty results are fine
- Check: correct table(s), correct columns from the schema above, correct WHERE/JOIN/GROUP BY logic
- Accept any valid SQL that correctly addresses the objective
- Minor differences (aliases, column order, extra whitespace) are acceptable

Return ONLY JSON (no markdown):
{{"is_correct": true/false, "feedback": "one short sentence"}}"""

    try:
        response = model.generate_content(prompt)
        text = response.text.strip().replace('```json', '').replace('```', '').strip()
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            result = json.loads(match.group())
            return result.get("is_correct", False), result.get("feedback", "")
    except Exception as e:
        print(f"[Gemini] Validation error: {e}")

    # Fallback: query ran without error → assume correct
    return True, "✅ Query executed successfully!"


def _fallback(level: int, round_number: int):
    """Fallback challenges when Gemini is unavailable."""
    pool = [
        {
            "title": "🗡️ The Adventurer's Registry",
            "story": "The dungeon master needs a complete list of all customers.",
            "objective": "Select all columns from the customers table",
            "solution_query": "SELECT * FROM customers",
            "hints": ["Use SELECT *", "Specify the table with FROM", "No filtering needed"],
            "concept": "SELECT", "difficulty": "easy", "points": 50
        },
        {
            "title": "⚔️ The Veteran Warriors",
            "story": "Only experienced warriors (age > 30) may enter the advanced dungeon.",
            "objective": "Find all customers where age is greater than 30",
            "solution_query": "SELECT * FROM customers WHERE age > 30",
            "hints": ["Use WHERE clause", "Use > operator", "Filter on the age column"],
            "concept": "WHERE", "difficulty": "easy", "points": 60
        },
        {
            "title": "📜 The Quest Ledger",
            "story": "The guild master wants to see which heroes have placed orders.",
            "objective": "Join customers and orders to show customer names with their orders",
            "solution_query": "SELECT customers.name, orders.* FROM customers JOIN orders ON customers.id = orders.customer_id",
            "hints": ["Use JOIN", "Match customers.id = orders.customer_id", "Select from both tables"],
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
            "objective": "Get total amount spent per customer, ordered by total descending",
            "solution_query": "SELECT customer_id, SUM(amount) AS total FROM orders GROUP BY customer_id ORDER BY total DESC",
            "hints": ["Use GROUP BY customer_id", "Use SUM(amount)", "ORDER BY total DESC"],
            "concept": "GROUP BY", "difficulty": "medium", "points": 90
        },
    ]
    return pool[(level + round_number) % len(pool)]
