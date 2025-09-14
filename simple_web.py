#!/usr/bin/env python3
"""
Simple Web Interface for Codebase Q&A System
This version has minimal dependencies for quick testing
"""

import os
import json
import tempfile
from pathlib import Path
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Simple file tree function
def get_simple_file_tree(directory, prefix="", max_depth=3, current_depth=0):
    """Generate a simple file tree structure"""
    if current_depth >= max_depth:
        return []
    
    tree = []
    try:
        items = sorted(Path(directory).iterdir(), key=lambda x: (x.is_file(), x.name))
        for i, item in enumerate(items):
            if item.name.startswith('.'):
                continue
                
            is_last = i == len(items) - 1
            current_prefix = "└── " if is_last else "├── "
            
            tree.append({
                "name": item.name,
                "type": "file" if item.is_file() else "directory",
                "path": str(item),
                "prefix": prefix + current_prefix,
                "size": item.stat().st_size if item.is_file() else 0
            })
            
            if item.is_dir() and current_depth < max_depth - 1:
                next_prefix = prefix + ("    " if is_last else "│   ")
                tree.extend(get_simple_file_tree(item, next_prefix, max_depth, current_depth + 1))
    except PermissionError:
        pass
    
    return tree

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/load-local', methods=['POST'])
def load_local():
    """Load local project"""
    project_path = './my_project'
    
    if not os.path.exists(project_path):
        return jsonify({"success": False, "message": "Local project directory not found"}), 400
    
    # Generate file tree
    project_files = get_simple_file_tree(project_path)
    
    # Count files by type
    file_types = {}
    for file_info in project_files:
        if file_info['type'] == 'file':
            ext = os.path.splitext(file_info['name'])[1].lower()
            file_types[ext] = file_types.get(ext, 0) + 1
    
    return jsonify({
        "success": True,
        "message": "Local project loaded successfully",
        "file_count": len(project_files),
        "file_tree": project_files[:50],  # Limit to first 50 files
        "file_types": file_types
    })

@app.route('/api/file-tree')
def get_file_tree():
    """Get the file tree of the current project"""
    project_path = './my_project'
    if not os.path.exists(project_path):
        return jsonify({"file_tree": []})
    
    project_files = get_simple_file_tree(project_path)
    return jsonify({"file_tree": project_files})

@app.route('/api/file-content')
def get_file_content():
    """Get the content of a specific file"""
    file_path = request.args.get('path', '')
    project_path = './my_project'
    
    if not file_path or not project_path:
        return jsonify({"success": False, "message": "Invalid file path"}), 400
    
    # Ensure the file is within the project directory
    full_path = os.path.join(project_path, file_path)
    if not full_path.startswith(project_path):
        return jsonify({"success": False, "message": "Access denied"}), 403
    
    try:
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return jsonify({
            "success": True,
            "content": content,
            "file_name": os.path.basename(file_path)
        })
    except Exception as e:
        return jsonify({"success": False, "message": f"Error reading file: {str(e)}"}), 500

@app.route('/api/ask-question', methods=['POST'])
def ask_question():
    """Simple question answering (placeholder)"""
    data = request.get_json()
    question = data.get('question', '').strip()
    
    if not question:
        return jsonify({"success": False, "message": "Question is required"}), 400
    
    # Simple response for testing
    response = f"""
    You asked: "{question}"
    
    This is a simple demo response. The full Q&A system requires additional dependencies.
    
    To enable full functionality:
    1. Run: python install.py
    2. Then run: python run_web.py
    
    The full system will provide intelligent answers about your codebase using AI models.
    """
    
    return jsonify({
        "success": True,
        "answer": response,
        "sources": [{"file": "demo", "content": "This is a demo response"}]
    })

if __name__ == '__main__':
    print("🚀 Starting Simple Codebase Q&A Web Interface...")
    print("📱 Open your browser and go to: http://localhost:5000")
    print("⚠️  This is a simplified version. Run 'python install.py' for full functionality.")
    print("\n" + "="*50)
    
    app.run(debug=True, host='0.0.0.0', port=5000)


