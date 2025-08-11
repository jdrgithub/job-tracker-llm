"""
Vector store operations for AI-powered job opportunity search.
"""
import os
from typing import List, Optional, Dict, Any
from pathlib import Path
import logging

VECTOR_AVAILABLE = False
Document = None

try:
    from openai import OpenAI
    import chromadb
    from langchain.schema import Document
    VECTOR_AVAILABLE = True
except ImportError:
    logging.warning("Vector search dependencies not available. Install openai and chromadb for vector search.")
except Exception as e:
    logging.warning(f"Vector search disabled due to initialization error: {e}")

# Define Document class if not available
if Document is None:
    class Document:
        def __init__(self, page_content: str, metadata: dict = None):
            self.page_content = page_content
            self.metadata = metadata or {}

try:
    from .models import JobOpportunity, SearchResult
    from .storage import JobStorage
except ImportError:
    from models import JobOpportunity, SearchResult
    from storage import JobStorage

logger = logging.getLogger(__name__)


class JobVectorStore:
    """Handles vector search operations for job opportunities."""
    
    def __init__(self, 
                 storage: JobStorage,
                 vector_db_dir: str = "data/vector_index",
                 embedding_model: Optional[str] = None):
        self.storage = storage
        self.vector_db_dir = Path(vector_db_dir)
        self.vector_db_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            # Import here to avoid GUI errors at module level
            try:
                from langchain_openai import OpenAIEmbeddings
                from langchain_community.vectorstores import FAISS
            except ImportError:
                from langchain.embeddings import OpenAIEmbeddings
                from langchain.vectorstores import FAISS
            
            # Initialize embedding model
            if embedding_model:
                self.embedding_model = OpenAIEmbeddings(model=embedding_model)
            else:
                self.embedding_model = OpenAIEmbeddings()
            
            # Set VECTOR_AVAILABLE to True if we get here
            global VECTOR_AVAILABLE
            VECTOR_AVAILABLE = True
            
            # Initialize or load vector store using FAISS (no GUI dependencies)
            vector_db_path = self.vector_db_dir / "faiss_index"
            
            if vector_db_path.exists():
                self.vectorstore = FAISS.load_local(
                    str(vector_db_path),
                    self.embedding_model
                )
                logger.info("Loaded existing vector store")
            else:
                self.vectorstore = None
                logger.info("No existing vector store found")
                
        except Exception as e:
            logger.error(f"Error initializing vector store: {e}")
            self.vectorstore = None
            # Don't fail the entire application if vector store fails
            logger.warning("Continuing without vector search capabilities")
    
    def _opportunity_to_document(self, opportunity: JobOpportunity, filename: str) -> Document:
        """Convert a job opportunity to a document for vector storage."""
        # Create comprehensive text representation
        content_lines = [
            f"Company: {opportunity.company}",
            f"Role: {opportunity.role}",
            f"Recruiter: {opportunity.recruiter_name or 'Unknown'}",
            f"Contact: {opportunity.recruiter_contact or 'Unknown'}",
            f"Status: {'Active' if opportunity.active else opportunity.status or 'Inactive'}",
            f"Interest Level: {opportunity.interest_level}/5",
            f"Source: {opportunity.source or 'Unknown'}",
            f"Next Steps: {opportunity.next_steps or 'None'}",
            f"Notes: {opportunity.notes or 'None'}",
            f"Job Description: {opportunity.job_description or 'None'}",
            f"Resume Used: {opportunity.resume_text or 'None'}",
            f"Cover Letter: {opportunity.cover_letter_text or 'None'}",
            "",
            "Interactions:"
        ]
        
        # Add interaction history
        for interaction in opportunity.interactions:
            content_lines.append(
                f"- [{interaction.date.strftime('%Y-%m-%d %H:%M')}] "
                f"{interaction.type}: {interaction.notes or 'No notes'}"
            )
        
        content = "\n".join(content_lines)
        
        # Create metadata
        metadata = {
            "company": opportunity.company,
            "role": opportunity.role,
            "recruiter": opportunity.recruiter_name or "",
            "interest_level": opportunity.interest_level,
            "active": opportunity.active,
            "status": opportunity.status or "",
            "source": opportunity.source or "",
            "filename": filename,
            "timestamp": opportunity.timestamp.isoformat()
        }
        
        return Document(page_content=content, metadata=metadata)
    
    def build_index(self) -> bool:
        """Build or rebuild the vector index from all opportunities."""
        if not VECTOR_AVAILABLE or not self.embedding_model:
            logger.error("Vector search not available")
            return False
        
        try:
            # Get all opportunities
            opportunities = self.storage.list_opportunities()
            
            if not opportunities:
                logger.warning("No opportunities found to index")
                return False
            
            # Convert to documents
            documents = []
            for opp in opportunities:
                try:
                    opportunity = self.storage.load_opportunity(opp['filepath'])
                    doc = self._opportunity_to_document(opportunity, opp['filename'])
                    documents.append(doc)
                except Exception as e:
                    logger.warning(f"Could not process {opp['filepath']}: {e}")
                    continue
            
            if not documents:
                logger.warning("No valid documents to index")
                return False
            
            # Create new vector store using FAISS
            from langchain_community.vectorstores import FAISS
            
            self.vectorstore = FAISS.from_documents(
                documents=documents,
                embedding=self.embedding_model
            )
            
            # Save the index
            vector_db_path = self.vector_db_dir / "faiss_index"
            self.vectorstore.save_local(str(vector_db_path))
            
            logger.info(f"Built vector index with {len(documents)} documents")
            return True
            
        except Exception as e:
            logger.error(f"Error building vector index: {e}")
            return False
    
    def search(self, query: str, k: int = 5, filters: Optional[Dict[str, Any]] = None) -> List[SearchResult]:
        """Search opportunities using vector similarity."""
        if not self.vectorstore:
            logger.warning("Vector store not available. Run build_index() first.")
            return []
        
        try:
            # Perform vector search (FAISS doesn't support filters in the same way)
            results = self.vectorstore.similarity_search_with_score(
                query, 
                k=k
            )
            
            search_results = []
            for doc, score in results:
                try:
                    # Load the full opportunity
                    filename = doc.metadata.get('filename', '')
                    filepath = self.storage.data_dir / filename
                    
                    if filepath.exists():
                        opportunity = self.storage.load_opportunity(str(filepath))
                        search_results.append(SearchResult(
                            opportunity=opportunity,
                            relevance_score=1.0 - score,  # Convert distance to similarity
                            filename=filename
                        ))
                except Exception as e:
                    logger.warning(f"Could not load opportunity for search result: {e}")
                    continue
            
            return search_results
            
        except Exception as e:
            logger.error(f"Error performing vector search: {e}")
            return []
    
    def semantic_search(self, query: str, k: int = 5) -> List[SearchResult]:
        """Perform semantic search across all opportunity fields."""
        return self.search(query, k=k)
    
    def search_by_company(self, company_name: str, k: int = 5) -> List[SearchResult]:
        """Search for opportunities by company name."""
        return self.search(f"company: {company_name}", k=k)
    
    def search_by_role(self, role_name: str, k: int = 5) -> List[SearchResult]:
        """Search for opportunities by role/title."""
        return self.search(f"role: {role_name}", k=k)
    
    def search_by_recruiter(self, recruiter_name: str, k: int = 5) -> List[SearchResult]:
        """Search for opportunities by recruiter name."""
        return self.search(f"recruiter: {recruiter_name}", k=k)
    
    def search_active_opportunities(self, query: str, k: int = 5) -> List[SearchResult]:
        """Search only active opportunities."""
        filters = {"active": True}
        return self.search(query, k=k, filters=filters)
    
    def search_by_interest_level(self, min_level: int, max_level: int, k: int = 5) -> List[SearchResult]:
        """Search opportunities within an interest level range."""
        # Note: ChromaDB doesn't support numeric range filters directly
        # This is a simplified implementation
        results = self.search("", k=100)  # Get more results to filter
        filtered = [
            result for result in results 
            if min_level <= result.opportunity.interest_level <= max_level
        ]
        return filtered[:k]
    
    def get_similar_opportunities(self, opportunity: JobOpportunity, k: int = 5) -> List[SearchResult]:
        """Find opportunities similar to a given one."""
        query = f"company: {opportunity.company} role: {opportunity.role}"
        return self.search(query, k=k)
    
    def update_index(self) -> bool:
        """Update the vector index with new opportunities."""
        return self.build_index()
    
    def delete_index(self) -> bool:
        """Delete the vector index."""
        try:
            import shutil
            if self.vector_db_dir.exists():
                shutil.rmtree(self.vector_db_dir)
                logger.info("Deleted vector index")
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting vector index: {e}")
            return False
    
    def get_index_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector index."""
        if not self.vectorstore:
            return {"status": "not_available"}
        
        try:
            # Get collection info
            collection = self.vectorstore._collection
            count = collection.count()
            
            return {
                "status": "available",
                "document_count": count,
                "index_path": str(self.vector_db_dir),
                "embedding_model": "openai"  # Could be made configurable
            }
        except Exception as e:
            logger.error(f"Error getting index stats: {e}")
            return {"status": "error", "error": str(e)}
    
    def _remove_document_by_filename(self, filename: str) -> bool:
        """Remove a document from the vector store by filename."""
        if not self.vectorstore:
            return False
        
        try:
            collection = self.vectorstore._collection
            
            # Get all documents to find the one with matching filename
            results = collection.get()
            
            for i, metadata in enumerate(results['metadatas']):
                if metadata.get('filename') == filename:
                    # Remove this document
                    doc_id = results['ids'][i]
                    collection.delete(ids=[doc_id])
                    logger.info(f"Removed document from vector store: {filename}")
                    return True
            
            logger.warning(f"Document not found in vector store: {filename}")
            return False
            
        except Exception as e:
            logger.error(f"Error removing document from vector store: {e}")
            return False
