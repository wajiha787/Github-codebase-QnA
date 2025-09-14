"""
Authentication module for user login and registration
"""

import hashlib
import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

class AuthManager:
    """Handles user authentication and authorization"""
    
    def __init__(self, secret_key: str):
        self.secret_key = secret_key
        self.users = {}  # In production, use a database
    
    def hash_password(self, password: str) -> str:
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify password against hash"""
        return self.hash_password(password) == hashed
    
    def register_user(self, username: str, password: str, email: str) -> Dict[str, Any]:
        """Register a new user"""
        if username in self.users:
            return {"success": False, "message": "Username already exists"}
        
        hashed_password = self.hash_password(password)
        self.users[username] = {
            "password": hashed_password,
            "email": email,
            "created_at": datetime.now().isoformat()
        }
        
        return {"success": True, "message": "User registered successfully"}
    
    def login_user(self, username: str, password: str) -> Dict[str, Any]:
        """Authenticate user login"""
        if username not in self.users:
            return {"success": False, "message": "User not found"}
        
        user = self.users[username]
        if not self.verify_password(password, user["password"]):
            return {"success": False, "message": "Invalid password"}
        
        # Generate JWT token
        token = self.generate_token(username)
        return {
            "success": True, 
            "message": "Login successful",
            "token": token,
            "user": {"username": username, "email": user["email"]}
        }
    
    def generate_token(self, username: str) -> str:
        """Generate JWT token for user"""
        payload = {
            "username": username,
            "exp": datetime.utcnow() + timedelta(hours=24)
        }
        return jwt.encode(payload, self.secret_key, algorithm="HS256")
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify JWT token and return user info"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=["HS256"])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
