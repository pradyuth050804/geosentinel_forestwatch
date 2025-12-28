# How to Get Copernicus Data Space Credentials (FREE)

## Step-by-Step Registration

### 1. Go to Copernicus Data Space
Visit: **https://dataspace.copernicus.eu/**

### 2. Click "Register"
- Look for "Register" or "Sign Up" button in the top right
- Or go directly to: https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/auth?client_id=cdse-public&redirect_uri=https%3A%2F%2Fdataspace.copernicus.eu%2F&response_type=code&scope=openid

### 3. Fill in Registration Form
- **Email**: Your email address
- **Username**: Choose a username (remember this!)
- **Password**: Choose a strong password (remember this!)
- **First Name**: Your first name
- **Last Name**: Your last name
- **Country**: Your country
- **Organization**: Can be "Personal" or "Student"

### 4. Verify Email
- Check your email inbox
- Click the verification link
- Your account is now active!

### 5. Add to .env File
Open `.env` in the project root and add:

```env
COPERNICUS_USERNAME=your_username_here
COPERNICUS_PASSWORD=your_password_here
```

---

## Get Gemini API Key (Also FREE)

### 1. Go to Google AI Studio
Visit: **https://makersuite.google.com/app/apikey**

### 2. Sign in with Google Account
- Use your Gmail account
- Accept terms of service

### 3. Create API Key
- Click "Create API Key"
- Copy the key (starts with "AIza...")

### 4. Add to .env File
```env
GEMINI_API_KEY=AIzaSy...your_key_here
```

---

## Complete .env File Example

```env
# Copernicus Data Space (Free)
COPERNICUS_USERNAME=myusername
COPERNICUS_PASSWORD=mypassword123

# Google Gemini API (Free)
GEMINI_API_KEY=AIzaSyBXS9RwkwL2maUJ_1L9U_3y3Atgzk0nhBM

# Flask Configuration (leave as is)
FLASK_SECRET_KEY=dev-secret-key-geosentinel-2024
FLASK_ENV=development
FLASK_PORT=5000

# Processing Configuration (leave as is)
MAX_CLOUD_COVER=20
IMAGE_RESOLUTION=10
DEFORESTATION_THRESHOLD=0.5
```

---

## Important Notes

✅ **Both services are completely FREE**
✅ **No credit card required**
✅ **Copernicus**: Unlimited Sentinel-2 data access
✅ **Gemini**: Free tier includes 60 requests per minute

---

## Troubleshooting

**Can't register at Copernicus?**
- Try using a different browser
- Clear cookies and try again
- Use incognito/private mode

**Gemini API not working?**
- Make sure you're signed in to Google
- Try creating key in incognito mode
- Check that API key starts with "AIza"

**Forgot to save credentials?**
- Copernicus: Use password reset at login page
- Gemini: Just create a new API key

---

## Quick Links

- **Copernicus Registration**: https://dataspace.copernicus.eu/
- **Gemini API Key**: https://makersuite.google.com/app/apikey
- **Copernicus Documentation**: https://documentation.dataspace.copernicus.eu/

---

**After getting both credentials, update your `.env` file and you're ready to go!** 🚀
