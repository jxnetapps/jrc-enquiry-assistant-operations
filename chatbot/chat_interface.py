from typing import List, Dict, Optional
import logging
try:
    # openai>=1.0 client
    from openai import OpenAI
    _OPENAI_V1 = True
except Exception:  # pragma: no cover
    import openai  # type: ignore
    _OPENAI_V1 = False
from embedding.embedding_generator import EmbeddingGenerator
from database.db_factory import DatabaseFactory
from config import Config
from chatbot.chat_states import PreTrainedChatFlow
from chatbot.session_manager import session_manager

logger = logging.getLogger(__name__)

class ChatBot:
    def __init__(self, user_namespace: str = None, namespace: str = None):
        self.embedding_generator = EmbeddingGenerator()
        self.vector_db = DatabaseFactory.create_vector_db(user_namespace=user_namespace, namespace=namespace)
        self.user_namespace = user_namespace
        self.namespace = namespace
        self.setup_openai()
        
    def setup_openai(self):
        """Setup OpenAI client if API key is available"""
        if Config.OPENAI_API_KEY:
            if _OPENAI_V1:
                try:
                    # Initialize OpenAI client
                    # Note: Requires httpx==0.27.2 for compatibility with OpenAI 1.3.0
                    self._openai_client = OpenAI(api_key=Config.OPENAI_API_KEY)
                    logger.debug("OpenAI client initialized successfully")
                except TypeError as e:
                    # Handle version compatibility issues
                    error_msg = str(e)
                    if 'proxies' in error_msg.lower():
                        logger.error(
                            "OpenAI client initialization failed due to httpx version incompatibility. "
                            "Please install httpx==0.27.2: pip install httpx==0.27.2"
                        )
                    else:
                        logger.error(f"OpenAI client initialization issue: {e}")
                    self._openai_client = None
                except Exception as e:
                    logger.error(f"Failed to initialize OpenAI client: {e}")
                    self._openai_client = None
            else:
                openai.api_key = Config.OPENAI_API_KEY  # legacy
        else:
            logger.warning("OpenAI API key not found. Using simple response generation.")
            self._openai_client = None
            
    def get_relevant_context(self, query: str, top_k: int = None, max_sources: int = None) -> List[Dict]:
        """Get relevant context from vector database
        
        Args:
            query: The search query
            top_k: Number of top results to retrieve (overrides config if provided)
            max_sources: Maximum number of sources to return (limits results after retrieval)
        """
        top_k = top_k or Config.TOP_K_RESULTS
        
        try:
            query_embedding = self.embedding_generator.generate_embedding(query)
            results = self.vector_db.search_similar(query_embedding, top_k=top_k)
            
            context_docs = []
            seen_keys = set()  # Track seen URL+content combinations to avoid duplicates
            docs = results.get('documents', [[]])[0]
            metas = results.get('metadatas', [[]])[0]
            dists = results.get('distances', [[]])[0]
            
            for i in range(len(docs)):
                similarity = 1 - float(dists[i])
                if similarity >= Config.SIMILARITY_THRESHOLD:
                    metadata = metas[i] if isinstance(metas[i], dict) else {}
                    url = metadata.get('url', '')
                    content = docs[i]
                    
                    # Create a unique key for deduplication (URL + first 100 chars of content)
                    # This helps identify duplicate chunks from the same URL
                    content_hash = content[:100] if content else ''
                    unique_key = f"{url}_{content_hash}"
                    
                    # Skip if we've already seen this URL+content combination
                    if unique_key not in seen_keys:
                        seen_keys.add(unique_key)
                        context_docs.append({
                            'content': content,
                            'metadata': metadata,
                            'similarity': similarity
                        })

            # If nothing met the threshold, fall back to top results so the model has some context
            if not context_docs and docs:
                for i in range(min(len(docs), top_k)):
                    similarity = 1 - float(dists[i])
                    metadata = metas[i] if isinstance(metas[i], dict) else {}
                    url = metadata.get('url', '')
                    content = docs[i]
                    
                    # Deduplicate here too
                    content_hash = content[:100] if content else ''
                    unique_key = f"{url}_{content_hash}"
                    
                    if unique_key not in seen_keys:
                        seen_keys.add(unique_key)
                        context_docs.append({
                            'content': content,
                            'metadata': metadata,
                            'similarity': similarity
                        })
            
            # Limit number of sources if max_sources is specified
            if max_sources and max_sources > 0:
                context_docs = context_docs[:max_sources]

            return context_docs
            
        except Exception as e:
            logger.error(f"Error getting relevant context: {e}")
            return []
    
    def generate_llm_response(self, query: str, context_docs: List[Dict], max_response_length: Optional[int] = None, truncate_content: bool = False) -> str:
        """Generate response using OpenAI GPT"""
        if not Config.OPENAI_API_KEY:
            logger.info("OpenAI API key not set, using simple response generation")
            return self.generate_simple_response(query, context_docs, max_response_length=max_response_length, truncate_content=truncate_content)
            
        try:
            # Prepare context
            context_text = "\n\n".join([
                f"Source: {doc['metadata']['title']} ({doc['metadata']['url']})\n"
                f"Content: {doc['content']}\n"
                f"Relevance: {doc['similarity']:.2f}"
                for doc in context_docs
            ])
            
            # Create prompt
            prompt = f"""Based on the following context information, provide a helpful answer to the user's question.

Context:
{context_text}

User Question: {query}

Instructions:
- Answer based only on the provided context
- If the context doesn't contain relevant information, say so
- Be concise and helpful
- Cite your sources when appropriate

Answer:"""
            
            if _OPENAI_V1:
                if not hasattr(self, '_openai_client') or self._openai_client is None:
                    logger.warning("OpenAI client not available, using simple response")
                    return self.generate_simple_response(query, context_docs, max_response_length=max_response_length, truncate_content=truncate_content)
                
                logger.debug(f"Calling OpenAI API with model: {Config.LLM_MODEL}, max_tokens: {Config.LLM_MAX_TOKENS}")
                try:
                    response = self._openai_client.chat.completions.create(
                        model=Config.LLM_MODEL,
                        messages=[
                            {"role": "system", "content": "You are a helpful assistant that answers questions based on provided context."},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=Config.LLM_TEMPERATURE,
                        max_tokens=Config.LLM_MAX_TOKENS,
                    )
                    result = (response.choices[0].message.content or "").strip()
                    logger.debug(f"OpenAI API call successful, response length: {len(result)}")
                    
                    # Truncate response if max_response_length is specified
                    if max_response_length and max_response_length > 0 and len(result) > max_response_length:
                        # Truncate at word boundary
                        truncated = result[:max_response_length]
                        last_space = truncated.rfind(' ')
                        if last_space > max_response_length * 0.8:  # Only truncate at word if we're not losing too much
                            result = truncated[:last_space] + "... [response truncated]"
                        else:
                            result = truncated + "... [response truncated]"
                        logger.debug(f"Response truncated to {len(result)} characters")
                    
                    return result
                except Exception as api_error:
                    logger.error(f"OpenAI API error: {api_error}", exc_info=True)
                    logger.warning("Falling back to simple response due to API error")
                    return self.generate_simple_response(query, context_docs, max_response_length=max_response_length, truncate_content=truncate_content)
            else:
                response = openai.ChatCompletion.create(  # legacy
                    model=Config.LLM_MODEL,
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant that answers questions based on provided context."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=Config.LLM_TEMPERATURE,
                    max_tokens=Config.LLM_MAX_TOKENS
                )
                return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return self.generate_simple_response(query, context_docs, max_response_length=max_response_length, truncate_content=truncate_content)
    
    def generate_simple_response(self, query: str, context_docs: List[Dict], max_response_length: Optional[int] = None, truncate_content: bool = False) -> str:
        """Fallback response generation (used when OpenAI is not available)
        
        Args:
            query: The user's query
            context_docs: List of relevant context documents
            max_response_length: Maximum length of response text (characters)
            truncate_content: Whether to truncate individual source content
        """
        if not context_docs:
            return "I couldn't find relevant information to answer your question in my knowledge base."
        
        # Combine all context into a comprehensive response
        response_parts = []
        
        for i, doc in enumerate(context_docs, 1):
            title = doc['metadata'].get('title', 'Unknown Source')
            url = doc['metadata'].get('url', '')
            content = doc['content']
            similarity = doc.get('similarity', 0)
            
            # Truncate content if requested
            if truncate_content and len(content) > 500:
                content = content[:500] + "... [content truncated]"
            
            response_parts.append(f"{i}. From {title}")
            if url:
                response_parts.append(f"   ({url})")
            response_parts.append(f"   Relevance: {similarity:.1%}\n")
            response_parts.append(f"   {content}\n\n")
        
        response_parts.append("\nWould you like me to search for more specific information?")
        response = "".join(response_parts)
        
        # Truncate overall response if max_response_length is specified
        if max_response_length and max_response_length > 0 and len(response) > max_response_length:
            # Truncate at word boundary
            truncated = response[:max_response_length]
            last_space = truncated.rfind(' ')
            if last_space > max_response_length * 0.8:
                response = truncated[:last_space] + "... [response truncated]"
            else:
                response = truncated + "... [response truncated]"
        
        return response
    
    def chat(self, query: str, user_id: str = "default", 
             top_k: Optional[int] = None,
             max_sources: Optional[int] = None,
             max_response_length: Optional[int] = None,
             truncate_content: bool = False) -> Dict[str, any]:
        """Main chat method that handles both knowledge_base and pre_trained modes
        
        Args:
            query: The user's message
            user_id: The user ID for session management
            top_k: Number of top results to retrieve from vector DB
            max_sources: Maximum number of sources to include in response
            max_response_length: Maximum length of response text (characters)
            truncate_content: Whether to truncate content in sources
        """
        if Config.CHAT_BEHAVIOR == "pre_trained":
            return self._handle_pre_trained_chat(query, user_id, top_k=top_k, 
                                                 max_sources=max_sources,
                                                 max_response_length=max_response_length,
                                                 truncate_content=truncate_content)
        else:
            return self._handle_knowledge_base_chat(query, top_k=top_k,
                                                   max_sources=max_sources,
                                                   max_response_length=max_response_length,
                                                   truncate_content=truncate_content)
    
    def _handle_pre_trained_chat(self, query: str, user_id: str,
                                 top_k: Optional[int] = None,
                                 max_sources: Optional[int] = None,
                                 max_response_length: Optional[int] = None,
                                 truncate_content: bool = False) -> Dict[str, any]:
        """Handle pre_trained chat behavior with state management
        
        Args:
            query: The user's message
            user_id: The user ID for session management
            top_k: Number of top results to retrieve from vector DB
            max_sources: Maximum number of sources to include in response
            max_response_length: Maximum length of response text (characters)
            truncate_content: Whether to truncate content in sources
        """
        try:
            # Get the persistent flow for this user
            pre_trained_flow = session_manager.get_flow_for_user(user_id)
            
            # Process message through the predefined flow
            flow_response = pre_trained_flow.process_message(user_id, query)
            
            # If it's a knowledge query, use the knowledge base
            if flow_response.get("response") == "knowledge_query":
                knowledge_response = self._handle_knowledge_base_chat(query, top_k=top_k,
                                                                     max_sources=max_sources,
                                                                     max_response_length=max_response_length,
                                                                     truncate_content=truncate_content)
                return {
                    "response": knowledge_response["response"],
                    "mode": "pre_trained",
                    "state": flow_response["state"],
                    "collected_data": flow_response.get("collected_data", {}),
                    "requires_input": False
                }
            else:
                return {
                    "response": flow_response["response"],
                    "mode": "pre_trained",
                    "state": flow_response["state"],
                    "options": flow_response.get("options", []),
                    "collected_data": flow_response.get("collected_data", {}),
                    "requires_input": flow_response.get("requires_input", True),
                    "conversation_complete": flow_response.get("conversation_complete", False)
                }
        except Exception as e:
            logger.error(f"Error in pre_trained chat: {e}")
            return {
                "response": "I'm sorry, I encountered an error. Let's start over.",
                "mode": "pre_trained",
                "state": "error",
                "requires_input": True,
                "error": True
            }
    
    def _handle_knowledge_base_chat(self, query: str, top_k: Optional[int] = None,
                                     max_sources: Optional[int] = None, 
                                     max_response_length: Optional[int] = None,
                                     truncate_content: bool = False) -> Dict[str, any]:
        """Handle knowledge_base chat behavior (original functionality)
        
        Args:
            query: The user's message
            top_k: Number of top results to retrieve from vector DB
            max_sources: Maximum number of sources to include in response
            max_response_length: Maximum length of response text (characters)
            truncate_content: Whether to truncate content in sources
        """
        try:
            context_docs = self.get_relevant_context(query, top_k=top_k, max_sources=max_sources)
            response = self.generate_llm_response(query, context_docs, max_response_length=max_response_length)
            
            # If OpenAI is not available, use simple response with truncation options
            if not Config.OPENAI_API_KEY or (hasattr(self, '_openai_client') and self._openai_client is None):
                response = self.generate_simple_response(query, context_docs, 
                                                        max_response_length=max_response_length,
                                                        truncate_content=truncate_content)
            
            return {
                "response": response,
                "mode": "knowledge_base",
                "context_docs": len(context_docs),
                "requires_input": True
            }
        except Exception as e:
            logger.error(f"Error in knowledge_base chat: {e}")
            return {
                "response": "I'm sorry, I couldn't process your request. Please try again.",
                "mode": "knowledge_base",
                "requires_input": True,
                "error": True
            }
    
    def reset_chat_session(self, user_id: str) -> None:
        """Reset a user's chat session (for pre_trained mode)"""
        if Config.CHAT_BEHAVIOR == "pre_trained":
            session_manager.reset_user_session(user_id)
    
    def get_session_data(self, user_id: str) -> Optional[Dict[str, any]]:
        """Get collected data for a user session (for pre_trained mode)"""
        if Config.CHAT_BEHAVIOR == "pre_trained":
            return session_manager.get_user_session_data(user_id)
        return None
