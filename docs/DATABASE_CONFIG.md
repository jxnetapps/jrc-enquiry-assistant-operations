# Database Configuration Guide

This application supports two database backends:

## 1. Local Database (Default)
Uses FAISS for local vector storage.

### Configuration
Set the following environment variables:
```bash
VECTOR_DATABASE_TYPE=local
CHROMA_DB_PATH=./chroma_db
COLLECTION_NAME=web_content
```

## 2. Chroma Cloud Database
Uses Chroma Cloud for managed vector storage.

### Configuration
Set the following environment variables:
```bash
VECTOR_DATABASE_TYPE=cloud
CHROMA_CLOUD_API_KEY=your_chroma_cloud_api_key_here
CHROMA_CLOUD_TENANT_ID=your_tenant_id_here
CHROMA_CLOUD_DATABASE_ID=your_database_id_here
CHROMA_CLOUD_COLLECTION_NAME=web_content
```

### Getting Chroma Cloud Credentials
1. Sign up for Chroma Cloud at https://cloud.trychroma.com/
2. Create a new tenant
3. Create a database within your tenant
4. Generate an API key
5. Use the tenant ID, database ID, and API key in your configuration

## Installation

### Windows Users
For Windows users, ChromaDB requires Microsoft Visual C++ Build Tools. We provide an easy installation script:

```bash
# Run the Windows installation script
install-windows.bat
```

Or install manually:
```bash
# Install base requirements (works on all platforms)
pip install -r requirements.txt

# Install ChromaDB for cloud mode (optional)
pip install -r requirements-cloud.txt
```

If ChromaDB installation fails on Windows, you can still use local mode or try:
```bash
pip install chromadb --no-deps
```

### Other Platforms
```bash
# Install base requirements
pip install -r requirements.txt

# Install ChromaDB for cloud mode (optional)
pip install -r requirements-cloud.txt
```

## Environment Variables

Create a `.env` file in your project root with the following variables:

```bash
# Database Type: 'local' or 'cloud'
VECTOR_DATABASE_TYPE=local

# Local Database Settings
CHROMA_DB_PATH=./chroma_db
COLLECTION_NAME=web_content

# Chroma Cloud Settings (only needed when VECTOR_DATABASE_TYPE=cloud)
CHROMA_CLOUD_API_KEY=your_api_key
CHROMA_CLOUD_TENANT_ID=your_tenant_id
CHROMA_CLOUD_DATABASE_ID=your_database_id
CHROMA_CLOUD_COLLECTION_NAME=web_content

# Other settings...
OPENAI_API_KEY=your_openai_key
# ... (see config.py for all available options)
```

## Switching Between Modes

To switch from local to cloud:
1. Set `VECTOR_DATABASE_TYPE=cloud` in your `.env` file
2. Add your Chroma Cloud credentials
3. Restart the application

To switch from cloud to local:
1. Set `VECTOR_DATABASE_TYPE=local` in your `.env` file
2. Restart the application

## Data Migration

**Note**: Data is not automatically migrated between local and cloud databases. If you need to migrate data:

1. Export data from the current database
2. Switch database type
3. Re-import the data

## Production Recommendations

- **Development**: Use `local` mode for faster development and testing
- **Production**: Use `cloud` mode for better scalability and management
- **Hybrid**: Use `local` for testing and `cloud` for production with the same codebase
