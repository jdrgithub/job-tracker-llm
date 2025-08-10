#!/usr/bin/env python3
"""
Simplified CLI for job tracker without external dependencies.
"""
import json
import os
from pathlib import Path
from datetime import datetime
from typing import List, Optional, Dict, Any


class SimpleJobOpportunity:
    """Simple job opportunity model without pydantic."""
    
    def __init__(self, company: str, role: str, **kwargs):
        self.company = company
        self.role = role
        self.timestamp = kwargs.get('timestamp', datetime.now().isoformat())
        self.recruiter_name = kwargs.get('recruiter_name')
        self.recruiter_contact = kwargs.get('recruiter_contact')
        self.job_description = kwargs.get('job_description')
        self.resume_text = kwargs.get('resume_text')
        self.cover_letter_text = kwargs.get('cover_letter_text')
        self.notes = kwargs.get('notes')
        self.next_steps = kwargs.get('next_steps')
        self.company_link = kwargs.get('company_link')
        self.source = kwargs.get('source')
        self.active = kwargs.get('active', True)
        self.interest_level = kwargs.get('interest_level', 3)
        self.status = kwargs.get('status')
        self.interactions = kwargs.get('interactions', [])
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization."""
        return {
            'company': self.company,
            'role': self.role,
            'timestamp': self.timestamp,
            'recruiter_name': self.recruiter_name,
            'recruiter_contact': self.recruiter_contact,
            'job_description': self.job_description,
            'resume_text': self.resume_text,
            'cover_letter_text': self.cover_letter_text,
            'notes': self.notes,
            'next_steps': self.next_steps,
            'company_link': self.company_link,
            'source': self.source,
            'active': self.active,
            'interest_level': self.interest_level,
            'status': self.status,
            'interactions': self.interactions
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """Create from dictionary."""
        return cls(**data)


class SimpleJobStorage:
    """Simple storage without external dependencies."""
    
    def __init__(self, data_dir: str = "data/opportunities"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    def save_opportunity(self, opportunity: SimpleJobOpportunity) -> str:
        """Save opportunity to JSON file."""
        # Create filename
        safe_company = opportunity.company.lower().replace(' ', '-').replace('/', '-')
        safe_role = opportunity.role.lower().replace(' ', '-').replace('/', '-')
        timestamp = datetime.now().strftime("%Y-%m-%dT%H-%M")
        
        filename = f"{safe_company}_{safe_role}_{timestamp}.json"
        filepath = self.data_dir / filename
        
        # Ensure unique filename
        counter = 1
        original_filepath = filepath
        while filepath.exists():
            name_part = original_filepath.stem
            filepath = self.data_dir / f"{name_part}_{counter}.json"
            counter += 1
        
        # Save to file
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(opportunity.to_dict(), f, indent=2)
        
        print(f"Saved opportunity to: {filepath}")
        return str(filepath)
    
    def load_opportunity(self, filepath: str) -> SimpleJobOpportunity:
        """Load opportunity from JSON file."""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return SimpleJobOpportunity.from_dict(data)
    
    def list_opportunities(self) -> List[Dict[str, Any]]:
        """List all opportunities."""
        opportunities = []
        
        for filepath in self.data_dir.glob("*.json"):
            try:
                opportunity = self.load_opportunity(str(filepath))
                opportunities.append({
                    'filepath': str(filepath),
                    'filename': filepath.name,
                    'company': opportunity.company,
                    'role': opportunity.role,
                    'interest_level': opportunity.interest_level,
                    'active': opportunity.active,
                    'timestamp': opportunity.timestamp
                })
            except Exception as e:
                print(f"Warning: Could not load {filepath}: {e}")
                continue
        
        # Sort by timestamp (newest first)
        opportunities.sort(key=lambda x: x['timestamp'], reverse=True)
        return opportunities


def prompt(question: str, optional: bool = False, default: Optional[str] = None) -> str:
    """Simple prompt function."""
    while True:
        val = input(f"{question}{' (optional)' if optional else ''}: ").strip()
        if val or optional:
            return val if val else default


def prompt_choice(prompt_text: str, choices: List[str], default_choice_index: Optional[int] = None) -> str:
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


def add_opportunity():
    """Add a new job opportunity."""
    print("\n=== Add New Job Opportunity ===")
    
    # Get basic information
    company = prompt("Company name")
    role = prompt("Role/title")
    
    # Get additional details
    recruiter_name = prompt("Recruiter name", optional=True)
    recruiter_contact = prompt("Recruiter email or phone", optional=True)
    job_description = prompt("Job description", optional=True)
    notes = prompt("General notes", optional=True)
    next_steps = prompt("Expected next steps", optional=True)
    source = prompt("Source (e.g., LinkedIn, referral)", optional=True)
    
    # Get interest level
    interest_choices = ["1 - Very Low", "2 - Low", "3 - Medium", "4 - High", "5 - Very High"]
    interest_choice = prompt_choice("Interest level", interest_choices, default_choice_index=2)
    interest_level = int(interest_choice.split(' - ')[0])
    
    # Create opportunity
    opportunity = SimpleJobOpportunity(
        company=company,
        role=role,
        recruiter_name=recruiter_name if recruiter_name else None,
        recruiter_contact=recruiter_contact if recruiter_contact else None,
        job_description=job_description if job_description else None,
        notes=notes if notes else None,
        next_steps=next_steps if next_steps else None,
        source=source if source else None,
        interest_level=interest_level
    )
    
    # Save opportunity
    storage = SimpleJobStorage()
    filepath = storage.save_opportunity(opportunity)
    print(f"✓ Opportunity saved successfully!")


def list_opportunities():
    """List all opportunities."""
    print("\n=== Job Opportunities ===")
    
    storage = SimpleJobStorage()
    opportunities = storage.list_opportunities()
    
    if not opportunities:
        print("No opportunities found.")
        return
    
    print(f"{'#':<3} {'Company':<20} {'Role':<25} {'Interest':<10} {'Status':<10}")
    print("-" * 70)
    
    for i, opp in enumerate(opportunities, 1):
        status = "Active" if opp['active'] else "Inactive"
        print(f"{i:<3} {opp['company']:<20} {opp['role']:<25} {opp['interest_level']:<10} {status:<10}")
    
    print(f"\nTotal opportunities: {len(opportunities)}")


def update_opportunity():
    """Update an existing opportunity."""
    print("\n=== Update Job Opportunity ===")
    
    storage = SimpleJobStorage()
    opportunities = storage.list_opportunities()
    
    if not opportunities:
        print("No opportunities found to update.")
        return
    
    # Show opportunities
    print("Select an opportunity to update:")
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
    
    # Load opportunity
    opportunity = storage.load_opportunity(selected_opp['filepath'])
    
    # Show current details
    print(f"\nCurrent Details:")
    print(f"Company: {opportunity.company}")
    print(f"Role: {opportunity.role}")
    print(f"Interest Level: {opportunity.interest_level}/5")
    print(f"Status: {'Active' if opportunity.active else 'Inactive'}")
    print(f"Next Steps: {opportunity.next_steps or 'None'}")
    
    # Update options
    while True:
        action = prompt_choice("What would you like to do?", [
            "Update interest level",
            "Change next steps",
            "Update recruiter info",
            "Mark as inactive/rejected",
            "View full details",
            "Exit"
        ])
        
        if action == "Update interest level":
            interest_choices = ["1 - Very Low", "2 - Low", "3 - Medium", "4 - High", "5 - Very High"]
            interest_choice = prompt_choice("New interest level", interest_choices, default_choice_index=opportunity.interest_level-1)
            opportunity.interest_level = int(interest_choice.split(' - ')[0])
            print("✓ Interest level updated.")
            
        elif action == "Change next steps":
            opportunity.next_steps = prompt("Updated next steps")
            print("✓ Next steps updated.")
            
        elif action == "Update recruiter info":
            opportunity.recruiter_name = prompt("Recruiter name", default=opportunity.recruiter_name or "")
            opportunity.recruiter_contact = prompt("Recruiter contact", default=opportunity.recruiter_contact or "")
            print("✓ Recruiter info updated.")
            
        elif action == "Mark as inactive/rejected":
            status = prompt_choice("New status:", ["inactive", "rejected"])
            opportunity.active = False
            opportunity.status = status
            print(f"✓ Status set to {status}.")
            
        elif action == "View full details":
            print("\nFull Details:")
            print(f"Company: {opportunity.company}")
            print(f"Role: {opportunity.role}")
            print(f"Recruiter: {opportunity.recruiter_name or 'None'}")
            print(f"Contact: {opportunity.recruiter_contact or 'None'}")
            print(f"Interest Level: {opportunity.interest_level}/5")
            print(f"Status: {'Active' if opportunity.active else opportunity.status}")
            print(f"Source: {opportunity.source or 'None'}")
            print(f"Next Steps: {opportunity.next_steps or 'None'}")
            print(f"Notes: {opportunity.notes or 'None'}")
            
        elif action == "Exit":
            break
    
    # Save changes
    with open(selected_opp['filepath'], 'w', encoding='utf-8') as f:
        json.dump(opportunity.to_dict(), f, indent=2)
    print(f"✓ Changes saved to: {selected_opp['filepath']}")


def show_stats():
    """Show statistics about opportunities."""
    print("\n=== Job Search Statistics ===")
    
    storage = SimpleJobStorage()
    opportunities = storage.list_opportunities()
    
    if not opportunities:
        print("No opportunities found.")
        return
    
    total = len(opportunities)
    active = sum(1 for opp in opportunities if opp['active'])
    inactive = total - active
    avg_interest = sum(opp['interest_level'] for opp in opportunities) / total
    
    print(f"Total Opportunities: {total}")
    print(f"Active Opportunities: {active}")
    print(f"Inactive Opportunities: {inactive}")
    print(f"Average Interest Level: {avg_interest:.1f}/5")


def main():
    """Main CLI function."""
    print("Job Tracker CLI")
    print("=" * 20)
    
    while True:
        print("\nChoose an action:")
        print("1. Add new opportunity")
        print("2. List opportunities")
        print("3. Update opportunity")
        print("4. Show statistics")
        print("5. Exit")
        
        choice = input("\nEnter your choice (1-5): ").strip()
        
        if choice == "1":
            add_opportunity()
        elif choice == "2":
            list_opportunities()
        elif choice == "3":
            update_opportunity()
        elif choice == "4":
            show_stats()
        elif choice == "5":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 5.")


if __name__ == "__main__":
    main() 