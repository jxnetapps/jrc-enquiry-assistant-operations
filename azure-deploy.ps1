# Azure App Service Deployment Script for Windows
# Run this script from PowerShell with: .\azure-deploy.ps1

param(
    [Parameter(Mandatory=$true)]
    [string]$ResourceGroupName,
    
    [Parameter(Mandatory=$true)]
    [string]$WebAppName,
    
    [Parameter(Mandatory=$false)]
    [string]$Location = "East US",
    
    [Parameter(Mandatory=$false)]
    [string]$AppServicePlan = "B1"
)

Write-Host "Starting Azure App Service deployment..." -ForegroundColor Green

# Check if Azure CLI is installed
if (-not (Get-Command az -ErrorAction SilentlyContinue)) {
    Write-Host "Azure CLI not found. Please install it first." -ForegroundColor Red
    Write-Host "Download from: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli" -ForegroundColor Yellow
    exit 1
}

# Login to Azure
Write-Host "Logging in to Azure..." -ForegroundColor Yellow
az login

# Create resource group if it doesn't exist
Write-Host "Creating resource group: $ResourceGroupName" -ForegroundColor Yellow
az group create --name $ResourceGroupName --location $Location

# Create App Service plan if it doesn't exist
Write-Host "Creating App Service plan: $AppServicePlan" -ForegroundColor Yellow
az appservice plan create --name "$WebAppName-plan" --resource-group $ResourceGroupName --sku $AppServicePlan --is-linux

# Create web app
Write-Host "Creating web app: $WebAppName" -ForegroundColor Yellow
az webapp create --resource-group $ResourceGroupName --plan "$WebAppName-plan" --name $WebAppName --runtime "PYTHON|3.11"

# Configure app settings
Write-Host "Configuring app settings..." -ForegroundColor Yellow
az webapp config appsettings set --resource-group $ResourceGroupName --name $WebAppName --settings \
    ENVIRONMENT=production \
    DEBUG=false \
    WEBSITES_PORT=8000 \
    SCM_DO_BUILD_DURING_DEPLOYMENT=true \
    WEBSITES_ENABLE_APP_SERVICE_STORAGE=true

# Configure startup command
Write-Host "Configuring startup command..." -ForegroundColor Yellow
az webapp config set --resource-group $ResourceGroupName --name $WebAppName --startup-file "python web_app.py"

# Deploy application
Write-Host "Deploying application..." -ForegroundColor Yellow
az webapp deployment source config-zip --resource-group $ResourceGroupName --name $WebAppName --src "webchatbot.zip"

# Run database migrations
Write-Host "Running database migrations..." -ForegroundColor Yellow
az webapp ssh --resource-group $ResourceGroupName --name $WebAppName --command "cd /home/site/wwwroot && python scripts/migrate.py migrate"

Write-Host "Deployment completed successfully!" -ForegroundColor Green
Write-Host "Web app URL: https://$WebAppName.azurewebsites.net" -ForegroundColor Cyan
