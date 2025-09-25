#!/usr/bin/env python3
"""
Multi-Tools API Agent for Codebase Analysis
Enhanced version of simple_app.py with multiple analysis tools
"""

import os
import json
import shutil
import tempfile
import subprocess
import re
from pathlib import Path
from flask import Flask, render_template, request, jsonify
import git
from datetime import datetime
from collections import defaultdict, Counter
import requests

app = Flask(__name__)

# Global variables
current_project_path = None
project_files = []
tool_registry = None

# AI Configuration
AI_SERVICE = "openai"  # Options: "openai", "anthropic", "local", "none"
OPENAI_API_KEY = None
ANTHROPIC_API_KEY = None

class ToolRegistry:
    """Registry for managing analysis tools"""
    
    def __init__(self):
        self.tools = {}
        self.tool_descriptions = {}
    
    def register_tool(self, name, func, description, parameters=None, requires_api_key=False):
        """Register a new tool"""
        self.tools[name] = func
        self.tool_descriptions[name] = {
            "description": description,
            "parameters": parameters or {},
            "requires_api_key": requires_api_key
        }
    
    def list_tools(self):
        """List all available tools"""
        return self.tool_descriptions
    
    def execute_tool(self, name, **kwargs):
        """Execute a tool by name"""
        if name not in self.tools:
            raise ValueError(f"Tool '{name}' not found")
        return self.tools[name](**kwargs)

# Initialize tool registry
tool_registry = ToolRegistry()

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

# =============================================================================
# ANALYSIS TOOLS
# =============================================================================

def analyze_dependencies(project_path):
    """Analyze project dependencies and versions"""
    results = {
        "python_deps": [],
        "node_deps": {},
        "outdated": [],
        "security_issues": [],
        "total_deps": 0
    }
    
    # Check requirements.txt
    req_file = os.path.join(project_path, "requirements.txt")
    if os.path.exists(req_file):
        with open(req_file, 'r', encoding='utf-8') as f:
            deps = [line.strip() for line in f.readlines() if line.strip() and not line.startswith('#')]
            results["python_deps"] = deps
            results["total_deps"] += len(deps)
    
    # Check package.json
    pkg_file = os.path.join(project_path, "package.json")
    if os.path.exists(pkg_file):
        try:
            with open(pkg_file, 'r', encoding='utf-8') as f:
                pkg_data = json.load(f)
                deps = pkg_data.get("dependencies", {})
                dev_deps = pkg_data.get("devDependencies", {})
                results["node_deps"] = {**deps, **dev_deps}
                results["total_deps"] += len(results["node_deps"])
        except json.JSONDecodeError:
            results["node_deps"] = {"error": "Invalid JSON"}
    
    # Check Pipfile
    pipfile = os.path.join(project_path, "Pipfile")
    if os.path.exists(pipfile):
        try:
            with open(pipfile, 'r', encoding='utf-8') as f:
                content = f.read()
                # Simple regex to extract packages
                packages = re.findall(r'^(\w+)\s*=', content, re.MULTILINE)
                results["python_deps"].extend(packages)
                results["total_deps"] += len(packages)
        except:
            pass
    
    return results

def analyze_code_metrics(project_path):
    """Analyze code metrics and statistics"""
    metrics = {
        "total_files": 0,
        "total_lines": 0,
        "file_types": {},
        "largest_files": [],
        "complexity_estimate": 0
    }
    
    file_sizes = []
    
    for root, dirs, files in os.walk(project_path):
        for file in files:
            if file.startswith('.'):
                continue
                
            file_path = os.path.join(root, file)
            ext = os.path.splitext(file)[1].lower()
            
            if ext in ['.py', '.js', '.ts', '.jsx', '.tsx', '.html', '.css', '.md', '.txt', '.json']:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        lines = len(content.split('\n'))
                        
                        metrics["total_files"] += 1
                        metrics["total_lines"] += lines
                        metrics["file_types"][ext] = metrics["file_types"].get(ext, 0) + 1
                        
                        file_sizes.append({
                            "file": os.path.relpath(file_path, project_path),
                            "lines": lines,
                            "size": os.path.getsize(file_path)
                        })
                        
                        # Simple complexity estimate (functions, classes, conditionals)
                        if ext in ['.py', '.js', '.ts']:
                            func_count = len(re.findall(r'def\s+\w+|function\s+\w+|class\s+\w+', content))
                            metrics["complexity_estimate"] += func_count
                            
                except:
                    continue
    
    # Sort by lines and get top 10 largest files
    file_sizes.sort(key=lambda x: x['lines'], reverse=True)
    metrics["largest_files"] = file_sizes[:10]
    
    return metrics

