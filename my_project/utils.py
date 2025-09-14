"""
Utility functions and helpers
"""

import re
import hashlib
from datetime import datetime
from typing import List, Dict, Any, Optional
import json

def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password: str) -> Dict[str, Any]:
    """Validate password strength"""
    errors = []
    
    if len(password) < 8:
        errors.append("Password must be at least 8 characters long")
    
    if not re.search(r'[A-Z]', password):
        errors.append("Password must contain at least one uppercase letter")
    
    if not re.search(r'[a-z]', password):
        errors.append("Password must contain at least one lowercase letter")
    
    if not re.search(r'\d', password):
        errors.append("Password must contain at least one number")
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        errors.append("Password must contain at least one special character")
    
    return {
        "is_valid": len(errors) == 0,
        "errors": errors
    }

def sanitize_input(text: str) -> str:
    """Sanitize user input to prevent XSS"""
    # Remove potentially dangerous characters
    text = re.sub(r'<script.*?</script>', '', text, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r'<.*?>', '', text)  # Remove HTML tags
    text = text.strip()
    return text

def generate_api_key() -> str:
    """Generate a random API key"""
    timestamp = str(datetime.now().timestamp())
    random_string = hashlib.md5(timestamp.encode()).hexdigest()
    return f"api_{random_string}"

def format_timestamp(timestamp: str) -> str:
    """Format timestamp for display"""
    try:
        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except:
        return timestamp

def paginate_results(items: List[Any], page: int = 1, per_page: int = 10) -> Dict[str, Any]:
    """Paginate a list of items"""
    total_items = len(items)
    total_pages = (total_items + per_page - 1) // per_page
    
    start_index = (page - 1) * per_page
    end_index = start_index + per_page
    
    paginated_items = items[start_index:end_index]
    
    return {
        "items": paginated_items,
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total_items": total_items,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1
        }
    }

def log_activity(user_id: str, action: str, details: Dict[str, Any] = None):
    """Log user activity"""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "user_id": user_id,
        "action": action,
        "details": details or {}
    }
    
    # In production, save to database or log file
    print(f"Activity Log: {json.dumps(log_entry)}")

def calculate_file_hash(file_path: str) -> str:
    """Calculate SHA-256 hash of a file"""
    sha256_hash = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()
    except FileNotFoundError:
        return ""

def is_safe_filename(filename: str) -> bool:
    """Check if filename is safe (no path traversal)"""
    # Remove any path components
    filename = filename.split('/')[-1].split('\\')[-1]
    
    # Check for dangerous patterns
    dangerous_patterns = ['..', '/', '\\', ':', '*', '?', '"', '<', '>', '|']
    
    for pattern in dangerous_patterns:
        if pattern in filename:
            return False
    
    return True
