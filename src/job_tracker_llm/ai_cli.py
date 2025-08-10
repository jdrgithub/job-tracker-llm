#!/usr/bin/env python3
"""
AI-enhanced CLI for job tracker with ChatGPT integration.
"""
import os
import sys
from pathlib import Path
from typing import Optional

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Import with absolute paths
import sys
sys.path.insert(0, str(Path(__file__).parent))

from storage import JobStorage
from vector_store import JobVectorStore
from ai_assistant import JobTrackerAI
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def check_openai_setup():
    """Check if OpenAI is properly set up."""
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("⚠️  Warning: OPENAI_API_KEY not set.")
        print("   AI features will not be available.")
        print("   Set it with: export OPENAI_API_KEY='your-api-key-here'")
        return False
    
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        # Test the connection
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Hello"}],
            max_tokens=10
        )
        print("✅ OpenAI connection successful!")
        return True
    except Exception as e:
        print(f"❌ OpenAI connection failed: {e}")
        return False


def prompt_choice(prompt_text: str, choices: list, default_choice_index: Optional[int] = None) -> str:
    """Simple choice prompt function."""
    print(f"\n{prompt_text}")
    
    for i, choice in enumerate(choices, 1):
        suffix = " (default)" if default_choice_index == i - 1 else ""
        print(f"{i}. {choice}{suffix}")
    
    while True:
        user_input = input("Choose a number: ").strip()
        
        if not user_input and default_choice_index is not None:
            return choices[default_choice_index]
        
        if user_input.isdigit():
            selected_number = int(user_input)
            if 1 <= selected_number <= len(choices):
                return choices[selected_number - 1]
        
        print("Invalid selection. Please enter a number from the list.")


def get_ai_insights(ai_assistant: JobTrackerAI):
    """Get AI insights about job search."""
    print("\n🤖 Getting AI insights...")
    print("=" * 50)
    
    insights = ai_assistant.get_job_search_insights()
    print(insights)


def ask_ai_question(ai_assistant: JobTrackerAI):
    """Ask AI a specific question about opportunities."""
    print("\n🤖 Ask AI about your job opportunities")
    print("=" * 50)
    
    question = input("What would you like to know about your job search? ")
    if not question.strip():
        print("No question provided.")
        return
    
    print(f"\n🤖 AI Response:")
    print("-" * 30)
    
    response = ai_assistant.ask_about_opportunities(question)
    print(response)


def get_follow_up_suggestions(ai_assistant: JobTrackerAI):
    """Get AI suggestions for follow-ups."""
    print("\n🤖 Getting follow-up suggestions...")
    print("=" * 50)
    
    suggestions = ai_assistant.suggest_follow_ups()
    print(suggestions)


def analyze_specific_opportunity(ai_assistant: JobTrackerAI):
    """Analyze a specific opportunity with AI."""
    print("\n🤖 Analyze specific opportunity")
    print("=" * 50)
    
    # Get list of opportunities
    storage = ai_assistant.storage
    opportunities = storage.list_opportunities()
    
    if not opportunities:
        print("No opportunities found to analyze.")
        return
    
    # Show opportunities for selection
    print("Select an opportunity to analyze:")
    for i, opp in enumerate(opportunities, 1):
        status = "Active" if opp['active'] else "Inactive"
        print(f"  {i}. {opp['company']} - {opp['role']} ({status})")
    
    # Get selection
    choice = input("Enter number: ").strip()
    try:
        index = int(choice) - 1
        if 0 <= index < len(opportunities):
            selected_opp = opportunities[index]
        else:
            print("Invalid selection.")
            return
    except ValueError:
        print("Invalid number.")
        return
    
    print(f"\n🤖 Analyzing {selected_opp['company']} - {selected_opp['role']}...")
    print("-" * 50)
    
    analysis = ai_assistant.analyze_opportunity(selected_opp['company'], selected_opp['role'])
    print(analysis)


