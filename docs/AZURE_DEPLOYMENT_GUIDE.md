# Azure Deployment Guide

## Overview

This guide provides comprehensive steps to deploy the Web ChatBot application to Azure App Service, including configuration, deployment, and troubleshooting.

## Prerequisites

### Required Tools
- Azure subscription with active billing
- Azure CLI installed ([Download here](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli))
- PowerShell (Windows) or Bash (Linux/Mac)
- Git repository with application code

### Required Credentials
- OpenAI API key
- Supabase database credentials
- Chroma Cloud API key and credentials
- JWT secret key for authentication

## Pre-Deployment Checklist

### ✅ Environment Setup
- [ ] Azure subscription active
- [ ] Azure CLI installed and logged in
- [ ] GitHub repository with code
- [ ] Required API keys and credentials ready
- [ ] Application tested locally

### ✅ Azure Resources
- [ ] Resource group created
- [ ] App Service plan created
- [ ] App Service created
- [ ] Application Insights configured (optional)

## Deployment Steps

### 1. Azure CLI Setup

```bash
# Login to Azure
az login

# Set subscription (if multiple)
az account set --subscription "Your Subscription Name"

# Create resource group
az group create --name "jrc-chatbot-rg" --location "East US"

# Create App Service plan
az appservice plan create --name "jrc-chatbot-plan" --resource-group "jrc-chatbot-rg" --sku "B1" --is-linux

# Create App Service
az webapp create --resource-group "jrc-chatbot-rg" --plan "jrc-chatbot-plan" --name "jrc-chatbot-app" --runtime "PYTHON|3.11"
```

### 2. Application Configuration

#### Generate Azure Settings
```bash
# Generate all Azure settings from template
python scripts/generate-azure-config.py

# Show only required settings
python scripts/generate-azure-config.py required
```

#### Set Application Settings in Azure Portal

1. Go to Azure Portal
2. Navigate to your App Service
3. Go to Configuration → Application Settings
4. Add each setting:

**Essential Settings:**
```
ENVIRONMENT=azure
POSTGRESQL_CONNECTION_URI=postgresql://postgres:Wildcat@007@db.umwxkbcvqvqqybjwcash.supabase.co:5432/postgres
POSTGRESQL_DATABASE_NAME=postgres
JWT_SECRET_KEY=your_super_secure_production_jwt_secret_key
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your_secure_admin_password
OPENAI_API_KEY=sk-your-openai-api-key
DATABASE_TYPE=cloud
CHROMA_CLOUD_API_KEY=your_chroma_cloud_api_key
CHROMA_CLOUD_TENANT_ID=your_tenant_id
CHROMA_CLOUD_DATABASE_ID=your_database_id
```

**Additional Settings:**
```
HOST=0.0.0.0
PORT=8000
DEBUG=false
LOG_LEVEL=INFO
WEBSITES_PORT=8000
WEBSITES_ENABLE_APP_SERVICE_STORAGE=true
SCM_DO_BUILD_DURING_DEPLOYMENT=true
```

### 3. Deployment Methods

#### Method 1: Azure CLI Deployment
```bash
# Deploy from local directory
az webapp deployment source config-zip --resource-group "jrc-chatbot-rg" --name "jrc-chatbot-app" --src "deployment.zip"

# Deploy from GitHub
az webapp deployment source config --resource-group "jrc-chatbot-rg" --name "jrc-chatbot-app" --repo-url "https://github.com/yourusername/your-repo" --branch "main" --manual-integration
```

#### Method 2: GitHub Actions (Recommended)
```yaml
# .github/workflows/azure-deploy.yml
name: Deploy to Azure App Service

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    
    - name: Deploy to Azure
      uses: azure/webapps-deploy@v2
      with:
        app-name: 'jrc-chatbot-app'
        publish-profile: ${{ secrets.AZUREAPPSERVICE_PUBLISHPROFILE }}
```

#### Method 3: Visual Studio Code
1. Install Azure App Service extension
2. Right-click on project folder
3. Select "Deploy to Web App"
4. Choose your Azure subscription and App Service

### 4. Post-Deployment Configuration

#### Enable Application Insights (Optional)
```bash
# Create Application Insights
az monitor app-insights component create --app "jrc-chatbot-insights" --location "East US" --resource-group "jrc-chatbot-rg"

# Get instrumentation key
az monitor app-insights component show --app "jrc-chatbot-insights" --resource-group "jrc-chatbot-rg" --query "instrumentationKey" -o tsv
```

#### Configure Custom Domain (Optional)
```bash
# Add custom domain
az webapp config hostname add --webapp-name "jrc-chatbot-app" --resource-group "jrc-chatbot-rg" --hostname "yourdomain.com"
```

