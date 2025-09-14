#!/usr/bin/env python3
"""
Simple version of the web app that doesn't use ChromaDB
"""

import os
import json
import shutil
import tempfile
from pathlib import Path
from flask import Flask, render_template, request, jsonify
import git

app = Flask(__name__)

# Global variables
current_project_path = None
project_files = []

def get_file_tree(directory, prefix="", max_depth=3, current_depth=0):
    """Generate a file tree structure"""
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
                tree.extend(get_file_tree(item, next_prefix, max_depth, current_depth + 1))
    except PermissionError:
        pass
    
    return tree

def clone_github_repo(repo_url, target_dir):
    """Clone a GitHub repository"""
    try:
        if os.path.exists(target_dir):
            shutil.rmtree(target_dir)
        git.Repo.clone_from(repo_url, target_dir)
        return True, "Repository cloned successfully"
    except Exception as e:
        return False, f"Error cloning repository: {str(e)}"

def search_in_files(query, directory):
    """Intelligent text search in files"""
    results = []
    query_lower = query.lower()
    
    # Create search terms from the query
    search_terms = []
    
    # Extract key terms from common questions
    if 'api' in query_lower or 'endpoint' in query_lower:
        search_terms.extend(['api', 'endpoint', 'route', 'flask', 'app.route', 'post', 'get', 'put', 'delete'])
    if 'component' in query_lower or 'frontend' in query_lower:
        search_terms.extend(['component', 'react', 'jsx', 'frontend', 'app', 'main'])
    if 'technology' in query_lower or 'tech' in query_lower:
        search_terms.extend(['react', 'vite', 'fastapi', 'python', 'javascript', 'typescript', 'flask'])
    if 'authentication' in query_lower or 'auth' in query_lower:
        search_terms.extend(['auth', 'authentication', 'login', 'token', 'jwt', 'password'])
    if 'database' in query_lower or 'db' in query_lower:
        search_terms.extend(['database', 'db', 'sqlite', 'sql', 'table', 'query'])
    if 'deployment' in query_lower or 'deploy' in query_lower:
        search_terms.extend(['deployment', 'deploy', 'docker', 'server', 'production'])
    
    # If no specific terms found, use the original query words
    if not search_terms:
        search_terms = query_lower.split()
    
    try:
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith(('.py', '.js', '.ts', '.jsx', '.tsx', '.html', '.css', '.md', '.txt', '.json')):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            content_lower = content.lower()
                            
                            # Check if any search term is in the file
                            matches = []
                            for term in search_terms:
                                if term in content_lower:
                                    matches.append(term)
                            
                            if matches:
                                # Find the lines with matches
                                lines = content.split('\n')
                                for i, line in enumerate(lines):
                                    line_lower = line.lower()
                                    for term in matches:
                                        if term in line_lower:
                                            results.append({
                                                "file": file_path,
                                                "line": i + 1,
                                                "content": line.strip(),
                                                "context": '\n'.join(lines[max(0, i-2):i+3]),
                                                "matched_terms": matches
                                            })
                                            break
                                    if len(results) >= 20:  # Limit results per file
                                        break
                    except:
                        continue
    except Exception as e:
        print(f"Error searching files: {e}")
    
    return results[:15]  # Limit to 15 results

@app.route('/')
def index():
    return render_template('elegant.html')

@app.route('/api/clone-repo', methods=['POST'])
def clone_repo():
    """Clone a GitHub repository or load local project"""
    global current_project_path, project_files
    
    data = request.get_json()
    repo_url = data.get('repo_url', '').strip()
    
    if not repo_url:
        return jsonify({"success": False, "message": "Repository URL is required"}), 400
    
    # Handle local project
    if repo_url == 'local':
        current_project_path = './my_project'
        if not os.path.exists(current_project_path):
            return jsonify({"success": False, "message": "Local project directory not found"}), 400
    else:
        # Validate GitHub URL
        if not (repo_url.startswith('https://github.com/') or repo_url.startswith('git@github.com:')):
            return jsonify({"success": False, "message": "Please provide a valid GitHub repository URL"}), 400
        
        # Create temporary directory for the project
        temp_dir = tempfile.mkdtemp(prefix="codebase_qa_")
        current_project_path = temp_dir
        
        # Clone the repository
        success, message = clone_github_repo(repo_url, temp_dir)
        
        if not success:
            return jsonify({"success": False, "message": message}), 400
    
    # Generate file tree
    project_files = get_file_tree(current_project_path)
    
    return jsonify({
        "success": True,
        "message": "Repository loaded successfully",
        "file_count": len(project_files),
        "file_tree": project_files[:50]
    })

