# 🛡️ SensVerify LIVE

### 🌐 Live Links:

*Primary:* https://sensverify.onrender.com 🟢
*Backup:* https://sensverify.streamlit.app 🟢

| Primary - Render | https://sensverify.onrender.com |
| Backup - Streamlit | https://sensverify.streamlit.app |

# 🛡️ SensVerify Universal Defense Grid

SensVerify is an Autonomous Cyber Threat Grid & Real-Time Threat Verification platform.

---

## 🌟 Overview
SensVerify protects users from digital threats across 3 primary shields:
1. **💬 SMS Scam Shield**: Intercepts and analyzes electricity disconnection traps, fake banking alerts, lottery scams, and suspicious links.
2. **📧 Email Phishing Shield**: Evaluates sender domain authenticity, urgent coercion traps, lookalike spoofing, and credential harvesting links.
3. **📰 News Truth Shield**: Advanced news verification and misinformation detection with linguistic and semantic forensics.

### Key Capabilities
- **2-Step Frictionless Login (Zero Password, Zero OTP Gateway)**:
  - **Page 1**: Clean 10-digit mobile number input.
  - **Page 2**: Name + Optional Email + Continue with Google.
- **📷 Modern Single Camera & Upload**:
  - Upload photos, documents, and posters (JPG, PNG, PDF up to 200MB).
  - Modern single viewport with centered shutter and quick 🔄 flip icon for front and back camera.
- **🔍 Visual AI Forensics**:
  - Highlights suspicious trigger words with Impact % badges.
  - Horizontal word impact score breakdown graph for AI explainability.
- **24/7 Live Sensor Telemetry**: Real-time counter metrics linked to SQLite database.
- **Role-Based Access (User View vs. Admin Analytics)**:
  - **User View**: Dedicated "Scan Now" and private "My Scan History" tabs.
  - **Admin Analytics**: Protected with a private PIN (`1234`), 8 live metric cards, complete scan audit log, and user login history.

---

## 🚀 How to Run Locally

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run Streamlit on localhost
streamlit run app.py --server.port 8501
```

Open your browser and navigate to: **`http://localhost:8501`**

---

## 🌐 Cloud Deployment (Render / Streamlit Cloud)
- **Procfile** and **runtime.txt** are pre-configured.
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `streamlit run app.py --server.port=$PORT --server.address=0.0.0.0 --server.headless=true`
