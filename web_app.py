from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import asyncio
from typing import List, Optional
import logging

from config import Config
from crawler.web_crawler import WebCrawler
from crawler.content_processor import ContentProcessor
from embedding.embedding_generator import EmbeddingGenerator
from database.vector_db import VectorDB
from chatbot.chat_interface import ChatBot
from auth.authentication import AuthHandler, authenticate_user
from utils.scheduler import Scheduler

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
auth_handler = AuthHandler()
chatbot = ChatBot()
scheduler = Scheduler()

# Pydantic models
class LoginRequest(BaseModel):
    username: str
    password: str

class ChatRequest(BaseModel):
    message: str

class CrawlRequest(BaseModel):
    url: str
    max_pages: Optional[int] = None
    depth: Optional[int] = None

class ChatResponse(BaseModel):
    response: str
    sources: List[dict]

# Routes
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/api/login")
async def login(login_data: LoginRequest):
    if authenticate_user(login_data.username, login_data.password):
        token = auth_handler.create_token(login_data.username)
        return {"access_token": token, "token_type": "bearer"}
    raise HTTPException(status_code=401, detail="Invalid credentials")

@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(chat_data: ChatRequest, current_user: str = Depends(auth_handler.get_current_user)):
    try:
        response = chatbot.chat(chat_data.message)
        return ChatResponse(response=response, sources=[])
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail="Error processing message")

@app.post("/api/crawl")
async def crawl_website(crawl_data: CrawlRequest, current_user: str = Depends(auth_handler.get_current_user)):
    try:
        crawler = WebCrawler(
            max_pages=crawl_data.max_pages or Config.MAX_PAGES_TO_CRAWL,
            depth=crawl_data.depth or Config.CRAWL_DEPTH,
            delay=Config.CRAWL_DELAY,
            max_concurrent=Config.MAX_CONCURRENT_REQUESTS
        )
        processor = ContentProcessor()
        embedding_generator = EmbeddingGenerator()
        vector_db = VectorDB()
        
        pages = await crawler.crawl(crawl_data.url)
        processed_chunks = processor.process_pages(pages)
        
        if processed_chunks:
            texts = [chunk['content'] for chunk in processed_chunks]
            embeddings = embedding_generator.generate_embeddings(texts)
            vector_db.store_documents(processed_chunks, embeddings)
            
            return {
                "status": "success",
                "pages_crawled": len(pages),
                "chunks_processed": len(processed_chunks)
            }
        else:
            return {"status": "success", "message": "No quality content found"}
            
    except Exception as e:
        logger.error(f"Crawl error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/stats")
async def get_stats(current_user: str = Depends(auth_handler.get_current_user)):
    try:
        vector_db = VectorDB()
        count = vector_db.get_collection_stats()
        return {"document_count": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "2.0"}

# Start scheduler if enabled
if Config.SCHEDULE_CRAWL:
    @app.on_event("startup")
    async def start_scheduler():
        # Example: You might want to load scheduled tasks from a database
        logger.info("Scheduler started")
        # scheduler.schedule_crawl("https://edifyschools.com", Config.CRAWL_SCHEDULE)

if __name__ == "__main__":
    import uvicorn
    if Config.DEBUG:
        uvicorn.run("web_app:app", host=Config.HOST, port=Config.PORT, reload=True)
    else:
        uvicorn.run(app, host=Config.HOST, port=Config.PORT)
