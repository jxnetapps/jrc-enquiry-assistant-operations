#!/bin/bash
# Azure App Service deployment script

set -e

echo "Starting Azure App Service deployment..."

# Check if required environment variables are set
if [ -z "$AZURE_WEBAPP_NAME" ]; then
    echo "Error: AZURE_WEBAPP_NAME environment variable is not set"
    exit 1
fi

if [ -z "$AZURE_WEBAPP_PACKAGE_PATH" ]; then
    echo "Error: AZURE_WEBAPP_PACKAGE_PATH environment variable is not set"
    exit 1
fi

# Install Azure CLI if not present
if ! command -v az &> /dev/null; then
    echo "Installing Azure CLI..."
    curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
fi

# Login to Azure (if not already logged in)
echo "Logging in to Azure..."
az login --service-principal --username $AZURE_CLIENT_ID --password $AZURE_CLIENT_SECRET --tenant $AZURE_TENANT_ID

# Deploy to Azure App Service
echo "Deploying to Azure App Service: $AZURE_WEBAPP_NAME"
az webapp deployment source config-zip \
    --resource-group $AZURE_RESOURCE_GROUP \
    --name $AZURE_WEBAPP_NAME \
    --src $AZURE_WEBAPP_PACKAGE_PATH

echo "Deployment completed successfully!"
