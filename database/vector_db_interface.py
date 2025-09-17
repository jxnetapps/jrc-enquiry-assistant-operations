from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class VectorDBInterface(ABC):
    """Abstract interface for vector database implementations"""
    
    @abstractmethod
    def __init__(self, user_namespace: Optional[str] = None):
        """Initialize the vector database"""
        pass
    
    @abstractmethod
    def store_documents(self, documents: List[Dict], embeddings: List[List[float]]) -> None:
        """Store documents and their embeddings in the vector database"""
        pass
    
    @abstractmethod
    def search_similar(self, query_embedding: List[float], top_k: int = 5) -> Dict[str, Any]:
        """Search for similar documents"""
        pass
    
    @abstractmethod
    def get_collection_stats(self) -> int:
        """Get statistics about the collection"""
        pass
