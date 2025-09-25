#!/usr/bin/env python3
"""
Test script for Enhanced AI-Powered Multi-Tools Agent
Tests both basic analysis and AI-powered responses
"""

import requests
import json
import time

# Configuration
BASE_URL = "http://localhost:5000"

def test_ai_enhanced_features():
    """Test the enhanced AI features"""
    print("🤖 Testing Enhanced AI-Powered Multi-Tools Agent...")
    print("=" * 60)
    
    # Test 1: Load local project
    print("\n1️⃣ Loading local project...")
    try:
        response = requests.post(f"{BASE_URL}/api/clone-repo", 
                               json={"repo_url": "local"})
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Project loaded: {result['file_count']} files")
        else:
            print(f"❌ Failed to load project: {response.json()}")
            return
    except Exception as e:
        print(f"❌ Error loading project: {e}")
        return
    
    # Test 2: Test AI status
    print("\n2️⃣ Testing AI configuration...")
    try:
        response = requests.get(f"{BASE_URL}/api/ai/status")
        if response.status_code == 200:
            status = response.json()
            print(f"✅ AI Status: {status['service']} (configured: {status['is_configured']})")
        else:
            print(f"❌ Failed to get AI status: {response.json()}")
    except Exception as e:
        print(f"❌ Error getting AI status: {e}")
    
    # Test 3: Test intelligent questions (without API key - should use basic analysis)
    print("\n3️⃣ Testing intelligent question answering (Basic Mode)...")
    
    test_questions = [
        "Is there any database being used in this project?",
        "What dependencies does this project have?",
        "Are there any security issues?",
        "How many lines of code are there?",
        "What is the project structure like?"
    ]
    
    for question in test_questions:
        print(f"\n   Question: {question}")
        try:
            response = requests.post(f"{BASE_URL}/api/agent/analyze", 
                                   json={"question": question})
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ Response preview: {result['response'][:150]}...")
                print(f"   🔧 Tools used: {', '.join(result['tools_used'])}")
            else:
                print(f"   ❌ Failed: {response.json()}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    # Test 4: Test AI configuration (simulate API key setup)
    print(f"\n4️⃣ Testing AI configuration...")
    try:
        # Test with no API key (should work with basic analysis)
        response = requests.post(f"{BASE_URL}/api/ai/configure", 
                               json={"service": "none", "api_key": ""})
        if response.status_code == 200:
            result = response.json()
            print(f"✅ AI configured: {result['message']}")
        else:
            print(f"❌ Failed to configure AI: {response.json()}")
    except Exception as e:
        print(f"❌ Error configuring AI: {e}")
    
    # Test 5: Test individual tools
    print(f"\n5️⃣ Testing individual analysis tools...")
    tools_to_test = [
        "analyze_dependencies",
        "analyze_code_metrics", 
        "find_security_issues",
        "generate_architecture_summary"
    ]
    
    for tool_name in tools_to_test:
        print(f"\n   Testing {tool_name}...")
        try:
            response = requests.post(f"{BASE_URL}/api/tools/execute", 
                                   json={"tool_name": tool_name, "parameters": {}})
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ Success!")
                # Show sample of results
                if isinstance(result['result'], dict):
                    keys = list(result['result'].keys())
                    print(f"   📊 Result keys: {keys[:3]}...")
            else:
                print(f"   ❌ Failed: {response.json()}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print(f"\n" + "=" * 60)
    print("🎉 Enhanced AI Testing completed!")
    print("💡 The agent now provides intelligent responses to questions!")
    print("🌐 Open http://localhost:5000 to use the web interface")

def test_database_question_specifically():
    """Test the specific database question that was problematic"""
    print(f"\n🔍 Testing the specific database question...")
    
    try:
        response = requests.post(f"{BASE_URL}/api/agent/analyze", 
                               json={"question": "Is there any database being used in this project?"})
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Database Question Response:")
            print(f"   {result['response']}")
            print(f"   Tools used: {', '.join(result['tools_used'])}")
        else:
            print(f"❌ Failed: {response.json()}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🚀 Enhanced AI-Powered Multi-Tools Agent Test Suite")
    print("Make sure the server is running on http://localhost:5000")
    print()
    
    # Wait a moment for server to be ready
    print("⏳ Waiting for server to be ready...")
    time.sleep(3)
    
    test_ai_enhanced_features()
    test_database_question_specifically()
