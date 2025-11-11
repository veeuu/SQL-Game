import streamlit as st
import sqlite3
import time
import re
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional
import google.generativeai as genai

# Configure Gemini
genai.configure(api_key="AIzaSyC4lOtuBkp5Qen7p3QC9D_ahN1v4OlPQ04")

@dataclass
class Challenge:
    level: int
    title: str
    story: str
    schema: Dict[str, List[str]]
    objective: str
    expected_result: List[Tuple]
    ai_query: str
    hints: List[str]
    concept: str
    difficulty: str

class SQLDungeon:
    def __init__(self):
        self.conn = sqlite3.connect(':memory:', check_same_thread=False)
        self.cursor = self.conn.cursor()
        
    def setup_level_data(self, level: int):
        """Setup database for specific level"""
        self.cursor.executescript("""
            DROP TABLE IF EXISTS customers; 
            DROP TABLE IF EXISTS orders; 
            DROP TABLE IF EXISTS products;
            DROP TABLE IF EXISTS employees;
            DROP TABLE IF EXISTS departments;
            DROP TABLE IF EXISTS sales;
            DROP TABLE IF EXISTS categories;
        """)
        
        if level == 1:
            self.cursor.executescript("""
                CREATE TABLE customers (id INTEGER, name TEXT, city TEXT, age INTEGER);
                INSERT INTO customers VALUES 
                (1, 'Alice', 'NYC', 28), (2, 'Bob', 'LA', 35), 
                (3, 'Charlie', 'NYC', 42), (4, 'Diana', 'Chicago', 31),
                (5, 'Eve', 'NYC', 25), (6, 'Frank', 'LA', 38);
            """)
        elif level == 2:
            self.cursor.executescript("""
                CREATE TABLE customers (id INTEGER, name TEXT);
                CREATE TABLE orders (id INTEGER, customer_id INTEGER, amount REAL, order_date TEXT);
                INSERT INTO customers VALUES (1, 'Alice'), (2, 'Bob'), (3, 'Charlie'), (4, 'Diana');
                INSERT INTO orders VALUES 
                (1, 1, 100, '2024-01-15'), (2, 1, 150, '2024-02-20'), (3, 2, 200, '2024-01-10'), 
                (4, 3, 50, '2024-03-05'), (5, 3, 75, '2024-01-25'), (6, 3, 125, '2024-02-14'),
                (7, 4, 300, '2024-01-30'), (8, 2, 180, '2024-03-12');
            """)
        elif level == 3:
            self.cursor.executescript("""
                CREATE TABLE products (id INTEGER, name TEXT, category TEXT, price REAL);
                CREATE TABLE orders (id INTEGER, product_id INTEGER, quantity INTEGER);
                INSERT INTO products VALUES 
                (1, 'Laptop', 'Electronics', 1000), (2, 'Mouse', 'Electronics', 25),
                (3, 'Desk', 'Furniture', 300), (4, 'Chair', 'Furniture', 150),
                (5, 'Monitor', 'Electronics', 400), (6, 'Keyboard', 'Electronics', 75);
                INSERT INTO orders VALUES 
                (1, 1, 2), (2, 2, 5), (3, 1, 1), (4, 3, 3), (5, 4, 4), (6, 5, 2);
            """)
        elif level == 4:
            self.cursor.executescript("""
                CREATE TABLE sales (id INTEGER, product_id INTEGER, amount REAL, region TEXT);
                CREATE TABLE products (id INTEGER, name TEXT, category TEXT);
                INSERT INTO products VALUES 
                (1, 'Laptop', 'Electronics'), (2, 'Phone', 'Electronics'),
                (3, 'Desk', 'Furniture'), (4, 'Chair', 'Furniture');
                INSERT INTO sales VALUES 
                (1, 1, 5000, 'North'), (2, 1, 3000, 'South'), (3, 2, 2000, 'North'),
                (4, 2, 4000, 'South'), (5, 3, 1500, 'North'), (6, 3, 1200, 'South'),
                (7, 4, 800, 'North'), (8, 4, 900, 'South'), (9, 1, 2500, 'East');
            """)
        elif level == 5:
            self.cursor.executescript("""
                CREATE TABLE employees (id INTEGER, name TEXT, salary REAL, department TEXT);
                INSERT INTO employees VALUES 
                (1, 'Alice', 75000, 'Engineering'), (2, 'Bob', 82000, 'Engineering'),
                (3, 'Charlie', 68000, 'Sales'), (4, 'Diana', 71000, 'Sales'),
                (5, 'Eve', 95000, 'Engineering'), (6, 'Frank', 62000, 'Marketing'),
                (7, 'Grace', 88000, 'Engineering'), (8, 'Henry', 73000, 'Sales');
            """)
        elif level == 6:
            self.cursor.executescript("""
                CREATE TABLE products (id INTEGER, name TEXT, price REAL);
                CREATE TABLE sales (id INTEGER, product_id INTEGER, quantity INTEGER, sale_date TEXT);
                INSERT INTO products VALUES 
                (1, 'Laptop', 1000), (2, 'Mouse', 25), (3, 'Keyboard', 75);
                INSERT INTO sales VALUES 
                (1, 1, 2, '2024-01-15'), (2, 2, 10, '2024-01-16'), (3, 1, 1, '2024-01-17'),
                (4, 3, 5, '2024-01-18'), (5, 2, 8, '2024-01-19'), (6, 1, 3, '2024-01-20');
            """)
        elif level == 7:
            self.cursor.executescript("""
                CREATE TABLE employees (id INTEGER, name TEXT, manager_id INTEGER);
                INSERT INTO employees VALUES 
                (1, 'CEO', NULL), (2, 'VP Engineering', 1), (3, 'VP Sales', 1),
                (4, 'Engineer 1', 2), (5, 'Engineer 2', 2), (6, 'Sales Rep 1', 3),
                (7, 'Sales Rep 2', 3), (8, 'Senior Engineer', 2);
            """)
        elif level == 8:
            self.cursor.executescript("""
                CREATE TABLE customers (id INTEGER, name TEXT, email TEXT);
                CREATE TABLE orders (id INTEGER, customer_id INTEGER, amount REAL, status TEXT);
                CREATE TABLE products (id INTEGER, name TEXT, category TEXT, price REAL);
                CREATE TABLE order_items (order_id INTEGER, product_id INTEGER, quantity INTEGER);
                
                INSERT INTO customers VALUES 
                (1, 'Alice', 'alice@email.com'), (2, 'Bob', 'bob@email.com'), (3, 'Charlie', 'charlie@email.com');
                
                INSERT INTO products VALUES 
                (1, 'Laptop', 'Electronics', 1000), (2, 'Mouse', 'Electronics', 25),
                (3, 'Desk', 'Furniture', 300), (4, 'Chair', 'Furniture', 150);
                
                INSERT INTO orders VALUES 
                (1, 1, 1050, 'completed'), (2, 2, 325, 'completed'), 
                (3, 3, 450, 'pending'), (4, 1, 175, 'completed');
                
                INSERT INTO order_items VALUES 
                (1, 1, 1), (1, 2, 2), (2, 3, 1), (2, 2, 1), 
                (3, 4, 3), (4, 4, 1), (4, 2, 1);
            """)
        self.conn.commit()
    
    def execute_query(self, query: str) -> Tuple[Optional[List[Tuple]], float, str]:
        """Execute query and return results, time, and plan"""
        try:
            start = time.time()
            self.cursor.execute(query)
            results = self.cursor.fetchall()
            exec_time = (time.time() - start) * 1000
            
            # Get query plan
            self.cursor.execute(f"EXPLAIN QUERY PLAN {query}")
            plan = self.cursor.fetchall()
            plan_str = "\n".join([f"• {p[3]}" for p in plan])
            
            return results, exec_time, plan_str
        except Exception as e:
            return None, 0, str(e)

