from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List
import logging
from config import Config

logger = logging.getLogger(__name__)

class EmbeddingGenerator:
    def __init__(self, model_name: str = Config.EMBEDDING_MODEL):
        self.model = None
        self.model_name = model_name
        self._initialize_model()
        
    def _initialize_model(self):
        try:
            if "text-embedding" in self.model_name.lower():
                # For OpenAI embeddings (would need API key)
                logger.info("Using OpenAI embeddings - make sure OPENAI_API_KEY is set")
                # Implementation for OpenAI would go here
                pass
            else:
                # For local sentence-transformers models
                logger.info(f"Loading local model: {self.model_name}")
                self.model = SentenceTransformer(self.model_name)
                
        except Exception as e:
            logger.error(f"Failed to initialize embedding model: {e}")
            raise
            
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of texts"""
        if not self.model:
            raise ValueError("Embedding model not initialized")
            
        try:
            # Process in batches to avoid memory issues
            batch_size = Config.EMBEDDING_BATCH_SIZE
            all_embeddings = []
            
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i + batch_size]
                batch_embeddings = self.model.encode(batch, convert_to_numpy=True)
                all_embeddings.extend(batch_embeddings.tolist())
                
            return all_embeddings
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            raise
    
    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for a single text"""
        return self.generate_embeddings([text])[0]
