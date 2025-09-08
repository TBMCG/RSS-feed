# Azure Active Directory Setup Guide for TBMCG News Dashboard

This guide walks you through setting up Microsoft authentication for the TBMCG News Dashboard application.

## Prerequisites
- Microsoft Azure account (or Office 365 admin access)
- Admin rights to create app registrations in your Azure AD tenant

## Step 1: Access Azure Portal

1. Go to [Azure Portal](https://portal.azure.com)
2. Sign in with your TBMCG admin account
3. If you see multiple directories, make sure you're in the TBMCG directory (check top-right corner)

## Step 2: Create App Registration

1. In the Azure Portal, navigate to:
   - **Azure Active Directory** (search for it in the top search bar)
   - Click **App registrations** in the left menu
   - Click **+ New registration** button at the top

2. Fill in the registration form:
   - **Name**: `TBMCG News Dashboard`
   - **Supported account types**: Select one of these:
     - `Accounts in this organizational directory only (TBMCG only - Single tenant)` ✅ RECOMMENDED
     - This ensures only @tbmcg.com users can access
   - **Redirect URI**: 
     - Platform: `Web`
     - URL: `http://localhost:5000/auth/callback` (for development)

3. Click **Register**

## Step 3: Save Your Application (client) ID

After registration, you'll see the app overview page.

1. Copy the **Application (client) ID** (looks like: `12345678-1234-1234-1234-123456789abc`)
2. Save this - you'll need it for the `.env` file

## Step 4: Create Client Secret

1. In your app registration, go to **Certificates & secrets** (left menu)
2. Click **+ New client secret**
3. Add a description: `TBMCG News Dashboard Secret`
4. Choose expiration:
   - `180 days (6 months)` - Requires renewal
   - `365 days (12 months)` - Requires renewal  
   - `730 days (24 months)` - Requires renewal
   - `Custom` - Set your own date
5. Click **Add**
6. **IMPORTANT**: Copy the secret **Value** immediately (not the Secret ID)
   - ⚠️ You won't be able to see this again!
   - Save this for your `.env` file

## Step 5: Configure API Permissions

1. Go to **API permissions** (left menu)
2. You should see `User.Read` already added
3. Click **+ Add a permission**
4. Choose **Microsoft Graph**
5. Choose **Delegated permissions**
6. Search and select these permissions:
   - ✅ `email` - View users' email address
   - ✅ `openid` - Sign users in
   - ✅ `profile` - View users' basic profile
   - ✅ `User.Read` - Sign in and read user profile (already added)
7. Click **Add permissions**

## Step 6: Add Production Redirect URI (Optional)

If deploying to production:

1. Go to **Authentication** (left menu)
2. Under **Platform configurations**, find your Web platform
3. Click **Add URI**
4. Add your production URL: `https://news.tbmcg.com/auth/callback` (or your domain)
5. Click **Save**

## Step 7: Configure Your Application

Create a `.env` file in your project root with these values:

```bash
# Flask Secret Key (generate a random string)
SECRET_KEY=your-random-secret-key-here-make-it-long-and-random

# Azure AD Configuration
MICROSOFT_CLIENT_ID=paste-your-application-client-id-here
MICROSOFT_CLIENT_SECRET=paste-your-client-secret-value-here
MICROSOFT_TENANT_ID=paste-your-tenant-id-here-or-use-common

# Redirect URI (must match Azure configuration)
REDIRECT_URI=http://localhost:5000/auth/callback
```

### How to find your Tenant ID:

1. In Azure Portal, go to **Azure Active Directory**
2. Click **Overview**
3. Copy the **Tenant ID** (also called Directory ID)

OR

- Use `common` if you want to allow any Microsoft account (not recommended for company-only access)
- Use `organizations` to allow any work/school account
- Use your specific tenant ID for maximum security (recommended)

## Step 8: Test Your Configuration

1. Activate your Python virtual environment:
   ```bash
   source venv/bin/activate  # Linux/Mac
   # or
   venv\Scripts\activate  # Windows
   ```

2. Start the application:
   ```bash
   python app.py
   ```

3. Visit `http://localhost:5000`
4. Click login - you should be redirected to Microsoft login
5. Sign in with your @tbmcg.com account
6. You should be redirected back and logged in!

## Troubleshooting

### "Invalid client" error
- Check that your client secret is correct and not expired
- Ensure you copied the secret Value, not the Secret ID

### "Invalid redirect URI" error  
- Make sure the redirect URI in `.env` exactly matches what's in Azure
- Check for trailing slashes - they matter!
- Protocol must match (http vs https)

### "Unauthorized client" error
- Verify the tenant ID is correct
- Check that the app registration is in the right directory

### "User not authorized" after login
- Verify the user's email ends with @tbmcg.com
- Check the app.py code for the domain restriction

## Security Best Practices

1. **Never commit `.env` to git** - it's in `.gitignore` for a reason
2. **Rotate secrets regularly** - Set calendar reminders before expiry
3. **Use tenant-specific ID** - Don't use `common` for production
4. **Enable MFA** - Require multi-factor authentication for all users
5. **Monitor sign-ins** - Check Azure AD sign-in logs regularly

## Managing User Permissions

By default, all @tbmcg.com users can view the dashboard. To grant feed management permissions:

1. Edit `app.py` and find this line:
   ```python
   can_manage = email in ['admin@tbmcg.com']  # Add specific admin emails
   ```

2. Add authorized managers:
   ```python
   can_manage = email in [
       'admin@tbmcg.com',
       'john.doe@tbmcg.com',
       'jane.smith@tbmcg.com'
   ]
   ```

3. Restart the application

## Production Deployment Checklist

- [ ] Created production app registration in Azure
- [ ] Set production redirect URI
- [ ] Generated strong SECRET_KEY for Flask
- [ ] Set appropriate secret expiration (with renewal reminders)
- [ ] Documented admin users who can manage feeds
- [ ] Tested with multiple @tbmcg.com accounts
- [ ] Set up secret rotation schedule
- [ ] Configured monitoring/logging

## Support

If you encounter issues:

1. Check the Azure AD sign-in logs for error details
2. Verify all IDs and secrets are correctly copied
3. Ensure the user's email domain is @tbmcg.com
4. Check Flask application logs for detailed errors

For Azure-specific issues, consult the [Microsoft identity platform documentation](https://docs.microsoft.com/en-us/azure/active-directory/develop/).