# Multi-Tenant Deployment Guide
## FacilityApps Job Importer for Multiple Customers

## Overview
This guide covers deploying a multi-tenant version where multiple customers can use the same app with their own subdomains.

## Architecture

### URL Structure
- **Main App**: `facilityapps.co.uk` (admin panel)
- **Customer Apps**: `{customer}.facilityapps.co.uk`
- **Examples**:
  - `regularcleaning.facilityapps.co.uk`
  - `officeclean.facilityapps.co.uk`
  - `hospital.facilityapps.co.uk`

### Components
1. **Multi-tenant App** (`app_multi_tenant.py`) - Customer-facing app
2. **Admin Panel** (`admin_panel.py`) - Customer management
3. **Customer Database** - Store customer configurations
4. **Wildcard SSL** - `*.facilityapps.co.uk`

## Azure Deployment

### 1. Create Azure App Service
```bash
# Create resource group
az group create --name fa-multitenant-rg --location "West Europe"

# Create App Service plan
az appservice plan create \
    --name fa-multitenant-plan \
    --resource-group fa-multitenant-rg \
    --sku P1V2 \
    --is-linux

# Create web app
az webapp create \
    --resource-group fa-multitenant-rg \
    --plan fa-multitenant-plan \
    --name fa-multitenant-app \
    --runtime "PYTHON|3.11"
```

### 2. Configure Wildcard Domain
```bash
# Add wildcard custom domain
az webapp config hostname add \
    --webapp-name fa-multitenant-app \
    --resource-group fa-multitenant-rg \
    --hostname "*.facilityapps.co.uk"
```

### 3. Set Environment Variables
```bash
# Set app settings
az webapp config appsettings set \
    --resource-group fa-multitenant-rg \
    --name fa-multitenant-app \
    --settings \
        STREAMLIT_SERVER_PORT=8000 \
        STREAMLIT_SERVER_ADDRESS=0.0.0.0 \
        MULTI_TENANT_MODE=true
```

## DNS Configuration

### Wildcard DNS Setup
Add this **ONE** record to your DNS (ODR DNS):

```
# Wildcard CNAME record
*.facilityapps.co.uk  CNAME  fa-multitenant-app.azurewebsites.net
```

This single record will handle ALL subdomains automatically!

### Individual Subdomains (Optional)
You can also add individual records for specific customers:
```
regularcleaning.facilityapps.co.uk  CNAME  fa-multitenant-app.azurewebsites.net
officeclean.facilityapps.co.uk      CNAME  fa-multitenant-app.azurewebsites.net
hospital.facilityapps.co.uk         CNAME  fa-multitenant-app.azurewebsites.net
```

## SSL Certificate

### Wildcard SSL Certificate
1. **Azure App Service Managed Certificate** (Free)
   - Go to Azure Portal → App Service → Custom domains
   - Add `*.facilityapps.co.uk`
   - Azure will automatically create a wildcard certificate
   - Wait 6-8 hours for certificate to be issued

2. **Upload Your Own Certificate** (If you have one)
   - Go to TLS/SSL settings
   - Upload your wildcard certificate
   - Bind it to `*.facilityapps.co.uk`

## Application Configuration

### 1. Customer Database
Create a database to store customer configurations:

```sql
-- Customers table
CREATE TABLE customers (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    fa_domain VARCHAR(255) NOT NULL,
    fa_token_encrypted TEXT NOT NULL,
    admin_email VARCHAR(255) NOT NULL,
    features JSON,
    status ENUM('active', 'suspended', 'trial'),
    branding JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Customer sessions
CREATE TABLE customer_sessions (
    id VARCHAR(255) PRIMARY KEY,
    customer_id VARCHAR(50) NOT NULL,
    user_email VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES customers(id)
);
```

### 2. Environment Variables
Set these in Azure App Service:

```bash
# Database connection
DATABASE_URL=mysql://user:password@server:3306/database

# Encryption key for customer tokens
ENCRYPTION_KEY=your-32-character-secret-key

# Admin credentials
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your-secure-password

# System settings
SYSTEM_NAME="FacilityApps Job Importer"
SYSTEM_URL="facilityapps.co.uk"
```

## Customer Onboarding

