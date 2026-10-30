# 🚀 SensVerify Live Deployment Guide

Repository: `https://github.com/keert-cell/sensverify`
Branch: `main`

---

## Option A: Deploy via Streamlit Community Cloud (Recommended & 100% Free)

You can deploy directly using the **Deploy** button at the top-right of your running app or via [share.streamlit.io](https://share.streamlit.io):

1. **Repository**: `keert-cell/sensverify`
2. **Branch**: `main`
3. **Main file path**: `app.py` (or `sensverify/app.py` or `sensverify.py`)
4. **App URL (Path)**: `sensverify`
5. Click **Deploy!**

Your live URL will be:
👉 **`https://sensverify.streamlit.app`**

---

## Option B: Deploy on Render

1. Go to [Render Dashboard](https://dashboard.render.com/) and click **New + Web Service**.
2. Connect your repo: `keert-cell/sensverify`.
3. Configure:
   - **Name**: `sensverify`
   - **Region**: Singapore or Oregon
   - **Branch**: `main`
   - **Root Directory**: (Leave blank OR enter `sensverify` — both work)
   - **Runtime**: `Python 3`
   - **Build Command**:
     ```bash
     pip install -r requirements.txt
     ```
   - **Start Command**:
     ```bash
     streamlit run app.py --server.port=$PORT --server.address=0.0.0.0 --server.headless=true
     ```
4. Click **Create Web Service**.

Your live URL will be:
👉 **`https://sensverify.onrender.com`**
