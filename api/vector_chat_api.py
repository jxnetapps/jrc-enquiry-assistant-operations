from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, File
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional, TypeVar, Generic
import logging
import json
import asyncio

from config import Config
from crawler.web_crawler import WebCrawler
from crawler.content_processor import ContentProcessor
from embedding.embedding_generator import EmbeddingGenerator
from database.db_factory import DatabaseFactory
from database.answer_storage import answer_storage
from chatbot.chat_interface import ChatBot
from auth.authentication import AuthHandler
from utils.doc_parser import parse_pdf, parse_docx, parse_txt

# Setup logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api", tags=["Vector Chat"])

# Initialize components
auth_handler = AuthHandler()

def get_chatbot_for_user(user_id: str) -> ChatBot:
    return ChatBot(user_namespace=user_id)

T = TypeVar('T')

# Pydantic models
class ChatRequest(BaseModel):
    message: str
    user_id: Optional[str] = None
    namespace: Optional[str] = None  # Pinecone namespace (takes precedence over config)
    # Optional response limiting parameters for public API
    max_response_length: Optional[int] = None  # Maximum length of response text (characters)
    max_sources: Optional[int] = None  # Maximum number of sources to include in response
    top_k: Optional[int] = None  # Number of top results to retrieve from vector DB (overrides config)
    truncate_content: Optional[bool] = False  # Whether to truncate content in sources

class CrawlRequest(BaseModel):
    url: str
    max_pages: Optional[int] = None
    depth: Optional[int] = None
    namespace: Optional[str] = None  # Pinecone namespace (takes precedence over config)

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

