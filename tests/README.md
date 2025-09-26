# Web ChatBot Enhanced - Test Suite

This directory contains all test files for the Web ChatBot Enhanced application.

## Test Files

### API Tests
- `test_reorganized_api.py` - Tests the reorganized API structure
- `test_inquiry_simple.py` - Simple test for chat inquiry API
- `test_chat_inquiry_api.py` - Comprehensive chat inquiry API tests

### Application Tests
- `test_web_app.py` - Web application functionality tests
- `test_chat_functionality.py` - Chat functionality tests
- `test_chat_modes.py` - Different chat modes tests
- `test_session_persistence.py` - Session persistence tests

### System Tests
- `test_auto_login_and_storage.py` - Auto login and storage tests
- `test_complete_system.py` - Complete system integration tests
- `test_cloud_config.py` - Cloud configuration tests
- `test_database_config.py` - Database configuration tests

### Fix Tests
- `test_simple_chat_fix.py` - Simple chat fix tests
- `test_complete_chat_fix.py` - Complete chat fix tests
- `test_chat_flow_fix.py` - Chat flow fix tests

## Running Tests

### Prerequisites
1. Make sure the server is running on `http://localhost:8000`
2. Install all dependencies: `pip install -r requirements.txt`

### Quick Tests (Basic)
Run only essential tests for quick verification:
```bash
cd tests
python run_basic_tests.py
```

### All Tests
Run all available tests:
```bash
cd tests
python run_all_tests.py
```

### Individual Tests
Run specific test files:
```bash
cd tests
python test_reorganized_api.py
python test_inquiry_simple.py
# ... etc
```

## Test Categories

### 1. API Structure Tests
- Verify all API endpoints are accessible
- Check API route registration
- Test basic connectivity

### 2. Chat Inquiry Tests
- Test MongoDB integration
- Verify data validation
- Test CRUD operations
- Check search functionality

### 3. Vector Chat Tests
- Test chat functionality
- Verify document processing
- Check vector database operations

### 4. Authentication Tests
- Test login/logout
- Verify JWT token handling
- Check user management

### 5. System Integration Tests
- Test complete workflows
- Verify data persistence
- Check error handling

## Test Results

Tests will output:
- ✅ **PASSED** - Test completed successfully
- ❌ **FAILED** - Test failed with errors
- ⏰ **TIMEOUT** - Test took too long to complete
- ⚠️ **SKIPPED** - Test file not found or conditions not met

## Troubleshooting

### Common Issues

1. **Connection Error**
   - Make sure the server is running on `http://localhost:8000`
   - Check if the port is available

2. **Import Errors**
   - Make sure you're running tests from the project root
   - Install all dependencies: `pip install -r requirements.txt`

3. **Authentication Errors**
   - Check if the authentication system is properly configured
   - Verify JWT secret key is set

4. **Database Errors**
   - Ensure MongoDB is running and accessible
   - Check database connection configuration

### Getting Help

If tests fail:
1. Check the error messages in the test output
2. Verify all dependencies are installed
3. Make sure the server is running correctly
4. Check the application logs for more details

## Adding New Tests

To add new tests:
1. Create a new test file in this directory
2. Follow the naming convention: `test_*.py`
3. Use the existing test files as templates
4. Update this README if needed
