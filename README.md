# Web ChatBot 🤖

A sophisticated chatbot that crawls websites, processes content, and provides intelligent responses using vector embeddings and LLMs.

## Features

- 🌐 **Web Crawling**: Async crawler with depth control and polite delays
- 🧠 **AI-Powered**: Uses OpenAI GPT or local models for intelligent responses
- 🔍 **Vector Search**: Configurable vector database (Pinecone default, FAISS local, or Chroma Cloud)
- 🛡️ **Authentication**: JWT-based user authentication
- ⚡ **Rate Limiting**: Polite crawling with configurable delays
- 📊 **Content Filtering**: Quality-based content filtering
- 🕐 **Scheduling**: Automatic content updates
- 🌈 **API Documentation**: Interactive Swagger UI for easy testing
- 🎯 **Configurable Chat Behavior**: Switch between knowledge base and predefined question flows
- 🔄 **State Management**: State-driven conversations for structured interactions
- 📝 **Unified Chat Inquiry API**: Complete solution with public and admin endpoints (see [API Guide](docs/UNIFIED_API_GUIDE.md))

## Installation

1. **Create Virtual Environment (Recommended)**

   **Windows Users:**
   ```bash
   # Run the virtual environment setup script
   setup-venv.bat
   
   # If you get "Python is not installed" error but Python is installed:
   # Run the troubleshooter to find Python
   scripts\setup-venv-troubleshoot.bat
   ```
   
   **Linux/Mac Users:**
   ```bash
   # Make the script executable (first time only)
   chmod +x setup-venv.sh
   
   # Run the virtual environment setup script
   ./setup-venv.sh
   ```
   
   **Manual Setup:**
   ```bash
   # Create virtual environment
   python -m venv venv
   
   # Activate virtual environment
   # Windows:
   venv\Scripts\activate
   # Linux/Mac:
   source venv/bin/activate
   
   # Upgrade pip
   python -m pip install --upgrade pip
   
   # Install dependencies
   pip install -r requirements.txt
   ```

2. **Install dependencies (if not using setup script)**

   **Windows Users:**
   ```bash
   # Activate virtual environment first
   venv\Scripts\activate
   
   # Then run the automated installation script
   install-windows.bat
   ```
   
   **Other Platforms:**
   ```bash
   # Activate virtual environment first
   source venv/bin/activate
   
   # Install dependencies
   pip install -r requirements.txt
   ```

3. **Configure database**
   
   The application supports three database backends:
   
   **Pinecone Database (Default)**
   ```bash
   VECTOR_DATABASE_TYPE=pinecone
   PINECONE_API_KEY=your_pinecone_api_key
   PINECONE_INDEX_NAME=edify-edicenter
   PINECONE_NAMESPACE=optional_namespace  # Optional, can be overridden via API
   ```
   
   **Local Database (FAISS)**
   ```bash
   VECTOR_DATABASE_TYPE=local
   CHROMA_DB_PATH=./chroma_db
   COLLECTION_NAME=web_content
   ```
   
   **Chroma Cloud Database**
   ```bash
   VECTOR_DATABASE_TYPE=cloud
   CHROMA_CLOUD_API_KEY=your_api_key
   CHROMA_CLOUD_TENANT_ID=your_tenant_id
   CHROMA_CLOUD_DATABASE_ID=your_database_id
   CHROMA_CLOUD_COLLECTION_NAME=web_content
   ```
   
   **Note:** Namespace can be passed via API endpoints and takes precedence over config. If not provided, the default namespace is used.
   
   See [DATABASE_CONFIG.md](DATABASE_CONFIG.md) for detailed configuration instructions.

4. **Configure chat behavior**
   
   The application supports two chat modes:
   
   **Knowledge Base Mode (Default)**
   ```bash
   CHAT_BEHAVIOR=knowledge_base
   ```
   - Traditional Q&A based on crawled content
   - Uses vector search to find relevant information
   - Responds to any question about the knowledge base
   
   **Pre-trained Mode**
   ```bash
   CHAT_BEHAVIOR=pre_trained
   ```
   - Structured conversation flow
   - Collects user information through predefined questions
   - Can switch to knowledge base queries after data collection

