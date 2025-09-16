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
from database.vector_db import VectorDB
from config import Config

logger = logging.getLogger(__name__)

class ChatBot:
    def __init__(self):
        self.embedding_generator = EmbeddingGenerator()
        self.vector_db = VectorDB()
        self.setup_openai()
        
    def setup_openai(self):
        """Setup OpenAI client if API key is available"""
        if Config.OPENAI_API_KEY:
            if _OPENAI_V1:
                self._openai_client = OpenAI(api_key=Config.OPENAI_API_KEY)
            else:
                openai.api_key = Config.OPENAI_API_KEY  # legacy
        else:
            logger.warning("OpenAI API key not found. Using simple response generation.")
            
    def get_relevant_context(self, query: str, top_k: int = None) -> List[Dict]:
        """Get relevant context from vector database"""
        top_k = top_k or Config.TOP_K_RESULTS
        
        try:
            query_embedding = self.embedding_generator.generate_embedding(query)
            results = self.vector_db.search_similar(query_embedding, top_k=top_k)
            
            context_docs = []
            docs = results.get('documents', [[]])[0]
            metas = results.get('metadatas', [[]])[0]
            dists = results.get('distances', [[]])[0]
            for i in range(len(docs)):
                similarity = 1 - float(dists[i])
                if similarity >= Config.SIMILARITY_THRESHOLD:
                    context_docs.append({
                        'content': docs[i],
                        'metadata': metas[i],
                        'similarity': similarity
                    })

            # If nothing met the threshold, fall back to top results so the model has some context
            if not context_docs and docs:
                for i in range(min(len(docs), top_k)):
                    similarity = 1 - float(dists[i])
                    context_docs.append({
                        'content': docs[i],
                        'metadata': metas[i],
                        'similarity': similarity
                    })

            return context_docs
            
        except Exception as e:
            logger.error(f"Error getting relevant context: {e}")
            return []
    
    def generate_llm_response(self, query: str, context_docs: List[Dict]) -> str:
        """Generate response using OpenAI GPT"""
        if not Config.OPENAI_API_KEY:
            return self.generate_simple_response(query, context_docs)
            
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
                response = self._openai_client.chat.completions.create(
                    model=Config.LLM_MODEL,
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant that answers questions based on provided context."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=Config.LLM_TEMPERATURE,
                    max_tokens=Config.LLM_MAX_TOKENS,
                )
                return (response.choices[0].message.content or "").strip()
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
            return self.generate_simple_response(query, context_docs)
    
    def generate_simple_response(self, query: str, context_docs: List[Dict]) -> str:
        """Fallback response generation"""
        if not context_docs:
            return "I couldn't find relevant information to answer your question in my knowledge base."
        
        response = "Based on my knowledge:\n\n"
        for doc in context_docs:
            response += f"• From {doc['metadata']['title']}: {doc['content'][:200]}...\n"
        
        response += "\nWould you like me to search for more specific information?"
        return response
    
    def chat(self, query: str) -> str:
        """Main chat method"""
        context_docs = self.get_relevant_context(query)
        return self.generate_llm_response(query, context_docs)