class GeminiAssistant:
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
    
    def analyze_query(self, user_query: str, challenge: Challenge, execution_time: float, plan: str) -> str:
        """Get AI feedback on query optimization"""
        prompt = f"""You are an expert SQL optimization coach. Analyze this query:

Challenge: {challenge.objective}
User's Query: {user_query}
Execution Time: {execution_time:.2f}ms
Query Plan: {plan}

Provide brief, actionable feedback (2-3 sentences) on:
1. What the user did well
2. One specific optimization suggestion
3. Performance impact

Be encouraging and educational. Focus on interview-relevant optimization techniques."""
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except:
            return "AI analysis unavailable. Keep optimizing!"
    
    def get_hint(self, challenge: Challenge, attempt_number: int) -> str:
        """Generate contextual hints"""
        prompt = f"""Generate a helpful SQL optimization hint for this challenge:

Objective: {challenge.objective}
Concept: {challenge.concept}
Difficulty: {challenge.difficulty}
Attempt: {attempt_number}

Provide one specific, actionable hint (1 sentence). Make it progressively more helpful with each attempt."""
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except:
            return challenge.hints[min(attempt_number - 1, len(challenge.hints) - 1)]

def get_challenges() -> List[Challenge]:
    return [
        Challenge(
            level=1,
            title="🚪 The Gate of SELECT",
            story="You awaken in a dimly lit chamber. Ancient SQL runes glow on the walls. The first gate demands precision.",
            schema={"customers": ["id", "name", "city", "age"]},
            objective="Find all customers from NYC, ordered by age descending",
            expected_result=[(3, 'Charlie', 'NYC', 42), (1, 'Alice', 'NYC', 28), (5, 'Eve', 'NYC', 25)],
            ai_query="SELECT * FROM customers WHERE city = 'NYC'",
            hints=[
                "Use ORDER BY to sort results",
                "Avoid SELECT * - only select needed columns"
            ],
            concept="WHERE, ORDER BY",
            difficulty="🟢 Rookie"
        ),
        Challenge(
            level=2,
            title="⚔️ The Joins of Doom",
            story="Two ancient tablets lie before you. Only by uniting them can you unlock the passage.",
            schema={
                "customers": ["id", "name"],
                "orders": ["id", "customer_id", "amount", "order_date"]
            },
            objective="Get total revenue per customer (name and total), ordered by total descending",
            expected_result=[('Diana', 300.0), ('Charlie', 250.0), ('Alice', 250.0), ('Bob', 380.0)],
            ai_query="SELECT name, (SELECT SUM(amount) FROM orders WHERE customer_id = c.id) as total FROM customers c",
            hints=[
                "Subqueries in SELECT are slow - use JOIN instead",
                "Use GROUP BY with aggregate functions"
            ],
            concept="JOINs, GROUP BY, Aggregation",
            difficulty="🟢 Rookie"
        ),
        Challenge(
            level=3,
            title="🌊 Subquery Swamp",
            story="You wade through murky waters of nested queries. Find the efficient path or sink into recursion.",
            schema={
                "products": ["id", "name", "category", "price"],
                "orders": ["id", "product_id", "quantity"]
            },
            objective="Find products that have been ordered (product name only), no duplicates",
            expected_result=[('Chair',), ('Desk',), ('Laptop',), ('Monitor',), ('Mouse',)],
            ai_query="SELECT name FROM products WHERE id IN (SELECT product_id FROM orders)",
            hints=[
                "IN with subquery can be slow on large datasets",
                "Try using EXISTS or INNER JOIN with DISTINCT"
            ],
            concept="IN vs EXISTS vs JOIN",
            difficulty="🟡 Pro"
        ),
        Challenge(
            level=4,
            title="📊 Aggregation Tower",
            story="Numbers swirl around you. Master the art of grouping to climb higher.",
            schema={
                "sales": ["id", "product_id", "amount", "region"],
                "products": ["id", "name", "category"]
            },
            objective="Get total sales by category, only categories with sales > 5000",
            expected_result=[('Electronics', 16500.0), ('Furniture', 4400.0)],
            ai_query="SELECT category, SUM(amount) FROM products p, sales s WHERE p.id = s.product_id GROUP BY category",
            hints=[
                "Use HAVING to filter aggregated results, not WHERE",
                "Explicit JOIN is clearer than comma syntax"
            ],
            concept="GROUP BY, HAVING, Aggregation",
            difficulty="🟡 Pro"
        ),
        Challenge(
            level=5,
            title="🪟 Window Cave",
            story="Reflections of data echo through crystal windows. Rank them without losing context.",
            schema={"employees": ["id", "name", "salary", "department"]},
            objective="Rank employees by salary within each department (name, department, salary, rank)",
            expected_result=[
                ('Eve', 'Engineering', 95000.0, 1), ('Grace', 'Engineering', 88000.0, 2),
                ('Bob', 'Engineering', 82000.0, 3), ('Alice', 'Engineering', 75000.0, 4),
                ('Henry', 'Sales', 73000.0, 1), ('Diana', 'Sales', 71000.0, 2),
                ('Charlie', 'Sales', 68000.0, 3), ('Frank', 'Marketing', 62000.0, 1)
            ],
            ai_query="SELECT name, department, salary, (SELECT COUNT(*) FROM employees e2 WHERE e2.department = e1.department AND e2.salary >= e1.salary) as rank FROM employees e1 ORDER BY department, salary DESC",
            hints=[
                "Window functions are perfect for ranking within groups",
                "Use RANK() or ROW_NUMBER() OVER (PARTITION BY ... ORDER BY ...)"
            ],
            concept="Window Functions, RANK, PARTITION BY",
            difficulty="🟡 Pro"
        ),
        Challenge(
            level=6,
            title="🔍 Index Labyrinth",
            story="Paths branch infinitely. Only indexed routes lead to freedom.",
            schema={
                "products": ["id", "name", "price"],
                "sales": ["id", "product_id", "quantity", "sale_date"]
            },
            objective="Get total revenue per product (name, revenue), sorted by revenue desc",
            expected_result=[('Laptop', 6000.0), ('Keyboard', 375.0), ('Mouse', 450.0)],
            ai_query="SELECT name, SUM(price * quantity) as revenue FROM products, sales WHERE products.id = sales.product_id GROUP BY name ORDER BY revenue DESC",
            hints=[
                "Use explicit INNER JOIN for clarity",
                "Consider which columns would benefit from indexes"
            ],
            concept="JOINs, Aggregation, Index Awareness",
            difficulty="🔴 Optimizer"
        ),
        Challenge(
            level=7,
            title="🔄 Recursive Depths",
            story="The hierarchy spirals downward. Traverse the tree without getting lost.",
            schema={"employees": ["id", "name", "manager_id"]},
            objective="Get all employees and their manager names (employee_name, manager_name)",
            expected_result=[
                ('CEO', None), ('VP Engineering', 'CEO'), ('VP Sales', 'CEO'),
                ('Engineer 1', 'VP Engineering'), ('Engineer 2', 'VP Engineering'),
                ('Sales Rep 1', 'VP Sales'), ('Sales Rep 2', 'VP Sales'),
                ('Senior Engineer', 'VP Engineering')
            ],
            ai_query="SELECT e1.name, (SELECT name FROM employees WHERE id = e1.manager_id) as manager FROM employees e1",
            hints=[
                "Self-join is more efficient than correlated subquery",
                "Use LEFT JOIN to include employees without managers"
            ],
            concept="Self-Join, Hierarchical Data",
            difficulty="🔴 Optimizer"
        ),
        Challenge(
            level=8,
            title="🐉 Final Boss: Query Dragon",
            story="The dragon guards the exit. Only a master of all SQL arts can defeat it. Combine everything you've learned!",
            schema={
                "customers": ["id", "name", "email"],
                "orders": ["id", "customer_id", "amount", "status"],
                "products": ["id", "name", "category", "price"],
                "order_items": ["order_id", "product_id", "quantity"]
            },
            objective="Get customers with completed orders, their total spent, and product count (name, total_spent, product_count), only those who spent > 300",
            expected_result=[('Alice', 1225.0, 4), ('Bob', 325.0, 2)],
            ai_query="SELECT c.name, SUM(o.amount) as total, COUNT(DISTINCT oi.product_id) as products FROM customers c, orders o, order_items oi WHERE c.id = o.customer_id AND o.id = oi.order_id AND o.status = 'completed' GROUP BY c.name",
            hints=[
                "Use explicit JOINs for complex multi-table queries",
                "Apply HAVING to filter aggregated results",
                "Consider query execution order: FROM → WHERE → GROUP BY → HAVING → SELECT"
            ],
            concept="Multi-table JOINs, Complex Aggregation, Filtering",
            difficulty="🔴 Optimizer"
        )
    ]

