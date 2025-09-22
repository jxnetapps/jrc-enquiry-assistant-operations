from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import asyncio
from typing import List, Optional, TypeVar, Generic
import logging
from fastapi import UploadFile, File
import json

T = TypeVar('T')

from config import Config
from crawler.web_crawler import WebCrawler
from crawler.content_processor import ContentProcessor
from embedding.embedding_generator import EmbeddingGenerator
from database.db_factory import DatabaseFactory
from database.answer_storage import answer_storage
from chatbot.chat_interface import ChatBot
from auth.authentication import AuthHandler, authenticate_user
from utils.scheduler import Scheduler
from utils.doc_parser import parse_pdf, parse_docx, parse_txt

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
def get_chatbot_for_user(user_id: str) -> ChatBot:
    return ChatBot(user_namespace=user_id)
scheduler = Scheduler()

# Pydantic models
class LoginRequest(BaseModel):
    username: str
    password: str

class TokenRequest(BaseModel):
    user_id: str

class ChatRequest(BaseModel):
    message: str
    user_id: Optional[str] = None

class CrawlRequest(BaseModel):
    url: str
    max_pages: Optional[int] = None
    depth: Optional[int] = None

class ChatResponse(BaseModel):
    response: str
    sources: List[dict] = []
    mode: Optional[str] = None
    state: Optional[str] = None
    options: List[str] = []
    collected_data: Optional[dict] = None
    requires_input: bool = True
    conversation_complete: bool = False
    error: bool = False

class UploadResponse(BaseModel):
    status: str
    chunks_processed: int

class ApiResponse(BaseModel, Generic[T]):
    success: bool
    message: Optional[str] = None
    access_token: Optional[str] = None
    user_id: Optional[str] = None
    data: Optional[T] = None

# Routes
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/api/login", response_model=ApiResponse)
async def login(login_data: LoginRequest):
    try:
        user_id = authenticate_user(login_data.username, login_data.password)
        if user_id:
            token = auth_handler.create_token(user_id)
            return ApiResponse(
                success=True,
                message="Login successful",
                access_token=token,
                user_id=user_id
            )
        else:
            return ApiResponse(
                success=False,
                message="Invalid credentials"
            )
    except Exception as e:
        logger.error(f"Login error: {e}")
        return ApiResponse(
            success=False,
            message="Login failed"
        )

@app.post("/api/token", response_model=ApiResponse)
async def create_token(token_data: TokenRequest):
    """Create JWT token for a valid user_id"""
    try:
        from auth.user_store import user_store
        
        # Validate that user_id exists in the user store
        user_data = user_store.get_user_by_id(token_data.user_id)
        if not user_data:
            return ApiResponse(
                success=False,
                message="User not found"
            )
        
        # Create JWT token for the valid user_id
        token = auth_handler.create_token(token_data.user_id)
        
        return ApiResponse(
            success=True,
            message="Token created successfully",
            access_token=token,
            user_id=token_data.user_id,
            data={"username": user_data["user_name"]}
        )
        
    except Exception as e:
        logger.error(f"Token creation error: {e}")
        return ApiResponse(
            success=False,
            message="Error creating token"
        )


