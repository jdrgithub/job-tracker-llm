"""
Tests for the job tracker models.
"""
import pytest
from datetime import datetime
from job_tracker_llm.models import (
    JobOpportunity, Interaction, InteractionType, ContactMethod,
    SearchFilters, SearchResult
)


class TestJobOpportunity:
    """Test JobOpportunity model."""
    
    def test_create_opportunity(self):
        """Test creating a basic job opportunity."""
        opportunity = JobOpportunity(
            company="Test Company",
            role="Software Engineer"
        )
        
        assert opportunity.company == "Test Company"
        assert opportunity.role == "Software Engineer"
        assert opportunity.interest_level == 3  # Default
        assert opportunity.active is True
        assert len(opportunity.interactions) == 0
    
    def test_interest_level_validation(self):
        """Test interest level validation."""
        # Valid interest levels
        for level in [1, 2, 3, 4, 5]:
            opportunity = JobOpportunity(
                company="Test",
                role="Test",
                interest_level=level
            )
            assert opportunity.interest_level == level
        
        # Invalid interest levels should raise ValueError
        with pytest.raises(ValueError):
            JobOpportunity(company="Test", role="Test", interest_level=0)
        
        with pytest.raises(ValueError):
            JobOpportunity(company="Test", role="Test", interest_level=6)
    
    def test_email_validation(self):
        """Test email validation."""
        # Valid email
        opportunity = JobOpportunity(
            company="Test",
            role="Test",
            recruiter_contact="test@example.com"
        )
        assert opportunity.recruiter_contact == "test@example.com"
        
        # Invalid email should raise ValueError
        with pytest.raises(ValueError):
            JobOpportunity(
                company="Test",
                role="Test",
                recruiter_contact="invalid-email"
            )
    
    def test_add_interaction(self):
        """Test adding interactions."""
        opportunity = JobOpportunity(company="Test", role="Test")
        
        interaction = Interaction(
            type=InteractionType.FOLLOW_UP,
            notes="Test interaction"
        )
        
        opportunity.add_interaction(interaction)
        
        assert len(opportunity.interactions) == 1
        assert opportunity.interactions[0].type == InteractionType.FOLLOW_UP
        assert opportunity.interactions[0].notes == "Test interaction"
    
    def test_get_latest_interaction(self):
        """Test getting the latest interaction."""
        opportunity = JobOpportunity(company="Test", role="Test")
        
        # No interactions
        assert opportunity.get_latest_interaction() is None
        
        # Add interactions
        interaction1 = Interaction(type=InteractionType.INITIAL_CONTACT)
        interaction2 = Interaction(type=InteractionType.FOLLOW_UP)
        
        opportunity.add_interaction(interaction1)
        opportunity.add_interaction(interaction2)
        
        latest = opportunity.get_latest_interaction()
        assert latest.type == InteractionType.FOLLOW_UP
    
    def test_is_overdue_followup(self):
        """Test overdue follow-up detection."""
        opportunity = JobOpportunity(company="Test", role="Test")
        
        # No interactions
        assert not opportunity.is_overdue_followup()
        
        # Recent interaction
        recent_interaction = Interaction(type=InteractionType.INITIAL_CONTACT)
        opportunity.add_interaction(recent_interaction)
        assert not opportunity.is_overdue_followup(days_threshold=7)
        
        # Old interaction
        old_interaction = Interaction(type=InteractionType.INITIAL_CONTACT)
        old_interaction.date = datetime(2020, 1, 1)  # Very old
        opportunity.interactions = [old_interaction]
        assert opportunity.is_overdue_followup(days_threshold=7)
        
        # Inactive opportunity
        opportunity.active = False
        assert not opportunity.is_overdue_followup(days_threshold=7)


class TestInteraction:
    """Test Interaction model."""
    
    def test_create_interaction(self):
        """Test creating an interaction."""
        interaction = Interaction(
            type=InteractionType.INTERVIEW_SCREEN,
            method=ContactMethod.RECRUITER_EMAIL,
            notes="Test interview"
        )
        
        assert interaction.type == InteractionType.INTERVIEW_SCREEN
        assert interaction.method == ContactMethod.RECRUITER_EMAIL
        assert interaction.notes == "Test interview"
        assert isinstance(interaction.date, datetime)


class TestSearchFilters:
    """Test SearchFilters model."""
    
    def test_create_filters(self):
        """Test creating search filters."""
        filters = SearchFilters(
            company="Test Company",
            active_only=True,
            min_interest_level=3
        )
        
        assert filters.company == "Test Company"
        assert filters.active_only is True
        assert filters.min_interest_level == 3
    
    def test_interest_level_validation(self):
        """Test interest level validation in filters."""
        # Valid levels
        for level in [1, 2, 3, 4, 5]:
            filters = SearchFilters(min_interest_level=level)
            assert filters.min_interest_level == level
        
        # Invalid levels
        with pytest.raises(ValueError):
            SearchFilters(min_interest_level=0)
        
        with pytest.raises(ValueError):
            SearchFilters(max_interest_level=6)


class TestEnums:
    """Test enum values."""
    
    def test_interaction_types(self):
        """Test interaction type enum values."""
        assert InteractionType.INITIAL_CONTACT == "initial_contact"
        assert InteractionType.FOLLOW_UP == "follow_up"
        assert InteractionType.INTERVIEW_SCREEN == "interview_screen"
        assert InteractionType.INTERVIEW_TECHNICAL == "interview_technical"
        assert InteractionType.INTERVIEW_FINAL == "interview_final"
        assert InteractionType.REJECTION == "rejection"
        assert InteractionType.OFFER == "offer"
        assert InteractionType.OTHER == "other"
    
    def test_contact_methods(self):
        """Test contact method enum values."""
        assert ContactMethod.RECRUITER_EMAIL == "recruiter_email"
        assert ContactMethod.RECRUITER_CALL == "recruiter_call"
        assert ContactMethod.INBOUND_APPLICATION == "inbound_application"
        assert ContactMethod.LINKEDIN_MESSAGE == "linkedin_message"
        assert ContactMethod.REFERRAL == "referral"
