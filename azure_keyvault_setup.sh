#!/bin/bash

# Azure Key Vault Setup Script
# This script creates a Key Vault and stores secrets for multiple customers

echo "🔐 Setting up Azure Key Vault for multi-customer deployment..."

# Configuration
RESOURCE_GROUP="fa-customers-rg"
KEY_VAULT_NAME="fa-secrets-kv"  # Must be globally unique, 3-24 alphanumeric
LOCATION="West Europe"

# Check if logged in
if ! az account show &> /dev/null; then
    echo "❌ Not logged in to Azure. Please run: az login"
    exit 1
fi

echo "📦 Creating resource group..."
az group create --name $RESOURCE_GROUP --location "$LOCATION"

echo "🔐 Creating Key Vault..."
az keyvault create \
    --name $KEY_VAULT_NAME \
    --resource-group $RESOURCE_GROUP \
    --location "$LOCATION" \
    --sku standard

echo "✅ Key Vault created: $KEY_VAULT_NAME"
echo ""
echo "Now you can add secrets for each customer:"
echo ""
echo "Example for Customer 1 (regularcleaning):"
echo "  az keyvault secret set --vault-name $KEY_VAULT_NAME \\"
echo "    --name regularcleaning-fa-domain \\"
echo "    --value regularcleaning.facilityapps.com"
echo ""
echo "  az keyvault secret set --vault-name $KEY_VAULT_NAME \\"
echo "    --name regularcleaning-fa-token \\"
echo "    --value their-api-token-here"
echo ""
echo "  az keyvault secret set --vault-name $KEY_VAULT_NAME \\"
echo "    --name regularcleaning-username \\"
echo "    --value admin"
echo ""
echo "  az keyvault secret set --vault-name $KEY_VAULT_NAME \\"
echo "    --name regularcleaning-password \\"
echo "    --value secure-password-here"
echo ""
echo "🔑 To retrieve secrets, reference them in App Service with '@Microsoft.KeyVault(...)'"
echo "   Example: FA_TOKEN=@Microsoft.KeyVault(SecretUri=https://$KEY_VAULT_NAME.vault.azure.net/secrets/regularcleaning-fa-token/)"

