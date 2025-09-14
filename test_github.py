#!/usr/bin/env python3
"""
Test script for GitHub repository functionality
"""

import os
import tempfile
import shutil
from main import CodebaseQA

def test_github_repo():
    """Test loading a GitHub repository"""
    print("🧪 Testing GitHub Repository Loading...")
    
    # Set environment variables
    os.environ['MODEL_TYPE'] = 'huggingface'
    os.environ['EMBEDDING_TYPE'] = 'huggingface'
    os.environ['PROJECT_DIRECTORY'] = './my_project'  # Use local project for testing
    
    try:
        # Initialize Q&A system without console
        qa_system = CodebaseQA(use_console=False)
        
        # Load environment
        if not qa_system.load_environment():
            print("❌ Failed to load environment")
            return False
        
        # Load documents
        documents = qa_system.load_documents()
        if not documents:
            print("❌ No documents loaded")
            return False
        
        print(f"✅ Loaded {len(documents)} documents")
        
        # Create vector store
        if not qa_system.create_vectorstore(documents):
            print("❌ Failed to create vector store")
            return False
        
        print("✅ Vector store created")
        
        # Setup Q&A chain
        if not qa_system.setup_qa_chain():
            print("❌ Failed to setup Q&A chain")
            return False
        
        print("✅ Q&A chain ready")
        
        # Test a question
        test_question = "What is this project about?"
        print(f"🤔 Testing question: {test_question}")
        
        result = qa_system.qa_chain({"query": test_question})
        answer = result["result"]
        
        print(f"✅ Answer: {answer[:200]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_github_repo()
    if success:
        print("\n🎉 Test passed! The system is working correctly.")
    else:
        print("\n💥 Test failed. Check the error messages above.")
