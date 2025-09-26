#!/usr/bin/env python3
"""
Debug script to test find_by_id functionality
"""

import asyncio
from database.chat_inquiry_repository import ChatInquiryRepository

async def test_find_by_id():
    """Test the find_by_id method"""
    print("🔍 Testing find_by_id method...")
    
    repository = ChatInquiryRepository()
    
    # Test with ID 6
    print("\nTesting with ID 6:")
    result = await repository.find_by_id("6")
    print(f"Result: {result}")
    
    # Test with ID 7
    print("\nTesting with ID 7:")
    result = await repository.find_by_id("7")
    print(f"Result: {result}")
    
    # Test with non-existent ID
    print("\nTesting with non-existent ID 999:")
    result = await repository.find_by_id("999")
    print(f"Result: {result}")

if __name__ == "__main__":
    asyncio.run(test_find_by_id())
