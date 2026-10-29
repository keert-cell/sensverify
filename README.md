# 🛡️ SensVerify Universal Defense Grid

SensVerify is an Autonomous Cyber Threat Grid & Real-Time ALITS Threat Verification platform.

---

## 🌟 English Overview
SensVerify protects users from digital threats across 3 primary vectors:
1. **💬 SMS & Notification Scam Shield**: Intercepts and analyzes electricity disconnection traps, fake banking alerts, courier delivery scams, and WhatsApp fraud.
2. **📧 Email Phishing & Spoof Shield**: Evaluates sender domain authenticity, urgent coercion traps, lookalike spoofing, and credential harvesting links.
3. **🌐 URL & QR Threat Shield**: Inspects shortened URLs, punycode spoofing, unencrypted channels, and malicious redirect destinations.

### Key Capabilities
- **2-Step Frictionless Login (No Password, No OTP Gateway)**:
  - **Page 1**: Clean 10-digit mobile number input.
  - **Page 2**: Continue with Email or Continue with Google. Zero OTP dependency.
- **24/7 Live Sensor Badge**: Animated pulsing indicator with live scan telemetry timestamp.
- **3-Second Auto-Updating Telemetry**: Real-time counter metrics auto-refresh every 3 seconds.
- **Multi-Language Support**: Complete interface localized in English, తెలుగు (Telugu), हिन्दी (Hindi), தமிழ் (Tamil), and ಕನ್ನಡ (Kannada).
- **SQLite Database**: User profiles and logins saved cleanly in `users.db`.
- **Downloadable Forensic Defense Reports**: Instant high-resolution PDF generation with forensic threat breakdown.

---

## 🇮🇳 తెలుగు వివరణ (Telugu Guide)
SensVerify అనేది ఆటోమేటెడ్ సైబర్ ముప్పు గుర్తింపు మరియు నిరోధక వ్యవస్థ.

### ముఖ్యమైన ఫీచర్లు:
1. **రెండు దశల సులభమైన లాగిన్ (No Password, No OTP Gateway)**:
   - **మొదటి పేజీ**: కేవలం 10 అంకెల మొబైల్ నంబర్ మాత్రమే.
   - **రెండవ పేజీ**: ఈమెయిల్ లేదా Google తో డైరెక్ట్ కంటిన్యూ. ఎలాంటి పాస్‌వర్డ్ లేదా OTP అవసరం లేదు.
2. **24/7 లైవ్ సెన్సార్లు**: ప్రతి 3 సెకన్లకు లైవ్ కౌంటర్లు ఆటోమేటిక్ గా అప్‌డేట్ అవుతాయి.
3. **5 ప్రధాన భాషల మద్దతు**: ఇంగ్లీష్, తెలుగు, హిందీ, తమిళం, మరియు కన్నడ.
4. **3 రక్షిత ఎండ్‌పాయింట్లు**: SMS స్కామ్‌లు, ఈమెయిల్ ఫిషింగ్, మరియు ప్రమాదకర URLల స్కానింగ్.
5. **PDF డిఫెన్స్ రిపోర్ట్**: ఒకే క్లిక్‌తో సమగ్రమైన రక్షణ రిపోర్ట్ డౌన్‌లోడ్ చేసుకోవచ్చు.

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
- Build Command: `pip install -r requirements.txt`
- Start Command: `streamlit run app.py --server.port=$PORT --server.address=0.0.0.0 --server.headless=true`
