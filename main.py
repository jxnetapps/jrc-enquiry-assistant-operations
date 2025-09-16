import asyncio
import logging
from crawler.web_crawler import WebCrawler
from crawler.content_processor import ContentProcessor
from embedding.embedding_generator import EmbeddingGenerator
from database.vector_db import VectorDB
from chatbot.chat_interface import ChatBot
from config import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WebChatBot:
    def __init__(self):
        self.crawler = WebCrawler(
            max_pages=Config.MAX_PAGES_TO_CRAWL,
            depth=Config.CRAWL_DEPTH,
            delay=Config.CRAWL_DELAY,
            max_concurrent=Config.MAX_CONCURRENT_REQUESTS
        )
        self.processor = ContentProcessor()
        self.embedding_generator = EmbeddingGenerator()
        self.vector_db = VectorDB()
        self.chatbot = ChatBot()
    
    async def crawl_and_process(self, start_url: str):
        """Crawl website and process content"""
        logger.info(f"Starting crawl from: {start_url}")
        
        # Crawl web pages
        pages = await self.crawler.crawl(start_url)
        logger.info(f"Crawled {len(pages)} pages")
        
        if not pages:
            logger.warning("No pages were crawled successfully")
            return 0
        
        # Process content
        processed_chunks = self.processor.process_pages(pages)
        logger.info(f"Processed into {len(processed_chunks)} chunks")
        
        # Generate embeddings
        texts = [chunk['content'] for chunk in processed_chunks]
        embeddings = self.embedding_generator.generate_embeddings(texts)
        logger.info(f"Generated {len(embeddings)} embeddings")
        
        # Store in vector database
        self.vector_db.store_documents(processed_chunks, embeddings)
        logger.info("Data stored in vector database")
        
        return len(processed_chunks)
    
    def chat_loop(self):
        """Interactive chat loop"""
        print("Web ChatBot is ready! Type 'quit' to exit.")
        print("You can ask questions about the crawled web content.")
        
        while True:
            try:
                query = input("\nYou: ").strip()
                
                if query.lower() in ['quit', 'exit', 'bye']:
                    print("Goodbye!")
                    break
                
                if not query:
                    continue
                
                # Get response
                response = self.chatbot.chat(query)
                print(f"\nBot: {response}")
                
            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            except Exception as e:
                logger.error(f"Error in chat: {e}")
                print("Sorry, I encountered an error. Please try again.")

async def main():
    chatbot = WebChatBot()
    
    # Example: Crawl a website
    start_url = "https://example.com"  # Replace with your target website
    
    print("Web ChatBot - Knowledge Base Builder")
    print("1. Crawl website and build knowledge base")
    print("2. Start chat with existing knowledge base")
    
    choice = input("Choose option (1 or 2): ").strip()
    
    if choice == "1":
        success = await chatbot.crawl_and_process(start_url)
        if success > 0:
            print(f"Knowledge base built successfully with {success} chunks!")
        else:
            print("Crawl failed or no content found.")
    
    # Start chat interface
    chatbot.chat_loop()

if __name__ == "__main__":
    asyncio.run(main())
