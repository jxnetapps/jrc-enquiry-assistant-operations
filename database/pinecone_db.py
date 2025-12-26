import os
import logging
from typing import List, Dict, Any, Optional

from database.vector_db_interface import VectorDBInterface
from config import Config

# Try to import Pinecone, handle gracefully if not available
try:
    from pinecone import Pinecone
    PINECONE_AVAILABLE = True
except ImportError:
    PINECONE_AVAILABLE = False
    Pinecone = None

logger = logging.getLogger(__name__)

class PineconeDB(VectorDBInterface):
    """Pinecone implementation of VectorDBInterface"""
    
    def __init__(self, user_namespace: Optional[str] = None, namespace: Optional[str] = None):
        """
        Initialize Pinecone database connection
        
        Args:
            user_namespace: Optional user namespace for data isolation (legacy parameter)
            namespace: Optional namespace parameter (takes precedence over user_namespace and config)
        """
        if not PINECONE_AVAILABLE:
            raise ImportError(
                "Pinecone is not installed. Install it with: pip install pinecone"
            )
        
        # Determine namespace: API parameter > user_namespace > config
        if namespace:
            self.namespace = self._sanitize_namespace(namespace)
        elif user_namespace:
            self.namespace = self._sanitize_namespace(user_namespace)
        elif Config.PINECONE_NAMESPACE:
            self.namespace = self._sanitize_namespace(Config.PINECONE_NAMESPACE)
        else:
            self.namespace = None
        
        self.index_name = Config.PINECONE_INDEX_NAME
        
        try:
            # Validate API key
            if not Config.PINECONE_API_KEY:
                raise ValueError("PINECONE_API_KEY is not set in configuration")
            
            # Validate index name
            if not Config.PINECONE_INDEX_NAME:
                raise ValueError("PINECONE_INDEX_NAME is not set in configuration")
            
            # Initialize Pinecone client
            logger.info(f"Initializing Pinecone client with index: {self.index_name}")
            self.pc = Pinecone(api_key=Config.PINECONE_API_KEY)
            
            # Get or create index
            try:
                self.index = self.pc.Index(self.index_name)
                logger.info(f"Connected to Pinecone index: {self.index_name} (namespace: {self.namespace or 'default'})")
            except Exception as e:
                logger.error(f"Failed to connect to Pinecone index '{self.index_name}': {e}")
                logger.error(f"Please verify that the index '{self.index_name}' exists in your Pinecone account")
                raise
                
        except Exception as e:
            logger.error(f"Failed to initialize Pinecone database: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise
    
    @staticmethod
    def _sanitize_namespace(ns: Optional[str]) -> Optional[str]:
        """Sanitize namespace for Pinecone compatibility"""
        if not ns:
            return None
        # Pinecone namespaces can contain alphanumerics, hyphens, and underscores
        # Max length is 64 characters
        safe = []
        for ch in ns:
            if ch.isalnum() or ch in ("-", "_"):
                safe.append(ch)
            else:
                safe.append("_")
        return "".join(safe)[:64]
    
    def store_documents(self, documents: List[Dict], embeddings: List[List[float]]) -> None:
        """Store documents and their embeddings in Pinecone"""
        try:
            if not documents or not embeddings:
                return
            
            # Prepare data for Pinecone
            vectors = []
            for i, (doc, embedding) in enumerate(zip(documents, embeddings)):
                # Generate a safe vector ID (Pinecone requires string IDs, and hash can be negative)
                url_hash = abs(hash(doc.get('url', f'doc_{i}'))) % (10 ** 10)  # Limit to 10 digits
                vector_id = f"doc_{i}_{url_hash}"
                # Pinecone metadata has a size limit (typically 40KB per vector)
                # Store full content, but if it's too large, we'll truncate intelligently
                content = doc['content']
                # Pinecone metadata limit is approximately 40KB, but we'll be conservative
                # and limit content to ~30KB to leave room for other metadata fields
                MAX_METADATA_CONTENT_SIZE = 30000  # ~30KB for content
                if len(content) > MAX_METADATA_CONTENT_SIZE:
                    # Truncate at word boundary to avoid cutting words
                    truncated = content[:MAX_METADATA_CONTENT_SIZE]
                    last_space = truncated.rfind(' ')
                    if last_space > 0:
                        content = truncated[:last_space] + "... [content truncated due to size limit]"
                    else:
                        content = truncated + "... [content truncated due to size limit]"
                    logger.warning(f"Content truncated for document {i} (original size: {len(doc['content'])}, stored: {len(content)})")
                
                metadata = {
                    'url': doc['url'],
                    'title': doc['title'],
                    'content': content,  # May be truncated if too large for Pinecone metadata
                    'chunk_index': doc.get('chunk_index', 0),
                    'crawled_at': doc.get('crawled_at', ''),
                    'user_namespace': self.namespace or 'default'
                }
                vectors.append({
                    'id': vector_id,
                    'values': embedding,
                    'metadata': metadata
                })
            
            # Upsert to Pinecone index
            # Pinecone recommends batching in chunks of 100
            # If namespace is None, Pinecone uses default namespace (empty string)
            batch_size = 100
            for i in range(0, len(vectors), batch_size):
                batch = vectors[i:i + batch_size]
                upsert_kwargs = {'vectors': batch}
                if self.namespace is not None:
                    upsert_kwargs['namespace'] = self.namespace
                self.index.upsert(**upsert_kwargs)
            
            logger.info(f"Stored {len(documents)} documents in Pinecone index (namespace: {self.namespace or 'default'})")
            
        except Exception as e:
            logger.error(f"Error storing documents in Pinecone: {e}")
            raise
    
    def search_similar(self, query_embedding: List[float], top_k: int = 5) -> Dict[str, Any]:
        """Search for similar documents in Pinecone"""
        try:
            # Query the index
            # If namespace is None, Pinecone uses default namespace (empty string)
            query_kwargs = {
                'vector': query_embedding,
                'top_k': top_k,
                'include_metadata': True
            }
            if self.namespace is not None:
                query_kwargs['namespace'] = self.namespace
            results = self.index.query(**query_kwargs)
            
            # Debug logging
            logger.debug(f"Pinecone raw results: {results}")
            
            # Format results to match the expected interface
            documents = []
            metadatas = []
            distances = []
            
            if results.matches:
                for match in results.matches:
                    # Pinecone returns scores (similarity), convert to distance
                    # Higher score = more similar, so distance = 1 - score
                    score = match.score if match.score is not None else 0.0
                    distance = 1.0 - float(score)
                    
                    metadata = match.metadata or {}
                    content = metadata.get('content', '')
                    
                    documents.append(content)
                    metadatas.append(metadata)
                    distances.append(distance)
            
            # Return in the format expected by the chat interface
            return {
                "documents": [documents] if documents else [[]],
                "metadatas": [metadatas] if metadatas else [[]],
                "distances": [distances] if distances else [[]]
            }
            
        except Exception as e:
            logger.error(f"Error searching similar documents in Pinecone: {e}")
            raise
    
    def get_collection_stats(self) -> int:
        """Get statistics about the Pinecone index"""
        try:
            # Get index stats
            stats = self.index.describe_index_stats()
            if self.namespace:
                # If namespace is specified, get count for that namespace
                # stats.namespaces is a dict where keys are namespace names
                namespace_stats = stats.namespaces.get(self.namespace, {})
                return namespace_stats.get('vector_count', 0)
            else:
                # If no namespace (default namespace), use empty string as key
                # Default namespace is represented as empty string in stats
                default_namespace_stats = stats.namespaces.get('', {})
                if default_namespace_stats:
                    return default_namespace_stats.get('vector_count', 0)
                # Fallback to total count if namespace stats not available
                return stats.total_vector_count
        except Exception as e:
            logger.error(f"Error getting collection stats from Pinecone: {e}")
            return 0

