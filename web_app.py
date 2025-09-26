from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import TypeVar, Generic, Optional
import logging

T = TypeVar('T')

from config import Config
from database.mongodb_connection import mongodb_connection
from utils.scheduler import Scheduler

# Import API routers
from api.auth_api import router as auth_router
from api.vector_chat_api import router as vector_chat_router
from api.chat_inquiry_api import router as chat_inquiry_router
from api.enhanced_chat_inquiry_api import router as enhanced_chat_inquiry_router
from api.simple_chat_inquiry_api import router as simple_chat_inquiry_router
from api.sqlite_export_api import router as sqlite_export_router

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Web ChatBot", version="2.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Initialize components
scheduler = Scheduler()

# Pydantic models
# Import ApiResponse from models
from models.chat_inquiry_models import ApiResponse

# Include API routers
app.include_router(auth_router)
app.include_router(vector_chat_router)
app.include_router(chat_inquiry_router)
app.include_router(enhanced_chat_inquiry_router)
app.include_router(simple_chat_inquiry_router)
app.include_router(sqlite_export_router)

# Routes
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# Health check
@app.get("/health", response_model=ApiResponse)
async def health_check():
    return ApiResponse(
        success=True,
        message="Service is healthy",
        data={"status": "healthy", "version": "2.0"}
    )

# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """Initialize MongoDB connection on startup"""
    try:
        await mongodb_connection.connect()
        logger.info("MongoDB connection established")
    except Exception as e:
        logger.warning(f"Failed to connect to MongoDB: {e}")
        logger.warning("Application will start without MongoDB. Chat inquiry features will be disabled.")
        # Don't raise the exception, let the app start without MongoDB
    
    # Start scheduler if enabled
    if Config.SCHEDULE_CRAWL:
        logger.info("Scheduler started")
        # scheduler.schedule_crawl("https://edifyschools.com", Config.CRAWL_SCHEDULE)

@app.on_event("shutdown")
async def shutdown_event():
    """Close MongoDB connection on shutdown"""
    try:
        await mongodb_connection.disconnect()
        logger.info("MongoDB connection closed")
    except Exception as e:
        logger.error(f"Error closing MongoDB connection: {e}")

if __name__ == "__main__":
    import uvicorn
    if Config.DEBUG:
        uvicorn.run("web_app:app", host=Config.HOST, port=Config.PORT, reload=True)
    else:
        uvicorn.run(app, host=Config.HOST, port=Config.PORT)
