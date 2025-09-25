#!/usr/bin/env python3
"""
Startup script for Multi-Tools API Agent
"""

import sys
import os
import subprocess

def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = ['flask', 'gitpython']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\n💡 Install them with:")
        print("   pip install -r requirements_multi_tools.txt")
        return False
    
    return True

def main():
    print("🚀 Starting Multi-Tools API Agent...")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Check if my_project directory exists
    if not os.path.exists('./my_project'):
        print("⚠️  Local project directory './my_project' not found")
        print("   The agent will work with GitHub repositories or you can create a local project")
        print("   Create a 'my_project' directory with some code files to test locally")
        print()
    
    print("🌐 Starting web server...")
    print("📱 Open your browser and go to: http://localhost:5000")
    print("🔧 Available tools:")
    print("   - analyze_dependencies")
    print("   - analyze_code_metrics") 
    print("   - find_security_issues")
    print("   - analyze_git_history")
    print("   - find_todos_and_fixmes")
    print("   - generate_architecture_summary")
    print("\n🛑 Press Ctrl+C to stop the server")
    print("=" * 50)
    
    try:
        # Import and run the Flask app
        from multi_tools_agent import app
        app.run(debug=True, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
