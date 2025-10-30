#!/bin/bash

# Deploy Regular Cleaning FA Admin to Azure

echo "🚀 Deploying Regular Cleaning FA Admin to Azure..."

# Variables
RESOURCE_GROUP="fa-regular-cleaning-rg"
APP_NAME="regularcleaningFAadmin"
PLAN_NAME="regularcleaning-plan"
LOCATION="West Europe"

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

echo "📦 Creating resource group..."
az group create --name $RESOURCE_GROUP --location "$LOCATION"

echo "🏗️ Creating App Service plan..."
az appservice plan create \
    --name $PLAN_NAME \
    --resource-group $RESOURCE_GROUP \
    --sku B1 \
    --is-linux

echo "🌐 Creating web app..."
az webapp create \
    --resource-group $RESOURCE_GROUP \
    --plan $PLAN_NAME \
    --name $APP_NAME \
    --runtime "PYTHON|3.11"

echo "⚙️ Configuring app settings..."
echo "Please enter the FacilityApps API token for Regular Cleaning:"
read -s FA_TOKEN

az webapp config appsettings set \
    --resource-group $RESOURCE_GROUP \
    --name $APP_NAME \
    --settings \
        STREAMLIT_SERVER_PORT=8000 \
        STREAMLIT_SERVER_ADDRESS=0.0.0.0 \
        CUSTOMER_ID=regularcleaning \
        FA_DOMAIN=regularcleaning.facilityapps.com \
        FA_TOKEN="$FA_TOKEN"

echo "🔧 Setting startup command..."
az webapp config set \
    --resource-group $RESOURCE_GROUP \
    --name $APP_NAME \
    --startup-file "startup.txt"

echo "📝 Setting up GitHub deployment..."
az webapp deployment source config \
    --resource-group $RESOURCE_GROUP \
    --name $APP_NAME \
    --repo-url "https://github.com/MattATImplify/fa-task-importer" \
    --branch main \
    --manual-integration

echo "✅ Deployment configuration complete!"
echo "🌐 Your app will be available at: https://${APP_NAME}.azurewebsites.net"
echo ""
echo "Next steps:"
echo "1. Configure app settings in Azure Portal (API tokens, etc.)"
echo "2. Set up custom domain if needed"
echo "3. Configure SSL certificate"

