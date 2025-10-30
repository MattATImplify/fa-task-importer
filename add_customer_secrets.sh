#!/bin/bash

# Add Customer Secrets to Azure Key Vault
# This script prompts for and stores secrets for a single customer

echo "🔐 Add Customer Secrets to Azure Key Vault"
echo "==========================================="
echo ""

# Configuration
KEY_VAULT_NAME="fa-secrets-kv"

# Get customer info
echo "Enter customer ID (e.g., regularcleaning, ags1):"
read CUSTOMER_ID

echo "Enter FacilityApps domain (e.g., regularcleaning.facilityapps.com):"
read FA_DOMAIN

echo "Enter FacilityApps API token (hidden):"
read -s FA_TOKEN

echo "Enter username for this app:"
read USERNAME

echo "Enter password for this app (hidden):"
read -s PASSWORD

echo ""
echo "📝 Adding secrets to Key Vault..."

# Add secrets
az keyvault secret set \
    --vault-name $KEY_VAULT_NAME \
    --name "$CUSTOMER_ID-fa-domain" \
    --value "$FA_DOMAIN"

az keyvault secret set \
    --vault-name $KEY_VAULT_NAME \
    --name "$CUSTOMER_ID-fa-token" \
    --value "$FA_TOKEN"

az keyvault secret set \
    --vault-name $KEY_VAULT_NAME \
    --name "$CUSTOMER_ID-username" \
    --value "$USERNAME"

az keyvault secret set \
    --vault-name $KEY_VAULT_NAME \
    --name "$CUSTOMER_ID-password" \
    --value "$PASSWORD"

echo ""
echo "✅ Secrets added successfully for customer: $CUSTOMER_ID"
echo ""
echo "Secret names:"
echo "  - $CUSTOMER_ID-fa-domain"
echo "  - $CUSTOMER_ID-fa-token"
echo "  - $CUSTOMER_ID-username"
echo "  - $CUSTOMER_ID-password"

