#!/usr/bin/env python3
"""
Setup script for Codebase Q&A with Gemini API
"""

import os
import subprocess
import sys

def install_requirements():
    """Install required packages"""
    print("📦 Installing required packages...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Packages installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing packages: {e}")
        return False

def setup_environment():
    """Setup environment variables"""
    print("\n🔧 Setting up environment...")
    
    # Check if .env file exists
    if os.path.exists('.env'):
        print("✅ .env file already exists")
        return True
    
    # Create .env file from example
    if os.path.exists('env_example.txt'):
        try:
            with open('env_example.txt', 'r') as src:
                content = src.read()
            with open('.env', 'w') as dst:
                dst.write(content)
            print("✅ Created .env file from template")
            print("⚠️  Please edit .env and add your GEMINI_API_KEY")
            return True
        except Exception as e:
            print(f"❌ Error creating .env file: {e}")
            return False
    else:
        print("❌ env_example.txt not found")
        return False

def get_gemini_api_key():
    """Guide user to get Gemini API key"""
    print("\n🔑 Getting Gemini API Key:")
    print("1. Go to: https://makersuite.google.com/app/apikey")
    print("2. Sign in with your Google account")
    print("3. Click 'Create API Key'")
    print("4. Copy the API key")
    print("5. Edit .env file and replace 'your_gemini_api_key_here' with your actual key")
    print("\n💡 Gemini API has a generous free tier - perfect for testing!")

def main():
    print("🚀 Codebase Q&A Setup with Gemini AI")
    print("=" * 50)
    
    # Install requirements
    if not install_requirements():
        print("❌ Setup failed at package installation")
        return False
    
    # Setup environment
    if not setup_environment():
        print("❌ Setup failed at environment setup")
        return False
    
    # Guide for API key
    get_gemini_api_key()
    
    print("\n✅ Setup completed!")
    print("\n📋 Next steps:")
    print("1. Edit .env file and add your GEMINI_API_KEY")
    print("2. Run: python gemini_app.py")
    print("3. Open: http://localhost:5000")
    print("4. Test with any GitHub repository!")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
