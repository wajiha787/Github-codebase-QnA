"""
REST API endpoints for the application
"""

from flask import Flask, request, jsonify
from functools import wraps
import os
from auth import AuthManager
from database import DatabaseManager

app = Flask(__name__)

# Initialize managers
auth_manager = AuthManager(os.getenv("SECRET_KEY", "your-secret-key"))
db_manager = DatabaseManager()

def require_auth(f):
    """Decorator to require authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({"error": "No token provided"}), 401
        
        if token.startswith('Bearer '):
            token = token[7:]
        
        user_info = auth_manager.verify_token(token)
        if not user_info:
            return jsonify({"error": "Invalid token"}), 401
        
        request.current_user = user_info
        return f(*args, **kwargs)
    return decorated_function

@app.route('/api/register', methods=['POST'])
def register():
    """Register a new user"""
    data = request.get_json()
    
    if not data or not all(k in data for k in ('username', 'password', 'email')):
        return jsonify({"error": "Missing required fields"}), 400
    
    result = auth_manager.register_user(
        data['username'],
        data['password'],
        data['email']
    )
    
    if result['success']:
        # Also save to database
        db_manager.create_user(
            data['username'],
            data['email'],
            auth_manager.hash_password(data['password'])
        )
        return jsonify(result), 201
    else:
        return jsonify(result), 400

@app.route('/api/login', methods=['POST'])
def login():
    """Authenticate user and return token"""
    data = request.get_json()
    
    if not data or not all(k in data for k in ('username', 'password')):
        return jsonify({"error": "Missing username or password"}), 400
    
    result = auth_manager.login_user(data['username'], data['password'])
    
    if result['success']:
        return jsonify(result), 200
    else:
        return jsonify(result), 401

@app.route('/api/posts', methods=['GET'])
@require_auth
def get_posts():
    """Get all posts for the authenticated user"""
    user_id = request.current_user['username']  # In real app, use user ID
    posts = db_manager.get_user_posts(user_id)
    return jsonify({"posts": posts}), 200

@app.route('/api/posts', methods=['POST'])
@require_auth
def create_post():
    """Create a new post"""
    data = request.get_json()
    
    if not data or not all(k in data for k in ('title', 'content')):
        return jsonify({"error": "Missing title or content"}), 400
    
    user_id = request.current_user['username']  # In real app, use user ID
    success = db_manager.create_post(
        user_id,
        data['title'],
        data['content']
    )
    
    if success:
        return jsonify({"message": "Post created successfully"}), 201
    else:
        return jsonify({"error": "Failed to create post"}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "message": "API is running"}), 200

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