5. **Set up environment variables**

   **Quick Setup:**
   ```bash
   # Run the setup script to create .env file
   python setup_env.py
   ```
   
   **Manual Setup:**
   Create a `.env` file with your configuration:
   ```bash
   # Database Configuration
   VECTOR_DATABASE_TYPE=pinecone  # 'pinecone' (default), 'local', or 'cloud'
   CHAT_BEHAVIOR=knowledge_base  # or 'pre_trained' for structured flow
   
   # OpenAI Configuration (optional)
   OPENAI_API_KEY=your_openai_api_key
   
   # Pinecone Configuration (default database)
   PINECONE_API_KEY=your_pinecone_api_key
   PINECONE_INDEX_NAME=web-content
   PINECONE_NAMESPACE=optional_namespace  # Optional
   
   # Chroma Cloud Configuration (if using cloud database)
   CHROMA_CLOUD_API_KEY=your_chroma_cloud_api_key
   CHROMA_CLOUD_TENANT_ID=your_tenant_id
   CHROMA_CLOUD_DATABASE_ID=your_database_id
   ```
   
   **Configuration Template:**
   - Use `config_template.env` as a reference
   - Copy it to `.env` and customize as needed

## Usage

1. **Start the application**

   **Windows:**
   ```bash
   # Simple start (recommended)
   start.bat
   
   # Or SQLite mode
   scripts\start-sqlite.bat
   
   # Or development mode
   scripts\start-dev.bat
   
   # Or production mode
   scripts\start-prod.bat
   ```
   
   **Linux/Mac:**
   ```bash
   # Simple start (recommended)
   ./start.sh
   
   # Or development mode
   ./scripts/start-dev.sh
   
   # Or production mode
   ./scripts/start-prod.sh
   ```
   
   **Note:** All start scripts automatically activate the virtual environment if it exists.
   If the virtual environment is not found, you'll be prompted to create it first.
   
   **Alternative (Manual):**
   ```bash
   # Activate virtual environment first
   # Windows:
   venv\Scripts\activate
   # Linux/Mac:
   source venv/bin/activate
   
   # Then start the application
   python web_app.py
   ```

2. **Access the API documentation**
   - Open your browser and go to `http://localhost:8000`
   - You'll be automatically redirected to the Swagger documentation at `/docs`
   - Use the interactive API documentation to test all endpoints

