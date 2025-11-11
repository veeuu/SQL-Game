# SQL Challenge Definitions - 30 Levels
# Primary focus: SQL Practice with progressive difficulty

CHALLENGES = [
    # BEGINNER LEVELS (1-10) - Basic SQL Fundamentals
    {
        "level": 1,
        "title": "🎯 SELECT Basics",
        "difficulty": "Beginner",
        "concept": "SELECT, Basic Filtering",
        "story": "Welcome, adventurer! Your first task is to retrieve data from the ancient database.",
        "objective": "Select all columns from the 'users' table",
        "points": 50,
        "coins": 10,
        "hints": [
            "Use SELECT * to get all columns",
            "Don't forget FROM clause"
        ]
    },
    {
        "level": 2,
        "title": "🔍 WHERE Clause",
        "difficulty": "Beginner",
        "concept": "WHERE, Filtering",
        "story": "Not all data is useful. Learn to filter what you need.",
        "objective": "Find all users where age is greater than 25",
        "points": 50,
        "coins": 10,
        "hints": [
            "Use WHERE clause after FROM",
            "Use > operator for greater than"
        ]
    },
    {
        "level": 3,
        "title": "📊 ORDER BY",
        "difficulty": "Beginner",
        "concept": "Sorting Results",
        "story": "Chaos must be organized. Sort the data to find patterns.",
        "objective": "Get all users ordered by name alphabetically",
        "points": 50,
        "coins": 10,
        "hints": [
            "Use ORDER BY at the end",
            "ASC for ascending, DESC for descending"
        ]
    },
    {
        "level": 4,
        "title": "🎨 SELECT Specific Columns",
        "difficulty": "Beginner",
        "concept": "Column Selection",
        "story": "Efficiency is key. Only retrieve what you need.",
        "objective": "Select only name and email from users table",
        "points": 50,
        "coins": 10,
        "hints": [
            "List column names separated by commas",
            "Avoid SELECT * for better performance"
        ]
    },
    {
        "level": 5,
        "title": "🔢 LIMIT Results",
        "difficulty": "Beginner",
        "concept": "LIMIT Clause",
        "story": "Sometimes less is more. Limit your results wisely.",
        "objective": "Get the first 5 users from the table",
        "points": 50,
        "coins": 10,
        "hints": [
            "Use LIMIT at the end of query",
            "LIMIT 5 returns first 5 rows"
        ]
    },
    {
        "level": 6,
        "title": "🎭 DISTINCT Values",
        "difficulty": "Beginner",
        "concept": "Removing Duplicates",
        "story": "Duplicates cloud the truth. Find unique values.",
        "objective": "Get all unique cities from users table",
        "points": 60,
        "coins": 12,
        "hints": [
            "Use DISTINCT keyword after SELECT",
            "DISTINCT removes duplicate rows"
        ]
    },
    {
        "level": 7,
        "title": "🔗 AND/OR Operators",
        "difficulty": "Beginner",
        "concept": "Logical Operators",
        "story": "Combine conditions to narrow your search.",
        "objective": "Find users where age > 25 AND city = 'NYC'",
        "points": 60,
        "coins": 12,
        "hints": [
            "Use AND to combine conditions",
            "Both conditions must be true"
        ]
    },
    {
        "level": 8,
        "title": "📝 LIKE Pattern Matching",
        "difficulty": "Beginner",
        "concept": "Pattern Matching",
        "story": "Search for patterns in text data.",
        "objective": "Find all users whose name starts with 'A'",
        "points": 60,
        "coins": 12,
        "hints": [
            "Use LIKE with % wildcard",
            "'A%' matches names starting with A"
        ]
    },
    {
        "level": 9,
        "title": "🎯 IN Operator",
        "difficulty": "Beginner",
        "concept": "IN Clause",
        "story": "Check if values exist in a list.",
        "objective": "Find users in cities: NYC, LA, Chicago",
        "points": 60,
        "coins": 12,
        "hints": [
            "Use IN with list of values",
            "IN ('NYC', 'LA', 'Chicago')"
        ]
    },
    {
        "level": 10,
        "title": "🔄 BETWEEN Operator",
        "difficulty": "Beginner",
        "concept": "Range Queries",
        "story": "Find values within a range.",
        "objective": "Get users with age between 25 and 35",
        "points": 70,
        "coins": 15,
        "hints": [
            "Use BETWEEN for ranges",
            "BETWEEN is inclusive"
        ]
    },
    # INTERMEDIATE LEVELS (11-20) - JOINs and Aggregations
    {
        "level": 11,
        "title": "🔗 INNER JOIN Basics",
        "difficulty": "Intermediate",
        "concept": "INNER JOIN",
        "story": "Connect tables to reveal hidden relationships.",
        "objective": "Join users and orders tables on user_id",
        "points": 80,
        "coins": 20,
        "hints": [
            "Use INNER JOIN to combine tables",
            "Specify ON condition for matching"
        ]
    },
    {
        "level": 12,
        "title": "📊 COUNT Function",
        "difficulty": "Intermediate",
        "concept": "Aggregate Functions",
        "story": "Count the treasures in your database.",
        "objective": "Count total number of orders",
        "points": 80,
        "coins": 20,
        "hints": [
            "Use COUNT(*) or COUNT(column)",
            "Aggregate functions work on groups"
        ]
    },
    {
        "level": 13,
        "title": "💰 SUM and AVG",
        "difficulty": "Intermediate",
        "concept": "Aggregate Functions",
        "story": "Calculate totals and averages.",
        "objective": "Get total and average order amount",
        "points": 80,
        "coins": 20,
        "hints": [
            "Use SUM() for totals",
            "Use AVG() for averages"
        ]
    },
    {
        "level": 14,
        "title": "📦 GROUP BY",
        "difficulty": "Intermediate",
        "concept": "Grouping Data",
        "story": "Group similar data together for analysis.",
        "objective": "Count orders per user",
        "points": 90,
        "coins": 25,
        "hints": [
            "Use GROUP BY to group rows",
            "Combine with COUNT for aggregation"
        ]
    },
    {
        "level": 15,
        "title": "🎯 HAVING Clause",
        "difficulty": "Intermediate",
        "concept": "Filtering Groups",
        "story": "Filter grouped results with precision.",
        "objective": "Find users with more than 3 orders",
        "points": 90,
        "coins": 25,
        "hints": [
            "HAVING filters after GROUP BY",
            "WHERE filters before grouping"
        ]
    },
    {
        "level": 16,
        "title": "🔄 LEFT JOIN",
        "difficulty": "Intermediate",
        "concept": "Outer Joins",
        "story": "Include all records from the left table.",
        "objective": "Get all users and their orders (including users with no orders)",
        "points": 90,
        "coins": 25,
        "hints": [
            "LEFT JOIN keeps all left table rows",
            "NULL for unmatched right table rows"
        ]
    },
    {
        "level": 17,
        "title": "🎨 Multiple JOINs",
        "difficulty": "Intermediate",
        "concept": "Multi-table Joins",
        "story": "Connect multiple tables in one query.",
        "objective": "Join users, orders, and products tables",
        "points": 100,
        "coins": 30,
        "hints": [
            "Chain multiple JOIN clauses",
            "Each JOIN needs its own ON condition"
        ]
    },
    {
        "level": 18,
        "title": "🔍 Subqueries in WHERE",
        "difficulty": "Intermediate",
        "concept": "Subqueries",
        "story": "Query within a query for complex filtering.",
        "objective": "Find users who have placed orders above average",
        "points": 100,
        "coins": 30,
        "hints": [
            "Use subquery in WHERE clause",
            "Subquery returns value for comparison"
        ]
    },
    {
        "level": 19,
        "title": "📊 MAX and MIN",
        "difficulty": "Intermediate",
        "concept": "Aggregate Functions",
        "story": "Find the extremes in your data.",
        "objective": "Get the highest and lowest order amounts",
        "points": 100,
        "coins": 30,
        "hints": [
            "Use MAX() for maximum value",
            "Use MIN() for minimum value"
        ]
    },
    {
        "level": 20,
        "title": "🎯 CASE Statements",
        "difficulty": "Intermediate",
        "concept": "Conditional Logic",
        "story": "Add conditional logic to your queries.",
        "objective": "Categorize users by age groups",
        "points": 110,
        "coins": 35,
        "hints": [
            "CASE WHEN condition THEN result",
            "Use ELSE for default case"
        ]
    },
    # ADVANCED LEVELS (21-30) - Complex Queries and Optimization
    {
        "level": 21,
        "title": "🪟 ROW_NUMBER Window Function",
        "difficulty": "Advanced",
        "concept": "Window Functions",
        "story": "Rank rows without grouping.",
        "objective": "Assign row numbers to users ordered by age",
        "points": 120,
        "coins": 40,
        "hints": [
            "Use ROW_NUMBER() OVER (ORDER BY ...)",
            "Window functions don't reduce rows"
        ]
    },
    {
        "level": 22,
        "title": "🏆 RANK and DENSE_RANK",
        "difficulty": "Advanced",
        "concept": "Ranking Functions",
        "story": "Rank data with tie handling.",
        "objective": "Rank users by total order amount",
        "points": 120,
        "coins": 40,
        "hints": [
            "RANK() handles ties with gaps",
            "DENSE_RANK() has no gaps"
        ]
    },
    {
        "level": 23,
        "title": "📊 PARTITION BY",
        "difficulty": "Advanced",
        "concept": "Window Partitioning",
        "story": "Rank within groups using partitions.",
        "objective": "Rank orders within each user",
        "points": 130,
        "coins": 45,
        "hints": [
            "PARTITION BY divides into groups",
            "Ranking resets for each partition"
        ]
    },
    {
        "level": 24,
        "title": "🔄 Self JOIN",
        "difficulty": "Advanced",
        "concept": "Self Joins",
        "story": "Join a table to itself for hierarchical data.",
        "objective": "Find employees and their managers",
        "points": 130,
        "coins": 45,
        "hints": [
            "Use table aliases for self joins",
            "Join on manager_id = id"
        ]
    },
    {
        "level": 25,
        "title": "🎯 EXISTS vs IN",
        "difficulty": "Advanced",
        "concept": "Query Optimization",
        "story": "Choose the right operator for performance.",
        "objective": "Find users who have orders (using EXISTS)",
        "points": 140,
        "coins": 50,
        "hints": [
            "EXISTS is faster for large datasets",
            "EXISTS stops at first match"
        ]
    },
    {
        "level": 26,
        "title": "📦 Common Table Expressions (CTE)",
        "difficulty": "Advanced",
        "concept": "CTEs",
        "story": "Create temporary named result sets.",
        "objective": "Use WITH clause to simplify complex query",
        "points": 140,
        "coins": 50,
        "hints": [
            "WITH cte_name AS (query)",
            "CTEs improve readability"
        ]
    },
    {
        "level": 27,
        "title": "🔄 Recursive CTEs",
        "difficulty": "Advanced",
        "concept": "Recursive Queries",
        "story": "Traverse hierarchical data recursively.",
        "objective": "Get all employees in a management chain",
        "points": 150,
        "coins": 55,
        "hints": [
            "Use WITH RECURSIVE for hierarchies",
            "Base case + recursive case"
        ]
    },
    {
        "level": 28,
        "title": "🎯 Query Optimization",
        "difficulty": "Advanced",
        "concept": "Index Usage",
        "story": "Optimize slow queries with proper indexing.",
        "objective": "Rewrite query to use indexes efficiently",
        "points": 150,
        "coins": 55,
        "hints": [
            "Avoid SELECT *",
            "Use indexed columns in WHERE"
        ]
    },
    {
        "level": 29,
        "title": "📊 Complex Aggregations",
        "difficulty": "Advanced",
        "concept": "Advanced Aggregation",
        "story": "Master complex multi-level aggregations.",
        "objective": "Calculate running totals and moving averages",
        "points": 160,
        "coins": 60,
        "hints": [
            "Use window functions for running totals",
            "ROWS BETWEEN for moving averages"
        ]
    },
    {
        "level": 30,
        "title": "🐉 Final Challenge",
        "difficulty": "Expert",
        "concept": "All Concepts Combined",
        "story": "The ultimate SQL challenge. Prove your mastery!",
        "objective": "Solve complex real-world scenario with all techniques",
        "points": 200,
        "coins": 100,
        "hints": [
            "Combine CTEs, window functions, and joins",
            "Optimize for performance"
        ]
    }
]
