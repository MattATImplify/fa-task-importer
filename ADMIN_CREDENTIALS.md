# 🔐 Admin Credentials Configuration

## Master Admin Setup

The application uses a username and password authentication system configured via `.streamlit/secrets.toml`.

### Default Credentials (Local Development)
```
Username: admin
Password: Testing123
```

### Configuration File Location
`.streamlit/secrets.toml`

### Configuration Format
```toml
[auth]
master_username = "admin"
master_password = "Testing123"
```

---

## 🔒 Security Best Practices

### For Production Deployment:

1. **Change the default credentials** immediately
2. Use a **strong password** (minimum 12 characters, mix of letters, numbers, symbols)
3. **Never commit** the `secrets.toml` file to git (it's already in `.gitignore`)
4. Use different credentials for staging and production environments

### Recommended Password Requirements:
- Minimum 12 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one number
- At least one special character
- No common words or patterns

### Example Strong Password:
```
Fa!2025$SecureJob#Import
```

---

## 🚀 Deployment Credentials

### Streamlit Cloud Configuration

When deploying to Streamlit Cloud, add these secrets in the app settings:

1. Go to your Streamlit Cloud app
2. Click **Settings** → **Secrets**
3. Add:
```toml
[auth]
master_username = "your_production_username"
master_password = "your_production_password"

[production]
FA_DOMAIN = "regularcleaning.facilityapps.com"
FA_TOKEN = "your_production_api_token"
```

---

## 👤 User Management

### Current Implementation:
- **Single master admin** account
- Username and password stored in secrets
- Session-based authentication
- Logout functionality included

### Future Enhancements (if needed):
- Multiple user accounts
- Role-based access control (RBAC)
- Password reset functionality
- Two-factor authentication (2FA)
- Audit logging of user actions

---

## 🔄 Changing Credentials

### Local Environment:
1. Edit `.streamlit/secrets.toml`
2. Update `master_username` and `master_password`
3. Restart the Streamlit app

### Production (Streamlit Cloud):
1. Go to app settings
2. Click **Secrets**
3. Update the `[auth]` section
4. Save (app will automatically restart)

---

## 🆘 Troubleshooting

### "Authentication not configured" error
- Check that `.streamlit/secrets.toml` exists
- Verify the `[auth]` section is present
- Ensure `master_username` and `master_password` are set

### "Invalid username or password" error
- Verify credentials are correct (case-sensitive)
- Check for extra spaces
- Ensure secrets file is properly formatted (valid TOML syntax)

### Lost password?
- For local: Edit `.streamlit/secrets.toml` directly
- For production: Update secrets in Streamlit Cloud dashboard

