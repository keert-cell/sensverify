# 🚀 SensVerify Deployment Guide (Render & Cloud)

Follow these steps to deploy SensVerify on Render:

### Step 1: Push Code to GitHub
Ensure all files (`app.py`, `Procfile`, `runtime.txt`, `requirements.txt`, `assets/`, `manifest.json`) are committed and pushed to your GitHub repository:
```bash
git add .
git commit -m "SensVerify Final Verified Build"
git push origin main
```

### Step 2: Create Web Service on Render
1. Go to [Render Dashboard](https://dashboard.render.com/).
2. Click **New +** and select **Web Service**.
3. Connect your repository: `keert-cell/sensverify`.

### Step 3: Configure Settings
- **Name**: `sensverify`
- **Region**: Singapore or Oregon
- **Branch**: `main`
- **Runtime**: `Python 3`
- **Build Command**:
  ```bash
  pip install -r requirements.txt
  ```
- **Start Command**:
  ```bash
  streamlit run app.py --server.port=$PORT --server.address=0.0.0.0 --server.headless=true
  ```

### Step 4: Environment Variables (Optional)
If using Google OAuth, add:
- `GOOGLE_CLIENT_ID`
- `GOOGLE_CLIENT_SECRET`

### Step 5: Deploy
Click **Create Web Service**. Render will build and deploy your app at:
`https://sensverify.onrender.com`
