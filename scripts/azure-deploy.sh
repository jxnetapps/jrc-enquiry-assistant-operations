#!/bin/bash
# Azure App Service Deployment Script for Linux/Mac
# Run this script with: ./azure-deploy.sh

set -e

# Default values
RESOURCE_GROUP_NAME=""
WEBAPP_NAME=""
LOCATION="East US"
APP_SERVICE_PLAN="B1"

# Function to display usage
usage() {
    echo "Usage: $0 -g <resource-group> -w <webapp-name> [-l <location>] [-p <app-service-plan>]"
    echo "  -g: Resource group name (required)"
    echo "  -w: Web app name (required)"
    echo "  -l: Location (default: East US)"
    echo "  -p: App service plan (default: B1)"
    exit 1
}

# Parse command line arguments
while getopts "g:w:l:p:h" opt; do
    case $opt in
        g) RESOURCE_GROUP_NAME="$OPTARG" ;;
        w) WEBAPP_NAME="$OPTARG" ;;
        l) LOCATION="$OPTARG" ;;
        p) APP_SERVICE_PLAN="$OPTARG" ;;
        h) usage ;;
        *) usage ;;
    esac
done

# Check required parameters
if [ -z "$RESOURCE_GROUP_NAME" ] || [ -z "$WEBAPP_NAME" ]; then
    echo "Error: Resource group name and web app name are required"
    usage
fi

echo "Starting Azure App Service deployment..."
echo "Resource Group: $RESOURCE_GROUP_NAME"
echo "Web App Name: $WEBAPP_NAME"
echo "Location: $LOCATION"
echo "App Service Plan: $APP_SERVICE_PLAN"

# Check if Azure CLI is installed
if ! command -v az &> /dev/null; then
    echo "Azure CLI not found. Installing..."
    curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
fi

# Login to Azure
echo "Logging in to Azure..."
az login

# Create resource group if it doesn't exist
echo "Creating resource group: $RESOURCE_GROUP_NAME"
az group create --name $RESOURCE_GROUP_NAME --location "$LOCATION"

# Create App Service plan if it doesn't exist
echo "Creating App Service plan: $APP_SERVICE_PLAN"
az appservice plan create --name "$WEBAPP_NAME-plan" --resource-group $RESOURCE_GROUP_NAME --sku $APP_SERVICE_PLAN --is-linux

# Create web app
echo "Creating web app: $WEBAPP_NAME"
az webapp create --resource-group $RESOURCE_GROUP_NAME --plan "$WEBAPP_NAME-plan" --name $WEBAPP_NAME --runtime "PYTHON|3.11"

# Configure app settings
echo "Configuring app settings..."
az webapp config appsettings set --resource-group $RESOURCE_GROUP_NAME --name $WEBAPP_NAME --settings \
    ENVIRONMENT=production \
    DEBUG=false \
    WEBSITES_PORT=8000 \
    SCM_DO_BUILD_DURING_DEPLOYMENT=true \
    WEBSITES_ENABLE_APP_SERVICE_STORAGE=true

# Configure startup command
echo "Configuring startup command..."
az webapp config set --resource-group $RESOURCE_GROUP_NAME --name $WEBAPP_NAME --startup-file "python web_app.py"

# Deploy application
echo "Deploying application..."
az webapp deployment source config-zip --resource-group $RESOURCE_GROUP_NAME --name $WEBAPP_NAME --src "webchatbot.zip"

# Run database migrations
echo "Running database migrations..."
az webapp ssh --resource-group $RESOURCE_GROUP_NAME --name $WEBAPP_NAME --command "cd /home/site/wwwroot && python scripts/migrate.py migrate"

echo "Deployment completed successfully!"
echo "Web app URL: https://$WEBAPP_NAME.azurewebsites.net"
