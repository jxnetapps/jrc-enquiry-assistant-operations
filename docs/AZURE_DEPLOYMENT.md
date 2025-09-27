# Azure App Service Deployment Guide

This guide provides detailed steps to deploy the Web ChatBot application to Azure App Service.

## Prerequisites

### 1. Azure Account and CLI
- Azure subscription with active billing
- Azure CLI installed ([Download here](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli))
- PowerShell (for Windows) or Bash (for Linux/Mac)

### 2. Required Azure Resources
- Resource Group
- App Service Plan
- App Service (Web App)
- Azure Database for PostgreSQL (optional)
- Application Insights (optional)

### 3. Environment Variables
- OpenAI API Key
- Chroma Cloud credentials (if using cloud database)
- PostgreSQL connection string
- JWT secret key

## Deployment Methods

### Method 1: Azure CLI (Recommended)

#### Step 1: Prepare the Application

```bash
# 1. Clone the repository
git clone <your-repo-url>
cd web-chatbot-enhanced

# 2. Setup Azure environment
python scripts/setup-env.py production

# 3. Create deployment package
zip -r webchatbot.zip . -x "*.git*" "*.pyc" "__pycache__/*" "*.env*" "chroma_db/*" "logs/*"
```

#### Step 2: Deploy Using Scripts

**Windows:**
```powershell
# Make script executable
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Run deployment
.\azure-deploy.ps1 -ResourceGroupName "webchatbot-rg" -WebAppName "webchatbot-app" -Location "East US" -AppServicePlan "B1"
```

**Linux/Mac:**
```bash
# Make script executable
chmod +x azure-deploy.sh

# Run deployment
./azure-deploy.sh -g webchatbot-rg -w webchatbot-app -l "East US" -p B1
```

#### Step 3: Configure Application Settings

```bash
# Set environment variables
az webapp config appsettings set --resource-group webchatbot-rg --name webchatbot-app --settings \
    OPENAI_API_KEY="your_openai_api_key" \
    JWT_SECRET_KEY="your_jwt_secret_key" \
    POSTGRESQL_CONNECTION_URI="your_postgresql_connection_string" \
    CHROMA_CLOUD_API_KEY="your_chroma_cloud_api_key" \
    CHROMA_CLOUD_TENANT_ID="your_tenant_id" \
    CHROMA_CLOUD_DATABASE_ID="your_database_id"
```

### Method 2: Azure Portal

#### Step 1: Create Resources

1. **Create Resource Group:**
   - Go to Azure Portal
   - Click "Create a resource" → "Resource group"
   - Name: `webchatbot-rg`
   - Region: `East US`

2. **Create App Service Plan:**
   - Go to "Create a resource" → "Web App"
   - Resource Group: `webchatbot-rg`
   - Name: `webchatbot-app`
   - Runtime: `Python 3.11`
   - Operating System: `Linux`
   - Region: `East US`
   - Pricing Plan: `B1` (Basic)

3. **Create PostgreSQL Database (Optional):**
   - Go to "Create a resource" → "Azure Database for PostgreSQL"
   - Resource Group: `webchatbot-rg`
   - Server name: `webchatbot-db`
   - Admin username: `webchatbot_admin`
   - Password: `YourSecurePassword123!`
   - Location: `East US`

#### Step 2: Configure Application

1. **Go to your Web App:**
   - Navigate to your web app in Azure Portal
   - Go to "Configuration" → "Application settings"

2. **Add Application Settings:**
   ```
   ENVIRONMENT = production
   DEBUG = false
   WEBSITES_PORT = 8000
   OPENAI_API_KEY = your_openai_api_key
   JWT_SECRET_KEY = your_jwt_secret_key
   POSTGRESQL_CONNECTION_URI = postgresql://webchatbot_admin:YourSecurePassword123!@webchatbot-db.postgres.database.azure.com:5432/postgres
   CHROMA_CLOUD_API_KEY = your_chroma_cloud_api_key
   CHROMA_CLOUD_TENANT_ID = your_tenant_id
   CHROMA_CLOUD_DATABASE_ID = your_database_id
   ```

3. **Configure Startup Command:**
   - Go to "Configuration" → "General settings"
   - Startup Command: `python web_app.py`

#### Step 3: Deploy Code

1. **Using VS Code:**
   - Install "Azure App Service" extension
   - Right-click on your project folder
   - Select "Deploy to Web App"
   - Choose your web app

2. **Using Git:**
   - Go to "Deployment Center" in your web app
   - Choose "Local Git"
   - Follow the instructions to push your code

3. **Using ZIP Deploy:**
   - Create a ZIP file of your application
   - Use Azure CLI: `az webapp deployment source config-zip`

### Method 3: Docker Container

#### Step 1: Build and Push Docker Image

```bash
# Build Docker image
docker build -f Dockerfile.azure -t webchatbot:latest .

# Tag for Azure Container Registry
docker tag webchatbot:latest yourregistry.azurecr.io/webchatbot:latest

# Push to registry
docker push yourregistry.azurecr.io/webchatbot:latest
```

#### Step 2: Deploy Container

