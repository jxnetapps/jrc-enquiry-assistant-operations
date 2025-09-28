# Web ChatBot Enhanced - Installation Guide

## Quick Start

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd jrc-enquiry-assistant-operations
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**
   ```bash
   cp config_template.env .env
   # Edit .env with your configuration
   ```

4. **Run the application**
   ```bash
   # Set PORT environment variable if needed (default: 8001)
   $env:PORT="3000"; python web_app.py
   # Or on Linux/Mac: PORT=3000 python web_app.py
   ```

## Requirements

### Core Dependencies
The `requirements.txt` file includes all necessary dependencies:

- **FastAPI & Web Framework**: FastAPI, Uvicorn, AioHTTP
- **AI & ML**: OpenAI, Sentence Transformers, FAISS
- **Database**: MongoDB (Motor, PyMongo), SQLite (built-in)
- **Authentication**: JWT, PassLib, BCrypt
- **Document Processing**: PyPDF, Python-DocX
- **Data Validation**: Pydantic, Email Validator

### Optional Dependencies

Some features require additional packages that are commented out in `requirements.txt`:

#### ChromaDB Cloud Integration
```bash
pip install chromadb==0.4.15
```

#### MySQL Support
```bash
pip install PyMySQL==1.1.0
```

#### MSSQL Support
```bash
pip install pyodbc==5.0.1
```

## Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
# API Keys
OPENAI_API_KEY=your_openai_api_key_here

# Database Configuration
VECTOR_DATABASE_TYPE=local  # or 'cloud' for ChromaDB
MONGODB_CONNECTION_URI=mongodb+srv://user:pass@cluster.mongodb.net/
MONGODB_DATABASE_NAME=inquiryassistant
MONGODB_CHAT_INQUIRY_COLLECTION=chat_inquiry_information

# ChromaDB Configuration (if using cloud)
CHROMA_CLOUD_API_KEY=your_chroma_api_key
CHROMA_CLOUD_TENANT_ID=your_tenant_id
CHROMA_CLOUD_DATABASE_ID=your_database_id

# Authentication
JWT_SECRET_KEY=your_super_secret_jwt_key_here
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin123

# Application Settings
HOST=0.0.0.0
PORT=8000
DEBUG=True
```

## Testing

### Run Basic Tests
```bash
cd tests
python run_basic_tests.py
```

### Run All Tests
```bash
cd tests
python run_all_tests.py
```

### Run Individual Tests
```bash
cd tests
python test_reorganized_api.py
python test_inquiry_simple.py
```

## Current Status

### ✅ What's Working
- **Dependencies**: All required packages are installed correctly
- **API Structure**: All API endpoints are properly organized and accessible
- **Application Startup**: Application starts successfully
- **MongoDB Integration**: MongoDB connection is optional (app continues without it)
- **File Organization**: Clean project structure with organized tests and APIs

### ⚠️ MongoDB Connection
The application currently shows MongoDB connection warnings due to SSL handshake issues with MongoDB Atlas. This is expected and **does not prevent the application from working**. The chat inquiry features will be disabled until MongoDB is properly configured.

### 🔧 Port Configuration
If you encounter port conflicts, set a different PORT:
```bash
# Windows PowerShell
$env:PORT="3000"; python web_app.py

# Linux/Mac
PORT=3000 python web_app.py
```

## Project Structure

```
jrc-enquiry-assistant-operations/
├── api/                    # API modules
│   ├── auth_api.py        # Authentication APIs
│   ├── vector_chat_api.py # Vector chat APIs
│   └── chat_inquiry_api.py # Chat inquiry APIs
├── tests/                  # All test files
│   ├── run_all_tests.py   # Complete test runner
│   ├── run_basic_tests.py # Basic test runner
│   └── README.md          # Test documentation
├── database/               # Database modules
├── models/                 # Pydantic models
├── auth/                   # Authentication modules
├── chatbot/                # Chat bot modules
├── crawler/                # Web crawling modules
├── embedding/              # Embedding modules
├── utils/                  # Utility modules
├── static/                 # Static files
├── templates/              # HTML templates
├── requirements.txt        # All dependencies
├── web_app.py             # Main application
└── main.py                # Application entry point
```

## Troubleshooting

### Common Issues

1. **Import Errors**
   - Make sure all dependencies are installed: `pip install -r requirements.txt`
   - Check Python path and virtual environment

2. **Database Connection Errors**
   - Verify MongoDB connection string
   - Check if MongoDB is running and accessible
   - Verify database credentials

3. **Authentication Errors**
   - Check JWT secret key configuration
   - Verify user credentials in `.env` file

4. **API Errors**
   - Ensure server is running on correct port
   - Check CORS configuration
   - Verify API endpoint URLs

### Getting Help

1. Check the test output for specific error messages
2. Review the application logs
3. Verify all configuration settings
4. Ensure all dependencies are properly installed

## Development

### Adding New Features

1. **New API Endpoints**: Add to appropriate file in `api/` folder
2. **New Tests**: Add to `tests/` folder with `test_` prefix
3. **New Dependencies**: Add to `requirements.txt` with version pinning

### Code Organization

- **API Logic**: `api/` folder
- **Database Operations**: `database/` folder
- **Data Models**: `models/` folder
- **Business Logic**: `chatbot/`, `crawler/`, `embedding/` folders
- **Utilities**: `utils/` folder
- **Tests**: `tests/` folder

This structure ensures clean separation of concerns and easy maintenance.
