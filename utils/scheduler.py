import schedule
import time
import asyncio
import logging
from typing import Callable, Optional
from crawler.web_crawler import WebCrawler
from crawler.content_processor import ContentProcessor
from embedding.embedding_generator import EmbeddingGenerator
from database.vector_db import VectorDB
from config import Config

logger = logging.getLogger(__name__)

class Scheduler:
    def __init__(self):
        self.scheduled_tasks = {}
        
    def schedule_crawl(self, start_url: str, cron_expression: str, callback: Optional[Callable] = None):
        """Schedule automatic crawling"""
        def crawl_job():
            asyncio.run(self._run_crawl(start_url, callback))
            
        schedule.every().day.at("02:00").do(crawl_job)
        logger.info(f"Scheduled crawl for {start_url} at 02:00 daily")
        
    async def _run_crawl(self, start_url: str, callback: Optional[Callable] = None):
        """Run the crawl process"""
        try:
            crawler = WebCrawler(
                max_pages=Config.MAX_PAGES_TO_CRAWL,
                depth=Config.CRAWL_DEPTH,
                delay=Config.CRAWL_DELAY
            )
            processor = ContentProcessor()
            embedding_generator = EmbeddingGenerator()
            vector_db = VectorDB()
            
            logger.info("Starting scheduled crawl...")
            pages = await crawler.crawl(start_url)
            processed_chunks = processor.process_pages(pages)
            
            if processed_chunks:
                texts = [chunk['content'] for chunk in processed_chunks]
                embeddings = embedding_generator.generate_embeddings(texts)
                vector_db.store_documents(processed_chunks, embeddings)
                logger.info(f"Scheduled crawl completed: {len(processed_chunks)} chunks processed")
                
                if callback:
                    callback(len(processed_chunks))
                    
        except Exception as e:
            logger.error(f"Scheduled crawl failed: {e}")
            
    def run_pending(self):
        """Run pending scheduled tasks"""
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