### 1. Admin Creates Customer
1. Login to admin panel at `facilityapps.co.uk`
2. Go to "Customers" tab
3. Click "Add New Customer"
4. Fill in customer details:
   - Company name
   - Subdomain (e.g., "regularcleaning")
   - FacilityApps credentials
   - Admin email
   - Features to enable
5. System creates customer configuration
6. Customer gets access to their subdomain

### 2. Customer Access
1. Customer visits `{customer}.facilityapps.co.uk`
2. System detects subdomain and loads customer config
3. Customer logs in with their credentials
4. Customer sees branded interface with their settings

## Security Considerations

### 1. Data Isolation
- **Database**: Customer data separated by `customer_id`
- **Sessions**: Customer-scoped session management
- **API Keys**: Encrypted storage per customer
- **Files**: Customer-specific storage paths

### 2. Access Control
- **Customer Authentication**: Per-customer login system
- **Admin Authentication**: Separate admin panel access
- **API Security**: Rate limiting per customer
- **Audit Logging**: Track all customer actions

### 3. Compliance
- **GDPR**: Data protection per customer
- **Backup**: Customer data backup/restore
- **Retention**: Data retention policies
- **Monitoring**: Track usage per customer

## Monitoring & Analytics

### 1. Application Insights
- Track usage per customer
- Monitor performance
- Alert on errors
- Usage analytics

### 2. Custom Metrics
- Jobs imported per customer
- API calls per customer
- Storage usage per customer
- Revenue tracking

### 3. Alerts
- High error rates
- Resource usage spikes
- Security incidents
- Payment failures

## Scaling Strategy

### 1. Horizontal Scaling
- Multiple App Service instances
- Load balancer distribution
- Database read replicas
- CDN for static content

### 2. Database Scaling
- Read replicas for performance
- Sharding by customer if needed
- Caching with Redis
- Backup and restore procedures

### 3. Storage Scaling
- Azure Blob Storage for files
- CDN for global distribution
- Backup and archival policies
- Cost optimization

## Cost Optimization

### 1. Resource Management
- **App Service**: Start with P1V2, scale as needed
- **Database**: Use appropriate tier for your needs
- **Storage**: Implement lifecycle policies
- **CDN**: Use Azure Front Door for performance

### 2. Pricing Tiers
- **Basic**: £50/month per customer
- **Professional**: £150/month per customer
- **Enterprise**: £500/month per customer

### 3. Usage-Based Pricing
- **Per Job**: £0.10 per job imported
- **API Calls**: £0.01 per API call
- **Storage**: £0.05 per GB per month

## Deployment Checklist

### Pre-Deployment
- [ ] Azure subscription ready
- [ ] Domain registered and DNS access
- [ ] Customer database designed
- [ ] Security policies defined
- [ ] Monitoring setup planned

### Deployment
- [ ] Create Azure resources
- [ ] Configure DNS (wildcard CNAME)
- [ ] Set up SSL certificate
- [ ] Deploy application code
- [ ] Configure environment variables
- [ ] Test all subdomains

### Post-Deployment
- [ ] Test customer onboarding
- [ ] Verify data isolation
- [ ] Set up monitoring
- [ ] Configure backups
- [ ] Train support team
- [ ] Launch customer communication

## Testing

### 1. Subdomain Testing
```bash
# Test each subdomain
curl -I https://regularcleaning.facilityapps.co.uk
curl -I https://officeclean.facilityapps.co.uk
curl -I https://hospital.facilityapps.co.uk
```

### 2. Customer Isolation Testing
- Create test customers
- Verify data separation
- Test authentication
- Check API access

### 3. Load Testing
- Simulate multiple customers
- Test concurrent usage
- Monitor performance
- Check resource usage

## Support & Maintenance

### 1. Customer Support
- Customer-specific help desk
- Documentation per customer
- Training materials
- Video tutorials

### 2. System Maintenance
- Regular updates
- Security patches
- Performance optimization
- Backup verification

### 3. Monitoring
- 24/7 system monitoring
- Alert management
- Performance tracking
- Usage analytics

## Benefits of Multi-Tenant Architecture

- **Scalable**: Easy to add new customers
- **Cost-Effective**: Single infrastructure for all customers
- **Professional**: Each customer gets their own subdomain
- **Isolated**: Complete data separation
- **Maintainable**: Single codebase for all customers
- **Profitable**: Recurring revenue from multiple customers
- **Brandable**: Each customer feels like they have their own app
