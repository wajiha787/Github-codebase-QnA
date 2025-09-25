#!/usr/bin/env python3
"""
Direct test of Multi-Tools analysis functions
Tests the tools without requiring a web server
"""

import os
import sys
from pathlib import Path

# Add current directory to path to import multi_tools_agent
sys.path.append('.')

def test_tools_directly():
    """Test analysis tools directly without web server"""
    print("🧪 Testing Multi-Tools Analysis Functions Directly...")
    print("=" * 60)
    
    # Import the tools
    try:
        from multi_tools_agent import (
            analyze_dependencies,
            analyze_code_metrics,
            find_security_issues,
            analyze_git_history,
            find_todos_and_fixmes,
            generate_architecture_summary,
            tool_registry
        )
        print("✅ Successfully imported analysis tools")
    except ImportError as e:
        print(f"❌ Failed to import tools: {e}")
        return False
    
    # Test with current directory as project
    project_path = "."
    
    print(f"\n📁 Testing with project path: {os.path.abspath(project_path)}")
    print("-" * 60)
    
    # Test each tool
    tools_to_test = [
        ("analyze_dependencies", analyze_dependencies),
        ("analyze_code_metrics", analyze_code_metrics),
        ("find_security_issues", find_security_issues),
        ("analyze_git_history", analyze_git_history),
        ("find_todos_and_fixmes", find_todos_and_fixmes),
        ("generate_architecture_summary", generate_architecture_summary)
    ]
    
    results = {}
    
    for tool_name, tool_func in tools_to_test:
        print(f"\n🔧 Testing {tool_name}...")
        try:
            result = tool_func(project_path)
            results[tool_name] = result
            print(f"   ✅ Success!")
            
            # Show sample results
            if isinstance(result, dict):
                print(f"   📊 Keys: {list(result.keys())}")
                if 'total_deps' in result:
                    print(f"   📦 Dependencies: {result['total_deps']}")
                if 'total_files' in result:
                    print(f"   📄 Files: {result['total_files']}")
                if 'total_lines' in result:
                    print(f"   📏 Lines: {result['total_lines']}")
                if 'total_issues' in result:
                    print(f"   🔒 Security Issues: {result['total_issues']}")
                if 'total_commits' in result:
                    print(f"   📈 Commits: {result['total_commits']}")
            else:
                print(f"   📊 Result type: {type(result)}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
            results[tool_name] = {"error": str(e)}
    
    # Test tool registry
    print(f"\n🔧 Testing Tool Registry...")
    try:
        available_tools = tool_registry.list_tools()
        print(f"   ✅ Registry has {len(available_tools)} tools:")
        for tool_name in available_tools:
            print(f"      - {tool_name}")
    except Exception as e:
        print(f"   ❌ Registry error: {e}")
    
    # Summary
    print(f"\n📊 Test Summary:")
    print(f"   Total tools tested: {len(tools_to_test)}")
    successful = sum(1 for r in results.values() if "error" not in r)
    print(f"   Successful: {successful}")
    print(f"   Failed: {len(tools_to_test) - successful}")
    
    return successful == len(tools_to_test)

def test_with_sample_project():
    """Test with a sample project structure"""
    print(f"\n🏗️  Creating sample project for testing...")
    
    # Create a sample project directory
    sample_dir = "test_sample_project"
    if os.path.exists(sample_dir):
        import shutil
        shutil.rmtree(sample_dir)
    
    os.makedirs(sample_dir, exist_ok=True)
    
    # Create sample files
    sample_files = {
        "requirements.txt": "flask==2.3.3\ngitpython==3.1.32\nrequests==2.31.0",
        "main.py": """
import os
import json
from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return "Hello World!"

# TODO: Add error handling
# FIXME: This is a test comment
if __name__ == '__main__':
    app.run(debug=True)
""",
        "config.py": """
# Configuration file
DEBUG = True
SECRET_KEY = "hardcoded_secret_key"  # Security issue
API_KEY = "test_api_key"  # Another security issue

# NOTE: This needs to be moved to environment variables
""",
        "README.md": "# Sample Project\n\nThis is a test project for the Multi-Tools Agent."
    }
    
    for filename, content in sample_files.items():
        with open(os.path.join(sample_dir, filename), 'w') as f:
            f.write(content)
    
    print(f"   ✅ Created sample project in {sample_dir}")
    
    # Test with sample project
    try:
        from multi_tools_agent import analyze_dependencies, find_security_issues, find_todos_and_fixmes
        
        print(f"\n🔍 Testing with sample project...")
        
        # Test dependencies
        deps = analyze_dependencies(sample_dir)
        print(f"   📦 Dependencies found: {deps.get('total_deps', 0)}")
        
        # Test security issues
        security = find_security_issues(sample_dir)
        print(f"   🔒 Security issues found: {security.get('total_issues', 0)}")
        
        # Test TODOs
        todos = find_todos_and_fixmes(sample_dir)
        print(f"   📝 TODOs found: {len(todos.get('todos', []))}")
        print(f"   🔧 FIXMEs found: {len(todos.get('fixmes', []))}")
        
        print(f"   ✅ Sample project tests successful!")
        
    except Exception as e:
        print(f"   ❌ Sample project test failed: {e}")
    finally:
        # Clean up
        import shutil
        shutil.rmtree(sample_dir)
        print(f"   🧹 Cleaned up sample project")

if __name__ == "__main__":
    print("🚀 Multi-Tools Direct Testing")
    print("This tests the analysis functions without requiring a web server")
    print()
    
    # Test with current directory
    success = test_tools_directly()
    
    # Test with sample project
    test_with_sample_project()
    
    if success:
        print(f"\n🎉 All tests passed! The Multi-Tools Agent is working correctly.")
        print(f"💡 You can now run 'python start_multi_tools.py' to start the web server.")
    else:
        print(f"\n⚠️  Some tests failed. Check the errors above.")
    
    print(f"\n" + "=" * 60)
