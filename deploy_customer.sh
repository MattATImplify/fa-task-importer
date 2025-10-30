#!/bin/bash

# Generic deployment script for any customer

echo "🚀 Deploying FA Task Importer for customer..."

# Check if Azure CLI is installed
if ! command -v az &> /dev/null; then
    echo "❌ Azure CLI not found. Please install it first."
    exit 1
fi

# Check if logged in
if ! az account show &> /dev/null; then
    echo "❌ Not logged in to Azure. Please run: az login"
    exit 1
fi

# Get customer info
echo "Enter customer name (e.g., regularcleaning, ags1):"
read CUSTOMER_NAME

echo "Enter FacilityApps domain (e.g., regularcleaning.facilityapps.com):"
read FA_DOMAIN

echo "Enter FacilityApps API token (hidden):"
read -s FA_TOKEN

echo "Enter admin username for this app:"
read MASTER_USERNAME

echo "Enter admin password for this app (hidden):"
read -s MASTER_PASSWORD

# Generate resource names
RESOURCE_GROUP="fa-${CUSTOMER_NAME}-rg"
APP_NAME="${CUSTOMER_NAME}FAadmin"
PLAN_NAME="${CUSTOMER_NAME}-plan"
LOCATION="West Europe"

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
az webapp config appsettings set \
    --resource-group $RESOURCE_GROUP \
    --name $APP_NAME \
    --settings \
        STREAMLIT_SERVER_PORT=8000 \
        STREAMLIT_SERVER_ADDRESS=0.0.0.0 \
        CUSTOMER_ID=$CUSTOMER_NAME \
        FA_DOMAIN=$FA_DOMAIN \
        FA_TOKEN="$FA_TOKEN" \
        MASTER_USERNAME="$MASTER_USERNAME" \
        MASTER_PASSWORD="$MASTER_PASSWORD"

echo "🔧 Setting startup command..."
az webapp config set \
    --resource-group $RESOURCE_GROUP \
    --name $APP_NAME \
    --startup-file "startup.txt"

echo "✅ Deployment configuration complete!"
echo "🌐 Your app will be available at: https://${APP_NAME}.azurewebsites.net"
echo ""
echo "Next: Deploy code with: az webapp deploy --resource-group $RESOURCE_GROUP --name $APP_NAME --src-path deployment.zip --type zip"

