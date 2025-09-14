#!/usr/bin/env python3
"""
Installation script for Codebase Q&A System
"""

import subprocess
import sys
import os

def install_package(package):
    """Install a package using pip"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✅ {package} installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install {package}: {e}")
        return False

def main():
    print("🚀 Installing Codebase Q&A System Dependencies...")
    print("=" * 50)
    
    # Core dependencies
    packages = [
        "langchain==0.0.350",
        "openai==1.3.0",
        "chromadb==0.4.18",
        "python-dotenv==1.0.0",
        "rich==13.7.0",
        "colorama==0.4.6",
        "transformers==4.35.0",
        "torch==2.1.0",
        "sentence-transformers==2.2.2",
        "huggingface-hub==0.19.0",
        "accelerate==0.24.0",
        "flask==2.3.3",
        "flask-cors==4.0.0",
        "requests==2.31.0",
        "gitpython==3.1.40"
    ]
    
    success_count = 0
    total_count = len(packages)
    
    for package in packages:
        if install_package(package):
            success_count += 1
    
    print("=" * 50)
    print(f"📊 Installation Summary: {success_count}/{total_count} packages installed")
    
    if success_count == total_count:
        print("🎉 All dependencies installed successfully!")
        print("\n🚀 You can now run the web interface:")
        print("   python run_web.py")
        print("\n🌐 Then open your browser to: http://localhost:5000")
    else:
        print("⚠️  Some packages failed to install. You may need to install them manually.")
        print("   Try running: pip install -r requirements.txt")

if __name__ == "__main__":
    main()
