# Custom Domain Setup Guide
## regularcleaning.facilityapps.co.uk

This guide will help you configure your custom domain for the Azure App Service.

## Prerequisites
- Azure App Service deployed and running
- Access to your domain registrar (where facilityapps.co.uk is managed)
- Domain verification access

## Step 1: Get Domain Verification ID from Azure

### Option A: Azure Portal
1. Go to your App Service in Azure Portal
2. Navigate to **Settings** > **Custom domains**
3. Click **Add custom domain**
4. Enter: `regularcleaning.facilityapps.co.uk`
5. Azure will show you a **Domain verification ID** (looks like: `asuid.regularcleaning.facilityapps.co.uk=abc123def456`)

### Option B: Azure CLI
```bash
# Get the domain verification ID
az webapp config hostname get-external-ip \
    --resource-group fa-job-importer-rg \
    --name fa-job-importer
```

## Step 2: Configure DNS Records

You need to add **TWO** DNS records to your domain:

### Record 1: CNAME Record
- **Type**: CNAME
- **Name**: `regularcleaning` (or `regularcleaning.facilityapps.co.uk`)
- **Value**: `fa-job-importer.azurewebsites.net`
- **TTL**: 300 (5 minutes)

### Record 2: TXT Record (Domain Verification)
- **Type**: TXT
- **Name**: `asuid.regularcleaning` (or `asuid.regularcleaning.facilityapps.co.uk`)
- **Value**: `[The verification ID from Step 1]`
- **TTL**: 300 (5 minutes)

## Step 3: Add Domain in Azure Portal

1. Go to your App Service
2. Navigate to **Settings** > **Custom domains**
3. Click **Add custom domain**
4. Enter: `regularcleaning.facilityapps.co.uk`
5. Click **Validate**
6. Azure will verify the DNS records
7. Once verified, click **Add**

## Step 4: Configure SSL Certificate

### Option A: Free SSL (Let's Encrypt)
1. In **Custom domains** section
2. Click **Add binding** next to your domain
3. Select **SNI SSL**
4. Choose **Create App Service Managed Certificate**
5. Click **Add binding**

### Option B: Upload Your Own Certificate
If you have your own SSL certificate:
1. Go to **Settings** > **TLS/SSL settings**
2. Click **Private Key Certificates (.pfx)**
3. Upload your certificate
4. Bind it to your custom domain

## Step 5: Test Your Domain

1. Wait 5-10 minutes for DNS propagation
2. Visit: `https://regularcleaning.facilityapps.co.uk`
3. Verify it loads your Streamlit app
4. Check that SSL certificate is working (green lock icon)

## Common DNS Providers

### Cloudflare
1. Login to Cloudflare dashboard
2. Select your domain
3. Go to **DNS** > **Records**
4. Add the CNAME and TXT records as above

### GoDaddy
1. Login to GoDaddy
2. Go to **My Products** > **DNS**
3. Click **Manage** next to your domain
4. Add the records in **DNS Records** section

### Namecheap
1. Login to Namecheap
2. Go to **Domain List** > **Manage**
3. Click **Advanced DNS**
4. Add the records

### AWS Route 53
1. Login to AWS Console
2. Go to **Route 53** > **Hosted zones**
3. Select your domain
4. Click **Create record**
5. Add both records

## Troubleshooting

### Domain Not Verifying
- **Check DNS propagation**: Use `nslookup regularcleaning.facilityapps.co.uk`
- **Verify TXT record**: Use `dig TXT asuid.regularcleaning.facilityapps.co.uk`
- **Wait longer**: DNS can take up to 48 hours to propagate globally

### SSL Certificate Issues
- **Wait for certificate**: App Service managed certificates can take 6-8 hours
- **Check domain binding**: Ensure domain is properly bound to certificate
- **Force HTTPS**: Enable in **TLS/SSL settings**

### App Not Loading
- **Check CNAME**: Verify it points to `fa-job-importer.azurewebsites.net`
- **Check App Service**: Ensure it's running and healthy
- **Check logs**: Look at **Log stream** in Azure Portal

## Verification Commands

```bash
# Check CNAME record
nslookup regularcleaning.facilityapps.co.uk

# Check TXT record
dig TXT asuid.regularcleaning.facilityapps.co.uk

# Test HTTPS
curl -I https://regularcleaning.facilityapps.co.uk
```

## Expected Results

After successful configuration:
- ✅ `https://regularcleaning.facilityapps.co.uk` loads your app
- ✅ SSL certificate shows as valid (green lock)
- ✅ No redirect warnings
- ✅ App functions normally

## Next Steps

Once domain is working:
1. Update any hardcoded URLs in your app
2. Configure redirects from old URLs if needed
3. Set up monitoring for the custom domain
4. Consider setting up a CDN for better performance
