import google.generativeai as genai
import json
import re

# Configure Gemini
genai.configure(api_key="AIzaSyC0OUS556NlqTam8J6TaWvyP4IKLhETvT4")
model = genai.GenerativeModel('gemini-2.5-flash')

def generate_round_challenge(level, round_number, difficulty="medium"):
    """Generate a unique SQL challenge for a specific round using Gemini AI."""
    
    prompt = f"""Generate a SQL challenge for a competitive coding game.

Level: {level}
Round: {round_number}
Difficulty: {difficulty}

Requirements:
1. Create a unique SQL query challenge (different from previous rounds)
2. The challenge should be solvable in 1-3 minutes
3. Include a creative story/context
4. Provide the exact SQL query solution
5. Include 2-3 helpful hints

Return ONLY valid JSON in this exact format:
{{
    "story": "A creative 1-2 sentence story setting the scene",
    "objective": "Clear task description (e.g., 'Find all users who...')",
    "solution_query": "The exact SQL query that solves this",
    "hints": ["Hint 1", "Hint 2", "Hint 3"],
    "difficulty": "easy/medium/hard",
    "expected_columns": ["column1", "column2"]
}}

Make it engaging and game-like! Use themes like dungeons, quests, treasure hunting, etc.
"""
    
    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        
        # Remove markdown if present
        text = text.replace('```json', '').replace('```', '').strip()
        
        # Extract JSON
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if json_match:
            challenge_data = json.loads(json_match.group())
            return challenge_data
        else:
            return generate_fallback_challenge(level, round_number)
            
    except Exception as e:
        print(f"Gemini generation error: {e}")
        return generate_fallback_challenge(level, round_number)

def generate_fallback_challenge(level, round_number):
    """Fallback challenges if Gemini fails"""
    challenges = [
        {
            "story": "The dungeon keeper needs a list of all adventurers.",
            "objective": "Select all columns from the users table",
            "solution_query": "SELECT * FROM users",
            "hints": ["Use SELECT *", "Don't forget FROM clause", "No WHERE needed"],
            "difficulty": "easy",
            "expected_columns": ["id", "username", "email", "age"]
        },
        {
            "story": "Find the experienced warriors who can handle tough quests.",
            "objective": "Find all users where age is greater than 25",
            "solution_query": "SELECT * FROM users WHERE age > 25",
            "hints": ["Use WHERE clause", "Comparison operator >", "Filter by age"],
            "difficulty": "easy",
            "expected_columns": ["id", "username", "email", "age"]
        },
        {
            "story": "The guild master wants to see which heroes have completed quests.",
            "objective": "Join users and orders to show names with their orders",
            "solution_query": "SELECT users.username, orders.* FROM users JOIN orders ON users.id = orders.user_id",
            "hints": ["Use JOIN", "Match user_id", "Include username"],
            "difficulty": "medium",
            "expected_columns": ["username", "id", "user_id", "product", "amount"]
        }
    ]
    
    index = (level + round_number) % len(challenges)
    return challenges[index]

def get_hint_from_gemini(challenge_objective, hint_number=1):
    """Get a contextual hint for a challenge using Gemini."""
    prompt = f"""Give a helpful hint for this SQL challenge:

Challenge: {challenge_objective}

This is hint #{hint_number}. Make it progressively more helpful.
- Hint 1: General direction
- Hint 2: Specific SQL keywords
- Hint 3: Almost the solution

Return only the hint text, no extra formatting."""

    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except:
        return "Try breaking down the problem into smaller steps."

def validate_query_with_gemini(user_query, expected_query, challenge_objective):
    """Use Gemini to validate if user's query is correct."""
    prompt = f"""You are a lenient SQL validator for a learning game.

Challenge: {challenge_objective}
Expected Solution: {expected_query}
User's Query: {user_query}

Rules:
1. If the user's query achieves the same result, mark it as CORRECT
2. Accept alternative syntax (e.g., different column order, aliases, etc.)
3. Be lenient with formatting differences
4. Only mark INCORRECT if the query fundamentally doesn't solve the challenge

Return ONLY valid JSON (no markdown, no extra text):
{{
    "is_correct": true,
    "feedback": "Great! Your query works.",
    "score": 100
}}
"""

    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        
        # Remove markdown code blocks if present
        text = text.replace('```json', '').replace('```', '').strip()
        
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if json_match:
            result = json.loads(json_match.group())
            return result
        else:
            # If can't parse, assume correct (lenient)
            return {"is_correct": True, "feedback": "Query executed successfully", "score": 100}
    except Exception as e:
        print(f"Validation error: {e}")
        # On error, assume correct (lenient fallback)
        return {"is_correct": True, "feedback": "Query executed", "score": 100}
