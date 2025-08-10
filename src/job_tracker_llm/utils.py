"""
Utility functions for the job tracker application.
"""
import re
from typing import List, Optional, Any
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


def prompt(question: str, optional: bool = False, default: Optional[str] = None) -> str:
    """Prompt user for input with optional validation."""
    while True:
        val = input(f"{question}{' (optional)' if optional else ''}: ").strip()
        if val or optional:
            return val if val else default


def prompt_choice(prompt_text: str, choices: List[str], default_choice_index: Optional[int] = None) -> str:
    """
    Display a list of choices to the user and prompt them to pick one.
    
    Args:
        prompt_text: The question or instruction to show before the choices
        choices: The list of choices to present
        default_choice_index: The zero-based index of the default choice, or None
    
    Returns:
        The selected choice string
    """
    # Print the question or prompt
    print(f"\n{prompt_text}")

    # Loop through choices using 0-based index for logic, but display 1-based numbers
    for zero_index, choice_text in enumerate(choices):
        # Convert 0-based index to 1-based number for human-friendly display
        displayed_number = zero_index + 1

        # Determine whether this choice is the default
        is_default_choice = (default_choice_index == zero_index)

        # Add " (default)" to the label if this is the default
        label_suffix = " (default)" if is_default_choice else ""

        # Print the full line for this choice
        print(f"{displayed_number}. {choice_text}{label_suffix}")

    # Loop until valid user input is received
    while True:
        user_input = input("Choose a number: ").strip()

        # If user presses Enter without typing anything AND a default is allowed
        if not user_input and default_choice_index is not None:
            return choices[default_choice_index]

        # If user entered a valid number in the range of displayed choices
        if user_input.isdigit():
            selected_number = int(user_input)

            if 1 <= selected_number <= len(choices):
                # Convert 1-based selection back to 0-based index
                selected_index = selected_number - 1
                return choices[selected_index]

        # If we reach here, input was invalid — try again
        print("Invalid selection. Please enter a number from the list.")


def validate_email(email: str) -> bool:
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_phone(phone: str) -> bool:
    """Validate phone number format."""
    # Remove all non-digit characters
    digits_only = re.sub(r'\D', '', phone)
    # Check if it's a reasonable length (7-15 digits)
    return 7 <= len(digits_only) <= 15


def validate_url(url: str) -> bool:
    """Validate URL format."""
    pattern = r'^https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:[\w.])*)?)?$'
    return bool(re.match(pattern, url))


def format_date(date: datetime) -> str:
    """Format date for display."""
    return date.strftime("%Y-%m-%d %H:%M")


def format_duration(duration: timedelta) -> str:
    """Format duration for display."""
    days = duration.days
    hours = duration.seconds // 3600
    
    if days > 0:
        return f"{days} day{'s' if days != 1 else ''}"
    elif hours > 0:
        return f"{hours} hour{'s' if hours != 1 else ''}"
    else:
        minutes = (duration.seconds % 3600) // 60
        return f"{minutes} minute{'s' if minutes != 1 else ''}"


def calculate_days_since(date: datetime) -> int:
    """Calculate days since a given date."""
    return (datetime.now() - date).days


def get_interest_level_description(level: int) -> str:
    """Get a description for an interest level."""
    descriptions = {
        1: "Very Low - Not interested",
        2: "Low - Minimal interest",
        3: "Medium - Somewhat interested",
        4: "High - Very interested",
        5: "Very High - Extremely interested"
    }
    return descriptions.get(level, "Unknown")


def get_status_color(status: str) -> str:
    """Get color for status display."""
    colors = {
        "active": "green",
        "inactive": "yellow",
        "rejected": "red",
        "offer": "blue",
        "interview": "cyan"
    }
    return colors.get(status.lower(), "white")


