#!/usr/bin/env python3
"""
Web-based Codebase Q&A System
Run this script to start the web interface
"""

import os
import sys
from app import app

def main():
    print("🚀 Starting Codebase Q&A Web Interface...")
    print("📱 Open your browser and go to: http://localhost:5000")
    print("🔍 You can now:")
    print("   - Paste any GitHub repository URL")
    print("   - Load your local project")
    print("   - Ask questions about the codebase")
    print("   - Browse the project structure")
    print("\n" + "="*50)
    
    # Set default environment variables
    os.environ.setdefault('MODEL_TYPE', 'huggingface')
    os.environ.setdefault('EMBEDDING_TYPE', 'huggingface')
    
    # Run the Flask app
    app.run(debug=True, host='0.0.0.0', port=5000)

if __name__ == '__main__':
    main()