def find_security_issues(project_path):
    """Find potential security issues in the codebase"""
    security_issues = []
    
    # Common security patterns to check
    security_patterns = {
        'hardcoded_passwords': r'password\s*=\s*["\'][^"\']+["\']',
        'api_keys': r'api[_-]?key\s*=\s*["\'][^"\']+["\']',
        'sql_injection': r'execute\s*\(\s*["\'].*%.*["\']',
        'eval_usage': r'eval\s*\(',
        'exec_usage': r'exec\s*\(',
        'shell_injection': r'os\.system\s*\(|subprocess\.call\s*\(',
        'weak_random': r'random\.random\s*\(\)|Math\.random\s*\(\s*\)',
        'debug_mode': r'debug\s*=\s*True|DEBUG\s*=\s*True'
    }
    
    for root, dirs, files in os.walk(project_path):
        for file in files:
            if file.endswith(('.py', '.js', '.ts', '.jsx', '.tsx')):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                        for pattern_name, pattern in security_patterns.items():
                            matches = re.finditer(pattern, content, re.IGNORECASE)
                            for match in matches:
                                line_num = content[:match.start()].count('\n') + 1
                                security_issues.append({
                                    "file": os.path.relpath(file_path, project_path),
                                    "line": line_num,
                                    "issue": pattern_name,
                                    "code": match.group().strip(),
                                    "severity": "high" if pattern_name in ['hardcoded_passwords', 'api_keys'] else "medium"
                                })
                except:
                    continue
    
    return {
        "total_issues": len(security_issues),
        "issues": security_issues[:20],  # Limit to first 20
        "severity_breakdown": Counter([issue["severity"] for issue in security_issues])
    }

def analyze_git_history(project_path):
    """Analyze git commit history and patterns"""
    try:
        repo = git.Repo(project_path)
        
        # Get commit statistics
        commits = list(repo.iter_commits())
        
        # Analyze commit patterns
        commit_stats = {
            "total_commits": len(commits),
            "authors": {},
            "commit_frequency": {},
            "recent_commits": [],
            "file_changes": defaultdict(int)
        }
        
        for commit in commits[-50:]:  # Last 50 commits
            author = commit.author.name
            commit_stats["authors"][author] = commit_stats["authors"].get(author, 0) + 1
            
            # Date analysis
            date_str = commit.committed_datetime.strftime("%Y-%m")
            commit_stats["commit_frequency"][date_str] = commit_stats["commit_frequency"].get(date_str, 0) + 1
            
            # Recent commits
            if len(commit_stats["recent_commits"]) < 10:
                commit_stats["recent_commits"].append({
                    "hash": commit.hexsha[:8],
                    "message": commit.message.strip(),
                    "author": author,
                    "date": commit.committed_datetime.isoformat()
                })
            
            # File changes
            for file_path in commit.stats.files:
                commit_stats["file_changes"][file_path] += 1
        
        return commit_stats
        
    except Exception as e:
        return {"error": f"Git analysis failed: {str(e)}"}