def init_session_state():
    if 'current_level' not in st.session_state:
        st.session_state.current_level = 1
    if 'energy' not in st.session_state:
        st.session_state.energy = 100
    if 'score' not in st.session_state:
        st.session_state.score = 0
    if 'hints_used' not in st.session_state:
        st.session_state.hints_used = 0
    if 'query_correct' not in st.session_state:
        st.session_state.query_correct = False
    if 'dungeon' not in st.session_state:
        st.session_state.dungeon = SQLDungeon()
    if 'gemini' not in st.session_state:
        st.session_state.gemini = GeminiAssistant()
    if 'attempts' not in st.session_state:
        st.session_state.attempts = 0
    if 'ai_feedback' not in st.session_state:
        st.session_state.ai_feedback = None
    if 'show_schema' not in st.session_state:
        st.session_state.show_schema = True

def main():
    st.set_page_config(
        page_title="SQL Escape: The Optimization Dungeon",
        page_icon="🗝️",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS
    st.markdown("""
        <style>
        .main {background-color: #0e1117;}
        .stButton>button {
            width: 100%;
            border-radius: 8px;
            height: 3em;
            font-weight: 600;
        }
        .metric-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            border-radius: 10px;
            color: white;
            text-align: center;
        }
        .challenge-card {
            background: #1e1e1e;
            padding: 20px;
            border-radius: 10px;
            border-left: 4px solid #667eea;
        }
        .success-box {
            background: #10b981;
            padding: 15px;
            border-radius: 8px;
            color: white;
        }
        .error-box {
            background: #ef4444;
            padding: 15px;
            border-radius: 8px;
            color: white;
        }
        </style>
    """, unsafe_allow_html=True)
    
    init_session_state()
    
    # Header
    st.markdown("<h1 style='text-align: center; color: #667eea;'>🗝️ SQL Escape: The Optimization Dungeon</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-style: italic; color: #888;'>Every query gets you closer to freedom — but only optimized ones can save you.</p>", unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown("### 📊 Adventurer Stats")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Level", f"{st.session_state.current_level}/8")
            st.metric("Score", st.session_state.score)
        with col2:
            st.metric("Energy", f"{st.session_state.energy}/100")
            st.metric("Attempts", st.session_state.attempts)
        
        # Energy bar
        energy_color = "#10b981" if st.session_state.energy > 50 else "#f59e0b" if st.session_state.energy > 20 else "#ef4444"
        st.markdown(f"""
            <div style='background: #333; border-radius: 10px; padding: 3px;'>
                <div style='background: {energy_color}; width: {st.session_state.energy}%; height: 20px; border-radius: 8px; transition: width 0.3s;'></div>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown("### 🎮 Controls")
        
        if st.button("🔄 Reset Game", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
        
        st.markdown("---")
        st.markdown("### 🏆 Achievements")
        achievements = []
        if st.session_state.score >= 100:
            achievements.append("⚡ Query Novice")
        if st.session_state.score >= 300:
            achievements.append("🧙 SQL Wizard")
        if st.session_state.current_level >= 5:
            achievements.append("🗡️ Dungeon Explorer")
        if st.session_state.current_level > 8:
            achievements.append("👑 Dragon Slayer")
        
        for achievement in achievements:
            st.markdown(f"**{achievement}**")
    
    challenges = get_challenges()
    
    # Victory screen
    if st.session_state.current_level > len(challenges):
        st.balloons()
        st.markdown("""
            <div style='text-align: center; padding: 50px;'>
                <h1 style='color: #10b981; font-size: 3em;'>🎉 FREEDOM!</h1>
                <p style='font-size: 1.5em;'>You've escaped the SQL Dungeon!</p>
                <p style='font-size: 2em; color: #667eea;'>Final Score: {}</p>
            </div>
        """.format(st.session_state.score), unsafe_allow_html=True)
        return
    
    challenge = challenges[st.session_state.current_level - 1]
    st.session_state.dungeon.setup_level_data(challenge.level)
    
    # Challenge header
    st.markdown(f"## Level {challenge.level}: {challenge.title}")
    st.markdown(f"**Difficulty:** {challenge.difficulty} | **Concept:** {challenge.concept}")
    
    # Story
    st.info(f"📖 {challenge.story}")
    
    # Main content
    tab1, tab2, tab3 = st.tabs(["📝 Challenge", "🤖 AI Opponent", "📚 Schema"])
    
    with tab1:
        st.markdown(f"### 🎯 Objective")
        st.markdown(f"> {challenge.objective}")
        
        # Query input
        st.markdown("### ✍️ Your Query")
        user_query = st.text_area(
            "Write your SQL query:",
            height=150,
            key="user_query",
            placeholder="SELECT ..."
        )
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            run_btn = st.button("▶️ RUN", type="primary", use_container_width=True)
        with col2:
            hint_btn = st.button("💡 HINT (-20)", use_container_width=True)
        with col3:
            analyze_btn = st.button("🔍 AI ANALYZE", use_container_width=True, disabled=not st.session_state.query_correct)
        with col4:
            next_btn = st.button("🚪 NEXT LEVEL", use_container_width=True, disabled=not st.session_state.query_correct)
        
        if run_btn and user_query.strip():
            st.session_state.attempts += 1
            results, exec_time, plan = st.session_state.dungeon.execute_query(user_query)
            
            if results is None:
                st.markdown(f"<div class='error-box'>❌ Query Error: {plan}</div>", unsafe_allow_html=True)
                st.session_state.energy = max(0, st.session_state.energy - 10)
            else:
                if sorted(results) == sorted(challenge.expected_result):
                    st.markdown("<div class='success-box'>✅ Correct Output! Well done!</div>", unsafe_allow_html=True)
                    st.session_state.query_correct = True
                    if st.session_state.attempts == 1:
                        st.session_state.score += 100
                        st.success("🎉 First try bonus: +100 points!")
                    else:
                        st.session_state.score += 50
                    
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.metric("⚡ Execution Time", f"{exec_time:.3f}ms")
                    with col_b:
                        st.metric("📊 Rows Returned", len(results))
                    
                    with st.expander("📊 Query Plan"):
                        st.text(plan)
                    
                    with st.expander("📋 Results"):
                        st.dataframe(results, use_container_width=True)
                else:
                    st.markdown("<div class='error-box'>❌ Incorrect Output</div>", unsafe_allow_html=True)
                    col_x, col_y = st.columns(2)
                    with col_x:
                        st.write("**Expected:**")
                        st.dataframe(challenge.expected_result)
                    with col_y:
                        st.write("**Got:**")
                        st.dataframe(results)
                    st.session_state.energy = max(0, st.session_state.energy - 10)
        
        if hint_btn:
            hint = st.session_state.gemini.get_hint(challenge, st.session_state.attempts)
            st.warning(f"💡 {hint}")
            st.session_state.score = max(0, st.session_state.score - 20)
        
        if analyze_btn and st.session_state.query_correct:
            with st.spinner("🤖 AI analyzing your query..."):
                results, exec_time, plan = st.session_state.dungeon.execute_query(user_query)
                feedback = st.session_state.gemini.analyze_query(user_query, challenge, exec_time, plan)
                st.session_state.ai_feedback = feedback
                st.info(f"🤖 **AI Feedback:**\n\n{feedback}")
        
        if next_btn:
            st.session_state.current_level += 1
            st.session_state.energy = min(100, st.session_state.energy + 20)
            st.session_state.hints_used = 0
            st.session_state.query_correct = False
            st.session_state.attempts = 0
            st.session_state.ai_feedback = None
            st.rerun()
    
    with tab2:
        st.markdown("### 🤖 AI's Inefficient Query")
        st.code(challenge.ai_query, language="sql")
        
        if st.button("⚡ Analyze AI Performance"):
            results, exec_time, plan = st.session_state.dungeon.execute_query(challenge.ai_query)
            st.metric("AI Execution Time", f"{exec_time:.3f}ms")
            st.markdown("**Query Plan:**")
            st.text(plan)
            st.info("💡 Your goal is to write a query that's faster and more efficient than this!")
    
    with tab3:
        st.markdown("### 📚 Database Schema")
        for table, columns in challenge.schema.items():
            st.markdown(f"**`{table}`**")
            st.code(", ".join(columns))
            
            if st.checkbox(f"Show sample data from {table}", key=f"sample_{table}"):
                st.session_state.dungeon.cursor.execute(f"SELECT * FROM {table} LIMIT 5")
                data = st.session_state.dungeon.cursor.fetchall()
                st.dataframe(data, use_container_width=True)
    
    # Energy warning
    if st.session_state.energy <= 20:
        st.warning("⚠️ Low energy! Be careful with your queries!")
    
    if st.session_state.energy == 0:
        st.error("💀 Room collapsed! Restarting level...")
        time.sleep(2)
        st.session_state.energy = 100
        st.session_state.attempts = 0
        st.rerun()

if __name__ == "__main__":
    main()
