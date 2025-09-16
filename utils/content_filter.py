import re
from typing import List
import logging

logger = logging.getLogger(__name__)

class ContentFilter:
    def __init__(self):
        self.blacklisted_domains = {
            'facebook.com', 'twitter.com', 'instagram.com', 'linkedin.com',
            'youtube.com', 'tiktok.com', 'pinterest.com', 'reddit.com'
        }
        
        self.blacklisted_paths = {
            '/login', '/signup', '/register', '/logout', '/password',
            '/admin', '/dashboard', '/account', '/profile'
        }
        
        self.min_content_length = 200
        self.max_content_length = 20000
        
    def is_allowed_url(self, url: str) -> bool:
        """Check if URL is allowed to be crawled"""
        from urllib.parse import urlparse
        
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            
            # Check blacklisted domains
            if any(blacklisted in domain for blacklisted in self.blacklisted_domains):
                return False
                
            # Check blacklisted paths
            if any(parsed.path.startswith(path) for path in self.blacklisted_paths):
                return False
                
            # Check file extensions
            if any(parsed.path.endswith(ext) for ext in ['.pdf', '.doc', '.docx', '.zip', '.rar']):
                return False
                
            return True
            
        except Exception as e:
            logger.error(f"Error checking URL {url}: {e}")
            return False
            
    def is_quality_content(self, content: str, title: str) -> bool:
        """Check if content meets quality standards"""
        # Check length
        if len(content) < self.min_content_length or len(content) > self.max_content_length:
            return False
            
        # Check for meaningful content (avoid placeholder pages)
        if any(phrase in content.lower() for phrase in [
            'page not found', '404', 'under construction', 'coming soon',
            'login required', 'access denied'
        ]):
            return False
            
        # Check content density (avoid navigation-heavy pages)
        lines = content.split('\n')
        if len(lines) > 50 and len(content) / len(lines) < 20:  # Low content per line
            return False
            
        return True
