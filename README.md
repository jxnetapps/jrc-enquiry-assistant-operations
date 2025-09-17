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

3. **Set up environment variables**
