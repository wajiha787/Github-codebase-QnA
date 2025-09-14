"""
Database connection and management module
"""

import sqlite3
import json
from typing import List, Dict, Any, Optional
from contextlib import contextmanager

class DatabaseManager:
    """Manages database connections and operations"""
    
    def __init__(self, db_path: str = "app.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database with required tables"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Create users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1
                )
            """)
            
            # Create posts table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS posts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            """)
            
            conn.commit()
    
    @contextmanager
    def get_connection(self):
        """Get database connection with proper cleanup"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable dict-like access
        try:
            yield conn
        finally:
            conn.close()
    
    def execute_query(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """Execute SELECT query and return results"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
    
    def execute_update(self, query: str, params: tuple = ()) -> int:
        """Execute INSERT/UPDATE/DELETE query and return affected rows"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor.rowcount
    
    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Get user by username"""
        results = self.execute_query(
            "SELECT * FROM users WHERE username = ? AND is_active = 1",
            (username,)
        )
        return results[0] if results else None
    
    def create_user(self, username: str, email: str, password_hash: str) -> bool:
        """Create new user"""
        try:
            self.execute_update(
                "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
                (username, email, password_hash)
            )
            return True
        except sqlite3.IntegrityError:
            return False
    
    def get_user_posts(self, user_id: int) -> List[Dict[str, Any]]:
        """Get all posts by user"""
        return self.execute_query(
            "SELECT * FROM posts WHERE user_id = ? ORDER BY created_at DESC",
            (user_id,)
        )
    
    def create_post(self, user_id: int, title: str, content: str) -> bool:
        """Create new post"""
        try:
            self.execute_update(
                "INSERT INTO posts (user_id, title, content) VALUES (?, ?, ?)",
                (user_id, title, content)
            )
            return True
        except Exception:
            return False
