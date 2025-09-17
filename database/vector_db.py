import os
import json
import pickle
from typing import List, Dict, Any, Optional
import logging

import numpy as np
import faiss

from config import Config
from database.vector_db_interface import VectorDBInterface

logger = logging.getLogger(__name__)

class VectorDB(VectorDBInterface):
    def __init__(self, user_namespace: Optional[str] = None):
        self.index = None  # faiss.Index
        self.ids: List[str] = []
        self.texts: List[str] = []
        self.metadatas: List[Dict[str, Any]] = []
        self.dimension: int = 0
        self.user_namespace = self._sanitize_namespace(user_namespace) if user_namespace else None
        base_dir = os.path.join(Config.CHROMA_DB_PATH, "users", self.user_namespace) if self.user_namespace else Config.CHROMA_DB_PATH
        self.storage_dir = os.path.join(base_dir, Config.COLLECTION_NAME)
        self.index_path = os.path.join(self.storage_dir, "index.faiss")
        self.meta_path = os.path.join(self.storage_dir, "meta.pkl")
        self._last_loaded_mtime: float = 0.0
        self._initialize_db()

    @staticmethod
    def _sanitize_namespace(ns: Optional[str]) -> Optional[str]:
        if not ns:
            return None
        # Keep alphanumerics, dash and underscore. Replace others with underscore.
        safe = []
        for ch in ns:
            if ch.isalnum() or ch in ("-", "_"):
                safe.append(ch)
            else:
                safe.append("_")
        return "".join(safe)[:64]
        
    def _initialize_db(self):
        try:
            os.makedirs(self.storage_dir, exist_ok=True)
            if os.path.exists(self.index_path) and os.path.exists(self.meta_path):
                self.index = faiss.read_index(self.index_path)
                with open(self.meta_path, "rb") as f:
                    saved = pickle.load(f)
                    self.ids = saved.get("ids", [])
                    self.texts = saved.get("texts", [])
                    self.metadatas = saved.get("metadatas", [])
                    self.dimension = saved.get("dimension", 0)
                try:
                    self._last_loaded_mtime = max(os.path.getmtime(self.index_path), os.path.getmtime(self.meta_path))
                except Exception:
                    self._last_loaded_mtime = 0.0
                logger.info("Vector database loaded from disk")
            else:
                # Defer index creation until first add when we know dimension
                self.index = None
                self.dimension = 0
                logger.info("Vector database initialized (new store)")
        except Exception as e:
            logger.error(f"Failed to initialize vector database: {e}")
            raise
            
    def store_documents(self, documents: List[Dict], embeddings: List[List[float]]):
        """Store documents and their embeddings in the vector database"""
        try:
            if not documents or not embeddings:
                return
            # Normalize embeddings for cosine similarity (use Inner Product index)
            emb_array = np.array(embeddings, dtype=np.float32)
            if self.dimension == 0:
                self.dimension = int(emb_array.shape[1])
            if self.index is None:
                # Use IndexFlatIP with normalized vectors to approximate cosine similarity
                self.index = faiss.IndexFlatIP(self.dimension)
            # L2 normalize
            faiss.normalize_L2(emb_array)

            new_ids = [f"doc_{len(self.ids) + i}_{hash(doc['url'])}" for i, doc in enumerate(documents)]
            new_texts = [doc['content'] for doc in documents]
            new_metadatas = [
                {
                    'url': doc['url'],
                    'title': doc['title'],
                    'chunk_index': doc.get('chunk_index', 0),
                    'crawled_at': doc.get('crawled_at', '')
                }
                for doc in documents
            ]

            # Add to index and append metadata
            self.index.add(emb_array)
            self.ids.extend(new_ids)
            self.texts.extend(new_texts)
            self.metadatas.extend(new_metadatas)

            # Persist
            faiss.write_index(self.index, self.index_path)
            with open(self.meta_path, "wb") as f:
                pickle.dump({
                    "ids": self.ids,
                    "texts": self.texts,
                    "metadatas": self.metadatas,
                    "dimension": self.dimension,
                }, f)
            try:
                self._last_loaded_mtime = max(os.path.getmtime(self.index_path), os.path.getmtime(self.meta_path))
            except Exception:
                pass

            logger.info(f"Stored {len(documents)} documents in vector database")
        except Exception as e:
            logger.error(f"Error storing documents: {e}")
            raise
            
    def search_similar(self, query_embedding: List[float], top_k: int = 5):
        """Search for similar documents"""
        try:
            # Hot-reload index if another process updated it (e.g., upload endpoint)
            try:
                current_mtime = max(os.path.getmtime(self.index_path), os.path.getmtime(self.meta_path))
            except Exception:
                current_mtime = self._last_loaded_mtime
            if current_mtime > self._last_loaded_mtime:
                # Reload from disk
                self.index = faiss.read_index(self.index_path)
                with open(self.meta_path, "rb") as f:
                    saved = pickle.load(f)
                    self.ids = saved.get("ids", [])
                    self.texts = saved.get("texts", [])
                    self.metadatas = saved.get("metadatas", [])
                    self.dimension = saved.get("dimension", 0)
                self._last_loaded_mtime = current_mtime

            if self.index is None or self.index.ntotal == 0:
                return {"documents": [[]], "metadatas": [[]], "distances": [[]]}
            vec = np.array([query_embedding], dtype=np.float32)
            faiss.normalize_L2(vec)
            k = min(top_k, self.index.ntotal)
            distances, indices = self.index.search(vec, k)
            idxs = indices[0].tolist()
            # FAISS IndexFlatIP returns inner product (cosine similarity after normalization)
            sims = distances[0].tolist()
            # For backward compatibility with previous Chroma usage where lower distance is better,
            # expose 'distances' as cosine distance = 1 - cosine similarity
            dists = [1.0 - float(s) for s in sims]
            docs = [self.texts[i] for i in idxs]
            metas = [self.metadatas[i] for i in idxs]
            return {"documents": [docs], "metadatas": [metas], "distances": [dists]}
        except Exception as e:
            logger.error(f"Error searching similar documents: {e}")
            raise
            
    def get_collection_stats(self):
        """Get statistics about the collection"""
        try:
            return int(self.index.ntotal) if self.index is not None else 0
        except Exception as e:
            logger.error(f"Error getting collection stats: {e}")
            return 0
