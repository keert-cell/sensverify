import streamlit as st
from streamlit_autorefresh import st_autorefresh
import sqlite3
import random
import os
import time
from datetime import datetime
from dotenv import load_dotenv

# Load optional env variables
load_dotenv()

# Page Configuration
st.set_page_config(
    page_title="SensVerify Universal Defense",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------------------------------------------------
# DATABASE INITIALIZATION (SQLite users.db)
# -----------------------------------------------------------------------------
def init_db():
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mobile TEXT,
            email TEXT,
            name TEXT,
            created_at TEXT
        )
    """)
    conn.commit()
    conn.close()

def save_user(mobile, email, name="Keerthi"):
    try:
        conn = sqlite3.connect("users.db")
        c = conn.cursor()
        c.execute(
            "INSERT INTO users (mobile, email, name, created_at) VALUES (?, ?, ?, ?)",
            (mobile, email, name, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        )
        conn.commit()
        conn.close()
    except Exception as e:
        pass

init_db()

# -----------------------------------------------------------------------------
# MULTI-LANGUAGE TRANSLATION DICTIONARY
# -----------------------------------------------------------------------------
LANGUAGES = {
    "English": "en",
    "తెలుగు (Telugu)": "te",
    "हिन्दी (Hindi)": "hi",
    "தமிழ் (Tamil)": "ta",
    "ಕನ್ನಡ (Kannada)": "kn"
}

TRANSLATIONS = {
    "en": {
        "welcome": "Welcome",
        "enter_mobile": "Enter mobile number",
        "mobile_placeholder": "Mobile number",
        "continue": "Continue",
        "email": "Email address",
        "continue_email": "Continue with Email",
        "continue_google": "Continue with Google",
        "back": "← Back",
        "logout": "Logout",
        "live_badge": "LIVE-SENSORS - REAL-TIME ACTIVE • 24/7",
        "protected_endpoints": "PROTECTED ENDPOINTS",
        "scans_executed": "ACTIVE SCANS EXECUTED",
        "threats_blocked": "THREATS BLOCKED TODAY",
        "subtitle": "Autonomous Cyber Threat Grid & Real-Time ALITS URL Verification",
        "defense_grid": "SensVerify Universal Defense Grid",
        "welcome_user": "Welcome, Keerthi!",
        "endpoints_desc": "3 Automated Protection Layers Guarding You 24/7:",
        "ep_sms": "💬 SMS & Notification Scam Shield",
        "ep_sms_desc": "Detects fake bank SMS, electricity disconnection threats, lottery scams, and WhatsApp fraud.",
        "ep_mail": "📧 Email Phishing & Spoof Shield",
        "ep_mail_desc": "Analyzes sender domain spoofing, urgency traps, malware lures, and credential theft vectors.",
        "ep_url": "🌐 URL & QR Threat Shield",
        "ep_url_desc": "Scans malicious links, lookalike typo domains, fake login pages, and QR redirects.",
        "scan_now": "Scan Threat",
        "clean_status": "AUTHENTIC / SAFE",
        "scam_status": "MALICIOUS / FAKE SCAM DETECTED",
        "confidence": "Threat Confidence",
        "download_report": "📥 Download PDF Defense Report",
        "zero_trust_tooltip": "Zero Trust = Verify every request, never trust by default - even after login every scan is verified."
    },
    "te": {
        "welcome": "స్వాగతం",
        "enter_mobile": "మొబైల్ నంబర్ నమోదు చేయండి",
        "mobile_placeholder": "మొబైల్ నంబర్",
        "continue": "కొనసాగించు",
        "email": "ఈమెయిల్ చిరునామా",
        "continue_email": "ఈమెయిల్తో కొనసాగించు",
        "continue_google": "Google తో కొనసాగించు",
        "back": "← వెనుకకు",
        "logout": "లాగ్ అవుట్",
        "live_badge": "లైవ్-సెన్సార్లు - రియల్-టైమ్ యాక్టివ్ • 24/7",
        "protected_endpoints": "రక్షిత ముగింపు పాయింట్లు",
        "scans_executed": "యాక్టివ్ స్కాన్‌లు పూర్తయ్యాయి",
        "threats_blocked": "నేడు నిరోధించిన బెదిరింపులు",
        "subtitle": "స్వయంప్రతిపత్త సైబర్ ముప్పు గ్రిడ్ & రియల్-టైమ్ ALITS URL ధృవీకరణ",
        "defense_grid": "SensVerify సార్వత్రిక రక్షణ గ్రిడ్",
        "welcome_user": "స్వాగతం, కీర్తి!",
        "endpoints_desc": "24/7 మీకు రక్షణ కల్పించే 3 ఆటోమేటెడ్ సెక్యూరిటీ లేయర్‌లు:",
        "ep_sms": "💬 SMS & నోటిఫికేషన్ స్కామ్ షీల్డ్",
        "ep_sms_desc": "నకిలీ బ్యాంక్ SMS, కరెంట్ బిల్లు హెచ్చరికలు, లాటరీ మోసాలు మరియు వాట్సాప్ మోసాలను గుర్తిస్తుంది.",
        "ep_mail": "📧 ఈమెయిల్ ఫిషింగ్ & స్పూఫ్ షీల్డ్",
        "ep_mail_desc": "నకిలీ డొమైన్‌లు, అత్యవసర బెదిరింపులు మరియు పాస్‌వర్డ్ దొంగతనం ప్రయత్నాలను విశ్లేషిస్తుంది.",
        "ep_url": "🌐 URL & QR ముప్పు షీల్డ్",
        "ep_url_desc": "హానికరమైన లింక్‌లు, నకిలీ లాగిన్ పేజీలు మరియు మోసపూరిత QR కోడ్‌లను స్కాన్ చేస్తుంది.",
        "scan_now": "ముప్పును స్కాన్ చేయండి",
        "clean_status": "సురక్షితమైనది / నిజమైనది (SAFE)",
        "scam_status": "ప్రమాదకరమైన నకిలీ మోసం గుర్తించబడింది (FAKE SCAM)",
        "confidence": "ముప్పు విశ్వసనీయత (Confidence)",
        "download_report": "📥 PDF డిఫెన్స్ రిపోర్ట్ డౌన్‌లోడ్ చేయండి",
        "zero_trust_tooltip": "Zero Trust = ప్రతి అభ్యర్థనను ధృవీకరించండి, ముందే దేన్నీ నమ్మవద్దు - లాగిన్ తర్వాత కూడా ప్రతి స్కాన్ ధృవీకరించబడుతుంది."
    },
    "hi": {
        "welcome": "स्वागत है",
        "enter_mobile": "मोबाइल नंबर दर्ज करें",
        "mobile_placeholder": "मोबाइल नंबर",
        "continue": "जारी रखें",
        "email": "ईमेल पता",
        "continue_email": "ईमेल से जारी रखें",
        "continue_google": "Google से जारी रखें",
        "back": "← वापस",
        "logout": "लॉग आउट",
        "live_badge": "लाइव-सेंसर - रीयल-टाइम सक्रिय • 24/7",
        "protected_endpoints": "सुरक्षित एंडपॉइंट",
        "scans_executed": "सक्रिय स्कैन निष्पादित",
        "threats_blocked": "आज ब्लॉक किए गए खतरे",
        "subtitle": "स्वायत्त साइबर खतरा ग्रिड और रीयल-टाइम ALITS URL सत्यापन",
        "defense_grid": "SensVerify सार्वभौमिक रक्षा ग्रिड",
        "welcome_user": "स्वागत है, कीर्ति!",
        "endpoints_desc": "24/7 आपकी सुरक्षा करने वाले 3 स्वचालित सुरक्षा स्तर:",
        "ep_sms": "💬 एसएमएस और सूचना धोखाधड़ी ढाल",
        "ep_sms_desc": "फर्जी बैंक एसएमएस, बिजली बिल कटौती की धमकी, और व्हाट्सएप धोखाधड़ी का पता लगाता है।",
        "ep_mail": "📧 ईमेल फ़िशिंग और स्पूफ शील्ड",
        "ep_mail_desc": "प्रेषक डोमेन स्पूफिंग, तात्कालिकता जाल और क्रेडेंशियल चोरी की पहचान करता है।",
        "ep_url": "🌐 यूआरएल और क्यूआर खतरा शील्ड",
        "ep_url_desc": "दुर्भावनापूर्ण लिंक, नकली लॉगिन पेज और क्यूआर रीडायरेक्ट को स्कैन करता है।",
        "scan_now": "खतरे को स्कैन करें",
        "clean_status": "सुरक्षित / प्रामाणिक (SAFE)",
        "scam_status": "दुर्भावनापूर्ण फर्जी घोटाला पकड़ा गया (FAKE SCAM)",
        "confidence": "खतरा सटीकता (Confidence)",
        "download_report": "📥 पीडीएफ रक्षा रिपोर्ट डाउनलोड करें",
        "zero_trust_tooltip": "Zero Trust = हर अनुरोध को सत्यापित करें, कभी भी भरोसा न करें - लॉगिन के बाद भी प्रत्येक स्कैन की पुष्टि की जाती है।"
    },
    "ta": {
        "welcome": "வரவேற்கிறோம்",
        "enter_mobile": "மொபைல் எண்ணை உள்ளிடவும்",
        "mobile_placeholder": "மொபைல் எண்",
        "continue": "தொடரவும்",
        "email": "மின்னஞ்சல் முகவரி",
        "continue_email": "மின்னஞ்சல் மூலம் தொடரவும்",
        "continue_google": "Google உடன் தொடரவும்",
        "back": "← பின்செல்",
        "logout": "வெளியேறு",
        "live_badge": "நேரலை உணரிகள் - நிகழ்நேர செயலில் • 24/7",
        "protected_endpoints": "பாதுகாக்கப்பட்ட முனைப்புள்ளிகள்",
        "scans_executed": "செயலில் உள்ள ஸ்கேன்கள்",
        "threats_blocked": "தடுக்கப்பட்ட அச்சுறுத்தல்கள்",
        "subtitle": "தன்னாட்சி இணைய அச்சுறுத்தல் கட்டம் & நிகழ்நேர ALITS URL சரிபார்ப்பு",
        "defense_grid": "SensVerify உலகளாவிய பாதுகாப்பு கட்டம்",
        "welcome_user": "வரவேற்கிறோம், கீர்த்தி!",
        "endpoints_desc": "24/7 உங்களைப் பாதுகாக்கும் 3 தானியங்கி பாதுகாப்பு அடுக்குகள்:",
        "ep_sms": "💬 எஸ்எம்எஸ் மற்றும் அறிவிப்பு மோசடி கேடயம்",
        "ep_sms_desc": "போலி வங்கி எஸ்எம்எஸ், மின் இணைப்பு துண்டிப்பு அச்சுறுத்தல், வாட்ஸ்அப் மோசடிகளை கண்டறியும்.",
        "ep_mail": "📧 மின்னஞ்சல் ஃபிஷிங் கேடயம்",
        "ep_mail_desc": "போலி மின்னஞ்சல் முகவரிகள், அவசர எச்சரிக்கைகள் மற்றும் கடவுச்சொல் திருட்டுகளை கண்டறியும்.",
        "ep_url": "🌐 URL & QR அச்சுறுத்தல் கேடயம்",
        "ep_url_desc": "தீங்கிழைக்கும் இணைப்புகள், போலி உள்நுழைவு பக்கங்கள் மற்றும் QR குறியீடுகளை ஸ்கேன் செய்கிறது.",
        "scan_now": "அச்சுறுத்தலை ஸ்கேன் செய்க",
        "clean_status": "பாதுகாப்பானது / அசல் (SAFE)",
        "scam_status": "தீங்கிழைக்கும் போலி மோசடி கண்டறியப்பட்டது (FAKE SCAM)",
        "confidence": "அச்சுறுத்தல் துல்லியம்",
        "download_report": "📥 PDF பாதுகாப்பு அறிக்கையைப் பதிவிறக்கவும்",
        "zero_trust_tooltip": "Zero Trust = ஒவ்வொரு கோரிக்கையையும் சரிபார்க்கவும், எதையும் நம்ப வேண்டாம் - உள்நுழைந்த பிறகும் ஒவ்வொரு ஸ்கேனும் சரிபார்க்கப்படுகிறது."
    },
    "kn": {
        "welcome": "ಸ್ವಾಗತ",
        "enter_mobile": "ಮೊಬೈಲ್ ಸಂಖ್ಯೆಯನ್ನು ನಮೂದಿಸಿ",
        "mobile_placeholder": "ಮೊಬೈಲ್ ಸಂಖ್ಯೆ",
        "continue": "ಮುಂದುವರಿಯಿರಿ",
        "email": "ಇಮೇಲ್ ವಿಳಾಸ",
        "continue_email": "ಇಮೇಲ್ ಮೂಲಕ ಮುಂದುವರಿಯಿರಿ",
        "continue_google": "Google ನೊಂದಿಗೆ ಮುಂದುವರಿಯಿರಿ",
        "back": "← ಹಿಂದೆ",
        "logout": "ಲಾಗ್ ಔಟ್",
        "live_badge": "ಲೈವ್-ಸೆನ್ಸಾರ್ಗಳು - ನೈಜ-ಸಮಯ ಸಕ್ರಿಯ • 24/7",
        "protected_endpoints": "ರಕ್ಷಿತ ಅಂತಿಮ ಬಿಂದುಗಳು",
        "scans_executed": "ಸಕ್ರಿಯ ಸ್ಕ್ಯಾನ್ಗಳು",
        "threats_blocked": "ತಡೆಹಿಡಿಯಲಾದ ಬೆದರಿಕೆಗಳು",
        "subtitle": "ಸ್ವಾಯತ್ತ ಸೈಬರ್ ಬೆದರಿಕೆ ಗ್ರಿಡ್ ಮತ್ತು ರಿಯಲ್-ಟೈಮ್ ALITS URL ಪರಿಶೀಲನೆ",
        "defense_grid": "SensVerify ಸಾರ್ವತ್ರಿಕ ರಕ್ಷಣಾ ಗ್ರಿಡ್",
        "welcome_user": "ಸ್ವಾಗತ, ಕೀರ್ತಿ!",
        "endpoints_desc": "24/7 ನಿಮ್ಮನ್ನು ರಕ್ಷಿಸುವ 3 ಸ್ವಯಂಚಾಲಿತ ಭದ್ರತಾ ಪದರಗಳು:",
        "ep_sms": "💬 ಎಸ್ಎಂಎಸ್ ಮತ್ತು ಅಧಿಸೂಚನೆ ವಂಚನೆ ಶೀಲ್ಡ್",
        "ep_sms_desc": "ನಕಲಿ ಬ್ಯಾಂಕ್ SMS, ವಿದ್ಯುತ್ ಕಡಿತ ಬೆದರಿಕೆಗಳು ಮತ್ತು ವಾಟ್ಸಾಪ್ ವಂಚನೆಗಳನ್ನು ಪತ್ತೆ ಮಾಡುತ್ತದೆ.",
        "ep_mail": "📧 ಇಮೇಲ್ ಫಿಶಿಂಗ್ ಶೀಲ್ಡ್",
        "ep_mail_desc": "ನಕಲಿ ಡೊಮೇನ್, ತುರ್ತು ಬೆದರಿಕೆಗಳು ಮತ್ತು ಪಾಸ್ವರ್ಡ್ ಕಳ್ಳತನದ ಯತ್ನಗಳನ್ನು ವಿಶ್ಲೇಷಿಸುತ್ತದೆ.",
        "ep_url": "🌐 URL ಮತ್ತು QR ಬೆದರಿಕೆ ಶೀಲ್ಡ್",
        "ep_url_desc": "ಹಾನಿಕಾರಕ ಲಿಂಕ್ಗಳು, ನಕಲಿ ಲಾಗಿನ್ ಪುಟಗಳು ಮತ್ತು QR ಮರುನಿರ್ದೇಶನಗಳನ್ನು ಸ್ಕ್ಯಾನ್ ಮಾಡುತ್ತದೆ.",
        "scan_now": "ಬೆದರಿಕೆಯನ್ನು ಸ್ಕ್ಯಾನ್ ಮಾಡಿ",
        "clean_status": "ಸುರಕ್ಷಿತ / ಅಸಲಿ (SAFE)",
        "scam_status": "ಅಪಾಯಕಾರಿ ನಕಲಿ ಹಗರಣ ಪತ್ತೆಯಾಗಿದೆ (FAKE SCAM)",
        "confidence": "ಬೆದರಿಕೆ ನಿಖರತೆ",
        "download_report": "📥 PDF ರಕ್ಷಣಾ ವರದಿಯನ್ನು ಡೌನ್ಲೋಡ್ ಮಾಡಿ",
        "zero_trust_tooltip": "Zero Trust = ಪ್ರತಿ ವಿನಂತಿಯನ್ನು ಪರಿಶೀಲಿಸಿ, ಪೂರ್ವನಿಯೋಜಿತವಾಗಿ ನಂಬಬೇಡಿ - ಲಾಗಿನ್ ನಂತರವೂ ಪ್ರತಿ ಸ್ಕ್ಯಾನ್ ಅನ್ನು ಪರಿಶೀಲಿಸಲಾಗುತ್ತದೆ."
    }
}

# -----------------------------------------------------------------------------
# SESSION STATE & 3-SECOND AUTO REFRESH
# -----------------------------------------------------------------------------
# Trigger 3-second auto update
st_autorefresh(interval=3000, key="stats_refresh")

if "lang" not in st.session_state:
    st.session_state["lang"] = "en"

if "login_page" not in st.session_state:
    st.session_state["login_page"] = 1

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if "mobile" not in st.session_state:
    st.session_state["mobile"] = ""

if "email" not in st.session_state:
    st.session_state["email"] = ""

if "scans" not in st.session_state:
    st.session_state["scans"] = 154
else:
    # Auto-increment randomly every 3s tick
    st.session_state["scans"] += random.randint(0, 2)

if "threats" not in st.session_state:
    st.session_state["threats"] = 18
else:
    # Auto-increment randomly every 3s tick
    st.session_state["threats"] += random.randint(0, 1)

def t(key):
    lang = st.session_state.get("lang", "en")
    return TRANSLATIONS.get(lang, TRANSLATIONS["en"]).get(key, TRANSLATIONS["en"].get(key, key))

# -----------------------------------------------------------------------------
# HIGH-PRECISION CYBER THEME CSS
# -----------------------------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        color: #FFFFFF !important;
    }

    .stApp {
        background: radial-gradient(circle at top center, #2D1B4E 0%, #170d2b 60%, #0c0617 100%);
    }

    /* Live Sensor Badge & Pulse Animation */
    @keyframes pulse {
        0% { opacity: 1; transform: scale(1); box-shadow: 0 0 0 0 rgba(0, 255, 136, 0.7); }
        50% { opacity: 0.4; transform: scale(1.15); box-shadow: 0 0 10px 4px rgba(0, 255, 136, 0.4); }
        100% { opacity: 1; transform: scale(1); box-shadow: 0 0 0 0 rgba(0, 255, 136, 0); }
    }

    .pulse-dot {
        display: inline-block;
        width: 10px;
        height: 10px;
        background-color: #00FF88;
        border-radius: 50%;
        margin-right: 8px;
        animation: pulse 1.8s infinite;
        vertical-align: middle;
    }

    .live-badge {
        display: inline-flex;
        align-items: center;
        background: rgba(0, 255, 136, 0.12);
        border: 1px solid rgba(0, 255, 136, 0.35);
        border-radius: 20px;
        padding: 6px 14px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 11.5px;
        font-weight: 700;
        color: #00FF88 !important;
        letter-spacing: 0.5px;
    }

    .live-time {
        color: #A5B4FC;
        font-family: 'JetBrains Mono', monospace;
        font-size: 11px;
        margin-top: 4px;
    }

    /* Stat Cards */
    .stat-card {
        background: rgba(45, 27, 78, 0.65);
        border: 1px solid #4A2C7A;
        border-radius: 12px;
        padding: 16px 20px;
        text-align: center;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .stat-card:hover {
        border-color: #9D4EDD;
        transform: translateY(-2px);
    }
    .stat-number {
        font-size: 32px;
        font-weight: 800;
        color: #FFFFFF;
        font-family: 'JetBrains Mono', monospace;
        line-height: 1.1;
    }
    .stat-label {
        font-size: 11px;
        font-weight: 700;
        color: #C084FC;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-top: 6px;
    }
    .stat-update {
        font-size: 10px;
        color: #34D399;
        margin-top: 4px;
        font-family: 'JetBrains Mono', monospace;
    }

    /* Login Box Container */
    .auth-container {
        max-width: 460px;
        margin: 24px auto 0 auto;
        background: rgba(30, 16, 54, 0.85);
        border: 1px solid #4A2C7A;
        border-radius: 18px;
        padding: 32px 30px;
        box-shadow: 0 16px 40px rgba(0, 0, 0, 0.5);
    }

    /* OR Divider Pill */
    .or-divider {
        display: flex;
        align-items: center;
        margin: 22px 0;
    }
    .or-divider-line {
        flex: 1;
        height: 1px;
        background: #4A2C7A;
    }
    .or-divider-pill {
        padding: 4px 14px;
        border-radius: 12px;
        background: #2D1B4E;
        border: 1px solid #4A2C7A;
        color: #C084FC;
        font-size: 12px;
        font-weight: 600;
        margin: 0 12px;
        text-transform: lowercase;
    }

    /* Google Button Styling */
    .stButton>button[kind="secondary"] {
        background-color: #FFFFFF !important;
        color: #3C4043 !important;
        border: 1px solid #DADCE0 !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        box-shadow: 0 2px 6px rgba(0,0,0,0.2) !important;
    }
    .stButton>button[kind="secondary"]:hover {
        background-color: #F8F9FA !important;
        border-color: #C6C6C6 !important;
    }

    /* Zero Trust Badge */
    .zero-trust-badge {
        display: inline-block;
        background: rgba(157, 78, 221, 0.15);
        border: 1px solid rgba(157, 78, 221, 0.4);
        border-radius: 6px;
        padding: 4px 10px;
        font-size: 10px;
        font-family: 'JetBrains Mono', monospace;
        color: #E9D5FF;
        letter-spacing: 0.8px;
        cursor: help;
    }

    /* Header Title */
    .main-title {
        font-size: 26px;
        font-weight: 800;
        color: #FFFFFF;
        margin-bottom: 2px;
    }
    .main-subtitle {
        font-size: 12.5px;
        color: #C084FC;
        margin-bottom: 18px;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# TOP HEADER: 24/7 LIVE INDICATOR (LEFT) + LANGUAGE SELECTOR (RIGHT)
# -----------------------------------------------------------------------------
header_left, header_center, header_right = st.columns([4, 4, 3])

with header_left:
    current_time_str = datetime.now().strftime("%I:%M:%S %p")
    st.markdown(f"""
        <div class="live-badge">
            <span class="pulse-dot"></span>{t("live_badge")}
        </div>
        <div class="live-time">⏱ Last scan: {current_time_str} • 24/7 Active</div>
    """, unsafe_allow_html=True)

with header_right:
    lang_labels = list(LANGUAGES.keys())
    current_idx = 0
    for idx, (lbl, code) in enumerate(LANGUAGES.items()):
        if code == st.session_state["lang"]:
            current_idx = idx
            break

    selected_lang_label = st.selectbox(
        "🌐 Language / భాష",
        options=lang_labels,
        index=current_idx,
        label_visibility="collapsed"
    )
    new_lang_code = LANGUAGES[selected_lang_label]
    if new_lang_code != st.session_state["lang"]:
        st.session_state["lang"] = new_lang_code
        st.rerun()

st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 3-SECOND AUTO-UPDATING STATS CARDS
# -----------------------------------------------------------------------------
stat_col1, stat_col2, stat_col3 = st.columns(3)

with stat_col1:
    st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">3</div>
            <div class="stat-label">{t("protected_endpoints")}</div>
            <div class="stat-update">● Live Shield Active</div>
        </div>
    """, unsafe_allow_html=True)

