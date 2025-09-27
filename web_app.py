from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import TypeVar, Generic, Optional
import logging

T = TypeVar('T')

from config import Config
from database.postgresql_connection import postgresql_connection
from utils.scheduler import Scheduler

# Import API routers
from api.auth_api import router as auth_router
from api.vector_chat_api import router as vector_chat_router
from api.unified_chat_inquiry_api import router as unified_chat_inquiry_router
from api.users_api import router as users_router

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Web ChatBot Enhanced API",
    description="""
    # 🤖 Web ChatBot Enhanced API
    
    A sophisticated chatbot system that provides:
    
    ## 🚀 Features
    - **Web Crawling**: Async crawler with depth control and polite delays
    - **AI-Powered**: Uses OpenAI GPT or local models for intelligent responses
    - **Vector Search**: Configurable vector database (FAISS local or Chroma Cloud)
    - **Authentication**: JWT-based user authentication
    - **Rate Limiting**: Polite crawling with configurable delays
    - **Content Filtering**: Quality-based content filtering
    - **Scheduling**: Automatic content updates
    - **Chat Inquiry Management**: Complete CRUD operations for inquiries
    
    ## 📊 Database Support
    - **PostgreSQL**: Primary database with full ACID compliance
    - **SQLite**: Fallback database for local development
    - **Automatic Failover**: Seamless switching between databases
    
    ## 🔐 Authentication
    - **JWT Tokens**: Secure authentication for admin operations
    - **Public Endpoints**: No authentication required for public operations
    - **Role-based Access**: Different access levels for different operations
    
    ## 📝 API Categories
    1. **Authentication APIs** (`/api/auth/*`) - User login, registration, token management
    2. **Vector Chat APIs** (`/api/vector-chat/*`) - AI-powered chat and web crawling
    3. **Chat Inquiry APIs** (`/api/chat-inquiry/*`) - Inquiry management and statistics
    
    ## 🌐 Base URLs
    - **Development**: `http://localhost:8000`
    - **Production**: Configure as needed
    
    ## 📚 Documentation
    - **Swagger UI**: Interactive API documentation (this page)
    - **ReDoc**: Alternative documentation format
    - **OpenAPI JSON**: Machine-readable API specification
    """,
    version="2.0.0",
    contact={
        "name": "Web ChatBot Support",
        "email": "support@webchatbot.com",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
    servers=[
        {
            "url": "http://localhost:8000",
            "description": "Development server"
        },
        {
            "url": "https://api.webchatbot.com",
            "description": "Production server"
        }
    ],
    tags_metadata=[
        {
            "name": "Authentication",
            "description": "User authentication and authorization endpoints",
            "externalDocs": {
                "description": "Authentication Guide",
                "url": "https://docs.webchatbot.com/auth",
            },
        },
        {
            "name": "Vector Chat",
            "description": "AI-powered chat and web crawling functionality",
            "externalDocs": {
                "description": "Vector Chat Guide",
                "url": "https://docs.webchatbot.com/vector-chat",
            },
        },
        {
            "name": "Chat Inquiry",
            "description": "Inquiry management and statistics",
            "externalDocs": {
                "description": "Inquiry Management Guide",
                "url": "https://docs.webchatbot.com/inquiries",
            },
        },
        {
            "name": "User Management",
            "description": "User management and administration",
            "externalDocs": {
                "description": "User Management Guide",
                "url": "https://docs.webchatbot.com/users",
            },
        },
        {
            "name": "Database",
            "description": "Database management and health checks",
            "externalDocs": {
                "description": "Database Guide",
                "url": "https://docs.webchatbot.com/database",
            },
        },
    ]
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Initialize components
scheduler = Scheduler()

# Pydantic models
# Import ApiResponse from models
from models.chat_inquiry_models import ApiResponse

# Root endpoint - redirect to Swagger docs
@app.get("/", 
         summary="API Root",
         description="Redirect to Swagger Documentation",
         tags=["General"])
async def root():
    """
    Root endpoint that redirects to Swagger documentation.
    """
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/docs")

# Health check endpoint
@app.get("/health",
         summary="Health Check",
         description="Check the health status of the API and its dependencies",
         tags=["General"],
         response_model=dict)
async def health_check():
    """
    Health check endpoint to verify API and database connectivity.
    """
    try:
        # Check PostgreSQL connection
        postgres_status = await postgresql_connection.is_connected()
        
        # Check SQLite availability
        import os
        sqlite_available = os.path.exists("database/chat_inquiries.db")
        
        return {
            "status": "healthy",
            "timestamp": "2024-01-01T00:00:00Z",
            "services": {
                "api": "running",
                "postgresql": "connected" if postgres_status else "disconnected",
                "sqlite": "available" if sqlite_available else "unavailable"
            },
            "version": "2.0.0"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": "2024-01-01T00:00:00Z"
        }

# Azure App Service health check endpoint
@app.get("/health/azure",
         summary="Azure Health Check",
         description="Azure App Service health check endpoint",
         tags=["General"])
async def azure_health_check():
    """
    Azure App Service health check endpoint.
    """
    return {"status": "ok", "message": "Web ChatBot API is running"}

# API information endpoint
@app.get("/api/info",
         summary="API Information",
         description="Get detailed information about the API capabilities",
         tags=["General"],
         response_model=dict)
async def api_info():
    """
    Get comprehensive information about the API capabilities and features.
    """
    return {
        "api_name": "Web ChatBot Enhanced API",
        "version": "2.0.0",
        "description": "A sophisticated chatbot system with AI-powered responses and inquiry management",
        "features": [
            "Web Crawling with depth control",
            "AI-powered responses using OpenAI GPT",
            "Vector search with FAISS and Chroma",
            "JWT-based authentication",
            "Rate limiting and content filtering",
            "Automatic content updates",
            "Complete inquiry management system"
        ],
        "database_support": [
            "PostgreSQL (primary)",
            "SQLite (fallback)"
        ],
        "authentication": {
            "type": "JWT Bearer Token",
            "public_endpoints": "Available for public operations",
            "admin_endpoints": "Require authentication"
        },
        "rate_limits": {
            "crawling": "Configurable delays",
            "api_calls": "Standard HTTP limits",
            "content_processing": "Background processing"
        }
    }

# Include API routers
app.include_router(auth_router, tags=["Authentication"])
app.include_router(vector_chat_router, tags=["Vector Chat"])
app.include_router(unified_chat_inquiry_router, tags=["Chat Inquiry", "Database"])
app.include_router(users_router, tags=["User Management"])




# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """Initialize PostgreSQL connection on startup"""
    try:
        await postgresql_connection.connect()
        logger.info("PostgreSQL connection established")
        
        # Create tables if they don't exist
        await postgresql_connection.create_tables()
        logger.info("PostgreSQL tables initialized")
    except Exception as e:
        logger.warning(f"Failed to connect to PostgreSQL: {e}")
        logger.warning("Application will start with SQLite fallback. Chat inquiry features will use SQLite.")
        # Don't raise the exception, let the app start with SQLite fallback
    
    # Start scheduler if enabled
    if Config.SCHEDULE_CRAWL:
        logger.info("Scheduler started")
        # scheduler.schedule_crawl("https://edifyschools.com", Config.CRAWL_SCHEDULE)

@app.on_event("shutdown")
async def shutdown_event():
    """Close PostgreSQL connection on shutdown"""
    try:
        await postgresql_connection.disconnect()
        logger.info("PostgreSQL connection closed")
    except Exception as e:
        logger.error(f"Error closing PostgreSQL connection: {e}")

if __name__ == "__main__":
    import uvicorn
    if Config.DEBUG:
        uvicorn.run("web_app:app", host=Config.HOST, port=Config.PORT, reload=True)
    else:
        uvicorn.run(app, host=Config.HOST, port=Config.PORT)
