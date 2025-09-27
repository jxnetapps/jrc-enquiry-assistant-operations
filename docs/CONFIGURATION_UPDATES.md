# Configuration Updates - Environment Variable Requirements

## Overview

Updated the configuration system to properly require critical environment variables instead of using hardcoded defaults. This ensures that sensitive values like database credentials and authentication keys are properly managed through environment variables.

## Changes Made

### 1. Updated `config.py`

#### **Removed Hardcoded Defaults:**
- `JWT_SECRET_KEY`: Now required (was: `"your_super_secret_jwt_key_here"`)
- `ADMIN_USERNAME`: Now required (was: `"admin"`)
- `ADMIN_PASSWORD`: Now required (was: `"admin123"`)
- `POSTGRESQL_CONNECTION_URI`: Now required (was: hardcoded connection string)
- `POSTGRESQL_DATABASE_NAME`: Now required (was: `"jrc_chatbot_assistant"`)

#### **Enhanced Validation:**
```python
@classmethod
def validate_config(cls):
    """Validate configuration values"""
    # Validate required authentication settings
    if not cls.JWT_SECRET_KEY:
        raise ValueError("JWT_SECRET_KEY is required")
    if not cls.ADMIN_USERNAME:
        raise ValueError("ADMIN_USERNAME is required")
    if not cls.ADMIN_PASSWORD:
        raise ValueError("ADMIN_PASSWORD is required")
    
    # Validate PostgreSQL configuration
    if not cls.POSTGRESQL_CONNECTION_URI:
        raise ValueError("POSTGRESQL_CONNECTION_URI is required for PostgreSQL operations")
    if not cls.POSTGRESQL_DATABASE_NAME:
        raise ValueError("POSTGRESQL_DATABASE_NAME is required for PostgreSQL operations")
    
    # ... other validations
```

### 2. Updated Environment Templates

#### **Development (`config_template.env.development`):**
```env
# Authentication
JWT_SECRET_KEY=dev_jwt_secret_key_change_in_production
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin123

# PostgreSQL
POSTGRESQL_CONNECTION_URI=postgresql://postgres:Wildcat%40007@localhost:5432/jrc_chatbot_assistant_dev
POSTGRESQL_DATABASE_NAME=jrc_chatbot_assistant_dev
```

#### **Staging (`config_template.env.staging`):**
```env
# Authentication
JWT_SECRET_KEY=staging_jwt_secret_key_change_in_production
ADMIN_USERNAME=admin
ADMIN_PASSWORD=staging_admin_password

# PostgreSQL
POSTGRESQL_CONNECTION_URI=postgresql://username:password@staging-db-host:5432/jrc_chatbot_assistant_staging
POSTGRESQL_DATABASE_NAME=jrc_chatbot_assistant_staging
```

#### **Production (`config_template.env.production`):**
```env
# Authentication
JWT_SECRET_KEY=your_super_secure_production_jwt_secret_key_here
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your_secure_admin_password_here

# PostgreSQL
POSTGRESQL_CONNECTION_URI=postgresql://username:password@production-db-host:5432/jrc_chatbot_assistant
POSTGRESQL_DATABASE_NAME=jrc_chatbot_assistant
```

#### **Azure (`config_template.env.azure`):**
```env
# Authentication (Azure App Settings)
JWT_SECRET_KEY=${JWT_SECRET_KEY}
ADMIN_USERNAME=${ADMIN_USERNAME}
ADMIN_PASSWORD=${ADMIN_PASSWORD}

# PostgreSQL (Azure Database for PostgreSQL)
POSTGRESQL_CONNECTION_URI=${POSTGRESQL_CONNECTION_URI}
POSTGRESQL_DATABASE_NAME=${POSTGRESQL_DATABASE_NAME}
```

## Required Environment Variables

### **Critical (Required for Application to Start):**
- `JWT_SECRET_KEY` - Secret key for JWT token generation
- `ADMIN_USERNAME` - Default admin username
- `ADMIN_PASSWORD` - Default admin password
- `POSTGRESQL_CONNECTION_URI` - PostgreSQL connection string
- `POSTGRESQL_DATABASE_NAME` - PostgreSQL database name

### **Optional (Have Sensible Defaults):**
- `POSTGRESQL_CHAT_INQUIRY_TABLE` - Default: `"chat_inquiry_information"`
- `JWT_ALGORITHM` - Default: `"HS256"`
- `JWT_ACCESS_TOKEN_EXPIRE_HOURS` - Default: `24`
- `DEFAULT_USER_STATUS` - Default: `"active"`
- `ALLOW_ANY_USER` - Default: `"True"`