3. **Available API Endpoints**
   - **Authentication**: `/api/auth/*` - User login, registration, and management
   - **Vector Chat**: `/api/*` - AI-powered chat and web crawling
   - **Chat Inquiry**: `/api/chat-inquiry/*` - Inquiry management and statistics
   - **User Management**: `/api/users/*` - User administration (admin only)
   - **Database**: `/api/database/*` - Database status and health checks
   
   See [API Documentation](#api-documentation) section below for detailed request/response examples.

## Testing

### 1. Test Chat Modes

```
.\venv\Scripts\activate.ps1
OR
& C:/Dev/Trainings/python/web-scrapper/jrc-enquiry-assistant-operations/venv/Scripts/Activate.ps1
```

Run the comprehensive chat mode test:
```bash
python test_chat_modes.py
```

This will test:
- ✅ Knowledge base mode functionality
- ✅ Pre-trained mode with structured conversation flow
- ✅ Mode switching capabilities
- ✅ Session management

### 2. Test Web Application

Start the web application:
```bash
# Windows (automatically uses virtual environment)
start.bat

# Linux/Mac (automatically uses virtual environment)
./start.sh

# Or manually activate venv and run
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
python web_app.py
```

Then open your browser to `http://localhost:8000`

### 3. Test Knowledge Base Mode

1. **Set configuration:**
   ```bash
   # In .env file
   CHAT_BEHAVIOR=knowledge_base
   ```

2. **Crawl some content:**
   - Use the admin panel to crawl a website
   - Or upload documents (PDF, DOCX, TXT)

3. **Test chat:**
   - Ask questions about the crawled content
   - Verify responses are based on the knowledge base

### 4. Test Pre-trained Mode

1. **Set configuration:**
   ```bash
   # In .env file
   CHAT_BEHAVIOR=pre_trained
   ```

2. **Test the conversation flow:**
   - Start a chat session
   - Follow the predefined questions:
     - "Are you a new or existing parent?" → Choose "New Parent" or "Existing Parent"
     - "What type of school are you looking for?" → Choose "Day" or "Boarding"
     - Provide your name
     - Provide your mobile number
     - "Do you want to know more about the school?" → Choose "Yes" or "No"
     - If "Yes", ask knowledge-based questions

3. **Verify data collection:**
   - Check that user data is collected correctly
   - Verify conversation summary is displayed
   - Test reset functionality

### 5. Test API Endpoints

Test the chat API directly:
```bash
# Test knowledge base mode
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"message": "What is this website about?", "user_id": "test_user"}'

# Test pre-trained mode
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"message": "Hello", "user_id": "test_user"}'

# Reset chat session
curl -X POST "http://localhost:8000/api/chat/reset?user_id=test_user" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Get session data
curl -X GET "http://localhost:8000/api/chat/session/test_user" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 6. Test Database Configurations

Test both local and cloud database modes:

**Local Database:**
```bash
# Set in .env
VECTOR_DATABASE_TYPE=local
python test_database_config.py
```

**Pinecone:**
```bash
# Set in .env
VECTOR_DATABASE_TYPE=pinecone
PINECONE_API_KEY=your_api_key
PINECONE_INDEX_NAME=edify-edicenter
python test_database_config.py
```

**Chroma Cloud:**
```bash
# Set in .env
VECTOR_DATABASE_TYPE=cloud
python test_cloud_config.py
```

### 7. Test Chat Inquiry APIs

The system provides three different Chat Inquiry APIs for different use cases:

**Simple API (No Authentication):**
```bash
# Test basic CRUD operations
python test_simple_api.py

# Test delete functionality
python test_delete_api.py
```

**Enhanced API (Advanced Features):**
```bash
# Test advanced features with pagination, filtering, export
python test_enhanced_api.py
```

**Original API (With Authentication):**
```bash
# Test authenticated endpoints
python test_web_app.py
```

For detailed comparison of all APIs, see [Chat Inquiry API Comparison](docs/CHAT_INQUIRY_API_COMPARISON.md).

## Troubleshooting

### Common Issues

1. **Python Not Found in PATH (Windows):**
   
   If you get "Python is not installed or not in PATH" but Python is installed:
   
   **Option 1: Run Troubleshooter**
   ```bash
   scripts\setup-venv-troubleshoot.bat
   ```
   This will check for Python in common locations and show which commands work.
   
   **Option 2: Use Python Launcher**
   ```bash
   # Try using 'py' launcher instead
   py -m venv venv
   venv\Scripts\activate
   ```
   
   **Option 3: Use Full Path**
   ```bash
   # Find your Python installation (common locations):
   # C:\Python39\python.exe
   # C:\Python310\python.exe
   # C:\Users\YourName\AppData\Local\Programs\Python\Python39\python.exe
   
   # Then use full path:
   "C:\Path\To\Python\python.exe" -m venv venv
   ```
   
   **Option 4: Add Python to PATH**
   - Open System Properties → Environment Variables
   - Edit PATH variable
   - Add Python installation directory (e.g., `C:\Python39`)
   - Add Python Scripts directory (e.g., `C:\Python39\Scripts`)
   - Restart Command Prompt

2. **Missing Dependencies:**
   ```bash
   pip install -r requirements.txt
   # For cloud mode:
   pip install -r requirements-cloud.txt
   ```

3. **ChromaDB Installation Issues (Windows):**
   ```bash
   # Use the Windows installation script
   install-windows.bat
   
   # Or install manually
   pip install chromadb --no-deps
   ```

4. **OpenAI API Errors:**
   - Verify your API key is correct
   - Check your OpenAI account has sufficient credits
   - The app will fall back to simple responses if OpenAI is unavailable

5. **Pinecone Connection Issues:**
   - Verify your API key and index name
   - Ensure the index exists in your Pinecone account
   - Check your internet connection
   - Verify namespace is correct if using custom namespaces

6. **Chroma Cloud Connection Issues:**
   - Verify your API key, tenant ID, and database ID
   - Check your internet connection
   - Run `python debug_chroma_cloud.py` for diagnostics

### Debug Commands

```bash
# Test database configuration
python test_database_config.py

# Test cloud configuration
python test_cloud_config.py

# Debug Chroma Cloud connection
python debug_chroma_cloud.py

# Test chat functionality
python test_chat_functionality.py

# Test all chat modes
python test_chat_modes.py
```

## API Documentation

### Base URL
- **Local Development**: `http://localhost:8000`
- **Production**: Configure as needed

### Authentication

Most endpoints require JWT token authentication. Include the token in the Authorization header:
```bash
Authorization: Bearer <your-jwt-token>
```

### 1. Authentication API (`/api/auth`)

#### Login
**POST** `/api/auth/login`

**Request:**
```json
{
  "username": "admin",
  "password": "your_password"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Login successful",
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user_id": "user_123",
  "user_info": {
    "user_id": "user_123",
    "username": "admin",
    "role": "admin",
    "status": "active"
  }
}
```

#### Register
**POST** `/api/auth/register`

**Request:**
```json
{
  "username": "newuser",
  "password": "secure_password",
  "email": "user@example.com",
  "role": "user"
}
```

**Response:**
```json
{
  "success": true,
  "message": "User registered successfully",
  "user_id": "user_456",
  "data": {
    "username": "newuser"
  }
}
```

#### Get Current User
**GET** `/api/auth/me`

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
  "success": true,
  "message": "User information retrieved successfully",
  "user_id": "user_123",
  "data": {
    "user_id": "user_123",
    "username": "admin",
    "email": "admin@example.com",
    "role": "admin",
    "status": "active"
  }
}
```

#### Update Current User
**PUT** `/api/auth/me`

**Headers:**
```
Authorization: Bearer <token>
```

**Request:**
```json
{
  "email": "newemail@example.com"
}
```

**Response:**
```json
{
  "success": true,
  "message": "User updated successfully",
  "user_id": "user_123",
  "data": {
    "user_id": "user_123",
    "username": "admin",
    "email": "newemail@example.com"
  }
}
```

#### Update Password
**PUT** `/api/auth/me/password`

**Headers:**
```
Authorization: Bearer <token>
```

**Request:**
```json
{
  "current_password": "old_password",
  "new_password": "new_secure_password"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Password updated successfully",
  "user_id": "user_123"
}
```

#### Create Token for User
**POST** `/api/auth/token`

**Request:**
```json
{
  "user_id": "user_123"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Token created successfully",
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user_id": "user_123",
  "data": {
    "username": "admin",
    "role": "admin",
    "status": "active"
  }
}
```

### 2. Vector Chat API (`/api`)

#### Public Chat (No Authentication Required)
**POST** `/api/chat/public`

**Headers:**
```
Content-Type: application/json
```

**Request:**
```json
{
  "message": "What is this website about?",
  "user_id": "optional_user_id",
  "namespace": "custom_namespace",
  "max_response_length": 1000,
  "max_sources": 3,
  "top_k": 5,
  "truncate_content": false
}
```

**Request Parameters:**
- `message` (required): The user's question or message
- `user_id` (optional): User identifier (defaults to "public_user" if not provided)
- `namespace` (optional): Pinecone namespace (takes precedence over config)
- `max_response_length` (optional): Maximum length of response text in characters. If exceeded, response will be truncated at word boundary.
- `max_sources` (optional): Maximum number of sources to include in response. Limits the number of retrieved documents.
- `top_k` (optional): Number of top results to retrieve from vector database (overrides config `TOP_K_RESULTS`)
- `truncate_content` (optional): Whether to truncate individual source content to 500 characters (default: `false`)

**Note:** 
- No authentication required
- All response limiting parameters are optional
- If not specified, defaults from config are used

**Response:**
```json
{
  "success": true,
  "message": "Chat response generated successfully",
  "data": {
    "response": "This website is about...",
    "sources": [],
    "mode": "knowledge_base",
    "state": null,
    "options": [],
    "collected_data": null,
    "requires_input": true,
    "conversation_complete": false,
    "error": false
  }
}
```

#### Chat (Authentication Required)
**POST** `/api/chat`

**Headers:**
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Request:**
```json
{
  "message": "What is this website about?",
  "user_id": "test_user",
  "namespace": "custom_namespace"
}
```

**Note:** `namespace` is optional and takes precedence over config. If not provided, uses config namespace or default.

**Response:**
```json
{
  "success": true,
  "message": "Chat response generated successfully",
  "data": {
    "response": "This website is about...",
    "sources": [],
    "mode": "knowledge_base",
    "state": null,
    "options": [],
    "collected_data": null,
    "requires_input": true,
    "conversation_complete": false,
    "error": false
  }
}
```

#### Crawl Website
**POST** `/api/crawl`

**Headers:**
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Request:**
```json
{
  "url": "https://example.com",
  "max_pages": 100,
  "depth": 3,
  "namespace": "custom_namespace"
}
```

**Response:**
```json
{
  "status": "success",
  "pages_crawled": 45,
  "chunks_processed": 120
}
```

#### Upload Documents
**POST** `/api/upload-docs`

**Headers:**
```
Authorization: Bearer <token>
Content-Type: multipart/form-data
```

**Request:**
```
files: [file1.pdf, file2.docx]
namespace: custom_namespace (optional query parameter)
```

**Response:**
```json
{
  "status": "success",
  "chunks_processed": 25
}
```

#### Get Statistics
**GET** `/api/stats?namespace=custom_namespace`

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
  "document_count": 150
}
```