```bash
# Create web app with container
az webapp create --resource-group webchatbot-rg --plan webchatbot-plan --name webchatbot-app --deployment-local-git

# Configure container
az webapp config container set --name webchatbot-app --resource-group webchatbot-rg --docker-custom-image-name yourregistry.azurecr.io/webchatbot:latest
```

## CI/CD with GitHub Actions

### Step 1: Setup GitHub Secrets

Go to your GitHub repository → Settings → Secrets and variables → Actions

Add these secrets:
- `AZURE_WEBAPP_PUBLISH_PROFILE`
- `AZURE_RESOURCE_GROUP`
- `OPENAI_API_KEY`
- `JWT_SECRET_KEY`
- `POSTGRESQL_CONNECTION_URI`
- `CHROMA_CLOUD_API_KEY`
- `CHROMA_CLOUD_TENANT_ID`
- `CHROMA_CLOUD_DATABASE_ID`

### Step 2: Get Publish Profile

```bash
# Download publish profile
az webapp deployment list-publishing-profiles --name webchatbot-app --resource-group webchatbot-rg --xml
```

Copy the XML content and add it as `AZURE_WEBAPP_PUBLISH_PROFILE` secret.

### Step 3: Enable GitHub Actions

The workflow file `.github/workflows/azure-deploy.yml` is already configured. It will automatically deploy when you push to the `main` branch.

## Post-Deployment Configuration

### 1. Configure Custom Domain (Optional)

```bash
# Add custom domain
az webapp config hostname add --webapp-name webchatbot-app --resource-group webchatbot-rg --hostname yourdomain.com
```

### 2. Enable HTTPS

```bash
# Configure SSL certificate
az webapp config ssl bind --certificate-thumbprint YOUR_CERT_THUMBPRINT --ssl-type SNI --name webchatbot-app --resource-group webchatbot-rg
```

### 3. Configure Monitoring

1. **Application Insights:**
   - Go to your web app → Application Insights
   - Click "Turn on Application Insights"
   - Create new resource or use existing

2. **Log Analytics:**
   - Go to your web app → Monitoring → Logs
   - Configure log queries for monitoring

### 4. Configure Scaling

```bash
# Configure auto-scaling
az monitor autoscale create --resource webchatbot-app --resource-group webchatbot-rg --resource-type Microsoft.Web/sites --name webchatbot-autoscale --min-count 1 --max-count 10 --count 2
```

## Troubleshooting

### Common Issues

1. **Application Won't Start:**
   - Check startup command: `python web_app.py`
   - Verify Python version: 3.11
   - Check application logs in Azure Portal

2. **Database Connection Failed:**
   - Verify PostgreSQL connection string
   - Check firewall rules
   - Ensure database server is running

3. **Environment Variables Not Loading:**
   - Check Application Settings in Azure Portal
   - Verify variable names match exactly
   - Restart the web app after changes

4. **Memory Issues:**
   - Upgrade to higher App Service Plan
   - Check application memory usage
   - Optimize code for memory efficiency

### Debug Commands

```bash
# Check web app status
az webapp show --name webchatbot-app --resource-group webchatbot-rg

# View application logs
az webapp log tail --name webchatbot-app --resource-group webchatbot-rg

# Check app settings
az webapp config appsettings list --name webchatbot-app --resource-group webchatbot-rg

# Restart web app
az webapp restart --name webchatbot-app --resource-group webchatbot-rg
```

### Log Analysis

1. **Azure Portal:**
   - Go to your web app → Monitoring → Logs
   - Use KQL queries to analyze logs

2. **Application Insights:**
   - Go to Application Insights → Logs
   - Query traces, exceptions, and dependencies

## Security Best Practices

### 1. Environment Variables
- Never commit `.env` files to version control
- Use Azure Key Vault for sensitive data
- Rotate secrets regularly

### 2. Network Security
- Configure VNet integration if needed
- Use private endpoints for databases
- Enable firewall rules

### 3. Application Security
- Enable HTTPS only
- Configure CORS properly
- Use strong JWT secrets
- Implement rate limiting

### 4. Monitoring
- Enable Application Insights
- Set up alerts for errors
- Monitor performance metrics
- Regular security scans

## Cost Optimization

### 1. App Service Plan
- Start with B1 (Basic) plan
- Scale up based on usage
- Use auto-scaling for variable loads

### 2. Database
- Use Azure Database for PostgreSQL Flexible Server
- Configure auto-pause for development
- Monitor database usage

### 3. Storage
- Use Azure Storage for file uploads
- Configure lifecycle policies
- Monitor storage costs

## Maintenance

### 1. Regular Updates
- Keep Python dependencies updated
- Monitor security advisories
- Update Azure resources regularly

### 2. Backup
- Configure automated backups
- Test restore procedures
- Document recovery processes

### 3. Monitoring
- Set up health checks
- Monitor performance metrics
- Configure alerting rules

## Support

For additional help:
- Azure Documentation: [docs.microsoft.com/azure](https://docs.microsoft.com/azure)
- Azure Support: [portal.azure.com](https://portal.azure.com)
- GitHub Issues: Create an issue in your repository
