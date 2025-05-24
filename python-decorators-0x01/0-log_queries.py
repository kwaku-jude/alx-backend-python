#!/usr/bin/env python3
import sqlite3
import functools
from datetime import datetime

# Decorator to log SQL queries


def log_queries():
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Extract the SQL query from positional or keyword arguments
            query = args[0] if args else kwargs.get('query', '')
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print(f"[{timestamp}] [LOG] Executing SQL query: {query}")
            return func(*args, **kwargs)
        return wrapper
    return decorator


@log_queries()
def fetch_all_users(query):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    return results

# Create the database and user table if it doesn't exist


def initialize_database():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE
        )
    ''')
    conn.commit()
    conn.close()


# Initialize the database
initialize_database()

# Fetch users while logging the query
users = fetch_all_users(query="SELECT * FROM users")
print(users)


@log_queries()
def insert_user(query, params):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute(query, params)
    conn.commit()
    conn.close()


# # Insert sample users into the database
# insert_user(query="INSERT INTO users (name, email) VALUES (?, ?)",
#             params=("John Doe", "john.doe@example.com"))
# insert_user(query="INSERT INTO users (name, email) VALUES (?, ?)",
#             params=("Jane Smith", "jane.smith@example.com"))

# Fetch users again to verify insertion
users = fetch_all_users(query="SELECT * FROM users")
print(users)
