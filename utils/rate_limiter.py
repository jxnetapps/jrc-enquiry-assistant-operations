import asyncio
import time
from typing import Optional

class RateLimiter:
    def __init__(self, delay: float = 1.0):
        self.delay = delay
        self.last_request: Optional[float] = None
        
    async def wait(self):
        if self.last_request is not None:
            elapsed = time.time() - self.last_request
            if elapsed < self.delay:
                await asyncio.sleep(self.delay - elapsed)
                
        self.last_request = time.time()
