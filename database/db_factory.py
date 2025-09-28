from typing import Optional
import logging

from database.vector_db_interface import VectorDBInterface
from database.vector_db import VectorDB
from config import Config

# Try to import ChromaCloudDB, handle gracefully if not available
try:
    from database.chroma_cloud_db import ChromaCloudDB
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False
    ChromaCloudDB = None

logger = logging.getLogger(__name__)

class DatabaseFactory:
    """Factory class to create appropriate vector database implementation"""
    
    @staticmethod
    def create_vector_db(user_namespace: Optional[str] = None) -> VectorDBInterface:
        """
        Create a vector database instance based on configuration
        
        Args:
            user_namespace: Optional user namespace for data isolation
            
        Returns:
            VectorDBInterface: Appropriate database implementation
            
        Raises:
            ValueError: If database type is not supported
        """
        try:
            if Config.VECTOR_DATABASE_TYPE == "local":
                logger.info("Creating local FAISS vector database")
                return VectorDB(user_namespace=user_namespace)
            elif Config.VECTOR_DATABASE_TYPE == "cloud":
                if not CHROMADB_AVAILABLE:
                    raise ImportError(
                        "ChromaDB is not installed but cloud mode is requested.\n"
                        "Install ChromaDB with: pip install -r requirements-cloud.txt\n"
                        "Or for Windows: pip install chromadb --no-deps"
                    )
                logger.info("Creating Chroma Cloud vector database")
                return ChromaCloudDB(user_namespace=user_namespace)
            else:
                raise ValueError(f"Unsupported database type: {Config.VECTOR_DATABASE_TYPE}. Use 'local' or 'cloud'")
                
        except Exception as e:
            logger.error(f"Failed to create vector database: {e}")
            raise
    
    @staticmethod
    def validate_database_config():
        """Validate database configuration"""
        try:
            Config.validate_config()
            logger.info(f"Database configuration validated for type: {Config.VECTOR_DATABASE_TYPE}")
        except Exception as e:
            logger.error(f"Database configuration validation failed: {e}")
            raise
