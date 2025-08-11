#!/usr/bin/env python3
"""
Job Tracker LLM - Interactive Menu Interface

Provides a unified menu-based interface for job opportunity tracking
with AI-powered insights and analysis capabilities.
"""

import sys
import os
from pathlib import Path
from typing import Optional, List

# Ensure we can import our modules
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

try:
    from .models import JobOpportunity
    from .storage import JobStorage
    from .utils import prompt_choice, prompt, validate_interest_level
    from .vector_store import JobVectorStore
    from .ai_assistant import JobTrackerAI
except ImportError:
    from models import JobOpportunity
    from storage import JobStorage
    from utils import prompt_choice, prompt, validate_interest_level
    from vector_store import JobVectorStore
    from ai_assistant import JobTrackerAI


class JobTrackerMenu:
    """Interactive menu interface for job tracking functionality."""
    
    def __init__(self):
        """Initialize the menu with all required components."""
        self.storage = JobStorage()
        self.vector_store = JobVectorStore(self.storage)
        self.storage.set_vector_store(self.vector_store)
        self.ai_assistant = JobTrackerAI(self.storage, self.vector_store)
        self.running = True
    
    def display_main_menu(self) -> None:
        """Display the main application menu."""
        print("\n🤖 Job Tracker LLM")
        print("=" * 40)
        print("1. Add job opportunity")
        print("2. List opportunities")
        print("3. Search opportunities")
        print("4. Update opportunity")
        print("5. Show statistics")
        print("6. Export data")
        print("7. AI features")
        print("8. Setup AI")
        print("9. Exit")
        print("=" * 40)
    
    def display_ai_menu(self) -> None:
        """Display the AI features submenu."""
        print("\n🤖 AI Features")
        print("=" * 25)
        print("1. Get job search insights")
        print("2. Ask AI about opportunities")
        print("3. Get follow-up suggestions")
        print("4. Analyze specific opportunity")
        print("5. Generate follow-up email")
        print("6. Get career advice")
        print("7. Extract job details from description")
        print("8. Generate follow-up strategy")
        print("9. Back to main menu")
        print("=" * 25)
    
    def add_opportunity(self) -> None:
        """Add a new job opportunity with user input validation."""
        print("\n📝 Add New Job Opportunity")
        print("-" * 30)
        
        # Collect required information
        company = prompt("Company", required=True)
        role = prompt("Role/Position", required=True)
        
        # Collect optional information
        recruiter_name = prompt("Recruiter Name", required=False)
        recruiter_contact = prompt("Recruiter Contact", required=False)
        notes = prompt("Notes", required=False)
        
        # Get interest level with validation
        interest_level = validate_interest_level()
        
        # Create and save the opportunity
        opportunity = JobOpportunity(
            company=company,
            role=role,
            recruiter_name=recruiter_name,
            recruiter_contact=recruiter_contact,
            interest_level=interest_level,
            notes=notes
        )
        
        if self.storage.save_opportunity(opportunity):
            print("✅ Opportunity added successfully!")
        else:
            print("❌ Failed to add opportunity")
    
    def list_opportunities(self) -> None:
        """Display all job opportunities in a formatted list."""
        print("\n📋 Job Opportunities")
        print("-" * 25)
        
        opportunities = self.storage.list_opportunities()
        if not opportunities:
            print("No opportunities found.")
            return
        
        for i, opportunity in enumerate(opportunities, 1):
            self._display_opportunity_summary(i, opportunity)
    
    def _display_opportunity_summary(self, index: int, opportunity: JobOpportunity) -> None:
        """Display a single opportunity in a formatted way."""
        status = "🟢 Active" if opportunity.active else "🔴 Inactive"
        interest_stars = "🔥" * opportunity.interest_level
        
        print(f"{index}. {opportunity.company} - {opportunity.role}")
        print(f"   Interest: {interest_stars} ({opportunity.interest_level}/5) | {status}")
        
        if opportunity.recruiter_name:
            print(f"   Recruiter: {opportunity.recruiter_name}")
        
        print()
    
    def search_opportunities(self, query: Optional[str] = None) -> None:
        """Search opportunities with optional query parameter."""
        if not query:
            query = prompt("Search query", required=True)
        
        print(f"\n🔍 Search Results for: '{query}'")
        print("-" * 40)
        
        results = self.storage.search_opportunities(query)
        if not results:
            print("No opportunities found matching your search.")
            return
        
        for i, opportunity in enumerate(results, 1):
            print(f"{i}. {opportunity.company} - {opportunity.role}")
            print(f"   Interest: {'🔥' * opportunity.interest_level} ({opportunity.interest_level}/5)")
            print()
    
    def update_opportunity(self) -> None:
        """Update an existing job opportunity."""
        print("\n✏️  Update Opportunity")
        print("-" * 25)
        
        opportunities = self.storage.list_opportunities()
        if not opportunities:
            print("No opportunities to update.")
            return
        
        # Display opportunities for selection
        for i, opportunity in enumerate(opportunities, 1):
            print(f"{i}. {opportunity.company} - {opportunity.role}")
        
        # Get user selection
        choice = prompt_choice("Select opportunity to update", len(opportunities))
        if choice is None:
            return
        
        opportunity = opportunities[choice - 1]
        self._update_opportunity_fields(opportunity)
    
    def _update_opportunity_fields(self, opportunity: JobOpportunity) -> None:
        """Update specific fields of an opportunity."""
        print(f"\nUpdating: {opportunity.company} - {opportunity.role}")
        print("-" * 45)
        print("Press Enter to keep current value, or type new value:")
        
        # Update fields with current values as defaults
        opportunity.company = prompt(f"Company [{opportunity.company}]", default=opportunity.company)
        opportunity.role = prompt(f"Role [{opportunity.role}]", default=opportunity.role)
        opportunity.recruiter_name = prompt(f"Recruiter Name [{opportunity.recruiter_name or ''}]", 
                                          default=opportunity.recruiter_name)
        
        # Handle interest level separately due to validation
        interest_input = prompt(f"Interest Level [{opportunity.interest_level}]", required=False)
        if interest_input:
            new_interest = validate_interest_level(interest_input)
            if new_interest is not None:
                opportunity.interest_level = new_interest
        
        # Find the filepath for this opportunity
        basic_info = self.storage._list_opportunities_basic()
        filepath = None
        for info in basic_info:
            if (info['company'] == opportunity.company and 
                info['role'] == opportunity.role and
                info['timestamp'] == opportunity.timestamp):
                filepath = info['filepath']
                break
        
        if filepath:
            # Save the updated opportunity
            if self.storage.update_opportunity(opportunity, filepath):
                print("✅ Opportunity updated successfully!")
            else:
                print("❌ Failed to update opportunity")
        else:
            print("❌ Could not find opportunity file")
    
    def show_statistics(self) -> None:
        """Display comprehensive job search statistics."""
        print("\n📊 Job Search Statistics")
        print("-" * 30)
        
        stats = self.storage.get_statistics()
        
        print(f"Total Opportunities: {stats.get('total', 0)}")
        print(f"Active: {stats.get('active', 0)}")
        print(f"Inactive: {stats.get('inactive', 0)}")
        print(f"Average Interest Level: {stats.get('avg_interest', 0):.1f}/5")
        
        if stats.get('total', 0) > 0:
            print(f"Highest Interest: {stats.get('max_interest', 0)}/5")
            print(f"Lowest Interest: {stats.get('min_interest', 0)}/5")
    
    def export_data(self) -> None:
        """Export job data to CSV format."""
        print("\n📤 Export Data")
        print("-" * 15)
        
        filename = prompt("Export filename", default="job_opportunities.csv")
        
        if self.storage.export_to_csv(filename):
            print(f"✅ Data exported to {filename}")
        else:
            print("❌ Failed to export data")
    
    def handle_ai_features(self) -> None:
        """Handle the AI features submenu."""
        while True:
            self.display_ai_menu()
            choice = prompt_choice("Enter your choice", 9)
            
            if choice is None:
                continue
            
            if choice == 1:
                self._get_ai_insights()
            elif choice == 2:
                self._ask_ai_about_opportunities()
            elif choice == 3:
                self._get_follow_up_suggestions()
            elif choice == 4:
                self._analyze_opportunity()
            elif choice == 5:
                self._generate_email()
            elif choice == 6:
                self._get_career_advice()
            elif choice == 7:
                self._extract_job_details()
            elif choice == 8:
                self._generate_follow_up_strategy()
            elif choice == 9:
                break
    
    def _get_ai_insights(self) -> None:
        """Get AI-powered job search insights."""
        print("\n🤖 Getting AI insights...")
        insights = self.ai_assistant.get_job_search_insights()
        print(f"\n{insights}")
        input("\nPress Enter to continue...")
    
    def _ask_ai_about_opportunities(self) -> None:
        """Ask AI questions about opportunities."""
        question = prompt("What would you like to ask about your opportunities?", required=True)
        
        print("\n🤖 AI Response:")
        response = self.ai_assistant.ask_about_opportunities(question)
        print(response)
        input("\nPress Enter to continue...")
    
    def _get_follow_up_suggestions(self) -> None:
        """Get AI-generated follow-up suggestions."""
        print("\n🤖 Getting follow-up suggestions...")
        suggestions = self.ai_assistant.get_follow_up_suggestions()
        print(f"\n{suggestions}")
        input("\nPress Enter to continue...")
    
    def _analyze_opportunity(self) -> None:
        """Analyze a specific opportunity with AI."""
        opportunities = self.storage.list_opportunities()
        if not opportunities:
            print("No opportunities to analyze.")
            return
        
        print("\nSelect opportunity to analyze:")
        for i, opportunity in enumerate(opportunities, 1):
            print(f"{i}. {opportunity.company} - {opportunity.role}")
        
        choice = prompt_choice("Select opportunity", len(opportunities))
        if choice is None:
            return
        
        opportunity = opportunities[choice - 1]
        print(f"\n🤖 Analyzing {opportunity.company}...")
        analysis = self.ai_assistant.analyze_opportunity(opportunity)
        print(f"\n{analysis}")
        input("\nPress Enter to continue...")
    
    def _generate_email(self) -> None:
        """Generate a follow-up email using AI."""
        opportunities = self.storage.list_opportunities()
        if not opportunities:
            print("No opportunities to generate email for.")
            return
        
        print("\nSelect opportunity for email:")
        for i, opportunity in enumerate(opportunities, 1):
            print(f"{i}. {opportunity.company} - {opportunity.role}")
        
        choice = prompt_choice("Select opportunity", len(opportunities))
        if choice is None:
            return
        
        opportunity = opportunities[choice - 1]
        print(f"\n🤖 Generating email for {opportunity.company}...")
        email = self.ai_assistant.generate_follow_up_email(opportunity)
        print(f"\n{email}")
        input("\nPress Enter to continue...")
    
    def _get_career_advice(self) -> None:
        """Get AI-powered career advice."""
        print("\n🤖 Getting career advice...")
        advice = self.ai_assistant.get_career_advice()
        print(f"\n{advice}")
        input("\nPress Enter to continue...")
    
    def _extract_job_details(self) -> None:
        """Extract job details from a job description."""
        opportunities = self.storage.list_opportunities()
        if not opportunities:
            print("No opportunities found. Please add an opportunity first.")
            return
        
        print("\nSelect opportunity to add job details to:")
        for i, opportunity in enumerate(opportunities, 1):
            print(f"{i}. {opportunity.company} - {opportunity.role}")
        
        choice = prompt_choice("Select opportunity", len(opportunities))
        if choice is None:
            return
        
        opportunity = opportunities[choice - 1]
        description = prompt("Enter the job description:", required=True)
        
        print(f"\n🤖 Extracting job details for {opportunity.company}...")
        result = self.ai_assistant.add_job_details_from_description(opportunity, description)
        print(f"\n{result}")
        input("\nPress Enter to continue...")
    
    def _generate_follow_up_strategy(self) -> None:
        """Generate a follow-up strategy for a specific opportunity."""
        opportunities = self.storage.list_opportunities()
        if not opportunities:
            print("No opportunities to generate follow-up strategy for.")
            return
        
        print("\nSelect opportunity for strategy:")
        for i, opportunity in enumerate(opportunities, 1):
            print(f"{i}. {opportunity.company} - {opportunity.role}")
        
        choice = prompt_choice("Select opportunity", len(opportunities))
        if choice is None:
            return
        
        opportunity = opportunities[choice - 1]
        print(f"\n🤖 Generating follow-up strategy for {opportunity.company}...")
        strategy = self.ai_assistant.generate_follow_up_strategy(opportunity)
        print(f"\n{strategy}")
        input("\nPress Enter to continue...")
    
    def setup_ai(self) -> None:
        """Setup and test AI functionality."""
        print("\n🔧 AI Setup")
        print("-" * 15)
        
        # Check OpenAI API key
        if not os.getenv('OPENAI_API_KEY'):
            print("❌ OPENAI_API_KEY not set")
            print("Set it with: export OPENAI_API_KEY='your-api-key-here'")
            return
        
        print("✅ OpenAI API key found")
        
        # Test AI functionality
        print("Testing AI features...")
        try:
            insights = self.ai_assistant.get_job_search_insights()
            if insights and not insights.startswith("Error"):
                print("✅ AI features working!")
            else:
                print("❌ AI features not working properly")
        except Exception as e:
            print(f"❌ AI setup failed: {e}")
    
    def handle_main_menu(self) -> None:
        """Handle the main menu selection and routing."""
        choice = prompt_choice("Enter your choice", 9)
        
        if choice is None:
            return
        
        if choice == 1:
            self.add_opportunity()
        elif choice == 2:
            self.list_opportunities()
        elif choice == 3:
            self.search_opportunities()
        elif choice == 4:
            self.update_opportunity()
        elif choice == 5:
            self.show_statistics()
        elif choice == 6:
            self.export_data()
        elif choice == 7:
            self.handle_ai_features()
        elif choice == 8:
            self.setup_ai()
        elif choice == 9:
            print("Goodbye! 👋")
            self.running = False
    
    def run(self) -> int:
        """Main application loop."""
        try:
            while self.running:
                self.display_main_menu()
                self.handle_main_menu()
                
                if self.running:
                    input("\nPress Enter to continue...")
            
            return 0
        except KeyboardInterrupt:
            print("\n\nGoodbye! 👋")
            return 0
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")
            return 1


def main() -> int:
    """Application entry point."""
    menu = JobTrackerMenu()
    return menu.run()


if __name__ == "__main__":
    sys.exit(main()) 