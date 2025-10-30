# Multi-Customer Deployment Guide

This guide explains how to deploy the FacilityApps Job Importer to multiple customers in a scalable way.

## Architecture Overview

For **100 customers**, we use:
1. **Azure Key Vault** - Secure storage for all API keys, tokens, and passwords
2. **Separate App Service per customer** - Complete isolation and independent scaling
3. **CSV-based customer configuration** - Easy to manage customer list
4. **Automated scripts** - Deploy and manage customers at scale

## Why This Approach?

✅ **Security**: Secrets stored in Azure Key Vault, never in code or files  
✅ **Isolation**: Each customer has their own App Service instance  
✅ **Scalability**: Can deploy 100+ customers easily  
✅ **Maintenance**: Update one script to affect all customers  
✅ **Cost Control**: Only pay for resources actually used  

## Setup Steps

### 1. Initial Setup (One-Time)

```bash
# Step 1: Create Key Vault
./azure_keyvault_setup.sh

# This creates:
# - Resource Group: fa-customers-rg
# - Key Vault: fa-secrets-kv (you'll need to make this globally unique)
```

### 2. Add Customer Secrets

For each customer, add their secrets to Key Vault:

```bash
# Run this for each customer
./add_customer_secrets.sh

# It will prompt for:
# - Customer ID (e.g., "regularcleaning")
# - FA Domain
# - FA API Token
# - Username
# - Password
```

**Alternative**: Bulk add via CSV

Create a file `secrets.csv`:
```csv
customer_id,fa_domain,fa_token,username,password
regularcleaning,regularcleaning.facilityapps.com,token123,admin,pass123
ags1,ags1.facilityapps.com,token456,admin,pass456
```

Then import:
```bash
# (Custom script to be created)
./bulk_import_secrets.sh secrets.csv
```

### 3. Deploy Customers

```bash
# Edit customers.csv with your customer list
nano customers.csv

# Deploy all customers
./deploy_multiple_customers.sh
```

The script will:
- Create App Service for each customer
- Configure Key Vault references
- Set up managed identity
- Grant necessary permissions

### 4. Deploy Application Code

Each App Service needs your application code. You can:

**Option A: Git Deployment**
```bash
# Deploy to all apps via Git
for app in $(az webapp list --resource-group fa-customers-rg --query "[].name" -o tsv); do
    az webapp deployment source config-local-git --name $app --resource-group fa-customers-rg
    git remote add $app https://$USERNAME@$app.scm.azurewebsites.net/$app.git
    git push $app main
done
```

**Option B: CI/CD Pipeline**
Use Azure DevOps or GitHub Actions to automatically deploy to all customers.

**Option C: Container Registry**
Package as Docker image and deploy to all apps.

## Managing 100 Customers

### Adding a New Customer

1. **Add secrets**:
   ```bash
   ./add_customer_secrets.sh
   ```

2. **Add to CSV**:
   ```bash
   echo "customer_id,name,fa_domain,app_name" >> customers.csv
   ```

3. **Deploy**:
   ```bash
   az webapp create \
       --resource-group fa-customers-rg \
       --plan fa-customers-plan \
       --name newcustomerFA \
       --runtime "PYTHON|3.11"
   
   # Configure with Key Vault references (see deploy_multiple_customers.sh)
   ```

### Updating Secrets

```bash
# Update a specific customer's secret
az keyvault secret set \
    --vault-name fa-secrets-kv \
    --name "regularcleaning-fa-token" \
    --value "new-token-value"

# No need to restart app - Key Vault changes are picked up automatically
```

### Deploying Code Updates

Deploy to all customers at once:
```bash
# Using Git
for app in $(az webapp list --resource-group fa-customers-rg --query "[].name" -o tsv); do
    git push $app main
done

# Or use CI/CD to deploy to all automatically
```

### Monitoring

```bash
# View all app URLs
az webapp list --resource-group fa-customers-rg --query "[].{Name:name,URL:defaultHostName}" -o table

# Check status of all apps
az webapp list --resource-group fa-customers-rg --query "[].{Name:name,State:state}" -o table

# View logs for a specific customer
az webapp log tail --name customerFA --resource-group fa-customers-rg
```

## Cost Estimation

For **100 customers** on Basic B1 plan:

- **App Service Plan** (shared): ~£50/month
- **App Services** (100 x £0): £0 (included in plan)
- **Key Vault**: ~£5/month
- **Storage**: Minimal
- **Bandwidth**: Pay as you go

**Total**: ~£55/month for 100 customers

For higher traffic customers, scale to higher tier:
- **Standard S1**: ~£75/month per customer
- **Premium**: ~£166/month per customer

## Security Best Practices

1. **Never store secrets in code** ✅ Using Key Vault
2. **Use managed identity** ✅ Configured in scripts
3. **Least privilege access** ✅ Each app only accesses its own secrets
4. **Enable HTTPS only** ✅ Configured automatically
5. **Regular secret rotation** ✅ Easy via Key Vault
6. **Audit logs** ✅ Key Vault provides audit trail

## Troubleshooting

### Secret Not Found
```bash
# Verify secret exists
az keyvault secret show --vault-name fa-secrets-kv --name "regularcleaning-fa-token"

# Check app has Key Vault access
az webapp identity show --name customerFA --resource-group fa-customers-rg
```

### App Won't Start
```bash
# Check logs
az webapp log tail --name customerFA --resource-group fa-customers-rg

# Check app settings
az webapp config appsettings list --name customerFA --resource-group fa-customers-rg
```

### Can't Access Key Vault
```bash
# Grant permissions
PRINCIPAL_ID=$(az webapp identity show --name customerFA --resource-group fa-customers-rg --query principalId -o tsv)
az keyvault set-policy --name fa-secrets-kv --object-id $PRINCIPAL_ID --secret-permissions get list
```

## Alternative: Single App, Database Configuration

If you prefer a single app instance with database-backed configuration:

```python
# app.py - Multi-tenant with database
import os
import psycopg2

def get_customer_config(customer_id):
    conn = psycopg2.connect(os.getenv("DATABASE_URL"))
    cur = conn.cursor()
    cur.execute("SELECT fa_domain, fa_token, username, password FROM customers WHERE customer_id = %s", (customer_id,))
    return cur.fetchone()
```

Benefits:
- Lower cost (1 app vs 100 apps)
- Easier to update (single deployment)
- Shared infrastructure

Trade-offs:
- Less isolation
- More complex code
- Potential single point of failure

## Summary

**Recommended Approach**: Separate App Services + Key Vault

**Why**:
- Most secure
- Best isolation
- Easiest to manage at scale
- Flexible pricing
- Industry best practice

**Deployment Time**:
- Initial setup: 30 minutes
- Each new customer: 2 minutes
- Deploy to 100 customers: 1 hour (automated)

