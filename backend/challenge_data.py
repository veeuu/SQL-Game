# Challenge Data Setup and Validation
import sqlite3

def setup_challenge_data(conn, level):
    """Setup test data for each challenge level"""
    c = conn.cursor()
    
    # Clear existing tables
    c.execute("DROP TABLE IF EXISTS users")
    c.execute("DROP TABLE IF EXISTS orders")
    c.execute("DROP TABLE IF EXISTS products")
    c.execute("DROP TABLE IF EXISTS employees")
    c.execute("DROP TABLE IF EXISTS departments")
    
    if level <= 10:  # Beginner levels - users table
        c.execute("""CREATE TABLE users (
            id INTEGER PRIMARY KEY,
            name TEXT,
            email TEXT,
            city TEXT,
            age INTEGER
        )""")
        c.execute("""INSERT INTO users VALUES
            (1, 'Alice Johnson', 'alice@email.com', 'NYC', 28),
            (2, 'Bob Smith', 'bob@email.com', 'LA', 35),
            (3, 'Charlie Brown', 'charlie@email.com', 'NYC', 42),
            (4, 'Diana Prince', 'diana@email.com', 'Chicago', 31),
            (5, 'Eve Adams', 'eve@email.com', 'NYC', 25),
            (6, 'Frank Miller', 'frank@email.com', 'LA', 38)
        """)
    
    if level >= 11:  # Intermediate+ levels - users and orders
        c.execute("""CREATE TABLE users (
            id INTEGER PRIMARY KEY,
            name TEXT,
            email TEXT
        )""")
        c.execute("""INSERT INTO users VALUES
            (1, 'Alice Johnson', 'alice@email.com'),
            (2, 'Bob Smith', 'bob@email.com'),
            (3, 'Charlie Brown', 'charlie@email.com'),
            (4, 'Diana Prince', 'diana@email.com')
        """)
        
        c.execute("""CREATE TABLE orders (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            amount REAL,
            order_date TEXT,
            status TEXT
        )""")
        c.execute("""INSERT INTO orders VALUES
            (1, 1, 150.00, '2024-01-15', 'completed'),
            (2, 1, 200.00, '2024-02-20', 'completed'),
            (3, 2, 75.50, '2024-01-10', 'completed'),
            (4, 3, 300.00, '2024-03-05', 'completed'),
            (5, 3, 125.75, '2024-01-25', 'completed'),
            (6, 3, 89.99, '2024-02-14', 'completed'),
            (7, 4, 450.00, '2024-01-30', 'completed'),
            (8, 2, 180.25, '2024-03-12', 'pending')
        """)
    
    if level >= 17:  # Multi-table joins
        c.execute("""CREATE TABLE products (
            id INTEGER PRIMARY KEY,
            name TEXT,
            category TEXT,
            price REAL
        )""")
        c.execute("""INSERT INTO products VALUES
            (1, 'Laptop', 'Electronics', 1000.00),
            (2, 'Mouse', 'Electronics', 25.00),
            (3, 'Desk', 'Furniture', 300.00),
            (4, 'Chair', 'Furniture', 150.00),
            (5, 'Monitor', 'Electronics', 400.00)
        """)
    
    if level >= 24:  # Self-join levels
        c.execute("""CREATE TABLE employees (
            id INTEGER PRIMARY KEY,
            name TEXT,
            manager_id INTEGER,
            salary REAL,
            department TEXT
        )""")
        c.execute("""INSERT INTO employees VALUES
            (1, 'CEO', NULL, 200000, 'Executive'),
            (2, 'VP Engineering', 1, 150000, 'Engineering'),
            (3, 'VP Sales', 1, 140000, 'Sales'),
            (4, 'Engineer 1', 2, 90000, 'Engineering'),
            (5, 'Engineer 2', 2, 85000, 'Engineering'),
            (6, 'Sales Rep 1', 3, 70000, 'Sales'),
            (7, 'Sales Rep 2', 3, 75000, 'Sales')
        """)
    
    conn.commit()

def get_expected_result(level):
    """Return expected results for each level"""
    expected_results = {
        1: [
            (1, 'Alice Johnson', 'alice@email.com', 'NYC', 28),
            (2, 'Bob Smith', 'bob@email.com', 'LA', 35),
            (3, 'Charlie Brown', 'charlie@email.com', 'NYC', 42),
            (4, 'Diana Prince', 'diana@email.com', 'Chicago', 31),
            (5, 'Eve Adams', 'eve@email.com', 'NYC', 25),
            (6, 'Frank Miller', 'frank@email.com', 'LA', 38)
        ],
        2: [
            (1, 'Alice Johnson', 'alice@email.com', 'NYC', 28),
            (2, 'Bob Smith', 'bob@email.com', 'LA', 35),
            (3, 'Charlie Brown', 'charlie@email.com', 'NYC', 42),
            (4, 'Diana Prince', 'diana@email.com', 'Chicago', 31),
            (6, 'Frank Miller', 'frank@email.com', 'LA', 38)
        ],
        3: [
            ('Alice Johnson',),
            ('Bob Smith',),
            ('Charlie Brown',),
            ('Diana Prince',),
            ('Eve Adams',),
            ('Frank Miller',)
        ],
        19: [
            (450.0, 75.5)  # MAX, MIN - order matters: MAX first, then MIN
        ]
    }
    return expected_results.get(level, [])
