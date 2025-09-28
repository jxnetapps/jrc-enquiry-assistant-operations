# Configuration Guide

## Overview

This guide covers all aspects of configuring the Web ChatBot application for different environments (development, production, Azure).

## Environment Management

### Environment Types
- **Development**: Local development with relaxed settings
- **Production**: Live production environment with strict security
- **Azure**: Azure App Service deployment

### Environment Files Structure

```
config-templates/
├── config_template.env              # Default template
├── config_template.env.development  # Development template
├── config_template.env.production   # Production template
└── config_template.env.azure        # Azure template
```

### Local Environment Files (Not in Git)
```
.env                    # Default local environment
.env.development        # Development environment
.env.production         # Production environment
.env.azure              # Azure environment
```

## Configuration Management

### 1. Setup Environment Files

```bash
# Create all environment files from templates
python scripts/env-manager.py setup

# Rebuild environment files from templates
python scripts/env-manager.py rebuild

# Show current configuration
python scripts/env-manager.py show
```

### 2. Environment-Specific Settings

#### Development Environment
- `POSTGRESQL_CONNECTION_URI` - Local PostgreSQL database
- `DEBUG=true` - Enable debug mode
- `ALLOW_ANY_USER=true` - Allow any user to login

#### Production Environment
- `POSTGRESQL_CONNECTION_URI` - Supabase database
- `DEBUG=false` - Disable debug mode
- `ALLOW_ANY_USER=false` - Require authentication

#### Azure Environment
- `POSTGRESQL_CONNECTION_URI` - Supabase database
- `ENVIRONMENT=azure` - Azure-specific settings
- All configuration via Azure App Settings

## Database Configuration

### PostgreSQL Settings

#### Local Development
```bash
POSTGRESQL_CONNECTION_URI=postgresql://postgres:password@localhost:5432/database
POSTGRESQL_DATABASE_NAME=database_name
POSTGRESQL_CHAT_INQUIRY_TABLE=chat_inquiry_information
```

#### Production/Azure (Supabase)
```bash
POSTGRESQL_CONNECTION_URI=postgresql://postgres:password@db.umwxkbcvqvqqybjwcash.supabase.co:5432/postgres
POSTGRESQL_DATABASE_NAME=postgres
POSTGRESQL_CHAT_INQUIRY_TABLE=chat_inquiry_information
```

### Vector Database Settings

#### Local Development
```bash
DATABASE_TYPE=local
CHROMA_DB_PATH=./chroma_db
COLLECTION_NAME=web_content
```

#### Production/Azure (Chroma Cloud)
```bash
DATABASE_TYPE=cloud
CHROMA_CLOUD_API_KEY=your_api_key
CHROMA_CLOUD_TENANT_ID=your_tenant_id
CHROMA_CLOUD_DATABASE_ID=your_database_id
CHROMA_CLOUD_COLLECTION_NAME=web_content
```

## Authentication Configuration

### JWT Settings
```bash
JWT_SECRET_KEY=your_super_secure_secret_key
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_HOURS=8
```

### Admin Settings
```bash
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your_secure_password
ALLOW_ANY_USER=false  # Set to true for development only
```

## OpenAI Configuration

```bash
OPENAI_API_KEY=sk-your-openai-api-key
LLM_MODEL=gpt-4
LLM_TEMPERATURE=0.1
LLM_MAX_TOKENS=2000
OPENAI_EMBEDDING_MODEL=text-embedding-ada-002
```

## Azure App Service Configuration

### Setting Environment Variables in Azure

1. Go to Azure Portal
2. Navigate to your App Service
3. Go to Configuration → Application Settings
4. Add each setting manually

### Generate Azure Settings

```bash
# Generate all Azure settings from template
python scripts/generate-azure-config.py

# Show only required settings
python scripts/generate-azure-config.py required
```

### Key Azure Settings
```
ENVIRONMENT=azure
POSTGRESQL_CONNECTION_URI=postgresql://postgres:password@db.umwxkbcvqvqqybjwcash.supabase.co:5432/postgres
JWT_SECRET_KEY=your_secret_key
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your_password
OPENAI_API_KEY=sk-your-api-key
```

## Security Best Practices

### 1. Never Commit Sensitive Data
- `.env` files are in `.gitignore`
- Only commit template files
- Use environment variables in production

### 2. Use Strong Passwords
- Generate secure JWT secret keys
- Use complex admin passwords
- Rotate credentials regularly

### 3. Environment Separation
- Different settings for each environment
- Production uses external services
- Development uses local services

## Troubleshooting

### Common Issues

1. **Configuration not loading**
   - Check if `.env` file exists
   - Verify environment variable names
   - Check file permissions

2. **Database connection failed**
   - Verify connection string format
   - Check database server status
   - Verify credentials

3. **Authentication issues**
   - Check JWT secret key
   - Verify admin credentials
   - Check token expiration

### Health Checks

```bash
# Check application health
curl http://localhost:8000/api/chat-inquiry/health

# Check database status
curl http://localhost:8000/api/chat-inquiry/database/status

# Check PostgreSQL health
curl http://localhost:8000/api/chat-inquiry/database/postgres-health
```

## Quick Reference

### Essential Commands
```bash
# Setup environment
python scripts/env-manager.py setup

# Start development
scripts/start-dev.bat    # Windows
scripts/start-dev.sh     # Linux/Mac

# Start production
scripts/start-prod.bat   # Windows
scripts/start-prod.sh    # Linux/Mac

# Generate Azure config
python scripts/generate-azure-config.py
```

### File Locations
- Templates: `config-templates/config_template.env.*`
- Local config: `.env.*` (not in git)
- Azure config: Azure App Settings
- Scripts: `scripts/env-manager.py`
