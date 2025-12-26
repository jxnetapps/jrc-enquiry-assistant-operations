import re
from typing import List, Dict

class ContentProcessor:
    @staticmethod
    def clean_text(text: str) -> str:
        """Clean and preprocess text content"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s.,!?;:]', ' ', text)
        return text.strip()
    
    @staticmethod
    def chunk_content(content: Dict[str, str], chunk_size: int = None, overlap: int = None) -> List[Dict[str, str]]:
        """Split content into overlapping chunks
        
        Args:
            content: Dictionary containing content to chunk
            chunk_size: Size of each chunk (defaults to Config.CHUNK_SIZE)
            overlap: Overlap between chunks (defaults to Config.CHUNK_OVERLAP)
        """
        # Use config defaults if not provided
        chunk_size = chunk_size or Config.CHUNK_SIZE
        overlap = overlap or Config.CHUNK_OVERLAP
        
        text = content['content']
        chunks = []
        
        start = 0
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            
            chunks.append({
                'url': content['url'],
                'title': content['title'],
                'content': chunk,
                'chunk_index': len(chunks),
                'crawled_at': content.get('crawled_at', '')
            })
            
            start = end - overlap  # Overlap chunks
            
        return chunks
    
    def process_pages(self, pages: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Process all crawled pages"""
        processed_chunks = []
        
        for page in pages:
            # Clean content
            page['content'] = self.clean_text(page['content'])
            
            # Chunk content
            chunks = self.chunk_content(page)
            processed_chunks.extend(chunks)
            
        return processed_chunks
