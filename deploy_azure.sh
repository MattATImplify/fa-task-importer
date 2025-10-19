#!/bin/bash

# Azure App Service Deployment Script
# Make sure you're logged in to Azure CLI: az login

echo "🚀 Deploying FacilityApps Job Importer to Azure..."

# Check if Azure CLI is installed
if ! command -v az &> /dev/null; then
    echo "❌ Azure CLI not found. Please install it first: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli"
    exit 1
fi

# Check if logged in
if ! az account show &> /dev/null; then
    echo "❌ Not logged in to Azure. Please run: az login"
    exit 1
fi

# Variables (update these)
RESOURCE_GROUP="fa-job-importer-rg"
APP_NAME="fa-job-importer"
LOCATION="West Europe"

echo "📦 Creating resource group..."
az group create --name $RESOURCE_GROUP --location "$LOCATION"

echo "🏗️ Creating App Service plan..."
az appservice plan create \
    --name "${APP_NAME}-plan" \
    --resource-group $RESOURCE_GROUP \
    --sku B1 \
    --is-linux

echo "🌐 Creating web app..."
az webapp create \
    --resource-group $RESOURCE_GROUP \
    --plan "${APP_NAME}-plan" \
    --name $APP_NAME \
    --runtime "PYTHON|3.11"

echo "⚙️ Configuring app settings..."
az webapp config appsettings set \
    --resource-group $RESOURCE_GROUP \
    --name $APP_NAME \
    --settings \
        STREAMLIT_SERVER_PORT=8000 \
        STREAMLIT_SERVER_ADDRESS=0.0.0.0

echo "🔧 Setting startup command..."
az webapp config set \
    --resource-group $RESOURCE_GROUP \
    --name $APP_NAME \
    --startup-file "startup.txt"

echo "📝 Setting up deployment source..."
az webapp deployment source config-local-git \
    --resource-group $RESOURCE_GROUP \
    --name $APP_NAME

echo "🔑 Getting deployment URL..."
DEPLOYMENT_URL=$(az webapp deployment source show \
    --resource-group $RESOURCE_GROUP \
    --name $APP_NAME \
    --query url -o tsv)

echo "📤 Adding Azure remote..."
git remote add azure $DEPLOYMENT_URL

echo "🚀 Deploying to Azure..."
git push azure main

echo "✅ Deployment complete!"
echo "🌐 Your app will be available at: https://$APP_NAME.azurewebsites.net"
echo ""
echo "📋 Next steps:"
echo "1. Configure your custom domain: regularcleaning.facilityapps.co.uk"
echo "2. Set environment variables in Azure Portal:"
echo "   - FA_DOMAIN: Your FacilityApps domain"
echo "   - FA_TOKEN: Your API token"
echo "   - MASTER_USERNAME: Admin username"
echo "   - MASTER_PASSWORD: Admin password"
echo "3. Enable HTTPS and configure SSL certificate"
