"""
Storage operations for job opportunities.
"""
import json
import os
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging

from .models import JobOpportunity, Interaction, InteractionType, ContactMethod

logger = logging.getLogger(__name__)


class JobStorage:
    """Handles storage operations for job opportunities."""
    
    def __init__(self, data_dir: str = "data/opportunities"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    def save_opportunity(self, opportunity: JobOpportunity) -> str:
        """Save a job opportunity to a JSON file."""
        try:
            # Create filename from company and role
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
                json.dump(opportunity.dict(), f, indent=2, default=str)
            
            logger.info(f"Saved opportunity to {filepath}")
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Error saving opportunity: {e}")
            raise
    
    def load_opportunity(self, filepath: str) -> JobOpportunity:
        """Load a job opportunity from a JSON file."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Convert string dates back to datetime objects
            if 'timestamp' in data and isinstance(data['timestamp'], str):
                data['timestamp'] = datetime.fromisoformat(data['timestamp'])
            
            # Convert interaction dates
            if 'interactions' in data:
                for interaction in data['interactions']:
                    if 'date' in interaction and isinstance(interaction['date'], str):
                        interaction['date'] = datetime.fromisoformat(interaction['date'])
            
            return JobOpportunity(**data)
            
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in {filepath}: {e}")
            raise
        except Exception as e:
            logger.error(f"Error loading opportunity from {filepath}: {e}")
            raise
    
    def update_opportunity(self, filepath: str, opportunity: JobOpportunity) -> None:
        """Update an existing job opportunity."""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(opportunity.dict(), f, indent=2, default=str)
            logger.info(f"Updated opportunity at {filepath}")
        except Exception as e:
            logger.error(f"Error updating opportunity at {filepath}: {e}")
            raise
    
    def list_opportunities(self) -> List[Dict[str, Any]]:
        """List all job opportunities with basic info."""
        opportunities = []
        
        try:
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
                        'timestamp': opportunity.timestamp,
                        'latest_interaction': opportunity.get_latest_interaction()
                    })
                except Exception as e:
                    logger.warning(f"Could not load {filepath}: {e}")
                    continue
            
            # Sort by timestamp (newest first)
            opportunities.sort(key=lambda x: x['timestamp'], reverse=True)
            return opportunities
            
        except Exception as e:
            logger.error(f"Error listing opportunities: {e}")
            raise
    
    def search_opportunities(self, 
                           company: Optional[str] = None,
                           role: Optional[str] = None,
                           recruiter: Optional[str] = None,
                           active_only: bool = True,
                           min_interest: Optional[int] = None,
                           max_interest: Optional[int] = None) -> List[Dict[str, Any]]:
        """Search opportunities based on criteria."""
        all_opportunities = self.list_opportunities()
        filtered = []
        
        for opp in all_opportunities:
            # Load full opportunity for detailed search
            try:
                opportunity = self.load_opportunity(opp['filepath'])
            except Exception:
                continue
            
            # Apply filters
            if company and company.lower() not in opportunity.company.lower():
                continue
            if role and role.lower() not in opportunity.role.lower():
                continue
            if recruiter and opportunity.recruiter_name:
                if recruiter.lower() not in opportunity.recruiter_name.lower():
                    continue
            if active_only and not opportunity.active:
                continue
            if min_interest and opportunity.interest_level < min_interest:
                continue
            if max_interest and opportunity.interest_level > max_interest:
                continue
            
            filtered.append(opp)
        
        return filtered
    
    def delete_opportunity(self, filepath: str) -> bool:
        """Delete a job opportunity file."""
        try:
            path = Path(filepath)
            if path.exists():
                path.unlink()
                logger.info(f"Deleted opportunity at {filepath}")
                return True
            else:
                logger.warning(f"File not found: {filepath}")
                return False
        except Exception as e:
            logger.error(f"Error deleting opportunity at {filepath}: {e}")
            return False
    
    def get_overdue_followups(self, days_threshold: int = 7) -> List[Dict[str, Any]]:
        """Get opportunities that need follow-up."""
        opportunities = self.list_opportunities()
        overdue = []
        
        for opp in opportunities:
            try:
                opportunity = self.load_opportunity(opp['filepath'])
                if opportunity.is_overdue_followup(days_threshold):
                    overdue.append(opp)
            except Exception:
                continue
        
        return overdue
    
    def export_to_csv(self, filepath: str) -> None:
        """Export all opportunities to CSV format."""
        import csv
        
        opportunities = self.list_opportunities()
        
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = [
                'company', 'role', 'recruiter_name', 'recruiter_contact',
                'interest_level', 'active', 'status', 'source',
                'timestamp', 'next_steps', 'notes'
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for opp in opportunities:
                try:
                    opportunity = self.load_opportunity(opp['filepath'])
                    writer.writerow({
                        'company': opportunity.company,
                        'role': opportunity.role,
                        'recruiter_name': opportunity.recruiter_name or '',
                        'recruiter_contact': opportunity.recruiter_contact or '',
                        'interest_level': opportunity.interest_level,
                        'active': opportunity.active,
                        'status': opportunity.status or '',
                        'source': opportunity.source or '',
                        'timestamp': opportunity.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                        'next_steps': opportunity.next_steps or '',
                        'notes': opportunity.notes or ''
                    })
                except Exception as e:
                    logger.warning(f"Could not export opportunity {opp['filepath']}: {e}")
                    continue
        
        logger.info(f"Exported {len(opportunities)} opportunities to {filepath}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about all opportunities."""
        opportunities = self.list_opportunities()
        
        if not opportunities:
            return {
                'total': 0,
                'active': 0,
                'inactive': 0,
                'avg_interest': 0,
                'by_status': {},
                'by_source': {}
            }
        
        stats = {
            'total': len(opportunities),
            'active': sum(1 for opp in opportunities if opp['active']),
            'inactive': sum(1 for opp in opportunities if not opp['active']),
            'avg_interest': sum(opp['interest_level'] for opp in opportunities) / len(opportunities),
            'by_status': {},
            'by_source': {}
        }
        
        # Count by status and source
        for opp in opportunities:
            try:
                opportunity = self.load_opportunity(opp['filepath'])
                
                # Status
                status = opportunity.status or 'unknown'
                stats['by_status'][status] = stats['by_status'].get(status, 0) + 1
                
                # Source
                source = opportunity.source or 'unknown'
                stats['by_source'][source] = stats['by_source'].get(source, 0) + 1
                
            except Exception:
                continue
        
        return stats
