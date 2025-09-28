#!/usr/bin/env python3
"""
Test script to verify Chroma Cloud configuration.
Run this script to test your cloud database configuration.
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

def test_cloud_config():
    """Test Chroma Cloud configuration and initialization"""
    try:
        # Check if cloud mode is configured
        if Config.VECTOR_DATABASE_TYPE != "cloud":
            logger.error(f"❌ Database type is set to '{Config.VECTOR_DATABASE_TYPE}', not 'cloud'")
            logger.info("Please set VECTOR_DATABASE_TYPE=cloud in your .env file")
            return False
        
        # Validate configuration
        logger.info("Validating Chroma Cloud configuration...")
        Config.validate_config()
        logger.info(f"✓ Configuration validated for database type: {Config.VECTOR_DATABASE_TYPE}")
        
        # Test database factory
        logger.info("Testing Chroma Cloud database factory...")
        try:
            db = DatabaseFactory.create_vector_db()
            logger.info(f"✓ Chroma Cloud database created successfully: {type(db).__name__}")
        except ImportError as e:
            if "ChromaDB is not installed" in str(e):
                logger.error(f"❌ ChromaDB not available: {e}")
                logger.info("Install ChromaDB with: pip install -r requirements-cloud.txt")
                logger.info("Or for Windows: pip install chromadb --no-deps")
                return False
            else:
                raise
        
        # Test basic operations
        logger.info("Testing basic Chroma Cloud operations...")
        
        # Test storing documents
        test_docs = [
            {
                'content': 'This is a test document for Chroma Cloud',
                'url': 'https://example.com/test-cloud',
                'title': 'Test Cloud Document',
                'chunk_index': 0,
                'crawled_at': '2024-01-01T00:00:00Z'
            }
        ]
        
        # Create a proper embedding with the right dimension (384 for all-MiniLM-L6-v2)
        test_embeddings = [[0.1] * 384]  # Mock embedding with correct dimension
        
        db.store_documents(test_docs, test_embeddings)
        logger.info("✓ Documents stored successfully in Chroma Cloud")
        
        # Test search
        search_results = db.search_similar(test_embeddings[0], top_k=1)
        logger.info(f"✓ Search completed: {len(search_results.get('documents', [[]])[0])} results")
        
        # Test stats
        stats = db.get_collection_stats()
        logger.info(f"✓ Collection stats: {stats} documents")
        
        logger.info("🎉 All Chroma Cloud tests passed! Cloud configuration is working correctly.")
        return True
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        return False

def main():
    """Main test function"""
    print("=" * 60)
    print("Chroma Cloud Configuration Test")
    print("=" * 60)
    
    print(f"Database Type: {Config.VECTOR_DATABASE_TYPE}")
    
    if Config.VECTOR_DATABASE_TYPE == "cloud":
        print(f"Chroma Cloud Tenant: {Config.CHROMA_CLOUD_TENANT_ID}")
        print(f"Chroma Cloud Database: {Config.CHROMA_CLOUD_DATABASE_ID}")
        print(f"Chroma Cloud Collection: {Config.CHROMA_CLOUD_COLLECTION_NAME}")
    else:
        print("❌ Not configured for cloud mode!")
        print("Set VECTOR_DATABASE_TYPE=cloud in your .env file")
        sys.exit(1)
    
    print("=" * 60)
    
    success = test_cloud_config()
    
    if success:
        print("\n✅ Chroma Cloud configuration test completed successfully!")
        print("\nYou can now run your application with cloud database:")
        print("  python web_app.py")
    else:
        print("\n❌ Chroma Cloud configuration test failed!")
        print("\nPlease check your configuration and try again.")
        print("See DATABASE_CONFIG.md for configuration details.")

if __name__ == "__main__":
    main()