#### Reset Chat Session
**POST** `/api/chat/reset?user_id=test_user`

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
  "status": "success",
  "message": "Chat session reset"
}
```

#### Get Chat Session
**GET** `/api/chat/session/{user_id}`

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
  "session_data": {
    "state": "collecting_info",
    "collected_data": {
      "name": "John Doe",
      "mobile": "1234567890"
    }
  }
}
```

#### Get Stored Answers
**GET** `/api/answers?limit=100`

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
  "answers": [
    {
      "user_id": "user_123",
      "session_id": "session_456",
      "data": {...}
    }
  ],
  "count": 10
}
```

#### Get User Answers
**GET** `/api/answers/{user_id}/{session_id}`

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
  "answers": {
    "user_id": "user_123",
    "session_id": "session_456",
    "data": {...}
  }
}
```

### 3. Chat Inquiry API (`/api/chat-inquiry`)

#### Create Inquiry (Public)
**POST** `/api/chat-inquiry/public`

**Request:**
```json
{
  "user_id": "user_123",
  "parent_type": "New Parent",
  "school_type": "Day",
  "name": "John Doe",
  "mobile": "1234567890",
  "question": "What are the admission requirements?",
  "answer": "The admission requirements include..."
}
```

**Response:**
```json
{
  "success": true,
  "message": "Inquiry created successfully",
  "data": {
    "id": "inquiry_789",
    "user_id": "user_123",
    "parent_type": "New Parent",
    "school_type": "Day",
    "name": "John Doe",
    "mobile": "1234567890",
    "question": "What are the admission requirements?",
    "answer": "The admission requirements include...",
    "created_at": "2024-01-01T12:00:00Z"
  }
}
```

