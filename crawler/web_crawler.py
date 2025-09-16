import aiohttp
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from typing import List, Set, Dict, Optional
import logging
import asyncio
import time
from datetime import datetime
from utils.rate_limiter import RateLimiter
from utils.content_filter import ContentFilter

logger = logging.getLogger(__name__)

class WebCrawler:
    def __init__(self, max_pages: int = 100, depth: int = 3, delay: float = 1.0, max_concurrent: int = 5):
        self.max_pages = max_pages
        self.max_depth = depth
        self.delay = delay
        self.max_concurrent = max_concurrent
        self.visited_urls: Set[str] = set()
        self.rate_limiter = RateLimiter(delay=delay)
        self.content_filter = ContentFilter()
        self.session: Optional[aiohttp.ClientSession] = None
        self.semaphore: Optional[asyncio.Semaphore] = None
        
    async def create_session(self):
        self.session = aiohttp.ClientSession(
            headers={'User-Agent': 'WebChatBot/2.0'},
            timeout=aiohttp.ClientTimeout(total=30)
        )
        self.semaphore = asyncio.Semaphore(self.max_concurrent)
        
    async def close_session(self):
        if self.session:
            await self.session.close()
            
    async def fetch_page(self, url: str) -> Optional[str]:
        async with self.semaphore:
            await self.rate_limiter.wait()
            
            try:
                async with self.session.get(url, allow_redirects=True, ssl=False) as response:
                    if response.status == 200:
                        content_type = response.headers.get('content-type', '')
                        if 'text/html' in content_type:
                            return await response.text()
                        else:
                            logger.warning(f"Skipping non-HTML content: {url}")
                    else:
                        logger.warning(f"Failed to fetch {url}: Status {response.status}")
            except Exception as e:
                logger.error(f"Error fetching {url}: {e}")
            return None
            
    def extract_links(self, html: str, base_url: str) -> List[str]:
        soup = BeautifulSoup(html, 'html.parser')
        links = []
        
        for link in soup.find_all('a', href=True):
            href = link['href']
            full_url = urljoin(base_url, href)
            
            # Normalize URL and filter
            parsed = urlparse(full_url)
            if parsed.scheme in ['http', 'https'] and not parsed.fragment:
                normalized_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
                if parsed.query:
                    normalized_url += f"?{parsed.query}"
                links.append(normalized_url)
                
        return list(set(links))  # Remove duplicates
    
    def extract_content(self, html: str, url: str) -> Optional[Dict[str, str]]:
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Remove unwanted elements
            for element in soup(['script', 'style', 'nav', 'footer', 'header', 'aside']):
                element.decompose()
                
            # Extract title
            title = soup.find('title')
            title_text = title.get_text().strip() if title else urlparse(url).netloc
            
            # Extract main content (try to find article/main content)
            main_content = soup.find('article') or soup.find('main') or soup.find('div', class_='content')
            if main_content:
                text = main_content.get_text()
            else:
                text = soup.get_text()
                
            # Clean and filter content
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            content = ' '.join(chunk for chunk in chunks if chunk)
            
            # Apply content filtering
            if not self.content_filter.is_quality_content(content, title_text):
                return None
                
            return {
                'url': url,
                'title': title_text,
                'content': content[:15000],  # Reasonable limit
                'crawled_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error extracting content from {url}: {e}")
            return None
    
    async def crawl(self, start_url: str) -> List[Dict[str, str]]:
        await self.create_session()
        
        try:
            pages_to_crawl = [(start_url, 0)]
            crawled_pages = []
            crawl_start = time.time()
            
            while pages_to_crawl and len(crawled_pages) < self.max_pages:
                if time.time() - crawl_start > 300:  # 5 minute timeout
                    logger.warning("Crawl timeout reached")
                    break
                    
                url, depth = pages_to_crawl.pop(0)
                
                if (url in self.visited_urls or depth > self.max_depth or 
                    not self.content_filter.is_allowed_url(url)):
                    continue
                    
                self.visited_urls.add(url)
                logger.info(f"Crawling: {url} (depth: {depth}, visited: {len(self.visited_urls)})")
                
                html = await self.fetch_page(url)
                if not html:
                    continue
                    
                # Extract content
                page_content = self.extract_content(html, url)
                if page_content:
                    crawled_pages.append(page_content)
                    
                    # Extract links for further crawling
                    if depth < self.max_depth and len(crawled_pages) < self.max_pages:
                        links = self.extract_links(html, url)
                        for link in links:
                            if (link not in self.visited_urls and 
                                len(pages_to_crawl) + len(self.visited_urls) < self.max_pages * 2):
                                pages_to_crawl.append((link, depth + 1))
                            
            logger.info(f"Crawl completed. Found {len(crawled_pages)} quality pages.")
            return crawled_pages
            
        finally:
            await self.close_session()