def generate_follow_up_email(ai_assistant: JobTrackerAI):
    """Generate a follow-up email with AI."""
    print("\n🤖 Generate follow-up email")
    print("=" * 50)
    
    # Get list of opportunities
    storage = ai_assistant.storage
    opportunities = storage.list_opportunities()
    
    if not opportunities:
        print("No opportunities found.")
        return
    
    # Show opportunities for selection
    print("Select an opportunity for email generation:")
    for i, opp in enumerate(opportunities, 1):
        status = "Active" if opp['active'] else "Inactive"
        print(f"  {i}. {opp['company']} - {opp['role']} ({status})")
    
    # Get selection
    choice = input("Enter number: ").strip()
    try:
        index = int(choice) - 1
        if 0 <= index < len(opportunities):
            selected_opp = opportunities[index]
        else:
            print("Invalid selection.")
            return
    except ValueError:
        print("Invalid number.")
        return
    
    # Get recruiter name (optional)
    recruiter_name = input("Recruiter name (optional, press Enter to skip): ").strip()
    if not recruiter_name:
        recruiter_name = None
    
    print(f"\n🤖 Generating email for {selected_opp['company']} - {selected_opp['role']}...")
    print("-" * 50)
    
    email = ai_assistant.generate_follow_up_email(
        selected_opp['company'], 
        selected_opp['role'], 
        recruiter_name
    )
    print(email)


def get_career_advice(ai_assistant: JobTrackerAI):
    """Get career advice from AI."""
    print("\n🤖 Get career advice")
    print("=" * 50)
    
    question = input("What career advice do you need? ")
    if not question.strip():
        print("No question provided.")
        return
    
    print(f"\n🤖 AI Career Advice:")
    print("-" * 30)
    
    advice = ai_assistant.get_career_advice(question)
    print(advice)


def setup_vector_database(ai_assistant: JobTrackerAI):
    """Set up vector database for AI features."""
    print("\n🔧 Setting up vector database...")
    print("=" * 50)
    
    vector_store = ai_assistant.vector_store
    
    # Check if vector store is available
    if not vector_store.vectorstore:
        print("Building vector index...")
        success = vector_store.build_index()
        if success:
            print("✅ Vector index built successfully!")
        else:
            print("❌ Failed to build vector index.")
            return
    else:
        print("Vector index already exists.")
    
    # Show index stats
    stats = vector_store.get_index_stats()
    if stats.get('status') == 'available':
        print(f"   Documents indexed: {stats.get('document_count', 0)}")
        print(f"   Index location: {stats.get('index_path', 'Unknown')}")


def main():
    """Main AI CLI function."""
    print("🤖 Job Tracker AI Assistant")
    print("=" * 30)
    
    # Check OpenAI setup
    openai_available = check_openai_setup()
    
    # Initialize components
    print("\nInitializing components...")
    storage = JobStorage()
    vector_store = JobVectorStore(storage)
    ai_assistant = JobTrackerAI(storage, vector_store)
    
    # Check if we have opportunities
    opportunities = storage.list_opportunities()
    if not opportunities:
        print("\n⚠️  No job opportunities found.")
        print("   Add some opportunities first using the simple CLI:")
        print("   python3 src/job_tracker_llm/simple_cli.py")
        return
    
    print(f"✅ Found {len(opportunities)} opportunities")
    
    # Main menu
    while True:
        print("\n🤖 AI Assistant Menu:")
        print("1. Get job search insights")
        print("2. Ask AI about opportunities")
        print("3. Get follow-up suggestions")
        print("4. Analyze specific opportunity")
        print("5. Generate follow-up email")
        print("6. Get career advice")
        print("7. Setup vector database")
        print("8. Exit")
        
        if not openai_available:
            print("\n⚠️  AI features disabled - OpenAI not configured")
            print("   Only option 7 (Setup) is available")
        
        choice = input("\nEnter your choice (1-8): ").strip()
        
        if choice == "1":
            if openai_available:
                get_ai_insights(ai_assistant)
            else:
                print("❌ AI features not available. Please configure OpenAI.")
        elif choice == "2":
            if openai_available:
                ask_ai_question(ai_assistant)
            else:
                print("❌ AI features not available. Please configure OpenAI.")
        elif choice == "3":
            if openai_available:
                get_follow_up_suggestions(ai_assistant)
            else:
                print("❌ AI features not available. Please configure OpenAI.")
        elif choice == "4":
            if openai_available:
                analyze_specific_opportunity(ai_assistant)
            else:
                print("❌ AI features not available. Please configure OpenAI.")
        elif choice == "5":
            if openai_available:
                generate_follow_up_email(ai_assistant)
            else:
                print("❌ AI features not available. Please configure OpenAI.")
        elif choice == "6":
            if openai_available:
                get_career_advice(ai_assistant)
            else:
                print("❌ AI features not available. Please configure OpenAI.")
        elif choice == "7":
            setup_vector_database(ai_assistant)
        elif choice == "8":
            print("Goodbye! 👋")
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 8.")


if __name__ == "__main__":
    main() 