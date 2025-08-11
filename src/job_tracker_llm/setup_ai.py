#!/usr/bin/env python3
"""
Setup script for AI features with OpenAI integration.
"""
import os
import sys
from pathlib import Path

# Add src to path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from job_tracker_llm.storage import JobStorage
from job_tracker_llm.vector_store import JobVectorStore
from job_tracker_llm.ai_assistant import JobTrackerAI
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def check_dependencies():
    """Check if required dependencies are installed."""
    print("Checking dependencies...")
    
    missing_deps = []
    
    try:
        import openai
        print("✅ OpenAI package installed")
    except ImportError:
        print("❌ OpenAI package not installed")
        missing_deps.append("openai")
    
    try:
        import chromadb
        print("✅ ChromaDB package installed")
    except ImportError:
        print("⚠️  ChromaDB package not installed (optional)")
        print("   Vector search will be limited, but core AI features will work")
        # Don't add to missing_deps since it's optional
    
    try:
        import langchain
        print("✅ LangChain package installed")
    except ImportError:
        print("❌ LangChain package not installed")
        missing_deps.append("langchain")
    
    if missing_deps:
        print(f"\n❌ Missing dependencies: {', '.join(missing_deps)}")
        print("Install them with: pip install -r requirements.txt")
        return False
    
    print("✅ All dependencies installed")
    return True


def setup_openai_api_key():
    """Set up OpenAI API key."""
    print("\nSetting up OpenAI API key...")
    
    # Check if already set
    current_key = os.getenv('OPENAI_API_KEY')
    if current_key:
        print(f"✅ OpenAI API key already set: {current_key[:8]}...")
        return True
    
    # Get API key from user
    print("To use AI features, you need an OpenAI API key.")
    print("Get one from: https://platform.openai.com/api-keys")
    print()
    
    api_key = input("Enter your OpenAI API key (or press Enter to skip): ").strip()
    
    if not api_key:
        print("⚠️  Skipping OpenAI setup. AI features will not be available.")
        return False
    
    # Test the API key
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Hello"}],
            max_tokens=10
        )
        print("✅ OpenAI API key is valid!")
        
        # Save to environment
        os.environ['OPENAI_API_KEY'] = api_key
        print("✅ API key set for this session")
        
        # Ask if user wants to save to shell profile
        save_profile = input("\nSave API key to shell profile for future sessions? (y/n): ").lower()
        if save_profile in ['y', 'yes']:
            profile_file = input("Enter profile file path (e.g., ~/.bashrc, ~/.zshrc): ").strip()
            if profile_file:
                try:
                    profile_path = Path(profile_file).expanduser()
                    with open(profile_path, 'a') as f:
                        f.write(f'\n# OpenAI API Key for Job Tracker\n')
                        f.write(f'export OPENAI_API_KEY="{api_key}"\n')
                    print(f"✅ API key saved to {profile_path}")
                    print("Restart your terminal or run 'source ~/.bashrc' to apply changes")
                except Exception as e:
                    print(f"❌ Could not save to profile: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Invalid API key: {e}")
        return False


def setup_vector_database():
    """Set up vector database for AI features."""
    print("\nSetting up vector database...")
    
    try:
        storage = JobStorage()
        vector_store = JobVectorStore(storage)
        
        # Check if we have opportunities
        opportunities = storage.list_opportunities()
        if not opportunities:
            print("⚠️  No job opportunities found.")
            print("   Add some opportunities first using the simple CLI:")
            print("   python3 src/job_tracker_llm/simple_cli.py")
            return False
        
        print(f"Found {len(opportunities)} opportunities to index")
        
        # Build vector index
        print("Building vector index...")
        success = vector_store.build_index()
        
        if success:
            print("✅ Vector index built successfully!")
            
            # Show stats
            stats = vector_store.get_index_stats()
            if stats.get('status') == 'available':
                print(f"   Documents indexed: {stats.get('document_count', 0)}")
                print(f"   Index location: {stats.get('index_path', 'Unknown')}")
            
            return True
        else:
            print("❌ Failed to build vector index")
            return False
            
    except Exception as e:
        print(f"❌ Error setting up vector database: {e}")
        return False


def test_ai_features():
    """Test AI features."""
    print("\nTesting AI features...")
    
    try:
        storage = JobStorage()
        vector_store = JobVectorStore(storage)
        ai_assistant = JobTrackerAI(storage, vector_store)
        
        if not ai_assistant.client:
            print("❌ OpenAI client not available")
            return False
        
        # Test basic AI functionality
        print("Testing AI insights...")
        insights = ai_assistant.get_job_search_insights()
        if insights and not insights.startswith("Error"):
            print("✅ AI insights working")
        else:
            print("❌ AI insights failed")
            return False
        
        print("✅ AI features working correctly!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing AI features: {e}")
        return False


def main():
    """Main setup function."""
    print("🤖 Job Tracker AI Setup")
    print("=" * 30)
    
    # Check dependencies
    deps_ok = check_dependencies()
    if not deps_ok:
        print("\n⚠️  Some dependencies missing, but continuing with available features")
    
    # Setup OpenAI API key
    openai_ready = setup_openai_api_key()
    
    # Setup vector database (optional)
    try:
        vector_ready = setup_vector_database()
    except Exception as e:
        print(f"⚠️  Vector database setup failed: {e}")
        print("   Core AI features will still work without vector search")
        vector_ready = False
    
    # Test AI features if OpenAI is ready
    ai_working = False
    if openai_ready:
        ai_working = test_ai_features()
    
    # Summary
    print("\n" + "=" * 30)
    print("Setup Summary:")
    print(f"✅ Dependencies: Installed")
    print(f"{'✅' if openai_ready else '❌'} OpenAI API: {'Configured' if openai_ready else 'Not configured'}")
    print(f"{'✅' if vector_ready else '❌'} Vector Database: {'Ready' if vector_ready else 'Not ready'}")
    print(f"{'✅' if ai_working else '❌'} AI Features: {'Working' if ai_working else 'Not working'}")
    
    if ai_working:
        print("\n🎉 AI setup completed successfully!")
        print("\nYou can now use the AI assistant:")
        print("  python3 src/job_tracker_llm/ai_cli.py")
    else:
        print("\n⚠️  AI setup incomplete. Some features may not work.")
        print("\nTo complete setup:")
        if not openai_ready:
            print("  1. Get OpenAI API key from https://platform.openai.com/api-keys")
            print("  2. Set environment variable: export OPENAI_API_KEY='your-key'")
        if not vector_ready:
            print("  3. Add job opportunities using the simple CLI")
        print("  4. Run this setup script again")


if __name__ == "__main__":
    main() 