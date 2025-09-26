from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo import MongoClient
from typing import Optional
import logging
from config import Config

logger = logging.getLogger(__name__)

class MongoDBConnection:
    """MongoDB connection manager using singleton pattern"""
    
    _instance: Optional['MongoDBConnection'] = None
    _client: Optional[AsyncIOMotorClient] = None
    _database: Optional[AsyncIOMotorDatabase] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MongoDBConnection, cls).__new__(cls)
        return cls._instance
    
    async def connect(self):
        """Establish connection to MongoDB with robust fallback"""
        try:
            if self._client is None:
                # Try multiple connection methods
                connection_methods = [
                    # Method 1: Default connection
                    lambda: AsyncIOMotorClient(Config.MONGODB_CONNECTION_URI),
                    
                    # Method 2: With TLS insecure
                    lambda: AsyncIOMotorClient(
                        Config.MONGODB_CONNECTION_URI,
                        tls=True,
                        tlsInsecure=True,
                        serverSelectionTimeoutMS=10000
                    ),
                    
                    # Method 3: With longer timeouts
                    lambda: AsyncIOMotorClient(
                        Config.MONGODB_CONNECTION_URI,
                        serverSelectionTimeoutMS=30000,
                        connectTimeoutMS=30000,
                        socketTimeoutMS=30000
                    )
                ]
                
                for i, method in enumerate(connection_methods, 1):
                    try:
                        logger.info(f"Trying MongoDB connection method {i}")
                        self._client = method()
                        self._database = self._client[Config.MONGODB_DATABASE_NAME]
                        
                        # Test the connection
                        await self._client.admin.command('ping')
                        logger.info(f"Successfully connected to MongoDB using method {i}")
                        return
                        
                    except Exception as e:
                        logger.warning(f"MongoDB connection method {i} failed: {e}")
                        if self._client:
                            try:
                                await self._client.close()
                            except:
                                pass
                            self._client = None
                        continue
                
                # If all methods fail, raise the last exception
                raise Exception("All MongoDB connection methods failed")
                
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            logger.info("Application will continue with SQLite fallback")
            # Don't raise the exception, let the app continue without MongoDB
            self._client = None
            self._database = None
    
    async def disconnect(self):
        """Close MongoDB connection"""
        if self._client:
            self._client.close()
            self._client = None
            self._database = None
            logger.info("Disconnected from MongoDB")
    
    def get_database(self) -> AsyncIOMotorDatabase:
        """Get the database instance"""
        if self._database is None:
            raise RuntimeError("MongoDB not connected. Call connect() first.")
        return self._database
    
    def get_collection(self, collection_name: str):
        """Get a collection from the database"""
        database = self.get_database()
        return database[collection_name]
    
    async def health_check(self) -> bool:
        """Check if MongoDB connection is healthy"""
        try:
            if self._client is None:
                return False
            await self._client.admin.command('ping')
            return True
        except Exception as e:
            logger.error(f"MongoDB health check failed: {e}")
            return False

# Global connection instance
mongodb_connection = MongoDBConnection()