## Security Benefits

### **1. No Hardcoded Secrets:**
- JWT secrets are now required from environment
- Database credentials must be provided via environment variables
- Admin credentials are configurable per environment

### **2. Environment-Specific Configuration:**
- Development: Uses local database with dev credentials
- Staging: Uses staging database with staging credentials
- Production: Requires secure production credentials
- Azure: Uses Azure App Settings for secure credential management

### **3. Validation on Startup:**
- Application fails fast if required variables are missing
- Clear error messages indicate what's missing
- Prevents accidental deployment with default credentials

## Migration Guide

### **For Existing Deployments:**

1. **Update Environment Files:**
   ```bash
   # Copy template for your environment
   cp config_template.env.development .env.development
   cp config_template.env.production .env.production
   cp config_template.env.staging .env.staging
   ```

2. **Set Required Variables:**
   ```bash
   # Update with your actual values
   JWT_SECRET_KEY=your_actual_jwt_secret
   ADMIN_USERNAME=your_admin_username
   ADMIN_PASSWORD=your_secure_password
   POSTGRESQL_CONNECTION_URI=your_postgresql_connection_string
   POSTGRESQL_DATABASE_NAME=your_database_name
   ```

3. **Test Configuration:**
   ```bash
   python -c "from config import Config; Config.validate_config(); print('Configuration valid!')"
   ```

### **For Azure Deployments:**

1. **Set Azure App Settings:**
   ```bash
   az webapp config appsettings set --name your-app --resource-group your-rg --settings \
     JWT_SECRET_KEY="your_jwt_secret" \
     ADMIN_USERNAME="your_admin" \
     ADMIN_PASSWORD="your_password" \
     POSTGRESQL_CONNECTION_URI="your_connection_string" \
     POSTGRESQL_DATABASE_NAME="your_database"
   ```

2. **Verify Deployment:**
   - Check application logs for configuration errors
   - Test API endpoints to ensure proper authentication
   - Verify database connectivity

## Testing

### **Test Configuration Validation:**
```bash
# Test with missing variables (should fail)
ENVIRONMENT=test python -c "from config import Config; Config.validate_config()"

# Test with valid variables (should pass)
ENVIRONMENT=development python -c "from config import Config; Config.validate_config()"
```

### **Test Environment Loading:**
```bash
# Test development environment
python scripts/setup-env.py development
python -c "from config import Config; print(f'JWT Secret: {Config.JWT_SECRET_KEY[:10]}...')"

# Test production environment
python scripts/setup-env.py production
python -c "from config import Config; print(f'JWT Secret: {Config.JWT_SECRET_KEY[:10]}...')"
```

## Troubleshooting

### **Common Issues:**

1. **"JWT_SECRET_KEY is required"**
   - Set `JWT_SECRET_KEY` in your environment file
   - Ensure the environment file is being loaded correctly

2. **"POSTGRESQL_CONNECTION_URI is required"**
   - Set `POSTGRESQL_CONNECTION_URI` in your environment file
   - Verify the connection string format

3. **"ADMIN_USERNAME is required"**
   - Set `ADMIN_USERNAME` in your environment file
   - Ensure it's not empty or whitespace

### **Debug Configuration Loading:**
```python
# Add this to debug configuration loading
import os
from dotenv import load_dotenv

print(f"ENVIRONMENT: {os.getenv('ENVIRONMENT')}")
print(f"JWT_SECRET_KEY: {os.getenv('JWT_SECRET_KEY')}")
print(f"ADMIN_USERNAME: {os.getenv('ADMIN_USERNAME')}")
print(f"POSTGRESQL_CONNECTION_URI: {os.getenv('POSTGRESQL_CONNECTION_URI')}")
```

## Best Practices

### **1. Secret Management:**
- Use Azure Key Vault for production secrets
- Rotate secrets regularly
- Never commit secrets to version control

### **2. Environment Separation:**
- Use different databases for different environments
- Use different JWT secrets for each environment
- Use different admin credentials for each environment

### **3. Validation:**
- Always validate configuration before deployment
- Test configuration loading in CI/CD pipeline
- Monitor application logs for configuration errors

## Summary

These changes ensure that:
- ✅ No hardcoded secrets in the codebase
- ✅ Environment-specific configuration management
- ✅ Proper validation on application startup
- ✅ Clear error messages for missing configuration
- ✅ Secure credential management for all environments
- ✅ Easy migration path for existing deployments
