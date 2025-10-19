#!/bin/bash

# Get Domain Verification Information for Azure App Service
# Run this after your App Service is deployed

echo "🔍 Getting domain verification information..."

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

# Variables
RESOURCE_GROUP="fa-job-importer-rg"
APP_NAME="fa-job-importer"
DOMAIN="regularcleaning.facilityapps.co.uk"

echo "📋 App Service Details:"
echo "Resource Group: $RESOURCE_GROUP"
echo "App Name: $APP_NAME"
echo "Custom Domain: $DOMAIN"
echo ""

echo "🌐 Getting external IP address..."
EXTERNAL_IP=$(az webapp config hostname get-external-ip \
    --resource-group $RESOURCE_GROUP \
    --name $APP_NAME \
    --query externalIp -o tsv 2>/dev/null)

if [ $? -eq 0 ] && [ ! -z "$EXTERNAL_IP" ]; then
    echo "External IP: $EXTERNAL_IP"
else
    echo "⚠️ Could not get external IP. You may need to add the domain manually in Azure Portal."
fi

echo ""
echo "📝 DNS Records to Add:"
echo ""
echo "1. CNAME Record:"
echo "   Type: CNAME"
echo "   Name: regularcleaning"
echo "   Value: $APP_NAME.azurewebsites.net"
echo "   TTL: 300"
echo ""
echo "2. TXT Record (Domain Verification):"
echo "   Type: TXT"
echo "   Name: asuid.regularcleaning"
echo "   Value: [Get this from Azure Portal when adding the domain]"
echo ""

echo "🔧 Next Steps:"
echo "1. Go to Azure Portal > Your App Service > Custom domains"
echo "2. Click 'Add custom domain'"
echo "3. Enter: $DOMAIN"
echo "4. Azure will show you the exact TXT record value"
echo "5. Add both DNS records to your domain registrar"
echo "6. Wait for verification and add SSL certificate"
echo ""
echo "📖 Full guide: custom_domain_setup.md"
