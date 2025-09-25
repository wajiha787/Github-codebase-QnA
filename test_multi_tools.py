#!/usr/bin/env python3
"""
Test script for Multi-Tools API Agent
"""

import requests
import json
import time

# Configuration
BASE_URL = "http://localhost:5000"
TEST_REPO_URL = "https://github.com/octocat/Hello-World"  # Small test repo

def test_api_endpoints():
    """Test all API endpoints"""
    print("🧪 Testing Multi-Tools API Agent...")
    print("=" * 50)
    
    # Test 1: List available tools
    print("\n1️⃣ Testing tool listing...")
    try:
        response = requests.get(f"{BASE_URL}/api/tools/list")
        if response.status_code == 200:
            tools = response.json()["tools"]
            print(f"✅ Found {len(tools)} tools:")
            for tool_name, desc in tools.items():
                print(f"   - {tool_name}: {desc['description']}")
        else:
            print(f"❌ Failed to list tools: {response.status_code}")
    except Exception as e:
        print(f"❌ Error listing tools: {e}")
    
    # Test 2: Clone repository
    print("\n2️⃣ Testing repository cloning...")
    try:
        data = {"repo_url": TEST_REPO_URL}
        response = requests.post(f"{BASE_URL}/api/clone-repo", json=data)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Repository cloned: {result['message']}")
            print(f"   Files found: {result['file_count']}")
        else:
            print(f"❌ Failed to clone repo: {response.json()}")
    except Exception as e:
        print(f"❌ Error cloning repository: {e}")
    
    # Test 3: Execute individual tools
    print("\n3️⃣ Testing individual tool execution...")
    tools_to_test = [
        "analyze_dependencies",
        "analyze_code_metrics", 
        "find_security_issues",
        "analyze_git_history",
        "find_todos_and_fixmes",
        "generate_architecture_summary"
    ]
    
    for tool_name in tools_to_test:
        print(f"\n   Testing {tool_name}...")
        try:
            data = {"tool_name": tool_name, "parameters": {}}
            response = requests.post(f"{BASE_URL}/api/tools/execute", json=data)
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ {tool_name}: Success")
                # Show a sample of the result
                if "result" in result:
                    result_data = result["result"]
                    if isinstance(result_data, dict):
                        print(f"      Sample data: {list(result_data.keys())}")
                    else:
                        print(f"      Result type: {type(result_data)}")
            else:
                print(f"   ❌ {tool_name}: {response.json()}")
        except Exception as e:
            print(f"   ❌ {tool_name}: Error - {e}")
    
    # Test 4: Test AI agent analysis
    print("\n4️⃣ Testing AI agent analysis...")
    test_questions = [
        "What dependencies does this project use?",
        "How many lines of code are there?",
        "Are there any security issues?",
        "What is the git history like?",
        "Are there any TODOs or FIXMEs?",
        "What is the project architecture?"
    ]
    
    for question in test_questions:
        print(f"\n   Question: {question}")
        try:
            data = {"question": question}
            response = requests.post(f"{BASE_URL}/api/agent/analyze", json=data)
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ Tools used: {result['tools_used']}")
                print(f"   Response preview: {result['response'][:100]}...")
            else:
                print(f"   ❌ Failed: {response.json()}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Testing completed!")

def test_file_operations():
    """Test file tree and content operations"""
    print("\n5️⃣ Testing file operations...")
    
    try:
        # Test file tree
        response = requests.get(f"{BASE_URL}/api/file-tree")
        if response.status_code == 200:
            file_tree = response.json()["file_tree"]
            print(f"✅ File tree loaded: {len(file_tree)} items")
        else:
            print(f"❌ Failed to load file tree: {response.status_code}")
        
        # Test file content (if files exist)
        if file_tree:
            first_file = next((f for f in file_tree if f["type"] == "file"), None)
            if first_file:
                file_path = first_file["path"]
                response = requests.get(f"{BASE_URL}/api/file-content?path={file_path}")
                if response.status_code == 200:
                    content = response.json()["content"]
                    print(f"✅ File content loaded: {len(content)} characters")
                else:
                    print(f"❌ Failed to load file content: {response.status_code}")
        
    except Exception as e:
        print(f"❌ Error in file operations: {e}")

if __name__ == "__main__":
    print("🚀 Multi-Tools API Agent Test Suite")
    print("Make sure the server is running on http://localhost:5000")
    print("Run: python multi_tools_agent.py")
    print()
    
    # Wait a moment for user to start server
    input("Press Enter when the server is ready...")
    
    test_api_endpoints()
    test_file_operations()
