# 🚀 Deployment Guide for regularcleaning.facilityapps.co.uk

## Prerequisites
- GitHub account
- Streamlit Cloud account (free)
- Domain access for regularcleaning.facilityapps.co.uk

## Step 1: Prepare for Deployment

### 1.1 Update Secrets
Edit `.streamlit/secrets.toml` with your production values:
```toml
[auth]
password = "your-secure-password-here"

[production]
FA_DOMAIN = "regularcleaning.facilityapps.com"
FA_TOKEN = "your-production-api-token"
```

### 1.2 Test Locally
```bash
# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run locally
streamlit run app.py
```

## Step 2: Deploy to Streamlit Cloud

### 2.1 Push to GitHub
```bash
# Initialize git (if not already done)
git init
git add .
git commit -m "Production ready with authentication"

# Create GitHub repository
# Push to GitHub
git remote add origin https://github.com/yourusername/fa-task-importer.git
git push -u origin main
```

### 2.2 Deploy on Streamlit Cloud
1. Go to https://share.streamlit.io
2. Click "New app"
3. Connect your GitHub repository
4. Set app URL to: `fa-task-importer`
5. Add secrets in the Streamlit Cloud dashboard:
   - `auth.password`: Your secure password
   - `production.FA_DOMAIN`: regularcleaning.facilityapps.com
   - `production.FA_TOKEN`: Your API token

## Step 3: Custom Domain Setup

### 3.1 DNS Configuration
Add CNAME record to your DNS:
```
CNAME    regularcleaning    your-app-name.streamlit.app
```

### 3.2 Streamlit Cloud Configuration
1. Go to your app settings
2. Enable "Custom domain"
3. Enter: `regularcleaning.facilityapps.co.uk`
4. Follow SSL certificate setup

## Step 4: Security Hardening

### 4.1 Environment Variables
Set these in Streamlit Cloud secrets:
- `auth.password`: Strong password
- `production.FA_DOMAIN`: Your FA domain
- `production.FA_TOKEN`: Your API token

### 4.2 Additional Security
- Enable HTTPS only
- Set up monitoring
- Regular password rotation

## Step 5: Testing

### 5.1 Test Authentication
1. Visit https://regularcleaning.facilityapps.co.uk
2. Enter password
3. Verify access to main app

### 5.2 Test Functionality
1. Load reference data
2. Upload test CSV
3. Test recurrence builder
4. Verify import functionality

## Troubleshooting

### Common Issues
- **Authentication fails**: Check password in secrets
- **API errors**: Verify FA_DOMAIN and FA_TOKEN
- **Domain not working**: Check DNS propagation (up to 24 hours)

### Support
- Streamlit Cloud docs: https://docs.streamlit.io/streamlit-community-cloud
- Custom domains: https://docs.streamlit.io/streamlit-community-cloud/deploy-your-app/custom-domain
