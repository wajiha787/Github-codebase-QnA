#!/usr/bin/env python3
"""
Codebase Q&A System with Gemini API Integration
"""

import os
import json
import shutil
import tempfile
from pathlib import Path
from flask import Flask, render_template, request, jsonify
import git
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Configure Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
else:
    model = None

# Global variables
current_project_path = None
project_files = []
project_context = ""

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

def extract_codebase_context(directory):
    """Extract relevant code context for Gemini"""
    context_parts = []
    
    try:
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith(('.py', '.js', '.ts', '.jsx', '.tsx', '.html', '.css', '.md', '.txt', '.json')):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            
                            # Only include files with substantial content
                            if len(content.strip()) > 50:
                                relative_path = os.path.relpath(file_path, directory)
                                context_parts.append(f"=== {relative_path} ===\n{content[:2000]}\n")
                    except:
                        continue
    except Exception as e:
        print(f"Error extracting context: {e}")
    
    return "\n".join(context_parts)

def search_in_files(query, directory):
    """Search for relevant files based on query"""
    results = []
    query_lower = query.lower()
    
    # Create search terms from the query
    search_terms = []
    
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
                            
                            matches = []
                            for term in search_terms:
                                if term in content_lower:
                                    matches.append(term)
                            
                            if matches:
                                results.append({
                                    "file": file_path,
                                    "content": content[:1000],  # First 1000 chars
                                    "matches": matches
                                })
                    except:
                        continue
    except Exception as e:
        print(f"Error searching files: {e}")
    
    return results[:10]

def ask_gemini(question, context):
    """Ask Gemini API with codebase context"""
    if not model:
        return "Gemini API key not configured. Please set GEMINI_API_KEY in your environment variables."
    
    try:
        prompt = f"""
You are an expert code analyst. Analyze the following codebase and answer the user's question intelligently.

CODEBASE CONTEXT:
{context}

USER QUESTION: {question}

Please provide a detailed, helpful answer about the codebase. Include:
1. Specific code examples when relevant
2. File names and line numbers when possible
3. Architecture explanations
4. Technology stack analysis
5. Best practices or recommendations

Format your response in markdown with clear sections and code blocks.
"""
        
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error calling Gemini API: {str(e)}"

@app.route('/')
def index():
    return render_template('elegant.html')

@app.route('/api/clone-repo', methods=['POST'])
def clone_repo():
    """Clone a GitHub repository or load local project"""
    global current_project_path, project_files, project_context
    
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
    
    # Extract codebase context for Gemini
    project_context = extract_codebase_context(current_project_path)
    
    return jsonify({
        "success": True,
        "message": "Repository loaded successfully",
        "file_count": len(project_files),
        "file_tree": project_files[:50],
        "gemini_available": model is not None
    })

@app.route('/api/ask-question', methods=['POST'])
def ask_question():
    """Ask a question about the codebase using Gemini API"""
    global current_project_path, project_context
    
    if not current_project_path:
        return jsonify({"success": False, "message": "No repository loaded. Please clone a repository first."}), 400
    
    data = request.get_json()
    question = data.get('question', '').strip()
    
    if not question:
        return jsonify({"success": False, "message": "Question is required"}), 400
    
    try:
        if model and project_context:
            # Use Gemini API for intelligent response
            answer = ask_gemini(question, project_context)
            
            # Also get relevant file references
            search_results = search_in_files(question, current_project_path)
            sources = []
            for result in search_results[:5]:
                sources.append({
                    "file": os.path.basename(result['file']),
                    "content": result['content'][:200] + "..." if len(result['content']) > 200 else result['content']
                })
            
            return jsonify({
                "success": True,
                "answer": answer,
                "sources": sources,
                "ai_powered": True
            })
        else:
            # Fallback to simple search if Gemini not available
            search_results = search_in_files(question, current_project_path)
            
            if search_results:
                answer = f"**Found {len(search_results)} relevant files:**\n\n"
                sources = []
                
                for i, result in enumerate(search_results[:5], 1):
                    answer += f"**{i}. {os.path.basename(result['file'])}**\n"
                    answer += f"```\n{result['content'][:300]}...\n```\n\n"
                    sources.append({
                        "file": os.path.basename(result['file']),
                        "content": result['content'][:200] + "..." if len(result['content']) > 200 else result['content']
                    })
                
                return jsonify({
                    "success": True,
                    "answer": answer,
                    "sources": sources,
                    "ai_powered": False
                })
            else:
                return jsonify({
                    "success": True,
                    "answer": f"❌ I couldn't find any code related to '{question}' in the repository.\n\n💡 **Try asking about:**\n- Specific file names (e.g., 'api.py', 'App.jsx')\n- Technology terms (e.g., 'React', 'Flask', 'Python')\n- Function names (e.g., 'login', 'register', 'database')\n- File types (e.g., 'Python files', 'JavaScript files')",
                    "sources": [],
                    "ai_powered": False
                })
        
    except Exception as e:
        return jsonify({"success": False, "message": f"Error processing question: {str(e)}"}), 500

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

@app.route('/api/project-info')
def get_project_info():
    """Get information about the current project"""
    global current_project_path, project_files
    
    if not current_project_path:
        return jsonify({"success": False, "message": "No project loaded"}), 400
    
    # Count files by type
    file_types = {}
    total_files = len(project_files)
    
    for file_info in project_files:
        if file_info['type'] == 'file':
            ext = os.path.splitext(file_info['name'])[1].lower()
            file_types[ext] = file_types.get(ext, 0) + 1
    
    return jsonify({
        "success": True,
        "total_files": total_files,
        "file_types": file_types,
        "project_path": current_project_path,
        "gemini_available": model is not None
    })

if __name__ == '__main__':
    print("🚀 Starting Codebase Q&A with Gemini AI...")
    print("📱 Open your browser and go to: http://localhost:5000")
    if model:
        print("✅ Gemini API configured - AI-powered responses enabled")
    else:
        print("⚠️  Gemini API not configured - using fallback search")
        print("   Set GEMINI_API_KEY environment variable to enable AI features")
    print("=" * 50)
    app.run(debug=True, host='0.0.0.0', port=5000)