def find_todos_and_fixmes(project_path):
    """Find TODO, FIXME, and other task comments"""
    tasks = {
        "todos": [],
        "fixmes": [],
        "hacks": [],
        "notes": []
    }
    
    patterns = {
        'todos': r'(?:#|//|/\*)\s*TODO[:\s]*(.+)',
        'fixmes': r'(?:#|//|/\*)\s*FIXME[:\s]*(.+)',
        'hacks': r'(?:#|//|/\*)\s*HACK[:\s]*(.+)',
        'notes': r'(?:#|//|/\*)\s*NOTE[:\s]*(.+)'
    }
    
    for root, dirs, files in os.walk(project_path):
        for file in files:
            if file.endswith(('.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.cpp', '.c', '.h')):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        lines = content.split('\n')
                        
                        for i, line in enumerate(lines):
                            for task_type, pattern in patterns.items():
                                matches = re.finditer(pattern, line, re.IGNORECASE)
                                for match in matches:
                                    tasks[task_type].append({
                                        "file": os.path.relpath(file_path, project_path),
                                        "line": i + 1,
                                        "content": match.group(1).strip(),
                                        "full_line": line.strip()
                                    })
                except:
                    continue
    
    # Count totals
    task_types = list(tasks.keys())
    for task_type in task_types:
        if task_type != 'todos':  # Don't count todos twice
            tasks[f"{task_type}_count"] = len(tasks[task_type])
    
    return tasks

def generate_architecture_summary(project_path):
    """Generate a basic architecture summary"""
    architecture = {
        "entry_points": [],
        "api_endpoints": [],
        "database_files": [],
        "config_files": [],
        "test_files": [],
        "static_files": []
    }
    
    for root, dirs, files in os.walk(project_path):
        for file in files:
            file_path = os.path.relpath(os.path.join(root, file), project_path)
            
            # Entry points
            if file in ['main.py', 'app.py', 'index.js', 'server.js', 'app.js']:
                architecture["entry_points"].append(file_path)
            
            # API endpoints (simple detection)
            elif 'api' in file.lower() or 'route' in file.lower():
                architecture["api_endpoints"].append(file_path)
            
            # Database files
            elif file.endswith(('.db', '.sqlite', '.sql')):
                architecture["database_files"].append(file_path)
            
            # Config files
            elif file in ['config.py', 'settings.py', 'config.json', '.env', 'docker-compose.yml']:
                architecture["config_files"].append(file_path)
            
            # Test files
            elif 'test' in file.lower() or file.startswith('test_'):
                architecture["test_files"].append(file_path)
            
            # Static files
            elif file.endswith(('.css', '.js', '.html', '.png', '.jpg', '.svg')):
                architecture["static_files"].append(file_path)
    
    return architecture

# =============================================================================
# REGISTER TOOLS
# =============================================================================

# Register all tools
tool_registry.register_tool(
    "analyze_dependencies",
    analyze_dependencies,
    "Analyze project dependencies and check for outdated packages",
    {"project_path": "string"}
)

tool_registry.register_tool(
    "analyze_code_metrics",
    analyze_code_metrics,
    "Analyze code metrics like lines of code, file types, and complexity",
    {"project_path": "string"}
)

tool_registry.register_tool(
    "find_security_issues",
    find_security_issues,
    "Scan codebase for potential security vulnerabilities",
    {"project_path": "string"}
)

tool_registry.register_tool(
    "analyze_git_history",
    analyze_git_history,
    "Analyze git commit history and patterns",
    {"project_path": "string"}
)

tool_registry.register_tool(
    "find_todos_and_fixmes",
    find_todos_and_fixmes,
    "Find TODO, FIXME, and other task comments in the code",
    {"project_path": "string"}
)

tool_registry.register_tool(
    "generate_architecture_summary",
    generate_architecture_summary,
    "Generate a basic architecture summary of the project",
    {"project_path": "string"}
)

# =============================================================================
# FLASK ROUTES
# =============================================================================

@app.route('/')
def index():
    return render_template('multi_tools.html')

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