@app.post("/api/chat", response_model=ApiResponse[ChatResponse])
async def chat_endpoint(request: Request, current_user: str = Depends(auth_handler.get_current_user)):
    try:
        # Get the raw request body
        body = await request.body()
        
        # Try to parse as JSON
        try:
            if isinstance(body, bytes):
                body_str = body.decode('utf-8')
            else:
                body_str = body
            
            # Try to parse as JSON string first (for external API calls)
            if isinstance(body_str, str) and body_str.startswith('{'):
                try:
                    data = json.loads(body_str)
                except json.JSONDecodeError:
                    # If it's not a valid JSON string, try to parse as regular JSON
                    data = await request.json()
            else:
                # Parse as regular JSON
                data = await request.json()
        except Exception as json_error:
            logger.error(f"JSON parsing error: {json_error}")
            raise HTTPException(status_code=400, detail="Invalid JSON format")
        
        # Validate the parsed data against ChatRequest model
        try:
            chat_data = ChatRequest(**data)
        except Exception as validation_error:
            logger.error(f"Validation error: {validation_error}")
            raise HTTPException(status_code=400, detail=f"Invalid request format: {str(validation_error)}")
        
        chatbot = get_chatbot_for_user(current_user)  # current_user is now user_id
        user_id = chat_data.user_id or current_user
        chat_response = chatbot.chat(chat_data.message, user_id)
        
        # Store collected data if available
        collected_data = chat_response.get("collected_data")
        if collected_data and chat_response.get("mode") == "pre_trained":
            session_id = f"{current_user}_{user_id}"
            answer_storage.store_answers(current_user, session_id, collected_data)
        
        # Convert the new response format to ChatResponse
        chat_data = ChatResponse(
            response=chat_response["response"],
            sources=[],
            mode=chat_response.get("mode"),
            state=chat_response.get("state"),
            options=chat_response.get("options", []),
            collected_data=chat_response.get("collected_data"),
            requires_input=chat_response.get("requires_input", True),
            conversation_complete=chat_response.get("conversation_complete", False),
            error=chat_response.get("error", False)
        )
        
        return ApiResponse(
            success=True,
            message="Chat response generated successfully",
            data=chat_data
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chat error: {e}")
        return ApiResponse(
            success=False,
            message="Error processing message"
        )

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
        vector_db = DatabaseFactory.create_vector_db(user_namespace=current_user)  # current_user is now user_id
        
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

@app.post("/api/upload-docs", response_model=UploadResponse)
async def upload_documents(files: List[UploadFile] = File(...), current_user: str = Depends(auth_handler.get_current_user)):
    try:
        processor = ContentProcessor()
        embedding_generator = EmbeddingGenerator()
        vector_db = DatabaseFactory.create_vector_db(user_namespace=current_user)  # current_user is now user_id

        processed_chunks: List[dict] = []
        for f in files:
            data = await f.read()
            name = f.filename or "document"
            lower = name.lower()
            if lower.endswith(".pdf"):
                parsed = parse_pdf(data, name)
            elif lower.endswith(".docx") or lower.endswith(".doc"):
                parsed = parse_docx(data, name)
            else:
                parsed = parse_txt(data, name)

            page = {
                "url": f"uploaded://{name}",
                "title": parsed["title"],
                "content": parsed["content"],
                "crawled_at": "uploaded"
            }
            chunks = processor.process_pages([page])
            processed_chunks.extend(chunks)

        if processed_chunks:
            texts = [c["content"] for c in processed_chunks]
            embeddings = embedding_generator.generate_embeddings(texts)
            vector_db.store_documents(processed_chunks, embeddings)
            return UploadResponse(status="success", chunks_processed=len(processed_chunks))
        else:
            return UploadResponse(status="success", chunks_processed=0)
    except Exception as e:
        logger.error(f"Upload error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/stats")
async def get_stats(current_user: str = Depends(auth_handler.get_current_user)):
    try:
        vector_db = DatabaseFactory.create_vector_db(user_namespace=current_user)  # current_user is now user_id
        count = vector_db.get_collection_stats()
        return {"document_count": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chat/reset")
async def reset_chat_session(user_id: str, current_user: str = Depends(auth_handler.get_current_user)):
    """Reset a user's chat session (for pre_trained mode)"""
    try:
        chatbot = get_chatbot_for_user(current_user)
        chatbot.reset_chat_session(user_id)
        return {"status": "success", "message": "Chat session reset"}
    except Exception as e:
        logger.error(f"Reset chat error: {e}")
        raise HTTPException(status_code=500, detail="Error resetting chat session")

@app.get("/api/chat/session/{user_id}")
async def get_chat_session(user_id: str, current_user: str = Depends(auth_handler.get_current_user)):
    """Get collected data for a user session (for pre_trained mode)"""
    try:
        chatbot = get_chatbot_for_user(current_user)
        session_data = chatbot.get_session_data(user_id)
        return {"session_data": session_data}
    except Exception as e:
        logger.error(f"Get session error: {e}")
        raise HTTPException(status_code=500, detail="Error getting session data")

@app.get("/api/answers")
async def get_stored_answers(current_user: str = Depends(auth_handler.get_current_user), limit: int = 100):
    """Get all stored answers (admin only)"""
    try:
        answers = answer_storage.get_all_answers(limit)
        return {"answers": answers, "count": len(answers)}
    except Exception as e:
        logger.error(f"Get answers error: {e}")
        raise HTTPException(status_code=500, detail="Error getting stored answers")

@app.get("/api/answers/{user_id}/{session_id}")
async def get_user_answers(user_id: str, session_id: str, current_user: str = Depends(auth_handler.get_current_user)):
    """Get stored answers for a specific user session"""
    try:
        answers = answer_storage.get_answers(user_id, session_id)
        return {"answers": answers}
    except Exception as e:
        logger.error(f"Get user answers error: {e}")
        raise HTTPException(status_code=500, detail="Error getting user answers")

@app.get("/api/user/info", response_model=ApiResponse)
async def get_user_info(current_user: str = Depends(auth_handler.get_current_user)):
    """Get current user information"""
    try:
        from auth.user_store import user_store
        user_data = user_store.get_user_by_id(current_user)
        if user_data:
            return ApiResponse(
                success=True,
                message="User information retrieved successfully",
                user_id=user_data["user_id"],
                data={"username": user_data["user_name"]}
            )
        else:
            return ApiResponse(
                success=False,
                message="User not found"
            )
    except Exception as e:
        logger.error(f"Get user info error: {e}")
        return ApiResponse(
            success=False,
            message="Error getting user information"
        )

# Health check
@app.get("/health", response_model=ApiResponse)
async def health_check():
    return ApiResponse(
        success=True,
        message="Service is healthy",
        data={"status": "healthy", "version": "2.0"}
    )

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
