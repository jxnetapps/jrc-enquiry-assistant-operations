# Chat Inquiry Information API

This document describes the Chat Inquiry Information API endpoints that allow you to manage chat inquiry data in PostgreSQL with SQLite fallback.

## Overview

The API provides CRUD operations for chat inquiry information with the following features:
- Create new chat inquiries
- Retrieve inquiries by ID, email, or mobile
- Update inquiry information
- Delete inquiries
- Search inquiries with filters
- Get statistics about inquiries

## Base URL

```
http://localhost:8000/api/chat-inquiry
```

## Authentication

Most endpoints require JWT authentication. Include the token in the Authorization header:
```
Authorization: Bearer <your_jwt_token>
```

## Data Model

### Chat Inquiry Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| parentType | string | Yes | Type of parent (New Parent, Existing Parent, Prospective Parent) |
| schoolType | string | Yes | Type of school (Day School, Boarding School, International School, Montessori School) |
| firstName | string | Yes | Parent's first name (1-100 characters) |
| mobile | string | Yes | Mobile number (10 digits) |
| email | string | Yes | Email address |
| city | string | Yes | City (1-100 characters) |
| childName | string | Yes | Child's name (1-100 characters) |
| grade | string | Yes | Grade/Class (1-50 characters) |
| academicYear | string | Yes | Academic year (YYYY-YYYY or YYYY-YY format) |
| dateOfBirth | string | Yes | Date of birth (YYYY-MM-DD format) |
| schoolName | string | Yes | School name (1-200 characters) |

## API Endpoints

### 1. Create Chat Inquiry

**POST** `/api/chat-inquiry`

Creates a new chat inquiry record.

**Request Body:**
```json
{
  "parentType": "New Parent",
  "schoolType": "Day School",
  "firstName": "Agarwal",
  "mobile": "9885659894",
  "email": "sai@g.in",
  "city": "6987",
  "childName": "Janith",
  "grade": "MYP 4",
  "academicYear": "2026-2027",
  "dateOfBirth": "2025-09-01",
  "schoolName": "Edify"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Chat inquiry created successfully",
  "data": {
    "inquiry_id": "64f8a1b2c3d4e5f6a7b8c9d0"
  }
}
```

### 2. Get Chat Inquiry by ID

**GET** `/api/chat-inquiry/{inquiry_id}`

Retrieves a specific chat inquiry by its ID.

**Response:**
```json
{
  "success": true,
  "message": "Inquiry retrieved successfully",
  "data": {
    "id": "64f8a1b2c3d4e5f6a7b8c9d0",
    "parentType": "New Parent",
    "schoolType": "Day School",
    "firstName": "Agarwal",
    "mobile": "9885659894",
    "email": "sai@g.in",
    "city": "6987",
    "childName": "Janith",
    "grade": "MYP 4",
    "academicYear": "2026-2027",
    "dateOfBirth": "2025-09-01",
    "schoolName": "Edify",
    "status": "new",
    "source": "api",
    "created_at": "2023-09-05T10:30:00Z",
    "updated_at": "2023-09-05T10:30:00Z"
  }
}
```

### 3. Update Chat Inquiry

**PUT** `/api/chat-inquiry/{inquiry_id}`

Updates an existing chat inquiry. Only provided fields will be updated.

**Request Body:**
```json
{
  "firstName": "Agarwal Updated",
  "status": "contacted"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Inquiry updated successfully"
}
```

### 4. Delete Chat Inquiry

**DELETE** `/api/chat-inquiry/{inquiry_id}`

Deletes a chat inquiry.

**Response:**
```json
{
  "success": true,
  "message": "Inquiry deleted successfully"
}
```

### 5. Search Chat Inquiries

**POST** `/api/chat-inquiry/search`

Searches for inquiries with optional filters.

**Request Body:**
```json
{
  "parentType": "New Parent",
  "schoolType": "Day School",
  "grade": "MYP 4",
  "city": "6987",
  "status": "new",
  "search_text": "Agarwal",
  "skip": 0,
  "limit": 100
}
```

**Response:**
```json
{
  "success": true,
  "message": "Search completed successfully",
  "data": {
    "inquiries": [...],
    "count": 5,
    "skip": 0,
    "limit": 100
  }
}
```

### 6. Get Inquiry Statistics

**GET** `/api/chat-inquiry/stats`

Retrieves statistics about all inquiries.

**Response:**
```json
{
  "success": true,
  "message": "Statistics retrieved successfully",
  "data": {
    "total_inquiries": 150,
    "parent_type_distribution": {
      "New Parent": 100,
      "Existing Parent": 30,
      "Prospective Parent": 20
    },
    "school_type_distribution": {
      "Day School": 80,
      "Boarding School": 40,
      "International School": 30
    },
    "status_distribution": {
      "new": 120,
      "contacted": 20,
      "follow_up": 10
    }
  }
}
```

### 7. Get Inquiry by Email

**GET** `/api/chat-inquiry/by-email/{email}`

Retrieves an inquiry by email address.

### 8. Get Inquiry by Mobile

**GET** `/api/chat-inquiry/by-mobile/{mobile}`

Retrieves an inquiry by mobile number.

## Error Responses

All endpoints return consistent error responses:

```json
{
  "success": false,
  "message": "Error description",
  "error": "Detailed error message"
}
```

Common HTTP status codes:
- `200` - Success
- `400` - Bad Request (validation errors)
- `401` - Unauthorized (authentication required)
- `404` - Not Found
- `422` - Validation Error
- `500` - Internal Server Error

## Testing

### Using the Test Script

Run the simple test script to verify the API:

```bash
python test_inquiry_simple.py
```

### Using curl

```bash
# Create an inquiry
curl -X POST "http://localhost:8000/api/chat-inquiry" \
  -H "Content-Type: application/json" \
  -d '{
    "parentType": "New Parent",
    "schoolType": "Day School",
    "firstName": "Agarwal",
    "mobile": "9885659894",
    "email": "sai@g.in",
    "city": "6987",
    "childName": "Janith",
    "grade": "MYP 4",
    "academicYear": "2026-2027",
    "dateOfBirth": "2025-09-01",
    "schoolName": "Edify"
  }'
```

## PostgreSQL Configuration

The API uses PostgreSQL with SQLite fallback with the following configuration:
- **Connection URI**: `postgresql://postgres:Wildcat@007@localhost:5432/jrc_chatbot_assistant`
- **Database**: `jrc_chatbot_assistant`
- **Table**: `chat_inquiry_information`

## Repository Pattern

The API implements a repository pattern with PostgreSQL and SQLite support:

- `PostgreSQLInquiryRepository` - PostgreSQL operations for chat inquiries
- `SQLiteInquiryRepository` - SQLite fallback operations
- `PostgreSQLConnection` - PostgreSQL connection management
- `ChatInquiryRepository` - Main repository with fallback logic

This pattern allows easy addition of new tables and operations with automatic fallback to SQLite.
