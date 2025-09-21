# Web ChatBot 🤖

A sophisticated chatbot that crawls websites, processes content, and provides intelligent responses using vector embeddings and LLMs.

## Features

- 🌐 **Web Crawling**: Async crawler with depth control and polite delays
- 🧠 **AI-Powered**: Uses OpenAI GPT or local models for intelligent responses
- 🔍 **Vector Search**: Configurable vector database (FAISS local or Chroma Cloud)
- 🛡️ **Authentication**: JWT-based user authentication
- ⚡ **Rate Limiting**: Polite crawling with configurable delays
- 📊 **Content Filtering**: Quality-based content filtering
- 🕐 **Scheduling**: Automatic content updates
- 🌈 **Web Interface**: Modern FastAPI web app
- 🎯 **Configurable Chat Behavior**: Switch between knowledge base and predefined question flows
- 🔄 **State Management**: State-driven conversations for structured interactions

## Installation

1. **Install dependencies**

   **Windows Users:**
   ```bash
   # Run the automated installation script
   install-windows.bat
   ```
   
   **Other Platforms:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure database**
   
   The application supports two database backends:
   
   **Local Database (Default - FAISS)**
   ```bash
   DATABASE_TYPE=local
   CHROMA_DB_PATH=./chroma_db
   COLLECTION_NAME=web_content
   ```
   
   **Chroma Cloud Database**
   ```bash
   DATABASE_TYPE=cloud
   CHROMA_CLOUD_API_KEY=your_api_key
   CHROMA_CLOUD_TENANT_ID=your_tenant_id
   CHROMA_CLOUD_DATABASE_ID=your_database_id
   CHROMA_CLOUD_COLLECTION_NAME=web_content
   ```
   
   See [DATABASE_CONFIG.md](DATABASE_CONFIG.md) for detailed configuration instructions.

3. **Configure chat behavior**
   
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

4. **Set up environment variables**

   **Quick Setup:**
   ```bash
   # Run the setup script to create .env file
   python setup_env.py
   ```
   
   **Manual Setup:**
   Create a `.env` file with your configuration:
   ```bash
   # Database Configuration
   DATABASE_TYPE=local  # or 'cloud' for Chroma Cloud
   CHAT_BEHAVIOR=knowledge_base  # or 'pre_trained' for structured flow
   
   # OpenAI Configuration (optional)
   OPENAI_API_KEY=your_openai_api_key
   
   # Chroma Cloud Configuration (if using cloud database)
   CHROMA_CLOUD_API_KEY=your_chroma_cloud_api_key
   CHROMA_CLOUD_TENANT_ID=your_tenant_id
   CHROMA_CLOUD_DATABASE_ID=your_database_id
   ```
   
   **Configuration Template:**
   - Use `config_template.env` as a reference
   - Copy it to `.env` and customize as needed

## Testing

### 1. Test Chat Modes

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
DATABASE_TYPE=local
python test_database_config.py
```

**Chroma Cloud:**
```bash
# Set in .env
DATABASE_TYPE=cloud
python test_cloud_config.py
```

## Troubleshooting

### Common Issues

1. **Missing Dependencies:**
   ```bash
   pip install -r requirements.txt
   # For cloud mode:
   pip install -r requirements-cloud.txt
   ```

2. **ChromaDB Installation Issues (Windows):**
   ```bash
   # Use the Windows installation script
   install-windows.bat
   
   # Or install manually
   pip install chromadb --no-deps
   ```

3. **OpenAI API Errors:**
   - Verify your API key is correct
   - Check your OpenAI account has sufficient credits
   - The app will fall back to simple responses if OpenAI is unavailable

4. **Chroma Cloud Connection Issues:**
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
