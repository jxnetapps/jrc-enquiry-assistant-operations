import os
from dotenv import load_dotenv
from typing import Optional

load_dotenv()

class Config:
    # API Keys
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    
    # Database
    CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH", "./chroma_db")
    COLLECTION_NAME = os.getenv("COLLECTION_NAME", "web_content")
    
    # Database Type: 'local' for FAISS, 'cloud' for Chroma Cloud
    DATABASE_TYPE = os.getenv("DATABASE_TYPE", "local")
    
    # Chroma Cloud Configuration
    CHROMA_CLOUD_API_KEY = os.getenv("CHROMA_CLOUD_API_KEY")
    CHROMA_CLOUD_TENANT_ID = os.getenv("CHROMA_CLOUD_TENANT_ID")
    CHROMA_CLOUD_DATABASE_ID = os.getenv("CHROMA_CLOUD_DATABASE_ID")
    CHROMA_CLOUD_COLLECTION_NAME = os.getenv("CHROMA_CLOUD_COLLECTION_NAME", "web_content")
    
    # Crawler Settings
    MAX_PAGES_TO_CRAWL = int(os.getenv("MAX_PAGES_TO_CRAWL", "100"))
    CRAWL_DEPTH = int(os.getenv("CRAWL_DEPTH", "3"))
    USER_AGENT = os.getenv("USER_AGENT", "WebChatBot/2.0")
    CRAWL_DELAY = float(os.getenv("CRAWL_DELAY", "1.0"))
    MAX_CONCURRENT_REQUESTS = int(os.getenv("MAX_CONCURRENT_REQUESTS", "5"))
    
    # Embedding Settings
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    OPENAI_EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-ada-002")
    EMBEDDING_BATCH_SIZE = int(os.getenv("EMBEDDING_BATCH_SIZE", "32"))
    
    # Chat Settings
    SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", "0.3"))
    MAX_CONTEXT_LENGTH = int(os.getenv("MAX_CONTEXT_LENGTH", "4000"))
    TOP_K_RESULTS = int(os.getenv("TOP_K_RESULTS", "5"))
    
    # Chat Behavior: 'knowledge_base' or 'pre_trained'
    CHAT_BEHAVIOR = os.getenv("CHAT_BEHAVIOR", "knowledge_base")
    
    # Answer Storage Configuration
    ANSWER_STORAGE_TYPE = os.getenv("ANSWER_STORAGE_TYPE", "sqlite")  # sqlite, mysql, mssql
    
    # MySQL Configuration
    MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
    MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))
    MYSQL_USER = os.getenv("MYSQL_USER", "root")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
    MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "edify_answers")
    
    # MSSQL Configuration
    MSSQL_SERVER = os.getenv("MSSQL_SERVER", "localhost")
    MSSQL_DATABASE = os.getenv("MSSQL_DATABASE", "edify_answers")
    MSSQL_USER = os.getenv("MSSQL_USER", "sa")
    MSSQL_PASSWORD = os.getenv("MSSQL_PASSWORD", "")
    MSSQL_DRIVER = os.getenv("MSSQL_DRIVER", "ODBC Driver 17 for SQL Server")
    
    
    # LLM Settings
    LLM_MODEL = os.getenv("LLM_MODEL", "gpt-3.5-turbo")
    LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.1"))
    LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "1000"))
    
    # Authentication
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your_super_secret_jwt_key_here")
    ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")
    # Auth mode: when true, allow any username/password for testing and namespace data by username
    ALLOW_ANY_USER = os.getenv("ALLOW_ANY_USER", "True").lower() == "true"
    
    # Web Interface
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", "8000"))
    DEBUG = os.getenv("DEBUG", "True").lower() == "true"
    
    # Scheduling
    SCHEDULE_CRAWL = os.getenv("SCHEDULE_CRAWL", "False").lower() == "true"
    CRAWL_SCHEDULE = os.getenv("CRAWL_SCHEDULE", "0 2 * * *")
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
    RATE_LIMIT_PERIOD = int(os.getenv("RATE_LIMIT_PERIOD", "3600"))
    
    # MongoDB Configuration
    MONGODB_CONNECTION_URI = os.getenv("MONGODB_CONNECTION_URI", "mongodb+srv://chat_inquiry_admin:6ggw7abyVnjEaTbJ@inquiryassistant.ny6bkka.mongodb.net/?retryWrites=true&w=majority&appName=inquiryassistant")
    MONGODB_DATABASE_NAME = os.getenv("MONGODB_DATABASE_NAME", "inquiryassistant")
    MONGODB_CHAT_INQUIRY_COLLECTION = os.getenv("MONGODB_CHAT_INQUIRY_COLLECTION", "chat_inquiry_information")
    
    @classmethod
    def validate_config(cls):
        """Validate configuration values"""
        if not cls.OPENAI_API_KEY and cls.EMBEDDING_MODEL == cls.OPENAI_EMBEDDING_MODEL:
            raise ValueError("OPENAI_API_KEY is required when using OpenAI embeddings")
        
        if cls.DATABASE_TYPE == "cloud":
            if not cls.CHROMA_CLOUD_API_KEY:
                raise ValueError("CHROMA_CLOUD_API_KEY is required when using cloud database")
            if not cls.CHROMA_CLOUD_TENANT_ID:
                raise ValueError("CHROMA_CLOUD_TENANT_ID is required when using cloud database")
            if not cls.CHROMA_CLOUD_DATABASE_ID:
                raise ValueError("CHROMA_CLOUD_DATABASE_ID is required when using cloud database")
        
        # Validate MongoDB configuration
        if not cls.MONGODB_CONNECTION_URI:
            raise ValueError("MONGODB_CONNECTION_URI is required for MongoDB operations")
