"""
Storage operations for job opportunities.
"""
import json
import os
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging

try:
    from .models import JobOpportunity, Interaction, InteractionType, ContactMethod
except ImportError:
    from models import JobOpportunity, Interaction, InteractionType, ContactMethod

logger = logging.getLogger(__name__)


class JobStorage:
    """Handles storage operations for job opportunities with vector DB as primary storage."""
    
    def __init__(self, data_dir: str = "data/opportunities"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.vector_store = None  # Will be set by unified_cli.py
    
    def set_vector_store(self, vector_store):
        """Set the vector store for primary storage operations."""
        self.vector_store = vector_store
    
    def save_opportunity(self, opportunity: JobOpportunity) -> str:
        """Save a job opportunity to both vector DB and JSON backup."""
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
            
            # Save to JSON backup
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(opportunity.dict(), f, indent=2, default=str)
            
            # Save to vector DB as primary storage
            if self.vector_store and self.vector_store.vectorstore:
                try:
                    # Add to vector store
                    doc = self.vector_store._opportunity_to_document(opportunity, filepath.name)
                    self.vector_store.vectorstore.add_documents([doc])
                    self.vector_store.vectorstore.persist()
                    logger.info(f"Added opportunity to vector store: {opportunity.company}")
                except Exception as e:
                    logger.warning(f"Failed to add to vector store: {e}")
            
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
    
    def update_opportunity(self, opportunity: JobOpportunity, filepath: str) -> bool:
        """Update an existing job opportunity in both vector DB and JSON backup."""
        try:
            # Update JSON backup
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(opportunity.dict(), f, indent=2, default=str)
            
            # Update vector DB
            if self.vector_store and self.vector_store.vectorstore:
                try:
                    # Remove old version and add updated version
                    filename = Path(filepath).name
                    self.vector_store._remove_document_by_filename(filename)
                    
                    # Add updated version
                    doc = self.vector_store._opportunity_to_document(opportunity, filename)
                    self.vector_store.vectorstore.add_documents([doc])
                    self.vector_store.vectorstore.persist()
                    logger.info(f"Updated opportunity in vector store: {opportunity.company}")
                except Exception as e:
                    logger.warning(f"Failed to update vector store: {e}")
            
            logger.info(f"Updated opportunity at {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating opportunity at {filepath}: {e}")
            return False
    
    def add_interaction(self, filepath: str, interaction: Interaction) -> bool:
        """Add an interaction to an opportunity and update both storages."""
        try:
            # Load current opportunity
            opportunity = self.load_opportunity(filepath)
            
            # Add interaction
            opportunity.interactions.append(interaction)
            
            # Update both storages
            return self.update_opportunity(opportunity, filepath)
            
        except Exception as e:
            logger.error(f"Error adding interaction: {e}")
            return False
    
    def add_ai_insights(self, filepath: str, insights: str, insight_type: str = "general") -> bool:
        """Add AI-generated insights to an opportunity."""
        try:
            # Load current opportunity
            opportunity = self.load_opportunity(filepath)
            
            # Add AI insight as a special interaction
            ai_interaction = Interaction(
                date=datetime.now(),
                type=InteractionType.other,
                method=ContactMethod.other,
                notes=f"AI {insight_type} insight: {insights}"
            )
            
            opportunity.interactions.append(ai_interaction)
            
            # Update both storages
            return self.update_opportunity(opportunity, filepath)
            
        except Exception as e:
            logger.error(f"Error adding AI insights: {e}")
            return False
    
    def add_job_details(self, filepath: str, details: Dict[str, Any]) -> bool:
        """Add detailed job information (salary, requirements, etc.) to an opportunity."""
        try:
            # Load current opportunity
            opportunity = self.load_opportunity(filepath)
            
            # Update opportunity with new details
            for key, value in details.items():
                if hasattr(opportunity, key):
                    setattr(opportunity, key, value)
            
            # Update both storages
            return self.update_opportunity(opportunity, filepath)
            
        except Exception as e:
            logger.error(f"Error adding job details: {e}")
            return False
    
    def list_opportunities(self) -> List[JobOpportunity]:
        """List all job opportunities as JobOpportunity objects."""
        try:
            # Get basic info first
            basic_info = self._list_opportunities_basic()
            
            # Convert to JobOpportunity objects
            opportunities = []
            for info in basic_info:
                try:
                    opportunity = self.load_opportunity(info['filepath'])
                    opportunities.append(opportunity)
                except Exception as e:
                    logger.warning(f"Could not load opportunity {info['filepath']}: {e}")
                    continue
            
            return opportunities
            
        except Exception as e:
            logger.error(f"Error listing opportunities: {e}")
            return []
    
    def _list_opportunities_basic(self) -> List[Dict[str, Any]]:
        """List all job opportunities with basic info (for internal use)."""
        if self.vector_store and self.vector_store.vectorstore:
            try:
                # Try to get from vector store first
                return self._list_from_vector_store()
            except Exception as e:
                logger.warning(f"Vector store listing failed, falling back to JSON: {e}")
        
        # Fallback to JSON files
        return self._list_from_json_files()
    
    def _list_from_vector_store(self) -> List[Dict[str, Any]]:
        """List opportunities from vector store."""
        try:
            # Get all documents from vector store
            collection = self.vector_store.vectorstore._collection
            results = collection.get()
            
            opportunities = []
            for i, doc_id in enumerate(results['ids']):
                try:
                    metadata = results['metadatas'][i]
                    filename = metadata.get('filename', '')
                    filepath = self.data_dir / filename
                    
                    if filepath.exists():
                        opportunity = self.load_opportunity(str(filepath))
                        opportunities.append({
                            'filepath': str(filepath),
                            'filename': filename,
                            'company': opportunity.company,
                            'role': opportunity.role,
                            'interest_level': opportunity.interest_level,
                            'active': opportunity.active,
                            'timestamp': opportunity.timestamp,
                            'latest_interaction': opportunity.get_latest_interaction()
                        })
                except Exception as e:
                    logger.warning(f"Could not process vector store document: {e}")
                    continue
            
            # Sort by timestamp (newest first)
            opportunities.sort(key=lambda x: x['timestamp'], reverse=True)
            return opportunities
            
        except Exception as e:
            logger.error(f"Error listing from vector store: {e}")
            raise
    
    def _list_from_json_files(self) -> List[Dict[str, Any]]:
        """List opportunities from JSON files (fallback method)."""
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
                           max_interest: Optional[int] = None) -> List[JobOpportunity]:
        """Search opportunities based on criteria."""
        all_opportunities = self.list_opportunities()
        filtered = []
        
        for opp in all_opportunities:
            # Apply filters
            if company and company.lower() not in opp.company.lower():
                continue
            if role and role.lower() not in opp.role.lower():
                continue
            if recruiter and opp.recruiter_name:
                if recruiter.lower() not in opp.recruiter_name.lower():
                    continue
            if active_only and not opp.active:
                continue
            if min_interest and opp.interest_level < min_interest:
                continue
            if max_interest and opp.interest_level > max_interest:
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
    
    def get_overdue_followups(self, days_threshold: int = 7) -> List[JobOpportunity]:
        """Get opportunities that need follow-up."""
        opportunities = self.list_opportunities()
        overdue = []
        
        for opp in opportunities:
            if opp.is_overdue_followup(days_threshold):
                overdue.append(opp)
        
        return overdue
    
    def export_to_csv(self, filepath: str) -> bool:
        """Export all opportunities to CSV format."""
        import csv
        
        opportunities = self.list_opportunities()
        
        try:
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = [
                    'company', 'role', 'recruiter_name', 'recruiter_contact',
                    'interest_level', 'active', 'status', 'source',
                    'timestamp', 'next_steps', 'notes'
                ]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for opp in opportunities:
                    writer.writerow({
                        'company': opp.company,
                        'role': opp.role,
                        'recruiter_name': opp.recruiter_name or '',
                        'recruiter_contact': opp.recruiter_contact or '',
                        'interest_level': opp.interest_level,
                        'active': opp.active,
                        'status': opp.status or '',
                        'source': opp.source or '',
                        'timestamp': opp.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                        'next_steps': opp.next_steps or '',
                        'notes': opp.notes or ''
                    })
            
            logger.info(f"Exported {len(opportunities)} opportunities to {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting to CSV: {e}")
            return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about all opportunities."""
        opportunities = self.list_opportunities()
        
        if not opportunities:
            return {
                'total': 0,
                'active': 0,
                'inactive': 0,
                'avg_interest': 0,
                'max_interest': 0,
                'min_interest': 0,
                'by_status': {},
                'by_source': {}
            }
        
        stats = {
            'total': len(opportunities),
            'active': sum(1 for opp in opportunities if opp.active),
            'inactive': sum(1 for opp in opportunities if not opp.active),
            'avg_interest': sum(opp.interest_level for opp in opportunities) / len(opportunities),
            'max_interest': max(opp.interest_level for opp in opportunities),
            'min_interest': min(opp.interest_level for opp in opportunities),
            'by_status': {},
            'by_source': {}
        }
        
        # Count by status and source
        for opp in opportunities:
            # Status
            status = opp.status or 'unknown'
            stats['by_status'][status] = stats['by_status'].get(status, 0) + 1
            
            # Source
            source = opp.source or 'unknown'
            stats['by_source'][source] = stats['by_source'].get(source, 0) + 1
        
        return stats
