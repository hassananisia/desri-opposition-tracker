# Deploying to Streamlit Community Cloud

## Prerequisites
1. GitHub account (free at github.com)
2. Streamlit Community Cloud account (free at share.streamlit.io)
3. Your app files ready

## Step 1: Create GitHub Repository

1. **Go to GitHub.com** and sign in
2. Click the **"+"** icon (top right) → **"New repository"**
3. Configure repository:
   - **Repository name**: `desri-opposition-tracker` (or your preferred name)
   - **Description**: "DESRI Public Engagement Intelligence Hub"
   - **Public** or **Private** (Private recommended for internal tools)
   - **DON'T** initialize with README (we'll upload our files)
4. Click **"Create repository"**

## Step 2: Prepare Your Files

### Required Files Structure:
```
desri-opposition-tracker/
├── desri_hub_app.py           # Main app file
├── supabase_config.py          # Database configuration
├── requirements.txt            # Python dependencies
├── .gitignore                  # Files to exclude
├── README.md                   # Project description
└── data/                       # Data files
    └── Opposition_Tracker_Data_June_2025.csv
```

### Create requirements.txt:
```txt
streamlit>=1.29.0
pandas>=2.0.0
plotly>=5.14.0
folium>=0.14.0
streamlit-folium>=0.15.0
supabase>=2.0.0
python-dotenv>=1.0.0
Pillow>=10.0.0
```

### Create .gitignore:
```
# Environment variables
.env
.env.local

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Temporary files
*.tmp
*.bak
*.log

# Sensitive data
secrets.toml
```

### Create README.md:
```markdown
# DESRI Public Engagement Intelligence Hub

Internal tool for tracking and managing community opposition to renewable energy projects.

## Features
- Opposition Tracker with interactive map
- 2025 Opposition Report analytics
- Public Hearings Q&A Resources
- Survey response management

## Access
This app is deployed on Streamlit Community Cloud for authorized DESRI users only.
```

## Step 3: Upload to GitHub

### Option A: Using GitHub Desktop (Easiest)
1. Download **GitHub Desktop** from desktop.github.com
2. Sign in with your GitHub account
3. Click **"Add"** → **"Add Existing Repository"**
4. Browse to your project folder
5. If prompted, click **"Create a Repository"**
6. Review files, add commit message: "Initial commit"
7. Click **"Commit to main"**
8. Click **"Publish repository"**

### Option B: Using Git Command Line
```bash
# Navigate to your project folder
cd C:\Users\AnisiaHassanFerreira\desri_opposition_to_renewables

# Initialize git
git init

# Add all files
git add .

# Commit files
git commit -m "Initial commit"

# Add remote repository (replace with your repo URL)
git remote add origin https://github.com/YOUR_USERNAME/desri-opposition-tracker.git

# Push to GitHub
git branch -M main
git push -u origin main
```

### Option C: Upload via GitHub Web
1. Go to your new repository on GitHub
2. Click **"uploading an existing file"**
3. Drag and drop all your files (except .env)
4. Write commit message: "Initial commit"
5. Click **"Commit changes"**

## Step 4: Deploy on Streamlit Community Cloud

1. **Go to** [share.streamlit.io](https://share.streamlit.io)
2. **Sign in** with your GitHub account
3. Click **"New app"**
4. Configure deployment:
   - **Repository**: Select `YOUR_USERNAME/desri-opposition-tracker`
   - **Branch**: `main`
   - **Main file path**: `desri_hub_app.py`
   - **App URL**: Choose custom URL (e.g., `desri-tracker`)
5. Click **"Deploy"**

## Step 5: Add Secrets (IMPORTANT!)

Your app needs Supabase credentials to work:

1. **In Streamlit Cloud**, go to your app
2. Click **"⋮"** (three dots) → **"Settings"**
3. Navigate to **"Secrets"** section
4. Add your secrets in TOML format:

```toml
# Supabase Configuration
SUPABASE_URL = "https://hrssrhmrtlymkwsrqbct.supabase.co"
SUPABASE_KEY = "your-supabase-anon-key-here"
```

5. Click **"Save"**
6. App will automatically restart with secrets

## Step 6: Manage Access (For Private Apps)

### If Repository is Private:
- Only you can deploy and view the app
- Share access by inviting collaborators to GitHub repo

### To Share App Access:
1. In Streamlit Cloud, go to app settings
2. Under **"Sharing"**, you can:
   - Make app public (anyone with link)
   - Require viewer authentication
   - Set up SSO if available

### Recommended for DESRI:
- Keep GitHub repository **Private**
- Deploy app as **Private**
- Share app link only with authorized DESRI team members
- Consider password protection or SSO for additional security

## Step 7: Monitoring & Updates

### View App Logs:
1. In Streamlit Cloud dashboard
2. Click on your app
3. Click **"Manage app"** → **"Logs"**

### Update Your App:
1. Make changes locally
2. Push to GitHub:
   ```bash
   git add .
   git commit -m "Update: description of changes"
   git push
   ```
3. Streamlit Cloud auto-deploys changes

### Troubleshooting Deployment:

**App won't start?**
- Check logs for error messages
- Verify all dependencies in requirements.txt
- Ensure secrets are properly configured

**Database connection failing?**
- Verify SUPABASE_URL and SUPABASE_KEY in secrets
- Check if Supabase allows connections from Streamlit Cloud
- May need to update Supabase security settings

**Import errors?**
- Add missing packages to requirements.txt
- Check package version compatibility

## Important Security Notes

### DO:
✅ Keep `.env` file local only (never commit)
✅ Use Streamlit Secrets for credentials
✅ Keep repository private for internal tools
✅ Regularly update dependencies
✅ Monitor app usage and logs

### DON'T:
❌ Commit secrets to GitHub
❌ Share app URL publicly if contains sensitive data
❌ Use service_role key in production
❌ Ignore security warnings in logs

## Quick Deployment Checklist

- [ ] Created GitHub repository
- [ ] Added all necessary files
- [ ] Created requirements.txt with all dependencies
- [ ] Created .gitignore to exclude .env
- [ ] Pushed code to GitHub
- [ ] Deployed on Streamlit Cloud
- [ ] Added secrets (SUPABASE_URL, SUPABASE_KEY)
- [ ] Tested app is working
- [ ] Set appropriate access controls
- [ ] Shared link with team

## Useful Links

- **Streamlit Cloud**: https://share.streamlit.io
- **Streamlit Docs**: https://docs.streamlit.io/streamlit-community-cloud
- **GitHub**: https://github.com
- **Supabase Dashboard**: https://app.supabase.com

---

*For DESRI internal use only*