#### Get All Inquiries (Public)
**GET** `/api/chat-inquiry/public?page=1&page_size=10&search=admission&sort_by=created_at&sort_order=desc`

**Response:**
```json
{
  "success": true,
  "message": "Inquiries retrieved successfully",
  "data": {
    "data": [
      {
        "id": "inquiry_789",
        "user_id": "user_123",
        "parent_type": "New Parent",
        "school_type": "Day",
        "name": "John Doe",
        "mobile": "1234567890",
        "question": "What are the admission requirements?",
        "answer": "The admission requirements include...",
        "created_at": "2024-01-01T12:00:00Z"
      }
    ],
    "total_count": 50,
    "page": 1,
    "page_size": 10,
    "total_pages": 5,
    "has_next": true,
    "has_previous": false
  }
}
```

#### Get Inquiry by ID (Public)
**GET** `/api/chat-inquiry/public/{inquiry_id}`

**Response:**
```json
{
  "success": true,
  "message": "Inquiry retrieved successfully",
  "data": {
    "id": "inquiry_789",
    "user_id": "user_123",
    "parent_type": "New Parent",
    "school_type": "Day",
    "name": "John Doe",
    "mobile": "1234567890",
    "question": "What are the admission requirements?",
    "answer": "The admission requirements include...",
    "created_at": "2024-01-01T12:00:00Z"
  }
}
```

#### Get Inquiries by User (Public)
**GET** `/api/chat-inquiry/public/user/{user_id}?page=1&page_size=10`

**Response:**
```json
{
  "success": true,
  "message": "User inquiries retrieved successfully",
  "data": [
    {
      "id": "inquiry_789",
      "user_id": "user_123",
      "parent_type": "New Parent",
      "school_type": "Day",
      "name": "John Doe",
      "mobile": "1234567890",
      "question": "What are the admission requirements?",
      "answer": "The admission requirements include...",
      "created_at": "2024-01-01T12:00:00Z"
    }
  ]
}
```