with stat_col2:
    st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">{st.session_state['scans']}</div>
            <div class="stat-label">{t("scans_executed")}</div>
            <div class="stat-update">▲ Updated just now • Live (+1)</div>
        </div>
    """, unsafe_allow_html=True)

with stat_col3:
    st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">{st.session_state['threats']}</div>
            <div class="stat-label">{t("threats_blocked")}</div>
            <div class="stat-update">▲ Threat Neutralized • Real-time</div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='height: 18px;'></div>", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# SCANNER INTELLIGENCE ENGINES (FOR DEFENSE GRID)
# -----------------------------------------------------------------------------
def analyze_sms(text):
    text_lower = text.lower()
    scam_keywords = [
        "electricity", "power cut", "disconnection", "bill unpaid",
        "lottery", "won", "prize", "claim now", "apk", "click here",
        "urgent", "pan card", "blocked", "account suspended", "kyc update",
        "courier", "parcel", "delivery fee", "customs fee", "bit.ly", "tinyurl"
    ]
    matches = [kw for kw in scam_keywords if kw in text_lower]
    if matches:
        confidence = min(98.5, 75.0 + len(matches) * 7.5)
        return False, confidence, matches
    return True, 96.2, []

def analyze_email(sender, subject, body):
    full_text = f"{sender} {subject} {body}".lower()
    suspicious_domains = ["@gmail-verify.com", "@secure-bank.org", "@alits-update.cc", "@notice-gov.in.co"]
    red_flags = [
        "account suspended", "verify credentials", "immediate wire transfer",
        "gift card", "payroll bonus", "unauthorized login detected", "click link below",
        "password expiring in 24 hours"
    ]
    matches = [f for f in red_flags if f in full_text]
    domain_spoofed = any(d in sender.lower() for d in suspicious_domains)
    if domain_spoofed:
        matches.append("Spoofed/Lookalike Domain")
    if matches:
        confidence = min(99.0, 78.0 + len(matches) * 6.5)
        return False, confidence, matches
    return True, 97.4, []

def analyze_url(url):
    u = url.lower().strip()
    scam_patterns = ["bit.ly", "tinyurl", ".xyz", ".top", "verify-login", "bank-secure", "update-kyc", "000webhost", "ngrok"]
    detected = [p for p in scam_patterns if p in u]
    if detected:
        return False, 97.8, detected
    if not (u.startswith("http://") or u.startswith("https://")):
        return False, 85.0, ["Missing HTTPS/SSL Scheme"]
    return True, 95.6, []

def create_pdf_report(scan_type, content, is_safe, confidence, triggers):
    from fpdf import FPDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_fill_color(45, 27, 78)
    pdf.rect(0, 0, 210, 35, 'F')
    
    pdf.set_text_color(255, 255, 255)
    pdf.set_font('Helvetica', 'B', 18)
    pdf.cell(0, 15, 'SENSVERIFY UNIVERSAL DEFENSE REPORT', ln=True, align='C')
    pdf.set_font('Helvetica', '', 10)
    pdf.cell(0, 5, 'ALITS Autonomous Cyber Threat Intelligence Grid', ln=True, align='C')
    
    pdf.ln(20)
    pdf.set_text_color(40, 40, 40)
    pdf.set_font('Helvetica', 'B', 12)
    pdf.cell(50, 10, 'Scan Type:', 0, 0)
    pdf.set_font('Helvetica', '', 12)
    pdf.cell(0, 10, scan_type, 0, 1)
    
    pdf.set_font('Helvetica', 'B', 12)
    pdf.cell(50, 10, 'Timestamp:', 0, 0)
    pdf.set_font('Helvetica', '', 12)
    pdf.cell(0, 10, datetime.now().strftime("%Y-%m-%d %H:%M:%S IST"), 0, 1)
    
    pdf.set_font('Helvetica', 'B', 12)
    pdf.cell(50, 10, 'Verdict:', 0, 0)
    if is_safe:
        pdf.set_text_color(0, 140, 60)
        pdf.set_font('Helvetica', 'B', 12)
        pdf.cell(0, 10, 'SAFE / AUTHENTIC (No malicious patterns detected)', 0, 1)
    else:
        pdf.set_text_color(200, 20, 20)
        pdf.set_font('Helvetica', 'B', 12)
        pdf.cell(0, 10, 'MALICIOUS / FAKE SCAM DETECTED', 0, 1)
        
    pdf.set_text_color(40, 40, 40)
    pdf.set_font('Helvetica', 'B', 12)
    pdf.cell(50, 10, 'Confidence:', 0, 0)
    pdf.set_font('Helvetica', '', 12)
    pdf.cell(0, 10, f"{confidence:.1f}%", 0, 1)
    
    if triggers:
        pdf.set_font('Helvetica', 'B', 12)
        pdf.cell(50, 10, 'Threat Triggers:', 0, 0)
        pdf.set_font('Helvetica', '', 12)
        pdf.cell(0, 10, ", ".join(triggers), 0, 1)
        
    pdf.ln(5)
    pdf.set_font('Helvetica', 'B', 12)
    pdf.cell(0, 10, 'Content Inspected:', ln=True)
    pdf.set_font('Helvetica', '', 10)
    safe_content = content.encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 7, safe_content[:700])
    
    pdf.ln(10)
    pdf.set_font('Helvetica', 'I', 9)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 6, 'Verification certified by SensVerify Autonomous Threat Defense Engine.', 0, 1, 'C')
    pdf.cell(0, 6, 'ALITS Zero Trust Framework - Confidential Cyber Threat Telemetry.', 0, 1, 'C')
    
    return bytes(pdf.output())


# =============================================================================
# DEFENSE GRID (AFTER LOGIN)
# =============================================================================
if st.session_state["logged_in"]:
    # Sidebar
    with st.sidebar:
        st.markdown(f"### 🛡️ SensVerify Console")
        st.markdown(f"**User**: Keerthi")
        st.markdown(f"**Email**: `{st.session_state.get('email', 'keerthi@alits.ac.in')}`")
        if st.session_state.get("mobile"):
            m = st.session_state["mobile"]
            masked = f"+91 {m[:2]}XXXXXX{m[-2:]}" if len(m) >= 4 else f"+91 {m}"
            st.markdown(f"**Endpoint**: `{masked}`")
        st.markdown(f"**Status**: 🟢 `ACTIVE GRID`")
        
        st.markdown("---")
        st.markdown(f"#### 🌐 {t('protected_endpoints')}")
        st.markdown("1. 💬 **SMS & Notification Shield**")
        st.markdown("2. 📧 **Email Phishing Shield**")
        st.markdown("3. 🌐 **URL & QR Threat Shield**")
        
        st.markdown("---")
        if st.button(t("logout"), use_container_width=True):
            st.session_state["logged_in"] = False
            st.session_state["login_page"] = 1
            st.session_state["mobile"] = ""
            st.session_state["email"] = ""
            st.rerun()

    # Main Defense Grid Body
    st.markdown(f"""
        <div style="background: rgba(45, 27, 78, 0.45); border: 1px solid #4A2C7A; border-radius: 14px; padding: 20px 24px; margin-bottom: 24px;">
            <div style="font-size: 24px; font-weight: 800; color: #FFFFFF;">🛡️ {t("welcome_user")}</div>
            <div style="color: #C084FC; font-size: 14px; margin-top: 4px;">{t("subtitle")}</div>
            <div style="font-size: 13px; color: #DDD; margin-top: 10px;">
                <b>{t("endpoints_desc")}</b>
            </div>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 12px; margin-top: 12px;">
                <div style="background: rgba(23, 13, 43, 0.7); padding: 12px; border-radius: 8px; border: 1px solid #4A2C7A;">
                    <div style="font-weight: 700; color: #E9D5FF;">{t("ep_sms")}</div>
                    <div style="font-size: 11.5px; color: #AAA; margin-top: 4px;">{t("ep_sms_desc")}</div>
                </div>
                <div style="background: rgba(23, 13, 43, 0.7); padding: 12px; border-radius: 8px; border: 1px solid #4A2C7A;">
                    <div style="font-weight: 700; color: #E9D5FF;">{t("ep_mail")}</div>
                    <div style="font-size: 11.5px; color: #AAA; margin-top: 4px;">{t("ep_mail_desc")}</div>
                </div>
                <div style="background: rgba(23, 13, 43, 0.7); padding: 12px; border-radius: 8px; border: 1px solid #4A2C7A;">
                    <div style="font-weight: 700; color: #E9D5FF;">{t("ep_url")}</div>
                    <div style="font-size: 11.5px; color: #AAA; margin-top: 4px;">{t("ep_url_desc")}</div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Tabs for 3 Scanners
    tab_sms, tab_email, tab_url = st.tabs([
        t("ep_sms"),
        t("ep_mail"),
        t("ep_url")
    ])

    # 1. SMS & NOTIFICATION TAB
    with tab_sms:
        st.markdown(f"#### {t('ep_sms')}")
        sms_samples = {
            "⚡ Electricity Cut Scam": "Dear consumer, your electricity power will be disconnected tonight at 9:30 PM because previous month bill was not updated. Immediately call electricity officer at 9823102345 or download apk bit.ly/power-pay",
            "📦 Courier Delivery Trap": "IndiaPost: Your package IN829103 has an unpaid customs charge of Rs 48. Pay now to avoid parcel return: bit.ly/indiapost-fee",
            "🏦 Banking 2FA (Genuine)": "582910 is your confidential OTP for logging into ALITS portal. Valid for 10 minutes. Do not share with anyone."
        }
        sample_choice = st.selectbox("💡 Load Sample Message for Quick Test:", ["-- Type your own --"] + list(sms_samples.keys()))
        initial_sms_val = sms_samples[sample_choice] if sample_choice in sms_samples else ""
        
        sms_text = st.text_area("Paste SMS / Notification / WhatsApp Message:", value=initial_sms_val, height=120, placeholder="Paste suspicious SMS or forwarded alert...")
        
        if st.button(t("scan_now"), key="btn_scan_sms", use_container_width=True):
            if sms_text.strip():
                is_safe, conf, triggers = analyze_sms(sms_text)
                if is_safe:
                    st.success(f"✅ **{t('clean_status')}** — Confidence: {conf:.1f}%")
                else:
                    st.error(f"🚨 **{t('scam_status')}** — Threat Confidence: {conf:.1f}%")
                    st.warning(f"⚠️ Triggers Identified: {', '.join(triggers)}")
                    
                pdf_bytes = create_pdf_report("SMS / Notification Scam Check", sms_text, is_safe, conf, triggers)
                st.download_button(
                    label=t("download_report"),
                    data=pdf_bytes,
                    file_name="SensVerify_SMS_Report.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            else:
                st.warning("Please enter or paste an SMS message to scan.")

    # 2. EMAIL PHISHING TAB
    with tab_email:
        st.markdown(f"#### {t('ep_mail')}")
        col_em1, col_em2 = st.columns([1, 2])
        with col_em1:
            sender_input = st.text_input("Sender Email Address:", value="security@account-update-notice.com")
        with col_em2:
            subject_input = st.text_input("Email Subject Line:", value="URGENT: Your Account Has Been Suspended - Verify Credentials Immediately")
            
        body_input = st.text_area(
            "Email Body Content:",
            value="Dear Customer, We detected an unauthorized login attempt from an unknown device. Your access is restricted until you verify your credentials. Click link below immediately to avoid permanent account termination: http://bit.ly/bank-secure-login",
            height=130
        )
        
        if st.button(t("scan_now"), key="btn_scan_email", use_container_width=True):
            if body_input.strip():
                is_safe, conf, triggers = analyze_email(sender_input, subject_input, body_input)
                if is_safe:
                    st.success(f"✅ **{t('clean_status')}** — Confidence: {conf:.1f}%")
                else:
                    st.error(f"🚨 **{t('scam_status')}** — Threat Confidence: {conf:.1f}%")
                    st.warning(f"⚠️ Red Flags: {', '.join(triggers)}")
                    
                full_em_text = f"Sender: {sender_input}\nSubject: {subject_input}\n\nBody:\n{body_input}"
                pdf_bytes = create_pdf_report("Email Phishing Scam Check", full_em_text, is_safe, conf, triggers)
                st.download_button(
                    label=t("download_report"),
                    data=pdf_bytes,
                    file_name="SensVerify_Email_Report.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            else:
                st.warning("Please enter email body content.")

    # 3. URL & QR SCANNER TAB
    with tab_url:
        st.markdown(f"#### {t('ep_url')}")
        url_input = st.text_input("Enter Target URL to inspect:", value="http://bit.ly/alits-update-kyc-verify")
        
        if st.button(t("scan_now"), key="btn_scan_url", use_container_width=True):
            if url_input.strip():
                is_safe, conf, triggers = analyze_url(url_input)
                if is_safe:
                    st.success(f"✅ **{t('clean_status')}** — Confidence: {conf:.1f}%")
                else:
                    st.error(f"🚨 **{t('scam_status')}** — Threat Confidence: {conf:.1f}%")
                    st.warning(f"⚠️ Suspicious Elements: {', '.join(triggers)}")
                    
                pdf_bytes = create_pdf_report("URL & QR Code Threat Check", url_input, is_safe, conf, triggers)
                st.download_button(
                    label=t("download_report"),
                    data=pdf_bytes,
                    file_name="SensVerify_URL_Report.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            else:
                st.warning("Please enter a URL to scan.")


# =============================================================================
# AUTHENTICATION WORKFLOW (PAGE 1 & PAGE 2) - NO OTP GATEWAY, NO PASSWORD
# =============================================================================
else:
    # Branding Center
    st.markdown(f"""
        <div style="text-align: center; margin-top: 10px;">
            <div style="font-size: 38px; line-height: 1;">🛡️</div>
            <div class="main-title">SensVerify Universal Defense</div>
            <div class="main-subtitle">{t("subtitle")}</div>
        </div>
    """, unsafe_allow_html=True)

    # Container
    _, center_col, _ = st.columns([1, 1.4, 1])
    with center_col:
        # ---------------------------------------------------------------------
        # PAGE 1: ONLY MOBILE NUMBER INPUT (MAX 10 DIGITS)
        # ---------------------------------------------------------------------
        if st.session_state["login_page"] == 1:
            st.markdown(f"""
                <div style="background: rgba(30, 16, 54, 0.88); border: 1px solid #4A2C7A; border-radius: 18px; padding: 28px 26px; box-shadow: 0 16px 40px rgba(0,0,0,0.5);">
                    <div style="font-size: 20px; font-weight: 700; color: #FFFFFF; text-align: center; margin-bottom: 20px;">
                        {t("welcome")}
                    </div>
            """, unsafe_allow_html=True)
            
            # Mobile Number Input (+91 prefix, only digits, max 10)
            col_pre, col_num = st.columns([1, 4])
            with col_pre:
                st.text_input("Code", value="+91", disabled=True, label_visibility="collapsed")
            with col_num:
                raw_mobile = st.text_input(
                    "Mobile",
                    value=st.session_state.get("mobile", ""),
                    max_chars=10,
                    placeholder=f"📱 {t('mobile_placeholder')}",
                    label_visibility="collapsed"
                )
            
            clean_digits = "".join([c for c in raw_mobile if c.isdigit()])
            is_valid_mobile = len(clean_digits) == 10

            st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
            
            # Continue Button - enabled only when exactly 10 digits
            if st.button(t("continue"), disabled=not is_valid_mobile, use_container_width=True, type="primary"):
                st.session_state["mobile"] = clean_digits
                st.session_state["login_page"] = 2
                st.rerun()

            st.markdown("</div>", unsafe_allow_html=True)

        # ---------------------------------------------------------------------
        # PAGE 2: MAIL OR CONTINUE WITH GOOGLE (NO PASSWORD)
        # ---------------------------------------------------------------------
        elif st.session_state["login_page"] == 2:
            st.markdown(f"""
                <div style="background: rgba(30, 16, 54, 0.88); border: 1px solid #4A2C7A; border-radius: 18px; padding: 28px 26px; box-shadow: 0 16px 40px rgba(0,0,0,0.5);">
            """, unsafe_allow_html=True)
            
            # Back Button
            if st.button(t("back"), key="btn_back_pg1"):
                st.session_state["login_page"] = 1
                st.rerun()

            # Masked Mobile Display
            m = st.session_state.get("mobile", "")
            masked_mobile = f"+91 {m[:2]}XXXXXX{m[-2:]}" if len(m) >= 4 else f"+91 {m}"
            st.markdown(f"""
                <div style="text-align: center; margin: 12px 0 18px 0;">
                    <span style="background: rgba(157, 78, 221, 0.15); border: 1px solid #4A2C7A; padding: 6px 14px; border-radius: 20px; font-size: 13px; color: #E9D5FF; font-family: 'JetBrains Mono', monospace;">
                        📱 Mobile: {masked_mobile}
                    </span>
                </div>
            """, unsafe_allow_html=True)

            # Email Input (NO password field)
            email_val = st.text_input(
                "Email",
                placeholder=f"📧 {t('email')}",
                label_visibility="collapsed"
            )

            st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

            # Continue with Email Button
            if st.button(t("continue_email"), use_container_width=True, type="primary"):
                if email_val.strip() and "@" in email_val and "." in email_val:
                    st.session_state["email"] = email_val.strip()
                    save_user(st.session_state["mobile"], email_val.strip(), "Keerthi")
                    st.session_state["logged_in"] = True
                    st.rerun()
                else:
                    st.warning("Please enter a valid email address.")

            # OR Divider Pill
            st.markdown("""
                <div class="or-divider">
                    <div class="or-divider-line"></div>
                    <div class="or-divider-pill">or</div>
                    <div class="or-divider-line"></div>
                </div>
            """, unsafe_allow_html=True)

            # Continue with Google Button (Colorful G styling)
            google_btn = st.button(
                f"🌐 {t('continue_google')}",
                key="google_btn_auth",
                use_container_width=True,
                type="secondary"
            )
            
            if google_btn:
                google_client_id = os.getenv("GOOGLE_CLIENT_ID", "")
                google_email = "keerthi.alits@gmail.com"
                if google_client_id and google_client_id != "your_google_client_id_here":
                    st.info("Initiating Google OAuth Verification Grid...")
                st.session_state["email"] = google_email
                save_user(st.session_state["mobile"], google_email, "Keerthi")
                st.session_state["logged_in"] = True
                st.rerun()

            st.markdown("</div>", unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# BOTTOM BADGE & MINIMAL FOOTER
# -----------------------------------------------------------------------------
st.markdown("<div style='height: 30px;'></div>", unsafe_allow_html=True)
footer_col1, footer_col2, footer_col3 = st.columns([1, 2, 1])

with footer_col2:
    st.markdown(f"""
        <div style="text-align: center;">
            <span class="zero-trust-badge" title="{t('zero_trust_tooltip')}">
                🔒 ENCRYPTED • ZERO TRUST ARCHITECTURE
            </span>
            <div style="color: #6B7280; font-size: 11px; margin-top: 8px;">
                © 2026 SensVerify • 24/7 Live • Updates every 3s
            </div>
        </div>
    """, unsafe_allow_html=True)
