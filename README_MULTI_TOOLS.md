# 🔧 Multi-Tools API Agent

A comprehensive codebase analysis tool that provides multiple specialized analysis capabilities through a unified API interface.

## ✨ Features

### 🛠️ Analysis Tools
- **Dependency Analysis**: Analyze Python, Node.js, and other package dependencies
- **Code Metrics**: Calculate lines of code, file types, complexity estimates
- **Security Scanning**: Detect potential security vulnerabilities and issues
- **Git History Analysis**: Analyze commit patterns, authors, and changes
- **Task Detection**: Find TODO, FIXME, HACK, and NOTE comments
- **Architecture Summary**: Generate project structure and entry point analysis

### 🤖 AI Agent
- **Intelligent Tool Selection**: Automatically chooses relevant tools based on questions
- **Natural Language Interface**: Ask questions in plain English
- **Contextual Responses**: Provides intelligent analysis based on tool results

### 🌐 Web Interface
- **Modern UI**: Clean, responsive web interface
- **Real-time Analysis**: Execute tools and get instant results
- **Interactive File Browser**: Explore project structure
- **Tool Management**: Easy access to all analysis tools

## 🚀 Quick Start

### 1. Installation
```bash
# Install dependencies
pip install -r requirements_multi_tools.txt

# Or install individually
pip install Flask==2.3.3 GitPython==3.1.32 pathlib2==2.3.7
```

### 2. Run the Agent
```bash
python multi_tools_agent.py
```

### 3. Access the Interface
Open your browser and go to: `http://localhost:5000`

## 📋 API Endpoints

### Core Endpoints
- `GET /` - Web interface
- `POST /api/clone-repo` - Load repository (GitHub URL or 'local')
- `GET /api/tools/list` - List all available tools
- `POST /api/tools/execute` - Execute a specific tool
- `POST /api/agent/analyze` - AI agent analysis
- `GET /api/file-tree` - Get project file tree
- `GET /api/file-content` - Get specific file content

### Example API Usage

#### Load a Repository
```bash
curl -X POST http://localhost:5000/api/clone-repo \
  -H "Content-Type: application/json" \
  -d '{"repo_url": "https://github.com/user/repo"}'
```

#### List Available Tools
```bash
curl http://localhost:5000/api/tools/list
```

#### Execute a Tool
```bash
curl -X POST http://localhost:5000/api/tools/execute \
  -H "Content-Type: application/json" \
  -d '{"tool_name": "analyze_dependencies", "parameters": {}}'
```

#### AI Agent Analysis
```bash
curl -X POST http://localhost:5000/api/agent/analyze \
  -H "Content-Type: application/json" \
  -d '{"question": "What dependencies does this project use?"}'
```

## 🔧 Available Tools

### 1. `analyze_dependencies`
**Description**: Analyze project dependencies and check for outdated packages
**Parameters**: `project_path` (string)
**Returns**: Python deps, Node deps, total count, security issues

### 2. `analyze_code_metrics`
**Description**: Analyze code metrics like lines of code, file types, and complexity
**Parameters**: `project_path` (string)
**Returns**: File counts, line counts, file types, largest files, complexity

### 3. `find_security_issues`
**Description**: Scan codebase for potential security vulnerabilities
**Parameters**: `project_path` (string)
**Returns**: Security issues, severity breakdown, issue details

### 4. `analyze_git_history`
**Description**: Analyze git commit history and patterns
**Parameters**: `project_path` (string)
**Returns**: Commit stats, authors, frequency, recent commits

### 5. `find_todos_and_fixmes`
**Description**: Find TODO, FIXME, and other task comments in the code
**Parameters**: `project_path` (string)
**Returns**: TODO lists, FIXME lists, task counts

### 6. `generate_architecture_summary`
**Description**: Generate a basic architecture summary of the project
**Parameters**: `project_path` (string)
**Returns**: Entry points, API endpoints, test files, static files

## 🧪 Testing

Run the test suite to verify functionality:

```bash
python test_multi_tools.py
```

The test script will:
- Test all API endpoints
- Execute individual tools
- Test AI agent analysis
- Verify file operations

## 💡 Usage Examples

### Web Interface
1. Open `http://localhost:5000`
2. Load a repository (GitHub URL or 'local')
3. Use individual tools or ask the AI agent questions
4. Explore the file tree and content

### Programmatic Usage
```python
import requests

# Load repository
response = requests.post('http://localhost:5000/api/clone-repo', 
                        json={'repo_url': 'local'})

# Analyze dependencies
response = requests.post('http://localhost:5000/api/tools/execute',
                        json={'tool_name': 'analyze_dependencies'})

# AI agent analysis
response = requests.post('http://localhost:5000/api/agent/analyze',
                        json={'question': 'What are the security issues?'})
```

## 🔑 API Keys Required

**None!** This implementation uses only local analysis tools and doesn't require any external API keys. All analysis is performed locally on your machine.

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Web Interface │    │   Tool Registry  │    │  Analysis Tools │
│                 │◄──►│                  │◄──►│                 │
│  - Load Repos   │    │  - Tool Manager  │    │  - Dependencies │
│  - Execute Tools│    │  - AI Agent      │    │  - Security     │
│  - AI Analysis  │    │  - Tool Chaining │    │  - Git History  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 🚀 Future Enhancements

- **Custom Tool Creation**: Allow users to create custom analysis tools
- **Tool Result Caching**: Cache results for better performance
- **Batch Processing**: Process multiple repositories at once
- **Advanced AI Integration**: More sophisticated tool selection
- **Export Capabilities**: Export analysis results to various formats
- **Real-time Monitoring**: Monitor repositories for changes

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add your analysis tool to the registry
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is open source and available under the MIT License.

## 🆘 Support

If you encounter any issues or have questions:
1. Check the test suite: `python test_multi_tools.py`
2. Review the API documentation above
3. Check the console output for error messages
4. Ensure all dependencies are installed correctly

---

**Happy Analyzing! 🔍✨**
