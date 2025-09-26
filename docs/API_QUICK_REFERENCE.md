# 🚀 API Quick Reference Guide

## Overview

This guide provides quick access to all available Chat Inquiry APIs with their endpoints, authentication requirements, and use cases.

## 📋 API Summary Table

| API | Route Prefix | Auth | Database | Best For |
|-----|-------------|------|----------|----------|
| **Original** | `/api/chat-inquiry` | 🔒 JWT | MongoDB | Admin/Internal |
| **Enhanced** | `/api/v1/chat-inquiry` | 🔓 None | MongoDB + SQLite | Public/Advanced |
| **Simple** | `/api/simple/chat-inquiry` | 🔓 None | MongoDB + SQLite | Basic/Public |

---

## 🔧 Original API (`chat_inquiry_api.py`)

**Authentication Required:** ✅ JWT Token

### Endpoints
```http
POST   /api/chat-inquiry                    # Create inquiry
GET    /api/chat-inquiry/{id}               # Get by ID
PUT    /api/chat-inquiry/{id}               # Update by ID
DELETE /api/chat-inquiry/{id}               # Delete by ID
GET    /api/chat-inquiry/stats              # Get statistics
GET    /api/chat-inquiry/by-email/{email}   # Get by email
GET    /api/chat-inquiry/by-mobile/{mobile} # Get by mobile
GET    /api/chat-inquiry/by-parent-type/{type} # Get by parent type
GET    /api/chat-inquiry/by-school-type/{type} # Get by school type
GET    /api/chat-inquiry/by-grade/{grade}   # Get by grade
GET    /api/chat-inquiry/by-city/{city}     # Get by city
GET    /api/chat-inquiry/by-status/{status} # Get by status
```

### Example Usage
```bash
# Create inquiry (with auth)
curl -X POST "http://localhost:8000/api/chat-inquiry" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{"parentType": "New Parent", "schoolType": "Day School", ...}'

# Get by email (with auth)
curl -X GET "http://localhost:8000/api/chat-inquiry/by-email/test@example.com" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

---

## 🚀 Enhanced API (`enhanced_chat_inquiry_api.py`)

**Authentication Required:** ❌ None

### Endpoints
```http
POST   /api/v1/chat-inquiry/                # Create single inquiry
POST   /api/v1/chat-inquiry/bulk            # Create multiple inquiries
GET    /api/v1/chat-inquiry/                # Get all with pagination/filtering
GET    /api/v1/chat-inquiry/user/{user_id}  # Get by user_id with pagination
GET    /api/v1/chat-inquiry/stats           # Get statistics
GET    /api/v1/chat-inquiry/export          # Export data (JSON/CSV)
GET    /api/v1/chat-inquiry/health          # Health check
```

### Query Parameters (GET /api/v1/chat-inquiry/)
- `page`: Page number (default: 1)
- `page_size`: Records per page (default: 10, max: 100)
- `search`: General search term
- `parent_type`: Filter by parent type
- `school_type`: Filter by school type
- `status`: Filter by status
- `sort_by`: Sort field (default: created_at)
- `sort_order`: Sort direction (asc/desc, default: desc)

### Example Usage
```bash
# Create inquiry (no auth)
curl -X POST "http://localhost:8000/api/v1/chat-inquiry/" \
  -H "Content-Type: application/json" \
  -d '{"parentType": "New Parent", "schoolType": "Day School", ...}'

# Get all with pagination and filtering
curl -X GET "http://localhost:8000/api/v1/chat-inquiry/?page=1&page_size=10&search=John&parent_type=New%20Parent"

# Export data as CSV
curl -X GET "http://localhost:8000/api/v1/chat-inquiry/export?format=csv&limit=1000"

# Get by user_id with pagination
curl -X GET "http://localhost:8000/api/v1/chat-inquiry/user/user123?page=1&page_size=10"

# Health check
curl -X GET "http://localhost:8000/api/v1/chat-inquiry/health"
```

---

## 🎯 Simple API (`simple_chat_inquiry_api.py`)

**Authentication Required:** ❌ None

### Endpoints
```http
POST   /api/simple/chat-inquiry/            # Create inquiry
GET    /api/simple/chat-inquiry/            # Get all inquiries
GET    /api/simple/chat-inquiry/{id}        # Get by ID
DELETE /api/simple/chat-inquiry/{id}        # Delete by ID
GET    /api/simple/chat-inquiry/user/{user_id} # Get by user_id
GET    /api/simple/chat-inquiry/stats       # Get statistics
```

### Example Usage
```bash
# Create inquiry (no auth)
curl -X POST "http://localhost:8000/api/simple/chat-inquiry/" \
  -H "Content-Type: application/json" \
  -d '{"parentType": "New Parent", "schoolType": "Day School", ...}'

# Get all inquiries
curl -X GET "http://localhost:8000/api/simple/chat-inquiry/"

# Get by ID
curl -X GET "http://localhost:8000/api/simple/chat-inquiry/123"

# Delete by ID
curl -X DELETE "http://localhost:8000/api/simple/chat-inquiry/123"

# Get by user_id
curl -X GET "http://localhost:8000/api/simple/chat-inquiry/user/user123"

# Get statistics
curl -X GET "http://localhost:8000/api/simple/chat-inquiry/stats"
```

---

## 📊 Sample Request/Response

### Create Inquiry Request
```json
{
  "user_id": "user123",
  "parentType": "New Parent",
  "schoolType": "Day School",
  "firstName": "John Doe",
  "mobile": "9876543210",
  "email": "john@example.com",
  "city": "Mumbai",
  "childName": "Jane Doe",
  "grade": "Grade 1",
  "academicYear": "2024-2025",
  "dateOfBirth": "2020-01-01",
  "schoolName": "ABC School"
}
```

### Success Response
```json
{
  "success": true,
  "message": "Chat inquiry created successfully",
  "data": {
    "inquiry_id": "123"
  }
}
```

### Error Response
```json
{
  "success": false,
  "message": "Validation error",
  "error": "Missing required field: firstName"
}
```

---

## 🔍 Testing Scripts

### Quick Test Commands
```bash
# Test Simple API
python test_simple_api.py

# Test Enhanced API
python test_enhanced_api.py

# Test Delete Functionality
python test_delete_api.py

# Test Original API (requires auth)
python test_web_app.py
```

### Debug Commands
```bash
# Debug API endpoints
python debug_api.py

# View SQLite data
python simple_sqlite_viewer.py
```

---

## 🎯 Choosing the Right API

### Use **Original API** when:
- 🔒 You need **secure access** with authentication
- 🎯 You want **field-specific searches**
- 🏢 You're building **admin/internal** systems

### Use **Enhanced API** when:
- 🌐 You want **public access** without authentication
- 📈 You need **advanced features** (pagination, filtering, export)
- 🚀 You're building **public-facing** applications

### Use **Simple API** when:
- 🎯 You need **basic CRUD** operations
- 🚀 You want **quick implementation**
- 📱 You're building **mobile apps** or simple integrations

---

## 📚 Additional Resources

- **Detailed Comparison**: [Chat Inquiry API Comparison](CHAT_INQUIRY_API_COMPARISON.md)
- **API Documentation**: Available at `/docs` when server is running
- **Test Scripts**: Located in the `tests/` directory
- **Database Viewer**: Use `simple_sqlite_viewer.py` to view data

---

*Last updated: December 2024*
