#!/usr/bin/env python3
"""
Test script to verify user_id storage in SQLite
"""

import asyncio
from database.sqlite_inquiry_repository import SQLiteInquiryRepository

async def test_user_id_storage():
    """Test user_id storage directly in SQLite repository"""
    print("🧪 Testing user_id storage in SQLite repository")
    print("=" * 50)
    
    # Create repository instance
    repo = SQLiteInquiryRepository()
    
    # Test data with user_id
    test_data = {
        "user_id": "test_user_123",
        "parentType": "New Parent",
        "schoolType": "Day School",
        "firstName": "Test User",
        "mobile": "9876543210",
        "email": "test@example.com",
        "city": "Test City",
        "childName": "Test Child",
        "grade": "Grade 1",
        "academicYear": "2024-2025",
        "dateOfBirth": "2020-01-01",
        "schoolName": "Test School"
    }
    
    print(f"📝 Creating inquiry with user_id: {test_data['user_id']}")
    
    try:
        # Create inquiry
        inquiry_id = await repo.create_inquiry(test_data)
        print(f"✅ Created inquiry with ID: {inquiry_id}")
        
        # Find by user_id
        print(f"🔍 Searching for inquiries with user_id: {test_data['user_id']}")
        user_inquiries = await repo.find_by_user_id(test_data['user_id'])
        print(f"📊 Found {len(user_inquiries)} inquiries for user {test_data['user_id']}")
        
        if user_inquiries:
            print("📋 Inquiry details:")
            for inquiry in user_inquiries:
                print(f"  ID: {inquiry.get('id')}, user_id: {inquiry.get('user_id')}, firstName: {inquiry.get('firstName')}")
        
        # Find by ID to verify
        print(f"🔍 Finding inquiry by ID: {inquiry_id}")
        inquiry = await repo.find_by_id(inquiry_id)
        if inquiry:
            print(f"📋 Found inquiry: ID: {inquiry.get('id')}, user_id: {inquiry.get('user_id')}, firstName: {inquiry.get('firstName')}")
        else:
            print("❌ Inquiry not found by ID")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_user_id_storage())
