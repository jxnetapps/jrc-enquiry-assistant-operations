import os
import logging
from typing import List, Dict, Any, Optional

from database.vector_db_interface import VectorDBInterface
from config import Config

# Try to import ChromaDB, handle gracefully if not available
try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False
    chromadb = None
    Settings = None

logger = logging.getLogger(__name__)

class ChromaCloudDB(VectorDBInterface):
    """Chroma Cloud implementation of VectorDBInterface"""
    
    def __init__(self, user_namespace: Optional[str] = None):
        """Initialize Chroma Cloud database connection"""
        if not CHROMADB_AVAILABLE:
            raise ImportError(
                "ChromaDB is not installed. Install it with: pip install -r requirements-cloud.txt\n"
                "Or for Windows: pip install chromadb --no-deps"
            )
        
        self.user_namespace = self._sanitize_namespace(user_namespace) if user_namespace else None
        self.collection_name = f"{Config.CHROMA_CLOUD_COLLECTION_NAME}_{self.user_namespace}" if self.user_namespace else Config.CHROMA_CLOUD_COLLECTION_NAME
        
        try:
            # Initialize Chroma Cloud client
            # Use the CloudClient for Chroma Cloud
            self.client = chromadb.CloudClient(
                tenant=Config.CHROMA_CLOUD_TENANT_ID,
                database=Config.CHROMA_CLOUD_DATABASE_ID,
                api_key=Config.CHROMA_CLOUD_API_KEY
            )
            
            # Get or create collection
            try:
                self.collection = self.client.get_collection(
                    name=self.collection_name
                )
                logger.info(f"Connected to existing Chroma Cloud collection: {self.collection_name}")
            except Exception:
                # Collection doesn't exist, create it
                self.collection = self.client.create_collection(
                    name=self.collection_name
                )
                logger.info(f"Created new Chroma Cloud collection: {self.collection_name}")
                
        except Exception as e:
            logger.error(f"Failed to initialize Chroma Cloud database: {e}")
            raise
    
    @staticmethod
    def _sanitize_namespace(ns: Optional[str]) -> Optional[str]:
        """Sanitize namespace for Chroma Cloud compatibility"""
        if not ns:
            return None
        # Keep alphanumerics, dash and underscore. Replace others with underscore.
        safe = []
        for ch in ns:
            if ch.isalnum() or ch in ("-", "_"):
                safe.append(ch)
            else:
                safe.append("_")
        return "".join(safe)[:64]
    
    def store_documents(self, documents: List[Dict], embeddings: List[List[float]]) -> None:
        """Store documents and their embeddings in Chroma Cloud"""
        try:
            if not documents or not embeddings:
                return
            
            # Prepare data for Chroma
            ids = [f"doc_{i}_{hash(doc['url'])}" for i, doc in enumerate(documents)]
            texts = [doc['content'] for doc in documents]
            metadatas = [
                {
                    'url': doc['url'],
                    'title': doc['title'],
                    'chunk_index': doc.get('chunk_index', 0),
                    'crawled_at': doc.get('crawled_at', ''),
                    'user_namespace': self.user_namespace or 'default'
                }
                for doc in documents
            ]
            
            # Add to collection
            self.collection.add(
                ids=ids,
                embeddings=embeddings,
                documents=texts,
                metadatas=metadatas
            )
            
            logger.info(f"Stored {len(documents)} documents in Chroma Cloud collection")
            
        except Exception as e:
            logger.error(f"Error storing documents in Chroma Cloud: {e}")
            raise
    
    def search_similar(self, query_embedding: List[float], top_k: int = 5) -> Dict[str, Any]:
        """Search for similar documents in Chroma Cloud"""
        try:
            # Query the collection
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                include=['documents', 'metadatas', 'distances']
            )
            
            # Debug logging
            logger.debug(f"Chroma Cloud raw results: {results}")
            
            # Format results to match the expected interface
            # Chroma Cloud returns flat arrays, but the interface expects nested arrays
            documents = results.get('documents', [[]])
            metadatas = results.get('metadatas', [[]])
            distances = results.get('distances', [[]])
            
            # Convert distances to float if they're lists
            if distances and isinstance(distances[0], list):
                distances = [float(d) for d in distances[0]] if distances[0] else []
            elif distances:
                distances = [float(d) for d in distances]
            
            # Convert metadatas to proper format
            if metadatas and isinstance(metadatas[0], list):
                metadatas = metadatas[0] if metadatas[0] else []
            elif not metadatas:
                metadatas = []
            
            # Convert documents to proper format (flatten if nested)
            if documents and isinstance(documents[0], list):
                documents = documents[0] if documents[0] else []
            elif not documents:
                documents = []
            
            # Ensure we return the format expected by the chat interface
            return {
                "documents": [documents] if documents else [[]],
                "metadatas": [metadatas] if metadatas else [[]],
                "distances": [distances] if distances else [[]]
            }
            
        except Exception as e:
            logger.error(f"Error searching similar documents in Chroma Cloud: {e}")
            raise
    
    def get_collection_stats(self) -> int:
        """Get statistics about the Chroma Cloud collection"""
        try:
            # Get collection count
            count = self.collection.count()
            return count
        except Exception as e:
            logger.error(f"Error getting collection stats from Chroma Cloud: {e}")
            return 0