@app.route('/api/tools/list')
def list_tools():
    """List all available analysis tools"""
    return jsonify({
        "success": True,
        "tools": tool_registry.list_tools()
    })

@app.route('/api/tools/execute', methods=['POST'])
def execute_tool():
    """Execute a specific analysis tool"""
    global current_project_path
    
    if not current_project_path:
        return jsonify({"success": False, "message": "No repository loaded"}), 400
    
    data = request.get_json()
    tool_name = data.get('tool_name')
    parameters = data.get('parameters', {})
    
    if not tool_name:
        return jsonify({"success": False, "message": "Tool name is required"}), 400
    
    if tool_name not in tool_registry.tools:
        return jsonify({"success": False, "message": f"Tool '{tool_name}' not found"}), 400
    
    try:
        # Add project_path to parameters
        parameters['project_path'] = current_project_path
        
        # Execute the tool
        result = tool_registry.execute_tool(tool_name, **parameters)
        
        return jsonify({
            "success": True,
            "tool_name": tool_name,
            "result": result
        })
    except Exception as e:
        return jsonify({"success": False, "message": f"Error executing tool: {str(e)}"}), 500

@app.route('/api/agent/analyze', methods=['POST'])
def agent_analyze():
    """AI agent that analyzes project based on question"""
    global current_project_path
    
    if not current_project_path:
        return jsonify({"success": False, "message": "No repository loaded"}), 400
    
    data = request.get_json()
    question = data.get('question', '').strip().lower()
    
    if not question:
        return jsonify({"success": False, "message": "Question is required"}), 400
    
    # Determine which tools to run based on question
    tools_to_run = []
    
    if any(word in question for word in ['dependencies', 'packages', 'requirements', 'npm', 'pip']):
        tools_to_run.append('analyze_dependencies')
    
    if any(word in question for word in ['metrics', 'lines', 'complexity', 'size', 'statistics']):
        tools_to_run.append('analyze_code_metrics')
    
    if any(word in question for word in ['security', 'vulnerability', 'safe', 'secure']):
        tools_to_run.append('find_security_issues')
    
    if any(word in question for word in ['git', 'commit', 'history', 'changes', 'author']):
        tools_to_run.append('analyze_git_history')
    
    if any(word in question for word in ['todo', 'fixme', 'task', 'hack', 'note']):
        tools_to_run.append('find_todos_and_fixmes')
    
    if any(word in question for word in ['architecture', 'structure', 'entry', 'api', 'endpoint']):
        tools_to_run.append('generate_architecture_summary')
    
    # If no specific tools identified, run a basic analysis
    if not tools_to_run:
        tools_to_run = ['analyze_code_metrics', 'analyze_dependencies']
    
    # Execute tools
    results = {}
    for tool_name in tools_to_run:
        try:
            result = tool_registry.execute_tool(tool_name, project_path=current_project_path)
            results[tool_name] = result
        except Exception as e:
            results[tool_name] = {"error": str(e)}
    
    # Generate intelligent response
    response = generate_agent_response(question, results)
    
    return jsonify({
        "success": True,
        "question": question,
        "tools_used": tools_to_run,
        "results": results,
        "response": response
    })

def call_ai_service(question, analysis_data, service="openai"):
    """Call AI service to generate intelligent response"""
    
    if service == "none" or not OPENAI_API_KEY:
        return generate_basic_response(question, analysis_data)
    
    # Prepare context for AI
    context = f"""
You are an expert code analyst. A user asked: "{question}"

Here is the analysis data from the codebase:

{json.dumps(analysis_data, indent=2)}

Please provide a clear, intelligent answer to the user's question based on this data. 
Be specific and helpful. If the data doesn't contain enough information to answer the question, 
say so and suggest what additional analysis might be needed.

Format your response in a clear, professional manner with emojis for better readability.
"""
    
    if service == "openai":
        return call_openai_api(context)
    elif service == "anthropic":
        return call_anthropic_api(context)
    else:
        return generate_basic_response(question, analysis_data)