def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate text to a maximum length."""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."


def safe_filename(name: str) -> str:
    """Convert a string to a safe filename."""
    # Replace problematic characters
    safe = re.sub(r'[<>:"/\\|?*]', '-', name)
    # Replace multiple spaces/hyphens with single
    safe = re.sub(r'[\s-]+', '-', safe)
    # Remove leading/trailing hyphens
    safe = safe.strip('-')
    return safe.lower()


def parse_date_range(date_range: str) -> tuple[Optional[datetime], Optional[datetime]]:
    """Parse a date range string (e.g., '2024-01-01 to 2024-12-31')."""
    try:
        if ' to ' in date_range:
            start_str, end_str = date_range.split(' to ', 1)
            start_date = datetime.strptime(start_str.strip(), '%Y-%m-%d')
            end_date = datetime.strptime(end_str.strip(), '%Y-%m-%d')
            return start_date, end_date
        else:
            # Single date
            date = datetime.strptime(date_range.strip(), '%Y-%m-%d')
            return date, date
    except ValueError:
        logger.warning(f"Invalid date format: {date_range}")
        return None, None


def generate_filename(company: str, role: str) -> str:
    """Generate a filename for a job opportunity."""
    safe_company = safe_filename(company)
    safe_role = safe_filename(role)
    timestamp = datetime.now().strftime("%Y-%m-%dT%H-%M")
    return f"{safe_company}_{safe_role}_{timestamp}.json"


def format_currency(amount: Optional[float]) -> str:
    """Format currency amount."""
    if amount is None:
        return "Not specified"
    return f"${amount:,.0f}"


def parse_salary_range(salary_text: str) -> tuple[Optional[float], Optional[float]]:
    """Parse salary range from text."""
    if not salary_text:
        return None, None
    
    # Common patterns
    patterns = [
        r'\$(\d{1,3}(?:,\d{3})*(?:k)?)\s*-\s*\$(\d{1,3}(?:,\d{3})*(?:k)?)',
        r'(\d{1,3}(?:,\d{3})*(?:k)?)\s*-\s*(\d{1,3}(?:,\d{3})*(?:k)?)',
        r'\$(\d{1,3}(?:,\d{3})*(?:k)?)',
        r'(\d{1,3}(?:,\d{3})*(?:k)?)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, salary_text, re.IGNORECASE)
        if match:
            try:
                if len(match.groups()) == 2:
                    min_salary = parse_salary_amount(match.group(1))
                    max_salary = parse_salary_amount(match.group(2))
                    return min_salary, max_salary
                else:
                    salary = parse_salary_amount(match.group(1))
                    return salary, salary
            except ValueError:
                continue
    
    return None, None


def parse_salary_amount(amount_str: str) -> float:
    """Parse a salary amount string to float."""
    # Remove $ and commas
    clean = re.sub(r'[$,]', '', amount_str.lower())
    
    # Handle 'k' suffix (thousands)
    if clean.endswith('k'):
        return float(clean[:-1]) * 1000
    
    return float(clean)


def get_interaction_type_display_name(interaction_type: str) -> str:
    """Get a display name for an interaction type."""
    display_names = {
        "initial_contact": "Initial Contact",
        "follow_up": "Follow-up",
        "interview_screen": "Screening Interview",
        "interview_technical": "Technical Interview",
        "interview_final": "Final Interview",
        "rejection": "Rejection",
        "offer": "Offer",
        "other": "Other"
    }
    return display_names.get(interaction_type, interaction_type.title())


def get_contact_method_display_name(method: str) -> str:
    """Get a display name for a contact method."""
    display_names = {
        "recruiter_email": "Recruiter Email",
        "recruiter_call": "Recruiter Call",
        "inbound_application": "Inbound Application",
        "linkedin_message": "LinkedIn Message",
        "referral": "Referral"
    }
    return display_names.get(method, method.title())


def calculate_response_time(interactions: List[dict]) -> Optional[int]:
    """Calculate average response time in days."""
    if len(interactions) < 2:
        return None
    
    response_times = []
    for i in range(1, len(interactions)):
        try:
            prev_date = datetime.fromisoformat(interactions[i-1]['date'])
            curr_date = datetime.fromisoformat(interactions[i]['date'])
            days = (curr_date - prev_date).days
            if days >= 0:  # Only count positive time differences
                response_times.append(days)
        except (ValueError, KeyError):
            continue
    
    if response_times:
        return sum(response_times) // len(response_times)
    return None
