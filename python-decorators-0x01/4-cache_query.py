#!/usr/bin/env python3
import time
import sqlite3
import functools

query_cache = {}

# Decorator to handle DB connection


def with_db_connection(func):
    """Decorator to open and close a SQLite DB connection"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        conn = sqlite3.connect('users.db')
        try:
            return func(conn, *args, **kwargs)
        finally:
            conn.close()
    return wrapper

# Decorator to cache results of SQL queries


def cache_query(func):
    """Decorator to cache SQL query results using the query string as key"""
    @functools.wraps(func)
    def wrapper(conn, query, *args, **kwargs):
        if query in query_cache:
            print("[INFO] Returning cached result")
            return query_cache[query]
        print("[INFO] Executing and caching query")
        result = func(conn, query, *args, **kwargs)
        query_cache[query] = result
        return result
    return wrapper


@with_db_connection
@cache_query
def fetch_users_with_cache(conn, query):
    cursor = conn.cursor()
    cursor.execute(query)
    return cursor.fetchall()


# First call will cache the result
users = fetch_users_with_cache(query="SELECT * FROM users")

# Second call will use the cached result
users_again = fetch_users_with_cache(query="SELECT * FROM users")
