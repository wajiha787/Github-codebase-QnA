#!/usr/bin/env python3
"""
Test ChromaDB functionality
"""

import os
import sys
from pathlib import Path

# Add current directory to path
sys.path.append('.')

def test_chromadb():
    """Test if ChromaDB can be created and used"""
    try:
        print("Testing ChromaDB functionality...")
        
        # Test basic imports
        from langchain.vectorstores import Chroma
        from langchain.embeddings import HuggingFaceEmbeddings
        from langchain.schema import Document
        print("✅ All imports successful")
        
        # Test creating embeddings
        print("Creating Hugging Face embeddings...")
        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'}
        )
        print("✅ Embeddings created successfully")
        
        # Test creating documents
        test_docs = [
            Document(page_content="This is a test document about Python programming.", metadata={"source": "test1.py"}),
            Document(page_content="This is another test document about web development.", metadata={"source": "test2.js"}),
        ]
        print(f"✅ Created {len(test_docs)} test documents")
        
        # Test creating vector store
        print("Creating ChromaDB vector store...")
        vectorstore = Chroma.from_documents(
            test_docs, 
            embeddings,
            collection_name="test_collection",
            persist_directory="./test_chroma_db"
        )
        print("✅ Vector store created successfully")
        
        # Test similarity search
        print("Testing similarity search...")
        results = vectorstore.similarity_search("Python programming", k=1)
        print(f"✅ Similarity search returned {len(results)} results")
        
        # Clean up
        import shutil
        if os.path.exists("./test_chroma_db"):
            shutil.rmtree("./test_chroma_db")
        print("✅ Cleanup completed")
        
        print("\n🎉 ChromaDB test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ ChromaDB test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_chromadb()
    sys.exit(0 if success else 1)
