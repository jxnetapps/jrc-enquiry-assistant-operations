# Manual Deployment Script for Azure App Service
# Run this script locally to deploy directly to Azure

param(
    [string]$ResourceGroup = "jrc_grp",
    [string]$AppName = "jrc-enquiry-assistant-operations"
)

Write-Host "Starting manual deployment to Azure App Service..." -ForegroundColor Green
Write-Host "Resource Group: $ResourceGroup" -ForegroundColor Yellow
Write-Host "App Name: $AppName" -ForegroundColor Yellow

# Check if Azure CLI is installed
if (!(Get-Command az -ErrorAction SilentlyContinue)) {
    Write-Host "Azure CLI is not installed. Please install it first." -ForegroundColor Red
    exit 1
}

# Login to Azure (if not already logged in)
Write-Host "Checking Azure login status..." -ForegroundColor Blue
$loginStatus = az account show 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Please login to Azure first: az login" -ForegroundColor Red
    exit 1
}

# Stop the app service
Write-Host "Stopping app service..." -ForegroundColor Blue
az webapp stop --resource-group $ResourceGroup --name $AppName
Start-Sleep -Seconds 10

# Configure app settings
Write-Host "Configuring app settings..." -ForegroundColor Blue
az webapp config appsettings set --resource-group $ResourceGroup --name $AppName --settings `
    WEBSITES_ENABLE_APP_SERVICE_STORAGE=true `
    WEBSITES_PORT=8000 `
    ENVIRONMENT=production `
    DEBUG=false `
    PYTHONUNBUFFERED=1 `
    PYTHONDONTWRITEBYTECODE=1 `
    SCM_DO_BUILD_DURING_DEPLOYMENT=true

# Set startup command
Write-Host "Setting startup command..." -ForegroundColor Blue
az webapp config set --resource-group $ResourceGroup --name $AppName --startup-file "bash startup.sh"

# Set Python version
Write-Host "Setting Python version..." -ForegroundColor Blue
az webapp config set --resource-group $ResourceGroup --name $AppName --linux-fx-version "PYTHON|3.13"

# Create deployment package
Write-Host "Creating deployment package..." -ForegroundColor Blue
if (Test-Path "app.zip") {
    Remove-Item "app.zip"
}
Compress-Archive -Path "*.py", "*.txt", "*.sh", "*.json", "api", "auth", "chatbot", "chroma_db", "config-templates", "crawler", "database", "embedding", "models", "scripts", "utils", "web_app.py", "main.py", "config.py", "requirements.txt", "startup.sh" -DestinationPath "app.zip" -Force

# Deploy using zip
Write-Host "Deploying using zip..." -ForegroundColor Blue
az webapp deployment source config-zip --resource-group $ResourceGroup --name $AppName --src "app.zip"

# Start the app service
Write-Host "Starting app service..." -ForegroundColor Blue
az webapp start --resource-group $ResourceGroup --name $AppName
Start-Sleep -Seconds 15

# Verify deployment
Write-Host "Verifying deployment..." -ForegroundColor Blue
az webapp show --resource-group $ResourceGroup --name $AppName --query "{name:name, state:state, defaultHostName:defaultHostName}" --output table

Write-Host "Deployment completed successfully!" -ForegroundColor Green
Write-Host "App URL: https://$AppName.azurewebsites.net" -ForegroundColor Cyan
