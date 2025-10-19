# Custom Domain Setup Checklist
## regularcleaning.facilityapps.co.uk

### ✅ Prerequisites
- [ ] Azure App Service is deployed and running
- [ ] You have access to your domain registrar (facilityapps.co.uk)
- [ ] Azure CLI is installed and you're logged in

### ✅ Step 1: Get Verification Details
- [ ] Run: `./get_domain_info.sh`
- [ ] Note the CNAME value: `fa-job-importer.azurewebsites.net`
- [ ] Go to Azure Portal > App Service > Custom domains
- [ ] Click "Add custom domain" and enter: `regularcleaning.facilityapps.co.uk`
- [ ] Copy the TXT verification value (starts with `asuid.regularcleaning.facilityapps.co.uk=`)

### ✅ Step 2: Configure DNS Records
- [ ] **CNAME Record:**
  - Type: CNAME
  - Name: `regularcleaning`
  - Value: `fa-job-importer.azurewebsites.net`
  - TTL: 300
- [ ] **TXT Record:**
  - Type: TXT
  - Name: `asuid.regularcleaning`
  - Value: `[The verification ID from Azure]`
  - TTL: 300

### ✅ Step 3: Verify in Azure
- [ ] Wait 5-10 minutes for DNS propagation
- [ ] Click "Validate" in Azure Portal
- [ ] Domain should show as "Verified"
- [ ] Click "Add" to add the domain

### ✅ Step 4: Configure SSL
- [ ] Click "Add binding" next to your domain
- [ ] Select "SNI SSL"
- [ ] Choose "Create App Service Managed Certificate"
- [ ] Click "Add binding"
- [ ] Wait 6-8 hours for certificate to be issued

### ✅ Step 5: Test
- [ ] Visit: `https://regularcleaning.facilityapps.co.uk`
- [ ] Verify app loads correctly
- [ ] Check SSL certificate (green lock icon)
- [ ] Test all app functionality

### ✅ Troubleshooting
- [ ] If domain not verifying: Check DNS propagation with `nslookup`
- [ ] If SSL issues: Wait longer for certificate, check binding
- [ ] If app not loading: Verify CNAME points to correct Azure URL

### 📞 Support
- Azure Portal: Check "Log stream" for errors
- DNS Tools: Use `dig` or `nslookup` to verify records
- Domain Registrar: Check their DNS management interface
