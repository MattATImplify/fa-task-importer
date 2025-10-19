# Azure App Service Deployment Guide

## Overview
This guide will help you deploy the FacilityApps Bulk Job Importer to Azure App Service.

## Prerequisites
- Azure subscription
- Azure CLI installed (`az --version` to check)
- Git repository (already set up)

## Step 1: Create Azure App Service

### Option A: Using Azure Portal
1. Go to [Azure Portal](https://portal.azure.com)
2. Click "Create a resource"
3. Search for "Web App"
4. Click "Create"
5. Fill in:
   - **Resource Group**: Create new (e.g., "fa-job-importer-rg")
   - **Name**: `fa-job-importer` (must be globally unique)
   - **Runtime stack**: Python 3.11
   - **Operating System**: Linux
   - **Region**: Choose closest to your users
   - **Pricing Plan**: Basic B1 (or higher for production)

### Option B: Using Azure CLI
```bash
# Login to Azure
az login

# Create resource group
az group create --name fa-job-importer-rg --location "West Europe"

# Create App Service plan
az appservice plan create --name fa-job-importer-plan --resource-group fa-job-importer-rg --sku B1 --is-linux

# Create web app
az webapp create --resource-group fa-job-importer-rg --plan fa-job-importer-plan --name fa-job-importer --runtime "PYTHON|3.11"
```

## Step 2: Configure Deployment

### Create startup command
The app will use the startup command in `startup.txt` to run Streamlit.

### Set environment variables
In Azure Portal:
1. Go to your App Service
2. Navigate to "Configuration" > "Application settings"
3. Add these settings:
   - `FA_DOMAIN`: Your FacilityApps domain
   - `FA_TOKEN`: Your API token
   - `STREAMLIT_SERVER_PORT`: `8000`
   - `STREAMLIT_SERVER_ADDRESS`: `0.0.0.0`

## Step 3: Deploy from Git

### Option A: GitHub Actions (Recommended)
1. Go to your GitHub repository
2. Add the workflow file (`.github/workflows/azure-deploy.yml`)
3. Push to trigger deployment

### Option B: Local Git
```bash
# Add Azure remote
az webapp deployment source config-local-git --name fa-job-importer --resource-group fa-job-importer-rg

# Get deployment URL
az webapp deployment source show --name fa-job-importer --resource-group fa-job-importer-rg --query url

# Add remote and push
git remote add azure <deployment-url>
git push azure main
```

## Step 4: Configure Custom Domain

1. In Azure Portal, go to your App Service
2. Navigate to "Custom domains"
3. Click "Add custom domain"
4. Enter: `regularcleaning.facilityapps.co.uk`
5. Follow DNS configuration instructions
6. Add SSL certificate (Let's Encrypt is free)

## Step 5: Configure Authentication

Since we're using username/password authentication, you'll need to set the secrets in Azure:

1. Go to "Configuration" > "Application settings"
2. Add:
   - `MASTER_USERNAME`: Your admin username
   - `MASTER_PASSWORD`: Your admin password

## Step 6: Test Deployment

1. Visit your custom domain: `https://regularcleaning.facilityapps.co.uk`
2. Test login with your credentials
3. Test the step-by-step wizard
4. Verify API connection works

## Monitoring and Maintenance

- **Logs**: Available in "Log stream" in Azure Portal
- **Metrics**: Monitor in "Metrics" section
- **Scaling**: Adjust in "Scale out" section
- **Backups**: Configure in "Backup" section

## Cost Optimization

- **Development**: Use Basic B1 plan (~$13/month)
- **Production**: Use Standard S1 plan (~$75/month)
- **High Traffic**: Use Premium P1V2 plan (~$166/month)

## Security Considerations

1. **HTTPS Only**: Enable in "TLS/SSL settings"
2. **Authentication**: Already implemented in app
3. **Secrets**: Store in Azure Key Vault for production
4. **Network**: Consider VNet integration for enterprise

## Troubleshooting

### Common Issues:
1. **App won't start**: Check startup command and logs
2. **Import errors**: Verify all dependencies in requirements.txt
3. **Authentication fails**: Check environment variables
4. **API connection fails**: Verify FA_DOMAIN and FA_TOKEN

### Useful Commands:
```bash
# View logs
az webapp log tail --name fa-job-importer --resource-group fa-job-importer-rg

# Restart app
az webapp restart --name fa-job-importer --resource-group fa-job-importer-rg

# Check status
az webapp show --name fa-job-importer --resource-group fa-job-importer-rg --query state
```
