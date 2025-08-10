#!/usr/bin/env python3
"""
Setup script to initialize the vector database for job opportunity search.
"""
import os
import sys
from pathlib import Path

# Add src to path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from job_tracker_llm.storage import JobStorage
from job_tracker_llm.vector_store import JobVectorStore
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def check_openai_api_key():
    """Check if OpenAI API key is set."""
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("⚠️  Warning: OPENAI_API_KEY environment variable not set.")
        print("   Vector search will not be available.")
        print("   Set it with: export OPENAI_API_KEY='your-api-key-here'")
        return False
    return True


def setup_vector_database():
    """Set up the vector database for job opportunity search."""
    
    print("Job Tracker Vector Database Setup")
    print("=" * 40)
    
    # Check API key
    if not check_openai_api_key():
        response = input("\nDo you want to continue without vector search? (y/n): ").lower()
        if response not in ['y', 'yes']:
            print("Setup cancelled.")
            return False
    
    try:
        # Initialize storage and vector store
        print("\nInitializing storage and vector store...")
        storage = JobStorage()
        vector_store = JobVectorStore(storage)
        
        # Check if we have any opportunities
        opportunities = storage.list_opportunities()
        
        if not opportunities:
            print("\n⚠️  No job opportunities found.")
            print("   Add some opportunities first using: python -m job_tracker_llm.cli add")
            return True
        
        print(f"\nFound {len(opportunities)} opportunities to index.")
        
        # Build the vector index
        print("\nBuilding vector index...")
        success = vector_store.build_index()
        
        if success:
            print("✅ Vector index built successfully!")
            
            # Show index stats
            stats = vector_store.get_index_stats()
            if stats.get('status') == 'available':
                print(f"   Documents indexed: {stats.get('document_count', 0)}")
                print(f"   Index location: {stats.get('index_path', 'Unknown')}")
            
            return True
        else:
            print("❌ Failed to build vector index.")
            return False
            
    except Exception as e:
        logger.error(f"Setup failed: {e}")
        print(f"❌ Setup failed: {e}")
        return False


def test_vector_search():
    """Test the vector search functionality."""
    
    print("\nTesting vector search...")
    
    try:
        storage = JobStorage()
        vector_store = JobVectorStore(storage)
        
        if not vector_store.vectorstore:
            print("⚠️  Vector store not available. Run setup first.")
            return False
        
        # Test search
        results = vector_store.semantic_search("software engineer", k=3)
        
        if results:
            print(f"✅ Search test successful! Found {len(results)} results.")
            return True
        else:
            print("⚠️  Search test returned no results.")
            return True  # This might be normal if no opportunities match
            
    except Exception as e:
        logger.error(f"Search test failed: {e}")
        print(f"❌ Search test failed: {e}")
        return False


def main():
    """Main setup function."""
    
    try:
        # Set up vector database
        success = setup_vector_database()
        
        if success:
            # Test search functionality
            test_vector_search()
            
            print("\n🎉 Setup completed successfully!")
            print("\nYou can now use the following commands:")
            print("  python -m job_tracker_llm.cli add     # Add new opportunity")
            print("  python -m job_tracker_llm.cli list    # List opportunities")
            print("  python -m job_tracker_llm.cli search  # Search opportunities")
            print("  python -m job_tracker_llm.cli update  # Update opportunity")
            print("  python -m job_tracker_llm.cli stats   # Show statistics")
        else:
            print("\n❌ Setup failed. Please check the error messages above.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\nSetup cancelled by user.")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
