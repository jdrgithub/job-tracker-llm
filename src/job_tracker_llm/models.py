"""
Data models for the job tracker application.
"""
from datetime import datetime
from typing import List, Optional, Literal
from pydantic import BaseModel, Field, validator, EmailStr
from enum import Enum


class InteractionType(str, Enum):
    """Types of interactions with recruiters/companies."""
    INITIAL_CONTACT = "initial_contact"
    FOLLOW_UP = "follow_up"
    INTERVIEW_SCREEN = "interview_screen"
    INTERVIEW_TECHNICAL = "interview_technical"
    INTERVIEW_FINAL = "interview_final"
    REJECTION = "rejection"
    OFFER = "offer"
    OTHER = "other"
    
    @classmethod
    def _missing_(cls, value):
        """Handle backward compatibility for old interaction types."""
        # Map old values to new ones
        mapping = {
            "interview": "interview_screen",
            "recruiter_email": "initial_contact",
            "recruiter_call": "initial_contact",
            "email": "initial_contact",
            "phone": "initial_contact",
            "linkedin": "initial_contact"
        }
        if value in mapping:
            return cls(mapping[value])
        return cls.OTHER


class ContactMethod(str, Enum):
    """Methods of contact."""
    RECRUITER_EMAIL = "recruiter_email"
    RECRUITER_CALL = "recruiter_call"
    INBOUND_APPLICATION = "inbound_application"
    LINKEDIN_MESSAGE = "linkedin_message"
    REFERRAL = "referral"


class Interaction(BaseModel):
    """Represents a single interaction with a recruiter or company."""
    date: datetime = Field(default_factory=datetime.now)
    type: InteractionType
    method: Optional[ContactMethod] = None
    notes: Optional[str] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class JobOpportunity(BaseModel):
    """Represents a job opportunity with all associated metadata."""
    timestamp: datetime = Field(default_factory=datetime.now)
    company: str = Field(..., min_length=1, description="Company name")
    role: str = Field(..., min_length=1, description="Job role/title")
    recruiter_name: Optional[str] = None
    recruiter_contact: Optional[str] = None
    job_description: Optional[str] = None
    resume_text: Optional[str] = None
    cover_letter_text: Optional[str] = None
    notes: Optional[str] = None
    next_steps: Optional[str] = None
    company_link: Optional[str] = None
    source: Optional[str] = None
    active: bool = True
    interest_level: int = Field(3, ge=1, le=5, description="Interest level from 1-5")
    interactions: List[Interaction] = Field(default_factory=list)
    status: Optional[str] = None
    
    @validator('interest_level')
    def validate_interest_level(cls, v):
        if not 1 <= v <= 5:
            raise ValueError('Interest level must be between 1 and 5')
        return v
    
    @validator('recruiter_contact')
    def validate_contact(cls, v):
        if v and '@' in v:
            # Basic email validation
            if not v.count('@') == 1 or not '.' in v.split('@')[1]:
                raise ValueError('Invalid email format')
        return v
    
    def add_interaction(self, interaction: Interaction):
        """Add a new interaction to this opportunity."""
        self.interactions.append(interaction)
    
    def get_latest_interaction(self) -> Optional[Interaction]:
        """Get the most recent interaction."""
        if not self.interactions:
            return None
        return max(self.interactions, key=lambda x: x.date)
    
    def is_overdue_followup(self, days_threshold: int = 7) -> bool:
        """Check if this opportunity needs a follow-up."""
        if not self.interactions:
            return False
        
        latest = self.get_latest_interaction()
        if not latest:
            return False
        
        days_since = (datetime.now() - latest.date).days
        return days_since > days_threshold and self.active
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class SearchFilters(BaseModel):
    """Filters for searching opportunities."""
    company: Optional[str] = None
    role: Optional[str] = None
    recruiter: Optional[str] = None
    active_only: bool = True
    min_interest_level: Optional[int] = None
    max_interest_level: Optional[int] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    status: Optional[str] = None
    
    @validator('min_interest_level', 'max_interest_level')
    def validate_interest_levels(cls, v):
        if v is not None and not 1 <= v <= 5:
            raise ValueError('Interest level must be between 1 and 5')
        return v


class SearchResult(BaseModel):
    """Result of a search operation."""
    opportunity: JobOpportunity
    relevance_score: Optional[float] = None
    filename: str