@router.post("/chat/public", response_model=ApiResponse[ChatResponse])
async def chat_endpoint_public(chat_data: ChatRequest):
    """Public chat endpoint for vector-based conversations (no authentication required)"""
    try:
        # Use a default public user ID if not provided
        public_user_id = chat_data.user_id or "public_user"
        
        # Create chatbot with namespace if provided (API namespace takes precedence)
        namespace = chat_data.namespace
        chatbot = ChatBot(user_namespace=public_user_id, namespace=namespace)
        
        # Pass optional response limiting parameters
        chat_response = chatbot.chat(
            chat_data.message, 
            public_user_id,
            top_k=chat_data.top_k,
            max_sources=chat_data.max_sources,
            max_response_length=chat_data.max_response_length,
            truncate_content=chat_data.truncate_content or False
        )
        
        # Store collected data if available (using public user ID)
        collected_data = chat_response.get("collected_data")
        if collected_data and chat_response.get("mode") == "pre_trained":
            session_id = f"{public_user_id}_{public_user_id}"
            answer_storage.store_answers(public_user_id, session_id, collected_data)
        
        # Convert the new response format to ChatResponse
        response_data = ChatResponse(
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
            data=response_data
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Public chat error: {e}", exc_info=True)
        return ApiResponse(
            success=False,
            message=f"Error processing message: {str(e)}"
        )

@router.post("/chat", response_model=ApiResponse[ChatResponse])
async def chat_endpoint(request: Request, current_user: str = Depends(auth_handler.get_current_user)):
    """Chat endpoint for vector-based conversations (requires authentication)"""
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
        
        # Create chatbot with namespace if provided (API namespace takes precedence)
        namespace = chat_data.namespace
        chatbot = ChatBot(user_namespace=current_user, namespace=namespace)  # current_user is now user_id
        
        user_id = chat_data.user_id or current_user
        # Pass optional response limiting parameters (also available for authenticated endpoint)
        chat_response = chatbot.chat(
            chat_data.message, 
            user_id,
            top_k=chat_data.top_k,
            max_sources=chat_data.max_sources,
            max_response_length=chat_data.max_response_length,
            truncate_content=chat_data.truncate_content or False
        )
        
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

@router.post("/crawl")
async def crawl_website(crawl_data: CrawlRequest, current_user: str = Depends(auth_handler.get_current_user)):
    """Crawl a website and store content in vector database"""
    try:
        logger.info(f"Starting crawl request: url={crawl_data.url}, namespace={crawl_data.namespace}, user={current_user}")
        
        crawler = WebCrawler(
            max_pages=crawl_data.max_pages or Config.MAX_PAGES_TO_CRAWL,
            depth=crawl_data.depth or Config.CRAWL_DEPTH,
            delay=Config.CRAWL_DELAY,
            max_concurrent=Config.MAX_CONCURRENT_REQUESTS
        )
        processor = ContentProcessor()
        embedding_generator = EmbeddingGenerator()
        
        # Use namespace from API if provided (takes precedence over config)
        logger.info(f"Creating vector database with namespace: {crawl_data.namespace}")
        logger.info(f"Current VECTOR_DATABASE_TYPE: {Config.VECTOR_DATABASE_TYPE}")
        
        # Check if database type is correct for Pinecone
        if Config.VECTOR_DATABASE_TYPE != "pinecone":
            error_msg = (
                f"VECTOR_DATABASE_TYPE is set to '{Config.VECTOR_DATABASE_TYPE}' but Pinecone is required. "
                f"Please set VECTOR_DATABASE_TYPE=pinecone in your environment variables or .env file."
            )
            logger.error(error_msg)
            raise HTTPException(status_code=400, detail=error_msg)
        
        vector_db = DatabaseFactory.create_vector_db(user_namespace=current_user, namespace=crawl_data.namespace)
        logger.info(f"Vector database created successfully (type: {Config.VECTOR_DATABASE_TYPE})")
        
        logger.info(f"Starting crawl for URL: {crawl_data.url}")
        pages = await crawler.crawl(crawl_data.url)
        logger.info(f"Crawled {len(pages)} pages")
        
        if not pages:
            logger.warning("No pages were crawled")
            return {
                "status": "success",
                "message": "No pages were crawled",
                "pages_crawled": 0,
                "chunks_processed": 0
            }
        
        logger.info("Processing pages into chunks")
        processed_chunks = processor.process_pages(pages)
        logger.info(f"Processed {len(processed_chunks)} chunks")
        
        if processed_chunks:
            logger.info("Generating embeddings")
            texts = [chunk['content'] for chunk in processed_chunks]
            embeddings = embedding_generator.generate_embeddings(texts)
            logger.info(f"Generated {len(embeddings)} embeddings")
            
            logger.info(f"Storing {len(processed_chunks)} documents in vector database")
            vector_db.store_documents(processed_chunks, embeddings)
            logger.info("Documents stored successfully")
            
            return {
                "status": "success",
                "pages_crawled": len(pages),
                "chunks_processed": len(processed_chunks),
                "namespace": crawl_data.namespace or "default"
            }
        else:
            logger.warning("No quality content found after processing")
            return {
                "status": "success",
                "message": "No quality content found",
                "pages_crawled": len(pages),
                "chunks_processed": 0
            }
            
    except HTTPException:
        # Re-raise HTTP exceptions (like our 400 error) as-is
        raise
    except Exception as e:
        logger.error(f"Crawl error: {e}", exc_info=True)
        import traceback
        error_details = traceback.format_exc()
        logger.error(f"Full traceback: {error_details}")
        raise HTTPException(status_code=500, detail=f"Crawl failed: {str(e)}")

@router.post("/upload-docs", response_model=UploadResponse)
async def upload_documents(
    files: List[UploadFile] = File(...), 
    current_user: str = Depends(auth_handler.get_current_user),
    namespace: Optional[str] = None  # Pinecone namespace (takes precedence over config)
):
    """Upload documents and store content in vector database"""
    try:
        processor = ContentProcessor()
        embedding_generator = EmbeddingGenerator()
        # Use namespace from API if provided (takes precedence over config)
        vector_db = DatabaseFactory.create_vector_db(user_namespace=current_user, namespace=namespace)

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

@router.get("/stats")
async def get_stats(
    current_user: str = Depends(auth_handler.get_current_user),
    namespace: Optional[str] = None  # Pinecone namespace (takes precedence over config)
):
    """Get vector database statistics"""
    try:
        # Use namespace from API if provided (takes precedence over config)
        vector_db = DatabaseFactory.create_vector_db(user_namespace=current_user, namespace=namespace)
        count = vector_db.get_collection_stats()
        return {"document_count": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat/reset")
async def reset_chat_session(user_id: str, current_user: str = Depends(auth_handler.get_current_user)):
    """Reset a user's chat session (for pre_trained mode)"""
    try:
        chatbot = get_chatbot_for_user(current_user)
        chatbot.reset_chat_session(user_id)
        return {"status": "success", "message": "Chat session reset"}
    except Exception as e:
        logger.error(f"Reset chat error: {e}")
        raise HTTPException(status_code=500, detail="Error resetting chat session")

@router.get("/chat/session/{user_id}")
async def get_chat_session(user_id: str, current_user: str = Depends(auth_handler.get_current_user)):
    """Get collected data for a user session (for pre_trained mode)"""
    try:
        chatbot = get_chatbot_for_user(current_user)
        session_data = chatbot.get_session_data(user_id)
        return {"session_data": session_data}
    except Exception as e:
        logger.error(f"Get session error: {e}")
        raise HTTPException(status_code=500, detail="Error getting session data")

@router.get("/answers")
async def get_stored_answers(current_user: str = Depends(auth_handler.get_current_user), limit: int = 100):
    """Get all stored answers (admin only)"""
    try:
        answers = answer_storage.get_all_answers(limit)
        return {"answers": answers, "count": len(answers)}
    except Exception as e:
        logger.error(f"Get answers error: {e}")
        raise HTTPException(status_code=500, detail="Error getting stored answers")

@router.get("/answers/{user_id}/{session_id}")
async def get_user_answers(user_id: str, session_id: str, current_user: str = Depends(auth_handler.get_current_user)):
    """Get stored answers for a specific user session"""
    try:
        answers = answer_storage.get_answers(user_id, session_id)
        return {"answers": answers}
    except Exception as e:
        logger.error(f"Get user answers error: {e}")
        raise HTTPException(status_code=500, detail="Error getting user answers")