def call_openai_api(context):
    """Call OpenAI API for intelligent response"""
    try:
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {"role": "system", "content": "You are an expert code analyst who provides clear, helpful answers about codebases."},
                {"role": "user", "content": context}
            ],
            "max_tokens": 1000,
            "temperature": 0.7
        }
        
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            return result["choices"][0]["message"]["content"]
        else:
            return f"❌ OpenAI API Error: {response.status_code} - {response.text}"
            
    except Exception as e:
        return f"❌ Error calling OpenAI API: {str(e)}"

def call_anthropic_api(context):
    """Call Anthropic API for intelligent response"""
    try:
        headers = {
            "x-api-key": ANTHROPIC_API_KEY,
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "claude-3-sonnet-20240229",
            "max_tokens": 1000,
            "messages": [
                {"role": "user", "content": context}
            ]
        }
        
        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers=headers,
            json=data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            return result["content"][0]["text"]
        else:
            return f"❌ Anthropic API Error: {response.status_code} - {response.text}"
            
    except Exception as e:
        return f"❌ Error calling Anthropic API: {str(e)}"

def generate_basic_response(question, analysis_data):
    """Generate a basic intelligent response without AI API"""
    question_lower = question.lower()
    
    # Database-related questions
    if any(word in question_lower for word in ['database', 'db', 'sql', 'data']):
        db_info = analysis_data.get('generate_architecture_summary', {})
        db_files = db_info.get('database_files', [])
        
        if db_files:
            return f"""🗄️ **Database Analysis**:

Yes, this project uses databases! I found the following database-related files:
{chr(10).join(f"- {file}" for file in db_files)}

The project appears to have database integration based on the file structure."""
        else:
            return f"""🗄️ **Database Analysis**:

Based on my analysis, I don't see any obvious database files (like .db, .sqlite, .sql files) in the project structure. 

However, the project might be using:
- An external database service (cloud-based)
- Database configuration in code files
- ORM/ODM libraries for database access

To get more specific information about database usage, I'd need to examine the actual code files for database-related imports and configurations."""
    
    # Dependencies questions
    elif any(word in question_lower for word in ['dependencies', 'packages', 'libraries', 'requirements']):
        deps_info = analysis_data.get('analyze_dependencies', {})
        total_deps = deps_info.get('total_deps', 0)
        python_deps = deps_info.get('python_deps', [])
        node_deps = deps_info.get('node_deps', {})
        
        response = f"""📦 **Dependencies Analysis**:

This project has **{total_deps} total dependencies**:

"""
        if python_deps:
            response += f"**Python packages ({len(python_deps)}):**\n"
            for dep in python_deps[:5]:
                response += f"- {dep}\n"
            if len(python_deps) > 5:
                response += f"- ... and {len(python_deps) - 5} more\n"
            response += "\n"
        
        if node_deps:
            response += f"**Node.js packages ({len(node_deps)}):**\n"
            for pkg, version in list(node_deps.items())[:5]:
                response += f"- {pkg}: {version}\n"
            if len(node_deps) > 5:
                response += f"- ... and {len(node_deps) - 5} more\n"
        
        return response
    
    # Security questions
    elif any(word in question_lower for word in ['security', 'vulnerability', 'safe', 'secure']):
        security_info = analysis_data.get('find_security_issues', {})
        total_issues = security_info.get('total_issues', 0)
        issues = security_info.get('issues', [])
        
        if total_issues == 0:
            return f"""🔒 **Security Analysis**:

✅ **Good news!** I didn't find any obvious security issues in the codebase.

The security scan checked for common vulnerabilities like:
- Hardcoded passwords or API keys
- SQL injection patterns
- Unsafe eval/exec usage
- Shell injection risks
- Weak random number generation
- Debug mode enabled

Your codebase appears to follow good security practices!"""
        else:
            response = f"""🔒 **Security Analysis**:

⚠️ **Found {total_issues} potential security issues:**

"""
            for issue in issues[:5]:
                response += f"**{issue['issue'].replace('_', ' ').title()}** in {issue['file']} (line {issue['line']}):\n"
                response += f"```\n{issue['code']}\n```\n"
                response += f"Severity: {issue['severity']}\n\n"
            
            if len(issues) > 5:
                response += f"... and {len(issues) - 5} more issues\n\n"
            
            response += "**Recommendations:**\n"
            response += "- Review and fix these issues\n"
            response += "- Use environment variables for secrets\n"
            response += "- Implement proper input validation\n"
            response += "- Regular security audits\n"
            
            return response
    
    # Code metrics questions
    elif any(word in question_lower for word in ['lines', 'code', 'size', 'complexity', 'files']):
        metrics_info = analysis_data.get('analyze_code_metrics', {})
        total_files = metrics_info.get('total_files', 0)
        total_lines = metrics_info.get('total_lines', 0)
        file_types = metrics_info.get('file_types', {})
        complexity = metrics_info.get('complexity_estimate', 0)
        
        return f"""📊 **Code Metrics**:

**Project Statistics:**
- **Total files:** {total_files}
- **Total lines of code:** {total_lines:,}
- **Estimated complexity:** {complexity} functions/classes

**File Type Breakdown:**
{chr(10).join(f"- {ext or 'no extension'}: {count} files" for ext, count in list(file_types.items())[:5])}

**Analysis:**
This is a {'small' if total_lines < 1000 else 'medium' if total_lines < 10000 else 'large'} project with {'low' if complexity < 10 else 'medium' if complexity < 50 else 'high'} complexity."""
    
    # Default response
    else:
        return f"""🤖 **Analysis Results**:

I analyzed your codebase and found the following information:

{json.dumps(analysis_data, indent=2)}

**Note:** For more specific answers, try asking about:
- Dependencies and packages
- Security issues
- Database usage
- Code metrics and complexity
- Git history and contributors
- TODO items and tasks"""

