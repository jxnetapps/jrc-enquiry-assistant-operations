# API Documentation

## Overview

This document provides comprehensive API documentation for the Web ChatBot application, including all endpoints, request/response formats, and usage examples.

## Base URL

- **Local Development**: `http://localhost:8000`
- **Production**: `https://your-app.azurewebsites.net`

## Authentication

### JWT Token Authentication

Most endpoints require JWT token authentication. Include the token in the Authorization header:

```bash
Authorization: Bearer <your-jwt-token>
```

### Getting Authentication Token

```bash
# Login to get token
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "your_password"}'
```

## API Endpoints

### Health Check Endpoints

#### 1. General Health Check
```http
GET /api/chat-inquiry/health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00Z",
  "version": "1.0.0",
  "database_status": "connected",
  "postgresql_using_supabase": true,
  "postgresql_connection_type": "supabase"
}
```

#### 2. Database Status
```http
GET /api/chat-inquiry/database/status
```

**Response:**
```json
{
  "status": "healthy",
  "postgresql_connected": true,
  "postgresql_using_supabase": true,
  "postgresql_connection_type": "supabase",
  "postgresql_host": "db.umwxkbcvqvqqybjwcash.supabase.co",
  "postgresql_database": "postgres",
  "vector_database_connected": true,
  "vector_database_type": "cloud"
}
```

#### 3. PostgreSQL Health Check
```http
GET /api/chat-inquiry/database/postgres-health
```

**Response:**
```json
{
  "status": "healthy",
  "connection_type": "supabase",
  "using_supabase": true,
  "host": "db.umwxkbcvqvqqybjwcash.supabase.co",
  "database": "postgres",
  "response_time_ms": 45,
  "postgresql_version": "15.4",
  "current_database": "postgres",
  "current_user": "postgres"
}
```

### Chat Inquiry Endpoints

#### 1. Create Chat Inquiry
```http
POST /api/chat-inquiry/
```

**Request Body:**
```json
{
  "user_id": "user123",
  "question": "What are the admission requirements?",
  "context": "I'm a new parent looking for information about school admission"
}
```

**Response:**
```json
{
  "id": "inquiry_123",
  "user_id": "user123",
  "question": "What are the admission requirements?",
  "answer": "The admission requirements include...",
  "created_at": "2024-01-01T12:00:00Z",
  "status": "completed"
}
```

#### 2. Get Chat Inquiry by ID
```http
GET /api/chat-inquiry/{inquiry_id}
```

**Response:**
```json
{
  "id": "inquiry_123",
  "user_id": "user123",
  "question": "What are the admission requirements?",
  "answer": "The admission requirements include...",
  "created_at": "2024-01-01T12:00:00Z",
  "updated_at": "2024-01-01T12:05:00Z",
  "status": "completed"
}
```

#### 3. Get User's Chat Inquiries
```http
GET /api/chat-inquiry/user/{user_id}
```

**Query Parameters:**
- `limit` (optional): Number of results to return (default: 10)
- `offset` (optional): Number of results to skip (default: 0)

**Response:**
```json
{
  "inquiries": [
    {
      "id": "inquiry_123",
      "user_id": "user123",
      "question": "What are the admission requirements?",
      "answer": "The admission requirements include...",
      "created_at": "2024-01-01T12:00:00Z",
      "status": "completed"
    }
  ],
  "total": 1,
  "limit": 10,
  "offset": 0
}
```

#### 4. Update Chat Inquiry
```http
PUT /api/chat-inquiry/{inquiry_id}
```

**Request Body:**
```json
{
  "answer": "Updated answer with more details...",
  "status": "completed"
}
```

**Response:**
```json
{
  "id": "inquiry_123",
  "user_id": "user123",
  "question": "What are the admission requirements?",
  "answer": "Updated answer with more details...",
  "created_at": "2024-01-01T12:00:00Z",
  "updated_at": "2024-01-01T12:10:00Z",
  "status": "completed"
}
```

#### 5. Delete Chat Inquiry
```http
DELETE /api/chat-inquiry/{inquiry_id}
```

**Response:**
```json
{
  "message": "Chat inquiry deleted successfully",
  "inquiry_id": "inquiry_123"
}
```

### Database Management Endpoints

#### 1. Test PostgreSQL Connection
```http
POST /api/chat-inquiry/database/test-postgres
```

**Response:**
```json
{
  "status": "success",
  "message": "PostgreSQL connection successful",
  "connection_type": "supabase",
  "using_supabase": true,
  "host": "db.umwxkbcvqvqqybjwcash.supabase.co",
  "database": "postgres",
  "response_time_ms": 45
}
```