@app.route('/api/ask-question', methods=['POST'])
def ask_question():
    """Ask a question about the codebase using simple text search"""
    global current_project_path
    
    if not current_project_path:
        return jsonify({"success": False, "message": "No repository loaded. Please clone a repository first."}), 400
    
    data = request.get_json()
    question = data.get('question', '').strip()
    
    if not question:
        return jsonify({"success": False, "message": "Question is required"}), 400
    
    try:
        # Intelligent search in files
        search_results = search_in_files(question, current_project_path)
        
        if search_results:
            # Group results by file type and create intelligent response
            answer = ""
            sources = []
            
            # Analyze the question type and provide contextual response
            question_lower = question.lower()
            
            if 'api' in question_lower or 'endpoint' in question_lower:
                answer = "🔗 **API Endpoints Found:**\n\n"
                api_files = [r for r in search_results if 'api' in r['file'].lower() or 'route' in r['content'].lower()]
                for i, result in enumerate(api_files[:5], 1):
                    answer += f"**{i}. {os.path.basename(result['file'])}** (line {result['line']}):\n"
                    answer += f"   ```\n   {result['content']}\n   ```\n\n"
                    sources.append({
                        "file": result['file'],
                        "content": result['content'][:100] + "..." if len(result['content']) > 100 else result['content']
                    })
                    
            elif 'component' in question_lower or 'frontend' in question_lower:
                answer = "⚛️ **Frontend Components Found:**\n\n"
                frontend_files = [r for r in search_results if any(term in r['file'].lower() for term in ['jsx', 'js', 'tsx', 'ts', 'react'])]
                for i, result in enumerate(frontend_files[:5], 1):
                    answer += f"**{i}. {os.path.basename(result['file'])}** (line {result['line']}):\n"
                    answer += f"   ```\n   {result['content']}\n   ```\n\n"
                    sources.append({
                        "file": result['file'],
                        "content": result['content'][:100] + "..." if len(result['content']) > 100 else result['content']
                    })
                    
            elif 'technology' in question_lower or 'tech' in question_lower:
                answer = "🛠️ **Technologies Used:**\n\n"
                tech_files = [r for r in search_results if any(term in r['content'].lower() for term in ['react', 'vite', 'fastapi', 'python', 'javascript', 'typescript', 'flask'])]
                for i, result in enumerate(tech_files[:5], 1):
                    answer += f"**{i}. {os.path.basename(result['file'])}** (line {result['line']}):\n"
                    answer += f"   ```\n   {result['content']}\n   ```\n\n"
                    sources.append({
                        "file": result['file'],
                        "content": result['content'][:100] + "..." if len(result['content']) > 100 else result['content']
                    })
                    
            else:
                answer = f"📁 **Found {len(search_results)} relevant code snippets:**\n\n"
                for i, result in enumerate(search_results[:5], 1):
                    answer += f"**{i}. {os.path.basename(result['file'])}** (line {result['line']}):\n"
                    answer += f"   ```\n   {result['content']}\n   ```\n\n"
                    sources.append({
                        "file": result['file'],
                        "content": result['content'][:100] + "..." if len(result['content']) > 100 else result['content']
                    })
            
            return jsonify({
                "success": True,
                "answer": answer,
                "sources": sources
            })
        else:
            return jsonify({
                "success": True,
                "answer": f"❌ I couldn't find any code related to '{question}' in the repository.\n\n💡 **Try asking about:**\n- Specific file names (e.g., 'api.py', 'App.jsx')\n- Technology terms (e.g., 'React', 'Flask', 'Python')\n- Function names (e.g., 'login', 'register', 'database')\n- File types (e.g., 'Python files', 'JavaScript files')",
                "sources": []
            })
        
    except Exception as e:
        return jsonify({"success": False, "message": f"Error searching codebase: {str(e)}"}), 500

@app.route('/api/file-tree')
def get_file_tree_api():
    """Get the file tree of the current project"""
    global project_files
    return jsonify({"file_tree": project_files})

@app.route('/api/file-content')
def get_file_content():
    """Get the content of a specific file"""
    file_path = request.args.get('path', '')
    
    if not file_path or not current_project_path:
        return jsonify({"success": False, "message": "Invalid file path"}), 400
    
    # Ensure the file is within the project directory
    full_path = os.path.join(current_project_path, file_path)
    if not full_path.startswith(current_project_path):
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

if __name__ == '__main__':
    print("🚀 Starting Simple Codebase Q&A Web Interface...")
    print("📱 Open your browser and go to: http://localhost:5000")
    print("🔍 This version uses simple text search instead of AI")
    print("=" * 50)
    app.run(debug=True, host='0.0.0.0', port=5000)