def generate_agent_response(question, results):
    """Generate an intelligent response based on tool results"""
    return call_ai_service(question, results, AI_SERVICE)

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

@app.route('/api/ai/configure', methods=['POST'])
def configure_ai():
    """Configure AI service and API keys"""
    global AI_SERVICE, OPENAI_API_KEY, ANTHROPIC_API_KEY
    
    data = request.get_json()
    service = data.get('service', 'none')
    api_key = data.get('api_key', '')
    
    if service == 'openai':
        OPENAI_API_KEY = api_key
        AI_SERVICE = 'openai'
    elif service == 'anthropic':
        ANTHROPIC_API_KEY = api_key
        AI_SERVICE = 'anthropic'
    elif service == 'none':
        AI_SERVICE = 'none'
    else:
        return jsonify({"success": False, "message": "Invalid service. Use 'openai', 'anthropic', or 'none'"}), 400
    
    return jsonify({
        "success": True,
        "message": f"AI service configured: {service}",
        "service": AI_SERVICE,
        "has_api_key": bool(api_key)
    })

@app.route('/api/ai/status')
def ai_status():
    """Get current AI configuration status"""
    return jsonify({
        "service": AI_SERVICE,
        "has_openai_key": bool(OPENAI_API_KEY),
        "has_anthropic_key": bool(ANTHROPIC_API_KEY),
        "is_configured": AI_SERVICE != "none" and (
            (AI_SERVICE == "openai" and OPENAI_API_KEY) or
            (AI_SERVICE == "anthropic" and ANTHROPIC_API_KEY)
        )
    })

if __name__ == '__main__':
    print("🚀 Starting Multi-Tools API Agent...")
    print("📱 Open your browser and go to: http://localhost:5000")
    print("🔧 Available tools:")
    for tool_name, desc in tool_registry.list_tools().items():
        print(f"   - {tool_name}: {desc['description']}")
    print("=" * 50)
    app.run(debug=True, host='0.0.0.0', port=5000)
