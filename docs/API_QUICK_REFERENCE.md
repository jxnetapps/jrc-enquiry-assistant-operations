# 🚀 API Quick Reference Guide

## Overview

This guide provides quick access to the unified Chat Inquiry API with all endpoints, authentication requirements, and use cases.

## 📋 Unified API Summary

| API | Route Prefix | Auth | Database | Description |
|-----|-------------|------|----------|-------------|
| **Unified** | `/api/chat-inquiry` | Mixed | PostgreSQL + SQLite | Complete solution with public and admin endpoints |

---

## 🎯 Unified Chat Inquiry API (`unified_chat_inquiry_api.py`)

**Authentication:** Mixed (Public endpoints + JWT for admin operations)

### Public Endpoints (No Authentication Required)
```http
POST   /api/chat-inquiry/public                    # Create inquiry (public)
GET    /api/chat-inquiry/public/{id}               # Get by ID (public)
GET    /api/chat-inquiry/public                    # List inquiries (public)
```

### Admin Endpoints (JWT Authentication Required)
```http
POST   /api/chat-inquiry                          # Create inquiry (admin)
GET    /api/chat-inquiry/{id}                     # Get by ID (admin)
PUT    /api/chat-inquiry/{id}                     # Update by ID (admin)
DELETE /api/chat-inquiry/{id}                     # Delete by ID (admin)
GET    /api/chat-inquiry                          # List inquiries (admin)
GET    /api/chat-inquiry/stats                    # Get statistics (admin)
GET    /api/chat-inquiry/by-email/{email}         # Get by email (admin)
GET    /api/chat-inquiry/by-mobile/{mobile}       # Get by mobile (admin)
GET    /api/chat-inquiry/by-parent-type/{type}    # Get by parent type (admin)
GET    /api/chat-inquiry/by-school-type/{type}    # Get by school type (admin)
GET    /api/chat-inquiry/user/{user_id}           # Get by user ID (admin)
```

### Database Management Endpoints
```http
GET    /api/chat-inquiry/database/status          # Database status
POST   /api/chat-inquiry/database/test-postgres   # Test PostgreSQL connection
POST   /api/chat-inquiry/database/export-sqlite   # Export SQLite to PostgreSQL
GET    /api/chat-inquiry/database/export-status   # Export status
```

### Request/Response Models

#### Create Inquiry Request
```json
{
  "user_id": "optional-uuid",
  "parentType": "New Parent",
  "schoolType": "Day School",
  "firstName": "John",
  "mobile": "9876543210",
  "email": "john@example.com",
  "city": "Mumbai",
  "childName": "Jane",
  "grade": "5th",
  "academicYear": "2024-25",
  "dateOfBirth": "2015-06-15",
  "schoolName": "ABC School"
}
```

#### Response Format
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "user_id": "uuid",
    "parentType": "New Parent",
    "schoolType": "Day School",
    "firstName": "John",
    "mobile": "9876543210",
    "email": "john@example.com",
    "city": "Mumbai",
    "childName": "Jane",
    "grade": "5th",
    "academicYear": "2024-25",
    "dateOfBirth": "2015-06-15",
    "schoolName": "ABC School",
    "status": "active",
    "source": "api",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  },
  "message": "Inquiry created successfully"
}
```

### Query Parameters

#### List Inquiries
- `page` (int): Page number (default: 1)
- `page_size` (int): Items per page (default: 10, max: 100)
- `parent_type` (str): Filter by parent type
- `school_type` (str): Filter by school type
- `status` (str): Filter by status
- `search` (str): Search in name, child name, school name
- `sort_by` (str): Sort field (default: created_at)
- `sort_order` (str): Sort order (asc/desc, default: desc)

### Status Values
- `new` - New inquiry
- `active` - Active inquiry (default)
- `contacted` - Contacted
- `follow_up` - Follow up required
- `converted` - Converted
- `rejected` - Rejected

### Parent Types
- `New Parent`
- `Existing Parent`
- `Prospective Parent`

### School Types
- `Day School`
- `Boarding School`
- `International School`
- `Montessori School`

## 🔧 Database Configuration

### PostgreSQL (Primary)
- **Connection**: `postgresql://postgres:Wildcat%40007@localhost:5432/jrc_chatbot_assistant`
- **Table**: `chat_inquiry_information`
- **Features**: Full ACID compliance, advanced queries, concurrent access

### SQLite (Fallback)
- **File**: `chat_inquiries.db`
- **Table**: `chat_inquiry_information`
- **Features**: Local storage, zero configuration, backup solution

## 🚀 Quick Start

### 1. Start the Application
```bash
python web_app.py
```

### 2. Test Database Connection
```bash
curl http://localhost:8000/api/chat-inquiry/database/status
```

### 3. Create a Public Inquiry
```bash
curl -X POST http://localhost:8000/api/chat-inquiry/public \
  -H "Content-Type: application/json" \
  -d '{
    "parentType": "New Parent",
    "schoolType": "Day School",
    "firstName": "John",
    "mobile": "9876543210",
    "email": "john@example.com",
    "city": "Mumbai",
    "childName": "Jane",
    "grade": "5th",
    "academicYear": "2024-25",
    "dateOfBirth": "2015-06-15",
    "schoolName": "ABC School"
  }'
```

### 4. List Inquiries
```bash
curl "http://localhost:8000/api/chat-inquiry/public?page=1&page_size=10"
```

## 🔒 Authentication

### JWT Token (for admin endpoints)
```bash
# Get token from auth API
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "password"}'

# Use token in admin requests
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  http://localhost:8000/api/chat-inquiry/stats
```

## 📊 Error Handling

All endpoints return standardized error responses:

```json
{
  "success": false,
  "error": "Error message",
  "details": {
    "field": "Specific field error"
  }
}
```

## 🔄 Migration

### Export SQLite to PostgreSQL
```bash
curl -X POST http://localhost:8000/api/chat-inquiry/database/export-sqlite
```

### Check Export Status
```bash
curl http://localhost:8000/api/chat-inquiry/database/export-status
```

## 📈 Monitoring

### Database Status
```bash
curl http://localhost:8000/api/chat-inquiry/database/status
```

### Statistics
```bash
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  http://localhost:8000/api/chat-inquiry/stats
```

---

## 🎯 Use Cases

### Public Website Integration
- Use `/api/chat-inquiry/public` endpoints
- No authentication required
- Perfect for contact forms

### Admin Dashboard
- Use admin endpoints with JWT authentication
- Full CRUD operations
- Advanced filtering and statistics

### Data Migration
- Export SQLite data to PostgreSQL
- Monitor export progress
- Maintain data integrity

### Monitoring & Analytics
- Database health checks
- Inquiry statistics
- Performance metrics