#### Create Inquiry (Authenticated)
**POST** `/api/chat-inquiry`

**Headers:**
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Request:**
```json
{
  "user_id": "user_123",
  "parent_type": "New Parent",
  "school_type": "Day",
  "name": "John Doe",
  "mobile": "1234567890",
  "question": "What are the admission requirements?",
  "answer": "The admission requirements include..."
}
```

**Response:**
```json
{
  "success": true,
  "message": "Chat inquiry created successfully",
  "data": {
    "inquiry_id": "inquiry_789"
  }
}
```

#### Update Inquiry
**PUT** `/api/chat-inquiry/{inquiry_id}`

**Headers:**
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Request:**
```json
{
  "answer": "Updated answer text"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Inquiry updated successfully",
  "data": {
    "inquiry_id": "inquiry_789"
  }
}
```

#### Delete Inquiry
**DELETE** `/api/chat-inquiry/{inquiry_id}`

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
  "success": true,
  "message": "Inquiry deleted successfully",
  "data": {
    "inquiry_id": "inquiry_789"
  }
}
```

#### Get Inquiry by ID (Authenticated)
**GET** `/api/chat-inquiry/{inquiry_id}`

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
  "success": true,
  "message": "Inquiry retrieved successfully",
  "data": {
    "id": "inquiry_789",
    "user_id": "user_123",
    "parent_type": "New Parent",
    "school_type": "Day",
    "name": "John Doe",
    "mobile": "1234567890",
    "question": "What are the admission requirements?",
    "answer": "The admission requirements include...",
    "created_at": "2024-01-01T12:00:00Z"
  }
}
```

#### Bulk Create Inquiries
**POST** `/api/chat-inquiry/bulk`

**Request:**
```json
{
  "inquiries": [
    {
      "user_id": "user_123",
      "parent_type": "New Parent",
      "school_type": "Day",
      "name": "John Doe",
      "mobile": "1234567890",
      "question": "Question 1?",
      "answer": "Answer 1"
    },
    {
      "user_id": "user_456",
      "parent_type": "Existing Parent",
      "school_type": "Boarding",
      "name": "Jane Smith",
      "mobile": "0987654321",
      "question": "Question 2?",
      "answer": "Answer 2"
    }
  ]
}
```

**Response:**
```json
{
  "success": true,
  "message": "Bulk insert completed. 2 successful, 0 failed",
  "data": {
    "success_count": 2,
    "failed_count": 0,
    "created_ids": ["inquiry_789", "inquiry_790"],
    "errors": []
  }
}
```

#### Get Statistics
**GET** `/api/chat-inquiry/stats`

**Response:**
```json
{
  "success": true,
  "message": "Statistics retrieved successfully",
  "data": {
    "total_inquiries": 150,
    "by_parent_type": {
      "New Parent": 80,
      "Existing Parent": 70
    },
    "by_school_type": {
      "Day": 90,
      "Boarding": 60
    }
  }
}
```

#### Health Check
**GET** `/api/chat-inquiry/health`

**Response:**
```json
{
  "success": true,
  "message": "Inquiry service is healthy",
  "data": {
    "status": "healthy",
    "inquiry_count": 150,
    "timestamp": "2024-01-01T12:00:00Z"
  }
}
```

### 4. User Management API (`/api/users`)

**Note:** All endpoints require admin authentication.

#### Get Users
**GET** `/api/users?page=1&page_size=10&search=admin&role=admin&status=active&sort_by=created_at&sort_order=desc`

**Headers:**
```
Authorization: Bearer <admin_token>
```

**Response:**
```json
{
  "success": true,
  "message": "Users retrieved successfully",
  "data": {
    "users": [
      {
        "user_id": "user_123",
        "username": "admin",
        "email": "admin@example.com",
        "role": "admin",
        "status": "active",
        "created_at": "2024-01-01T12:00:00Z"
      }
    ],
    "total_count": 50,
    "page": 1,
    "page_size": 10,
    "total_pages": 5,
    "has_next": true,
    "has_previous": false
  }
}
```

#### Get User by ID
**GET** `/api/users/{user_id}`

**Headers:**
```
Authorization: Bearer <admin_token>
```

