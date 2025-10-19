# Multi-Tenant Architecture Design
## FacilityApps Job Importer for Multiple Customers

## Overview
This app will serve multiple customers, each with their own:
- Subdomain (e.g., `regularcleaning.facilityapps.co.uk`, `officeclean.facilityapps.co.uk`)
- API credentials
- Job configurations
- Data isolation

## Architecture Options

### Option 1: Subdomain-Based Multi-Tenancy (Recommended)
- **URL Pattern**: `{customer}.facilityapps.co.uk`
- **Examples**: 
  - `regularcleaning.facilityapps.co.uk`
  - `officeclean.facilityapps.co.uk`
  - `hospital.facilityapps.co.uk`
- **Benefits**: 
  - Easy to manage
  - Clear customer separation
  - Professional URLs
  - Easy SSL certificate management

### Option 2: Path-Based Multi-Tenancy
- **URL Pattern**: `facilityapps.co.uk/{customer}`
- **Examples**:
  - `facilityapps.co.uk/regularcleaning`
  - `facilityapps.co.uk/officeclean`
- **Benefits**: Single domain, easier SSL
- **Drawbacks**: Less professional, harder to brand

## Recommended Implementation: Subdomain-Based

### 1. Customer Management System
```python
# Customer configuration structure
CUSTOMERS = {
    "regularcleaning": {
        "name": "Regular Cleaning Ltd",
        "fa_domain": "regularcleaning.facilityapps.com",
        "fa_token": "token_here",
        "admin_email": "admin@regularcleaning.co.uk",
        "features": ["recurring_jobs", "csv_import", "api_integration"],
        "created_date": "2025-01-01",
        "status": "active"
    },
    "officeclean": {
        "name": "Office Clean Services",
        "fa_domain": "officeclean.facilityapps.com", 
        "fa_token": "token_here",
        "admin_email": "admin@officeclean.co.uk",
        "features": ["recurring_jobs", "csv_import"],
        "created_date": "2025-01-15",
        "status": "active"
    }
}
```

### 2. Subdomain Detection
```python
def get_customer_from_subdomain():
    """Extract customer from subdomain"""
    import os
    host = os.environ.get('HTTP_HOST', '')
    
    if host.startswith('facilityapps.co.uk'):
        # Extract subdomain
        subdomain = host.split('.')[0]
        return subdomain
    return None
```

### 3. Customer-Specific Configuration
```python
def get_customer_config(customer_id):
    """Get configuration for specific customer"""
    if customer_id in CUSTOMERS:
        return CUSTOMERS[customer_id]
    else:
        # Redirect to main site or show error
        st.error("Customer not found")
        st.stop()
```

## Implementation Plan

### Phase 1: Basic Multi-Tenancy
1. **Subdomain Detection**: Detect customer from URL
2. **Customer Database**: Store customer configurations
3. **Isolation**: Ensure data separation between customers
4. **Authentication**: Customer-specific login

### Phase 2: Customer Management
1. **Admin Panel**: Manage customers and their settings
2. **Customer Onboarding**: Self-service signup flow
3. **Billing Integration**: Track usage per customer
4. **Support Portal**: Customer-specific support

### Phase 3: Advanced Features
1. **White-labeling**: Custom branding per customer
2. **API Access**: Customer-specific API keys
3. **Analytics**: Usage tracking per customer
4. **Backup/Restore**: Customer data management

## Technical Implementation

### 1. Azure App Service Configuration
- **Single App Service** for all customers
- **Wildcard SSL Certificate** for `*.facilityapps.co.uk`
- **Custom Domain Mapping** for each subdomain

### 2. DNS Configuration
```
# Wildcard CNAME record
*.facilityapps.co.uk  CNAME  fa-job-importer.azurewebsites.net

# Individual subdomains (optional, for specific customers)
regularcleaning.facilityapps.co.uk  CNAME  fa-job-importer.azurewebsites.net
officeclean.facilityapps.co.uk      CNAME  fa-job-importer.azurewebsites.net
```

### 3. Database Schema
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

## Security Considerations

### 1. Data Isolation
- **Database**: Separate schemas or customer_id filtering
- **File Storage**: Customer-specific folders
- **API Keys**: Encrypted storage
- **Sessions**: Customer-scoped session management

### 2. Access Control
- **Authentication**: Customer-specific login
- **Authorization**: Role-based access within customer
- **API Security**: Rate limiting per customer
- **Audit Logging**: Track all customer actions

### 3. Compliance
- **GDPR**: Data protection per customer
- **SOC 2**: Security controls
- **Backup**: Customer data backup/restore
- **Retention**: Data retention policies

## Deployment Strategy

### 1. Azure App Service
- **Single App Service** with multiple custom domains
- **Application Settings** for customer configurations
- **Key Vault** for encrypted secrets
- **Application Insights** for monitoring

### 2. Domain Management
- **Wildcard SSL**: `*.facilityapps.co.uk`
- **DNS**: Wildcard CNAME record
- **CDN**: Azure Front Door for performance
- **Monitoring**: Uptime monitoring per subdomain

### 3. Scaling
- **Horizontal**: Multiple App Service instances
- **Database**: Read replicas for performance
- **Caching**: Redis for session management
- **Storage**: Azure Blob Storage for files

## Customer Onboarding Flow

### 1. Self-Service Signup
1. Customer visits `facilityapps.co.uk`
2. Clicks "Get Started" or "Sign Up"
3. Fills out company details
4. Provides FacilityApps credentials
5. System creates subdomain and configuration
6. Customer gets access to their subdomain

### 2. Admin-Approved Signup
1. Customer requests access
2. Admin reviews and approves
3. System provisions customer environment
4. Customer receives login credentials
5. Customer configures their settings

## Pricing Model

### 1. Tiered Pricing
- **Starter**: £50/month - Basic features, 1 subdomain
- **Professional**: £150/month - All features, 5 subdomains
- **Enterprise**: £500/month - Custom features, unlimited subdomains

### 2. Usage-Based Pricing
- **Per Job Import**: £0.10 per job imported
- **API Calls**: £0.01 per API call
- **Storage**: £0.05 per GB per month

## Next Steps

1. **Implement subdomain detection**
2. **Create customer management system**
3. **Set up database schema**
4. **Configure Azure for multi-tenancy**
5. **Build customer onboarding flow**
6. **Implement security and isolation**
7. **Create admin dashboard**
8. **Set up monitoring and analytics**

## Benefits of This Approach

- **Scalable**: Easy to add new customers
- **Professional**: Each customer gets their own subdomain
- **Isolated**: Complete data separation
- **Maintainable**: Single codebase for all customers
- **Profitable**: Recurring revenue from multiple customers
- **Brandable**: Each customer feels like they have their own app