#### 2. Get Database Statistics
```http
GET /api/chat-inquiry/database/stats
```

**Response:**
```json
{
  "total_inquiries": 150,
  "completed_inquiries": 145,
  "pending_inquiries": 5,
  "database_size_mb": 25.5,
  "last_updated": "2024-01-01T12:00:00Z"
}
```

### User Management Endpoints

#### 1. Create User
```http
POST /api/users/
```

**Request Body:**
```json
{
  "username": "newuser",
  "email": "user@example.com",
  "status": "active"
}
```

**Response:**
```json
{
  "id": "user_456",
  "username": "newuser",
  "email": "user@example.com",
  "status": "active",
  "created_at": "2024-01-01T12:00:00Z"
}
```

#### 2. Get User by ID
```http
GET /api/users/{user_id}
```

**Response:**
```json
{
  "id": "user_456",
  "username": "newuser",
  "email": "user@example.com",
  "status": "active",
  "created_at": "2024-01-01T12:00:00Z",
  "last_login": "2024-01-01T12:00:00Z"
}
```

#### 3. Update User
```http
PUT /api/users/{user_id}
```

**Request Body:**
```json
{
  "email": "updated@example.com",
  "status": "inactive"
}
```

**Response:**
```json
{
  "id": "user_456",
  "username": "newuser",
  "email": "updated@example.com",
  "status": "inactive",
  "created_at": "2024-01-01T12:00:00Z",
  "updated_at": "2024-01-01T12:10:00Z"
}
```

### Authentication Endpoints

#### 1. Login
```http
POST /api/auth/login
```

**Request Body:**
```json
{
  "username": "admin",
  "password": "your_password"
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 28800,
  "user": {
    "id": "admin",
    "username": "admin",
    "status": "active"
  }
}
```

#### 2. Logout
```http
POST /api/auth/logout
```

**Headers:**
```
Authorization: Bearer <your-jwt-token>
```

**Response:**
```json
{
  "message": "Successfully logged out"
}
```

#### 3. Refresh Token
```http
POST /api/auth/refresh
```

**Headers:**
```
Authorization: Bearer <your-jwt-token>
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 28800
}
```

## Error Handling

### Error Response Format

```json
{
  "error": "Error type",
  "message": "Detailed error message",
  "details": {
    "field": "Additional error details"
  },
  "timestamp": "2024-01-01T12:00:00Z"
}
```

### Common Error Codes

| Status Code | Error Type | Description |
|-------------|------------|-------------|
| 400 | Bad Request | Invalid request data |
| 401 | Unauthorized | Authentication required |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource not found |
| 422 | Validation Error | Invalid input data |
| 500 | Internal Server Error | Server error |

### Example Error Responses

#### Authentication Error
```json
{
  "error": "AuthenticationError",
  "message": "Invalid credentials",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

#### Validation Error
```json
{
  "error": "ValidationError",
  "message": "Invalid input data",
  "details": {
    "question": "Question is required",
    "user_id": "User ID must be a valid UUID"
  },
  "timestamp": "2024-01-01T12:00:00Z"
}
```

## Rate Limiting

### Rate Limit Headers

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640995200
```

### Rate Limit Exceeded Response

```json
{
  "error": "RateLimitExceeded",
  "message": "Rate limit exceeded. Try again later.",
  "retry_after": 3600,
  "timestamp": "2024-01-01T12:00:00Z"
}
```

## Testing

### Test Endpoints

#### 1. Test All Endpoints
```bash
python tests/test_unified_api.py
```

#### 2. Test Specific Functionality
```bash
python tests/test_chat_inquiry_api.py
python tests/test_postgres_health.py
```

#### 3. Debug API
```bash
python tests/debug_api.py
```

### Example Test Script

```python
import requests

# Test health endpoint
response = requests.get("http://localhost:8000/api/chat-inquiry/health")
print(f"Health Status: {response.json()}")

# Test database status
response = requests.get("http://localhost:8000/api/chat-inquiry/database/status")
print(f"Database Status: {response.json()}")
```

## Swagger Documentation

Interactive API documentation is available at:
- **Local**: `http://localhost:8000/docs`
- **Production**: `https://your-app.azurewebsites.net/docs`

## Quick Reference

### Essential Endpoints
- `GET /api/chat-inquiry/health` - Health check
- `POST /api/chat-inquiry/` - Create inquiry
- `GET /api/chat-inquiry/{id}` - Get inquiry
- `POST /api/auth/login` - Login
- `GET /api/chat-inquiry/database/status` - Database status

### Common Headers
```
Content-Type: application/json
Authorization: Bearer <token>
```

### Response Codes
- `200` - Success
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `404` - Not Found
- `500` - Internal Server Error
