#!/usr/bin/env python3
"""
Test script to verify database configuration works for both local and cloud modes.
Run this script to test your database configuration.
"""

import os
import sys
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import Config
from database.db_factory import DatabaseFactory

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_database_config():
    """Test database configuration and initialization"""
    try:
        # Validate configuration
        logger.info("Validating database configuration...")
        Config.validate_config()
        logger.info(f"✓ Configuration validated for database type: {Config.VECTOR_DATABASE_TYPE}")
        
        # Test database factory
        logger.info("Testing database factory...")
        try:
            db = DatabaseFactory.create_vector_db()
            logger.info(f"✓ Database created successfully: {type(db).__name__}")
        except ImportError as e:
            if "ChromaDB is not installed" in str(e):
                logger.warning(f"⚠️  ChromaDB not available: {e}")
                logger.info("You can install ChromaDB with: pip install -r requirements-cloud.txt")
                logger.info("Or for Windows: pip install chromadb --no-deps")
                return False
            else:
                raise
        
        # Test basic operations
        logger.info("Testing basic database operations...")
        
        # Test storing documents
        test_docs = [
            {
                'content': 'This is a test document',
                'url': 'https://example.com/test',
                'title': 'Test Document',
                'chunk_index': 0,
                'crawled_at': '2024-01-01T00:00:00Z'
            }
        ]
        
        # Create a proper embedding with the right dimension (384 for all-MiniLM-L6-v2)
        test_embeddings = [[0.1] * 384]  # Mock embedding with correct dimension
        
        db.store_documents(test_docs, test_embeddings)
        logger.info("✓ Documents stored successfully")
        
        # Test search
        search_results = db.search_similar(test_embeddings[0], top_k=1)
        logger.info(f"✓ Search completed: {len(search_results.get('documents', [[]])[0])} results")
        
        # Test stats
        stats = db.get_collection_stats()
        logger.info(f"✓ Collection stats: {stats} documents")
        
        logger.info("🎉 All tests passed! Database configuration is working correctly.")
        return True
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        return False

def main():
    """Main test function"""
    print("=" * 60)
    print("Database Configuration Test")
    print("=" * 60)
    
    print(f"Database Type: {Config.VECTOR_DATABASE_TYPE}")
    print(f"Collection Name: {Config.COLLECTION_NAME}")
    
    if Config.VECTOR_DATABASE_TYPE == "cloud":
        print(f"Chroma Cloud Tenant: {Config.CHROMA_CLOUD_TENANT_ID}")
        print(f"Chroma Cloud Database: {Config.CHROMA_CLOUD_DATABASE_ID}")
    else:
        print(f"Local Database Path: {Config.CHROMA_DB_PATH}")
    
    print("=" * 60)
    
    success = test_database_config()
    
    if success:
        print("\n✅ Database configuration test completed successfully!")
        print("\nYou can now run your application with:")
        print("  python web_app.py")
    else:
        print("\n❌ Database configuration test failed!")
        print("\nPlease check your configuration and try again.")
        print("See DATABASE_CONFIG.md for configuration details.")
        sys.exit(1)

if __name__ == "__main__":
    main()