**Response:**
```json
{
  "success": true,
  "message": "User retrieved successfully",
  "data": {
    "user_id": "user_123",
    "username": "admin",
    "email": "admin@example.com",
    "role": "admin",
    "status": "active",
    "created_at": "2024-01-01T12:00:00Z"
  }
}
```

#### Create User
**POST** `/api/users`

**Headers:**
```
Authorization: Bearer <admin_token>
Content-Type: application/json
```

**Request:**
```json
{
  "username": "newuser",
  "password": "secure_password",
  "email": "user@example.com",
  "role": "user",
  "status": "active"
}
```

**Response:**
```json
{
  "success": true,
  "message": "User created successfully",
  "data": {
    "user_id": "user_456",
    "username": "newuser",
    "email": "user@example.com",
    "role": "user",
    "status": "active"
  }
}
```

#### Update User
**PUT** `/api/users/{user_id}`

**Headers:**
```
Authorization: Bearer <admin_token>
Content-Type: application/json
```

**Request:**
```json
{
  "email": "updated@example.com",
  "role": "admin"
}
```

**Response:**
```json
{
  "success": true,
  "message": "User updated successfully",
  "data": {
    "user_id": "user_123",
    "username": "admin",
    "email": "updated@example.com",
    "role": "admin",
    "status": "active"
  }
}
```

#### Delete User
**DELETE** `/api/users/{user_id}`

**Headers:**
```
Authorization: Bearer <admin_token>
```

**Response:**
```json
{
  "success": true,
  "message": "User deleted successfully"
}
```

#### Reset User Password
**POST** `/api/users/{user_id}/reset-password`

**Headers:**
```
Authorization: Bearer <admin_token>
Content-Type: application/json
```

**Request:**
```json
{
  "password": "new_secure_password"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Password reset successfully"
}
```

#### Toggle User Status
**POST** `/api/users/{user_id}/toggle-status`

**Headers:**
```
Authorization: Bearer <admin_token>
```

**Response:**
```json
{
  "success": true,
  "message": "User status changed to inactive",
  "data": {
    "user_id": "user_123",
    "username": "admin",
    "status": "inactive"
  }
}
```

#### Get User Statistics
**GET** `/api/users/stats/overview`

**Headers:**
```
Authorization: Bearer <admin_token>
```

**Response:**
```json
{
  "success": true,
  "message": "User statistics retrieved successfully",
  "data": {
    "total_users": 150,
    "active_users": 120,
    "inactive_users": 30,
    "by_role": {
      "admin": 5,
      "user": 145
    }
  }
}
```

### 5. Database API (`/api/database`)

#### Get Database Status
**GET** `/api/database/status`

**Response:**
```json
{
  "success": true,
  "message": "Database status retrieved successfully",
  "data": {
    "postgresql_connected": true,
    "postgresql_status": "Connected",
    "postgresql_host": "db.example.com",
    "postgresql_database": "postgres",
    "postgresql_count": 150,
    "sqlite_available": true,
    "sqlite_count": 150,
    "total_inquiries": 150,
    "connection_type": "PostgreSQL"
  }
}
```

#### Test PostgreSQL Connection
**POST** `/api/database/test-postgres`

**Response:**
```json
{
  "success": true,
  "message": "PostgreSQL connection test successful",
  "data": {
    "connected": true,
    "host": "db.example.com",
    "port": "5432",
    "database": "postgres",
    "query_status": "Query execution successful",
    "connection_type": "PostgreSQL"
  }
}
```

#### Get PostgreSQL Health
**GET** `/api/database/postgres-health`

**Response:**
```json
{
  "success": true,
  "message": "PostgreSQL health check successful",
  "data": {
    "status": "connected",
    "healthy": true,
    "version": "PostgreSQL 15.4",
    "table_exists": true,
    "table_count": 150,
    "connection_uri": "postgresql://user:pass@host:port/db..."
  }
}
```

#### Get System Health
**GET** `/api/database/health`

**Response:**
```json
{
  "success": true,
  "message": "Health check completed",
  "data": {
    "status": "healthy",
    "postgresql": {
      "connected": true,
      "status": "connected"
    },
    "current_database": {
      "type": "postgresql",
      "status": "connected"
    },
    "inquiries": {
      "total_count": 150
    },
    "timestamp": "2024-12-28T12:00:00Z"
  }
}
```
