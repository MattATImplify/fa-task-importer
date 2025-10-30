#!/bin/bash

# Bulk Customer Deployment Script
# Deploys separate Azure App Services for each customer

echo "🚀 Bulk Customer Deployment Script"
echo "=================================="
echo ""

# Configuration
KEY_VAULT_NAME="fa-secrets-kv"  # Your Key Vault name
LOCATION="West Europe"
PLAN_NAME="fa-customers-plan"

# Customer configuration file
CUSTOMERS_FILE="customers.csv"

# Check if customers file exists
if [ ! -f "$CUSTOMERS_FILE" ]; then
    echo "📝 Creating sample customers.csv file..."
    cat > "$CUSTOMERS_FILE" << EOF
customer_id,customer_name,fa_domain,app_name
regularcleaning,Regular Cleaning,regularcleaning.facilityapps.com,regularcleaningFA
ags1,AGS1 Customer,ags1.facilityapps.com,ags1FA
officeclean,Office Clean,officeclean.facilityapps.com,officecleanFA
EOF
    echo "✅ Created $CUSTOMERS_FILE"
    echo ""
    echo "Please edit this file with your actual customer data, then run this script again."
    exit 0
fi

# Create resource group
RESOURCE_GROUP="fa-customers-rg"
if ! az group show --name $RESOURCE_GROUP &> /dev/null; then
    echo "📦 Creating resource group..."
    az group create --name $RESOURCE_GROUP --location "$LOCATION"
fi

# Create App Service Plan (shared across all customers)
if ! az appservice plan show --name $PLAN_NAME --resource-group $RESOURCE_GROUP &> /dev/null; then
    echo "🏗️ Creating App Service plan..."
    az appservice plan create \
        --name $PLAN_NAME \
        --resource-group $RESOURCE_GROUP \
        --sku B1 \
        --is-linux
fi

# Read customers file and deploy
echo "📋 Reading customers from $CUSTOMERS_FILE..."
tail -n +2 "$CUSTOMERS_FILE" | while IFS=',' read -r customer_id customer_name fa_domain app_name; do
    echo ""
    echo "🔄 Processing: $customer_id ($customer_name)"
    
    # Create web app if it doesn't exist
    if ! az webapp show --name $app_name --resource-group $RESOURCE_GROUP &> /dev/null; then
        echo "  Creating web app: $app_name"
        az webapp create \
            --resource-group $RESOURCE_GROUP \
            --plan $PLAN_NAME \
            --name $app_name \
            --runtime "PYTHON|3.11"
    fi
    
    # Configure app settings with Key Vault references
    echo "  Configuring app settings..."
    az webapp config appsettings set \
        --resource-group $RESOURCE_GROUP \
        --name $app_name \
        --settings \
            STREAMLIT_SERVER_PORT=8000 \
            STREAMLIT_SERVER_ADDRESS=0.0.0.0 \
            CUSTOMER_ID=$customer_id \
            FA_DOMAIN="@Microsoft.KeyVault(SecretUri=https://$KEY_VAULT_NAME.vault.azure.net/secrets/$customer_id-fa-domain/)" \
            FA_TOKEN="@Microsoft.KeyVault(SecretUri=https://$KEY_VAULT_NAME.vault.azure.net/secrets/$customer_id-fa-token/)" \
            MASTER_USERNAME="@Microsoft.KeyVault(SecretUri=https://$KEY_VAULT_NAME.vault.azure.net/secrets/$customer_id-username/)" \
            MASTER_PASSWORD="@Microsoft.KeyVault(SecretUri=https://$KEY_VAULT_NAME.vault.azure.net/secrets/$customer_id-password/)"
    
    # Set startup command
    az webapp config set \
        --resource-group $RESOURCE_GROUP \
        --name $app_name \
        --startup-file "gunicorn -w 1 -k uvicorn.workers.UvicornWorker app:app --bind 0.0.0.0:8000"
    
    # Configure managed identity (required for Key Vault access)
    echo "  Configuring managed identity..."
    PRINCIPAL_ID=$(az webapp identity assign \
        --resource-group $RESOURCE_GROUP \
        --name $app_name \
        --query principalId -o tsv)
    
    # Grant Key Vault access to the app
    az keyvault set-policy \
        --name $KEY_VAULT_NAME \
        --object-id $PRINCIPAL_ID \
        --secret-permissions get list
    
    echo "  ✅ Deployed: https://$app_name.azurewebsites.net"
done

echo ""
echo "🎉 Deployment complete!"
echo ""
echo "📝 Next steps:"
echo "1. Add secrets to Key Vault for each customer"
echo "2. Deploy code to each App Service (git push or CI/CD)"
echo "3. Configure custom domains if needed"

