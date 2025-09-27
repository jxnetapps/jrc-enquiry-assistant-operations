"""
Test the unified router directly
"""

import asyncio
from fastapi import FastAPI
from api.unified_chat_inquiry_api import router

app = FastAPI()
app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    print("Starting test server on http://localhost:8001")
    uvicorn.run(app, host="0.0.0.0", port=8001)
