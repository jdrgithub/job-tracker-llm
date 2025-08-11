"""
AI Assistant module that integrates ChatGPT with the job tracker vector database.
"""
import os
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logging.warning("OpenAI not available. Install with: pip install openai")

try:
    from .models import JobOpportunity, SearchResult
    from .storage import JobStorage
    from .vector_store import JobVectorStore
    from .utils import format_date, get_interest_level_description
except ImportError:
    from models import JobOpportunity, SearchResult
    from storage import JobStorage
    from vector_store import JobVectorStore
    from utils import format_date, get_interest_level_description

logger = logging.getLogger(__name__)


class JobTrackerAI:
    """AI assistant for job tracker using ChatGPT and vector search."""
    
    def __init__(self, storage: JobStorage, vector_store: JobVectorStore):
        self.storage = storage
        self.vector_store = vector_store
        self.client = None
        
        if OPENAI_AVAILABLE:
            api_key = os.getenv('OPENAI_API_KEY')
            if api_key:
                self.client = OpenAI(api_key=api_key)
            else:
                logger.warning("OPENAI_API_KEY not set. AI features will be limited.")
    
    def _get_context_from_opportunities(self, opportunities: List[JobOpportunity]) -> str:
        """Convert opportunities to context string for ChatGPT."""
        if not opportunities:
            return "No job opportunities found."
        
        context_parts = []
        for i, opp in enumerate(opportunities, 1):
            context_parts.append(f"Opportunity {i}:")
            context_parts.append(f"  Company: {opp.company}")
            context_parts.append(f"  Role: {opp.role}")
            context_parts.append(f"  Interest Level: {opp.interest_level}/5 ({get_interest_level_description(opp.interest_level)})")
            context_parts.append(f"  Status: {'Active' if opp.active else 'Inactive'}")
            context_parts.append(f"  Source: {opp.source or 'Unknown'}")
            context_parts.append(f"  Recruiter: {opp.recruiter_name or 'Unknown'}")
            context_parts.append(f"  Next Steps: {opp.next_steps or 'None'}")
            context_parts.append(f"  Notes: {opp.notes or 'None'}")
            
            if opp.interactions:
                context_parts.append("  Recent Interactions:")
                for interaction in opp.interactions[-3:]:  # Last 3 interactions
                    context_parts.append(f"    {format_date(interaction.date)} - {interaction.type}: {interaction.notes or 'No notes'}")
            
            context_parts.append("")
        
        return "\n".join(context_parts)
    
    def _get_statistics_context(self) -> str:
        """Get statistics context for ChatGPT."""
        stats = self.storage.get_statistics()
        
        context = f"""
Job Search Statistics:
- Total Opportunities: {stats['total']}
- Active Opportunities: {stats['active']}
- Inactive Opportunities: {stats['inactive']}
- Average Interest Level: {stats['avg_interest']:.1f}/5

Status Breakdown:
"""
        for status, count in stats['by_status'].items():
            context += f"- {status.title()}: {count}\n"
        
        context += "\nSource Breakdown:\n"
        for source, count in stats['by_source'].items():
            context += f"- {source.title()}: {count}\n"
        
        # Add overdue follow-ups
        overdue = self.storage.get_overdue_followups()
        if overdue:
            context += f"\nOverdue Follow-ups ({len(overdue)}):\n"
            for opp in overdue[:5]:  # Show first 5
                context += f"- {opp['company']} - {opp['role']}\n"
        
        return context
    
    def ask_about_opportunities(self, question: str, limit: int = 10) -> str:
        """Ask ChatGPT about job opportunities."""
        if not self.client:
            return "Error: OpenAI client not available. Please set OPENAI_API_KEY environment variable."
        
        try:
            # Get relevant opportunities using vector search
            search_results = self.vector_store.semantic_search(question, k=limit)
            opportunities = [result.opportunity for result in search_results]
            
            # If no vector search results, get all opportunities
            if not opportunities:
                all_opps = self.storage.list_opportunities()
                opportunities = []
                for opp_data in all_opps[:limit]:
                    try:
                        opp = self.storage.load_opportunity(opp_data['filepath'])
                        opportunities.append(opp)
                    except Exception as e:
                        logger.warning(f"Could not load opportunity: {e}")
            
            # Get context
            context = self._get_context_from_opportunities(opportunities)
            stats_context = self._get_statistics_context()
            
            # Create system prompt
            system_prompt = f"""You are an intelligent job search assistant. You have access to a job tracker database with the following information:

{stats_context}

Relevant Job Opportunities:
{context}

Please provide helpful, actionable advice based on this data. Be specific and reference the actual opportunities when possible. Focus on:
- Patterns and insights
- Recommendations for next steps
- Suggestions for improving the job search
- Analysis of interest levels and statuses
- Follow-up recommendations

Keep your response concise but informative."""
            
            # Get response from ChatGPT
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": question}
                ],
                max_tokens=1000,
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error asking ChatGPT: {e}")
            return f"Error: {str(e)}"
    
    def get_job_search_insights(self) -> str:
        """Get general insights about the job search."""
        if not self.client:
            return "Error: OpenAI client not available. Please set OPENAI_API_KEY environment variable."
        
        try:
            stats_context = self._get_statistics_context()
            
            # Get recent opportunities
            all_opps = self.storage.list_opportunities()
            recent_opportunities = []
            for opp_data in all_opps[:5]:  # Last 5 opportunities
                try:
                    opp = self.storage.load_opportunity(opp_data['filepath'])
                    recent_opportunities.append(opp)
                except Exception as e:
                    logger.warning(f"Could not load opportunity: {e}")
            
            context = self._get_context_from_opportunities(recent_opportunities)
            
            system_prompt = f"""You are an expert job search coach. Analyze this job search data and provide insights:

{stats_context}

Recent Opportunities:
{context}

Provide a comprehensive analysis including:
1. Overall job search health and progress
2. Patterns in the opportunities (companies, roles, sources)
3. Interest level analysis and recommendations
4. Follow-up strategy suggestions
5. Areas for improvement
6. Next steps to take

Be encouraging but honest. Provide specific, actionable advice."""
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": "Please analyze my job search and provide insights and recommendations."}
                ],
                max_tokens=1200,
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error getting insights: {e}")
            return f"Error: {str(e)}"
    
    def suggest_follow_ups(self) -> str:
        """Get AI suggestions for follow-ups."""
        if not self.client:
            return "Error: OpenAI client not available. Please set OPENAI_API_KEY environment variable."
        
        try:
            overdue = self.storage.get_overdue_followups()
            active_opportunities = []
            
            # Get active opportunities that might need follow-up
            all_opps = self.storage.list_opportunities()
            for opp_data in all_opps:
                if opp_data['active']:
                    try:
                        opp = self.storage.load_opportunity(opp_data['filepath'])
                        active_opportunities.append(opp)
                    except Exception as e:
                        logger.warning(f"Could not load opportunity: {e}")
            
            context = self._get_context_from_opportunities(active_opportunities)
            
            system_prompt = f"""You are a job search follow-up expert. Analyze these active opportunities and provide follow-up suggestions:

Active Opportunities:
{context}

Overdue Follow-ups: {len(overdue)} opportunities

For each opportunity, suggest:
1. Whether a follow-up is needed
2. What type of follow-up (email, call, LinkedIn message)
3. Suggested timing
4. Key points to mention
5. Tone and approach

Be specific and actionable. Consider the company, role, and previous interactions."""
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": "Please suggest follow-up strategies for my active job opportunities."}
                ],
                max_tokens=1000,
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error suggesting follow-ups: {e}")
            return f"Error: {str(e)}"
    
    def analyze_opportunity(self, company: str, role: str) -> str:
        """Get AI analysis of a specific opportunity."""
        if not self.client:
            return "Error: OpenAI client not available. Please set OPENAI_API_KEY environment variable."
        
        try:
            # Find the specific opportunity
            search_results = self.vector_store.search_by_company(company, k=5)
            target_opportunity = None
            
            for result in search_results:
                if result.opportunity.company.lower() == company.lower() and result.opportunity.role.lower() == role.lower():
                    target_opportunity = result.opportunity
                    break
            
            if not target_opportunity:
                return f"Could not find opportunity for {company} - {role}"
            
            # Get similar opportunities for comparison
            similar_results = self.vector_store.get_similar_opportunities(target_opportunity, k=3)
            similar_opportunities = [result.opportunity for result in similar_results if result.opportunity != target_opportunity]
            
            context = self._get_context_from_opportunities([target_opportunity])
            similar_context = self._get_context_from_opportunities(similar_opportunities) if similar_opportunities else "None"
            
            system_prompt = f"""You are analyzing a specific job opportunity. Provide detailed insights:

Target Opportunity:
{context}

Similar Opportunities (for comparison):
{similar_context}

Please provide:
1. Opportunity assessment and potential
2. Interest level analysis and recommendations
3. Follow-up strategy and timeline
4. Key talking points for interactions
5. Comparison with similar opportunities
6. Risk factors and considerations
7. Next steps and action items

Be thorough and provide specific, actionable advice."""
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Please analyze the opportunity at {company} for the {role} position."}
                ],
                max_tokens=1200,
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error analyzing opportunity: {e}")
            return f"Error: {str(e)}"
    
    def generate_follow_up_email(self, company: str, role: str, recruiter_name: str = None) -> str:
        """Generate a follow-up email template."""
        if not self.client:
            return "Error: OpenAI client not available. Please set OPENAI_API_KEY environment variable."
        
        try:
            # Find the opportunity
            search_results = self.vector_store.search_by_company(company, k=5)
            target_opportunity = None
            
            for result in search_results:
                if result.opportunity.company.lower() == company.lower() and result.opportunity.role.lower() == role.lower():
                    target_opportunity = result.opportunity
                    break
            
            if not target_opportunity:
                return f"Could not find opportunity for {company} - {role}"
            
            context = f"""
Company: {target_opportunity.company}
Role: {target_opportunity.role}
Recruiter: {recruiter_name or target_opportunity.recruiter_name or 'Unknown'}
Previous Contact: {target_opportunity.recruiter_contact or 'Unknown'}
Interest Level: {target_opportunity.interest_level}/5
Last Interaction: {target_opportunity.get_latest_interaction().date if target_opportunity.get_latest_interaction() else 'None'}
Notes: {target_opportunity.notes or 'None'}
"""
            
            system_prompt = f"""You are writing a professional follow-up email for a job opportunity. Use this context:

{context}

Write a professional, polite follow-up email that:
1. References the specific role and company
2. Shows continued interest
3. Asks about next steps or timeline
4. Is concise but friendly
5. Includes a clear call to action
6. Maintains professional tone

Format the email properly with subject line and body."""
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": "Please generate a follow-up email for this opportunity."}
                ],
                max_tokens=800,
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error generating email: {e}")
            return f"Error: {str(e)}"
    
    def get_career_advice(self, question: str) -> str:
        """Get general career advice based on job search context."""
        if not self.client:
            return "Error: OpenAI client not available. Please set OPENAI_API_KEY environment variable."
        
        try:
            stats_context = self._get_statistics_context()
            
            system_prompt = f"""You are a career coach with access to this job search data:

{stats_context}

Provide career advice based on this context and the user's question. Be specific and actionable, referencing patterns in their job search when relevant."""
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": question}
                ],
                max_tokens=1000,
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error getting career advice: {e}")
            return f"Error: {str(e)}" 