## Environment Configuration

### How Environment Variables Work in Azure

#### Local Development
- Uses `.env` files (`.env.development`, `.env.production`, etc.)
- Files are created by `python scripts/env-manager.py setup`
- Contains real credentials and settings

#### Azure App Service
- **NO `.env` files** - They don't exist in Azure
- Uses **Application Settings** instead
- Environment variables are set in Azure portal
- Application reads directly from environment variables

### Configuration Loading Priority

1. **Environment Variables** (Azure App Service) - **Highest Priority**
2. **`.env.{ENVIRONMENT}` file** (Local development)
3. **`.env` file** (Local fallback)

## Testing and Validation

### Health Check Endpoints

```bash
# General health
curl https://your-app.azurewebsites.net/api/chat-inquiry/health

# Database status
curl https://your-app.azurewebsites.net/api/chat-inquiry/database/status

# Detailed PostgreSQL health
curl https://your-app.azurewebsites.net/api/chat-inquiry/database/postgres-health
```

### Local Testing with Azure Configuration

```bash
# Set environment to azure
set ENVIRONMENT=azure

# Set Azure environment variables
set POSTGRESQL_CONNECTION_URI=postgresql://postgres:password@db.umwxkbcvqvqqybjwcash.supabase.co:5432/postgres
set JWT_SECRET_KEY=your_secret_key
set ADMIN_USERNAME=admin
set ADMIN_PASSWORD=your_password

# Start application
python web_app.py
```

## Troubleshooting

### Common Issues

#### 1. Application Won't Start
- Check Application Settings in Azure Portal
- Verify all required environment variables are set
- Check application logs in Azure Portal

#### 2. Database Connection Failed
- Verify PostgreSQL connection string format
- Check Supabase database status
- Verify credentials in Application Settings

#### 3. Authentication Issues
- Check JWT secret key in Application Settings
- Verify admin credentials
- Check token expiration settings

#### 4. Vector Database Issues
- Verify Chroma Cloud credentials
- Check collection name and database ID
- Verify API key permissions

### Logging and Monitoring

#### View Application Logs
```bash
# Stream logs
az webapp log tail --resource-group "jrc-chatbot-rg" --name "jrc-chatbot-app"

# Download logs
az webapp log download --resource-group "jrc-chatbot-rg" --name "jrc-chatbot-app"
```

#### Application Insights
- Monitor performance metrics
- Track errors and exceptions
- Analyze user behavior
- Set up alerts

## Security Best Practices

### 1. Secure Configuration
- Use strong, unique passwords
- Rotate credentials regularly
- Enable HTTPS only
- Use managed identities where possible

### 2. Network Security
- Configure IP restrictions if needed
- Use Azure Key Vault for sensitive data
- Enable Azure Security Center

### 3. Monitoring
- Set up alerts for critical issues
- Monitor failed authentication attempts
- Track resource usage

## Maintenance and Updates

### Updating Application
1. Make changes to code
2. Test locally with Azure configuration
3. Deploy to Azure
4. Verify health check endpoints
5. Monitor logs for issues

### Scaling
```bash
# Scale up App Service plan
az appservice plan update --name "jrc-chatbot-plan" --resource-group "jrc-chatbot-rg" --sku "S1"

# Scale out (multiple instances)
az webapp scale --resource-group "jrc-chatbot-rg" --name "jrc-chatbot-app" --instance-count 3
```

## Cost Optimization

### App Service Plan Tiers
- **F1 (Free)**: Development and testing
- **B1 (Basic)**: Small production workloads
- **S1 (Standard)**: Production workloads
- **P1 (Premium)**: High-performance workloads

### Monitoring Costs
- Use Azure Cost Management
- Set up billing alerts
- Monitor resource usage
- Optimize based on actual usage

## Quick Reference

### Essential Commands
```bash
# Generate Azure settings
python scripts/generate-azure-config.py

# Deploy to Azure
az webapp deployment source config-zip --resource-group "jrc-chatbot-rg" --name "jrc-chatbot-app" --src "deployment.zip"

# Check logs
az webapp log tail --resource-group "jrc-chatbot-rg" --name "jrc-chatbot-app"

# Restart app
az webapp restart --resource-group "jrc-chatbot-rg" --name "jrc-chatbot-app"
```

### Important URLs
- Azure Portal: https://portal.azure.com
- App Service: https://your-app.azurewebsites.net
- Health Check: https://your-app.azurewebsites.net/api/chat-inquiry/health
- Swagger Docs: https://your-app.azurewebsites.net/docs
