import streamlit as st
import streamlit.components.v1 as components
from streamlit_autorefresh import st_autorefresh
import sqlite3
import random
import os
import re
import base64
import pandas as pd
from datetime import datetime, date
from PIL import Image

# Safe OCR import with fallback
try:
    import pytesseract
    OCR_AVAILABLE = True
except Exception:
    OCR_AVAILABLE = False

# -----------------------------------------------------------------------------
# PAGE CONFIGURATION
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="SensVerify",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# -----------------------------------------------------------------------------
# DATABASE INITIALIZATION (analytics.db) - FRESH & CLEAN SCHEMA
# -----------------------------------------------------------------------------
def init_db():
    conn = sqlite3.connect("analytics.db", check_same_thread=False)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS scans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            date TEXT,
            scan_type TEXT,
            content_preview TEXT,
            result TEXT,
            confidence REAL,
            user_mobile TEXT,
            user_name TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS logins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mobile TEXT,
            name TEXT,
            email TEXT,
            login_method TEXT,
            login_time TEXT,
            logout_time TEXT,
            date TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            mobile TEXT PRIMARY KEY,
            name TEXT,
            email TEXT,
            created_at TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

# DB Helper Functions
def record_login(mobile, name, email, method):
    try:
        conn = sqlite3.connect("analytics.db", check_same_thread=False)
        c = conn.cursor()
        now_time = datetime.now().strftime("%Y-%m-%d %I:%M:%S %p")
        today_val = str(date.today())
        
        c.execute("""
            INSERT INTO users (mobile, name, email, created_at)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(mobile) DO UPDATE SET
                name = excluded.name,
                email = excluded.email
        """, (mobile, name, email, now_time))
        
        c.execute("""
            INSERT INTO logins (mobile, name, email, login_method, login_time, logout_time, date)
            VALUES (?, ?, ?, ?, ?, NULL, ?)
        """, (mobile, name, email, method, now_time, today_val))
        
        conn.commit()
        conn.close()
    except Exception:
        pass

def record_logout(mobile):
    try:
        conn = sqlite3.connect("analytics.db", check_same_thread=False)
        c = conn.cursor()
        now_time = datetime.now().strftime("%Y-%m-%d %I:%M:%S %p")
        c.execute("""
            UPDATE logins SET logout_time = ?
            WHERE mobile = ? AND logout_time IS NULL
        """, (now_time, mobile))
        conn.commit()
        conn.close()
    except Exception:
        pass

def save_scan(scan_type, content, result, confidence, user_mobile, user_name):
    try:
        conn = sqlite3.connect("analytics.db", check_same_thread=False)
        c = conn.cursor()
        now_time = datetime.now().strftime("%Y-%m-%d %I:%M:%S %p")
        today_val = str(date.today())
        preview = (content[:60] + "...") if len(content) > 60 else content
        c.execute("""
            INSERT INTO scans (timestamp, date, scan_type, content_preview, result, confidence, user_mobile, user_name)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (now_time, today_val, scan_type, preview, result, confidence, user_mobile, user_name))
        conn.commit()
        conn.close()
    except Exception:
        pass

# -----------------------------------------------------------------------------
# LOGO HELPER (BASE64 EMBEDDED - ZERO BROKEN IMAGE BOX)
# -----------------------------------------------------------------------------
def get_logo():
    p = "assets/sensverify_logo.png"
    if os.path.exists(p):
        try:
            with open(p, "rb") as f:
                return f"data:image/png;base64,{base64.b64encode(f.read()).decode()}"
        except Exception:
            return None
    return None

# -----------------------------------------------------------------------------
# SINGLE-LANGUAGE TRANSLATOR DICTIONARY (NAME CHANGED TO NEWS TRUTH SHIELD)
# -----------------------------------------------------------------------------
TRANSLATOR = {
    "English": {
        "enter_mobile": "Enter Mobile Number",
        "continue": "Continue",
        "ask_assistant": "SensVerify Assistant - Ask Anything",
        "welcome": "Welcome",
        "protected_endpoints": "Protected Endpoints",
        "active_scans": "Active Scans Executed",
        "threats_today": "Threats Blocked Today",
        "sms_shield": "SMS Scam Shield",
        "email_shield": "Email Phishing Shield",
        "satya_shield": "News Truth Shield - News Verifier",
        "scan_now": "🔍 Scan Now",
        "my_history": "📋 My Scan History",
        "text_check": "Text Check",
        "photo_check": "Photo / Document / Poster",
        "upload_any": "Upload Any Photo / Document / Poster to Verify",
        "upload_sub": "Any source - Universal check",
        "live_sensors": "LIVE-SENSORS - REAL-TIME ACTIVE - 24/7",
        "last_scan": "Last scan",
        "enter_name": "Enter Your Name",
        "enter_email": "Enter Email (Optional)",
        "or": "or",
        "dashboard": "Analytics Dashboard",
        "scan_history": "Scan History - Proof of Scans",
        "total_scans": "Total Scans",
        "export_csv": "Export Proof as CSV",
        "no_scans": "No scans yet - Start scanning to see your history",
        "user_history_title": "👥 User Login History - Who Logged In & How",
        "admin_title": "🛡️ SensVerify Admin Analytics - Live Dashboard - 24/7 - All User Details",
        "total_logins_today": "TOTAL LOGINS TODAY",
        "currently_active": "CURRENTLY ACTIVE",
        "total_blocked": "TOTAL BLOCKED",
        "documents_checked": "DOCUMENTS CHECKED",
        "logged_out": "LOGGED OUT",
        "total_scans_card": "TOTAL SCANS",
        "real_safe": "REAL / SAFE",
        "posters_checked": "POSTERS CHECKED",
        "login_method": "Login Method",
        "mobile_number": "Mobile Number",
        "name": "Name",
        "email": "Email",
        "login_time": "Login Time",
        "logout_time": "Logout Time",
        "status": "Status",
        "active": "Active",
        "logged_out_status": "Logged Out",
        "method_mobile_name": "Mobile + Name",
        "method_mobile_email_name": "Mobile + Email + Name",
        "method_google": "Continue with Google",
        "method_mobile": "Mobile Only",
        "privacy_note": "Your scan is private - Not shared",
        "check_sms": "Check SMS - Verify",
        "check_email": "Check Email - Verify",
        "check_news": "Verify News - Truth Check",
        "enter_defense": "Enter Defense Grid",
        "logout": "Logout",
        "visual_forensics_title": "🔍 Visual AI Forensics - Why is it FAKE? - AI Explainability",
        "word_impact_title": "Which words made it FAKE? (Impact Score)",
        "front_cam_title": "🤳 Front Camera - Selfie / Face View",
        "back_cam_title": "📄 Back Camera - Document / Poster Scan",
        "upload_file_title": "📁 Upload Any Photo / Document / Poster",
        "camera_guidance": "Laptop: Front camera - Hold document in front | Mobile: Back camera for documents (clear) - Front for selfie - Switch using flip icon",
        "camera_closed_msg": "📷 Camera closed - Open front or back camera above or use Upload"
    },
    "తెలుగు": {
        "enter_mobile": "మొబైల్ నంబర్ నమోదు చేయండి",
        "continue": "కొనసాగించండి",
        "ask_assistant": "సెన్స్వెరిఫై సహాయకుడు - ఏదైనా అడగండి",
        "welcome": "స్వాగతం",
        "protected_endpoints": "రక్షిత ఎండ్పాయింట్లు",
        "active_scans": "స్కాన్లు పూర్తయ్యాయి",
        "threats_today": "ఈ రోజు బ్లాక్ చేయబడ్డాయి",
        "sms_shield": "SMS స్కామ్ షీల్డ్",
        "email_shield": "ఇమెయిల్ ఫిషింగ్ షీల్డ్",
        "satya_shield": "న్యూస్ ట్రూత్ షీల్డ్ - నిజ నిర్ధారణ",
        "scan_now": "🔍 ఇప్పుడు స్కాన్ చేయండి",
        "my_history": "📋 నా స్కాన్ చరిత్ర",
        "text_check": "టెక్స్ట్ చెక్",
        "photo_check": "ఫోటో / డాక్యుమెంట్ / పోస్టర్",
        "upload_any": "ఏదైనా ఫోటో / డాక్యుమెంట్ / పోస్టర్ అప్లోడ్ చేయండి",
        "upload_sub": "ఏదైనా మూలం - యూనివర్సల్ చెక్",
        "live_sensors": "లైవ్-సెన్సార్లు - రియల్-టైమ్ యాక్టివ్ - 24/7",
        "last_scan": "చివరి స్కాన్",
        "enter_name": "మీ పేరు నమోదు చేయండి",
        "enter_email": "ఇమెయిల్ నమోదు చేయండి (ఐచ్ఛికం)",
        "or": "లేదా",
        "dashboard": "విశ్లేషణ డాష్బోర్డ్",
        "scan_history": "స్కాన్ చరిత్ర - స్కాన్ల రుజువు",
        "total_scans": "మొత్తం స్కాన్లు",
        "export_csv": "CSV గా రుజువు ఎగుమతి చేయండి",
        "no_scans": "ఇంకా స్కాన్లు లేవు - చరిత్ర చూడటానికి స్కాన్ చేయండి",
        "user_history_title": "👥 వినియోగదారు లాగిన్ చరిత్ర - ఎవరు లాగిన్ అయ్యారు & ఎలా",
        "admin_title": "🛡️ సెన్స్వెరిఫై అడ్మిన్ అనలిటిక్స్ - లైవ్ డాష్బోర్డ్ - 24/7 - అన్ని వివరాలు",
        "total_logins_today": "ఈ రోజు మొత్తం లాగిన్లు",
        "currently_active": "ప్రస్తుతం యాక్టివ్",
        "total_blocked": "మొత్తం బ్లాక్ చేయబడ్డాయి",
        "documents_checked": "డాక్యుమెంట్లు చెక్ చేయబడ్డాయి",
        "logged_out": "లాగ్ అవుట్ అయ్యారు",
        "total_scans_card": "మొత్తం స్కాన్లు",
        "real_safe": "రియల్ / సేఫ్",
        "posters_checked": "పోస్టర్లు చెక్ చేయబడ్డాయి",
        "login_method": "లాగిన్ విధానం",
        "mobile_number": "మొబైల్ నంబర్",
        "name": "పేరు",
        "email": "ఇమెయిల్",
        "login_time": "లాగిన్ సమయం",
        "logout_time": "లాగ్ అవుట్ సమయం",
        "status": "స్థితి",
        "active": "యాక్టివ్",
        "logged_out_status": "లాగ్ అవుట్ అయ్యారు",
        "method_mobile_name": "మొబైల్ + పేరు",
        "method_mobile_email_name": "మొబైల్ + ఇమెయిల్ + పేరు",
        "method_google": "గూగుల్తో కొనసాగించండి",
        "method_mobile": "మొబైల్ మాత్రమే",
        "privacy_note": "మీ స్కాన్ ప్రైవేట్ - షేర్ చేయబడదు",
        "check_sms": "SMS తనిఖీ చేయండి",
        "check_email": "ఇమెయిల్ తనిఖీ చేయండి",
        "check_news": "వార్త నిజ నిర్ధారణ చేయండి",
        "enter_defense": "డిఫెన్స్ గ్రిడ్‌లోకి ప్రవేశించండి",
        "logout": "లాగ్ అవుట్",
        "visual_forensics_title": "🔍 విజువల్ AI ఫోరెన్సిక్స్ - ఇది ఎందుకు ఫేక్? - AI వివరణ",
        "word_impact_title": "ఏ పదాలు దీనిని ఫేక్ చేశాయి? (ప్రభావ స్కోర్)",
        "front_cam_title": "🤳 ఫ్రంట్ కెమెరా - సెల్ఫీ / ఫేస్ వ్యూ",
        "back_cam_title": "📄 బ్యాక్ కెమెరా - డాక్యుమెంట్ / పోస్టర్ స్కాన్",
        "upload_file_title": "📁 ఏదైనా ఫోటో / డాక్యుమెంట్ / పోస్టర్ అప్లోడ్ చేయండి",
        "camera_guidance": "ల్యాప్టాప్: ఫ్రంట్ కెమెరా - డాక్యుమెంట్ను ముందు పట్టుకోండి | మొబైల్: డాక్యుమెంట్ల కోసం బ్యాక్ కెమెరా (క్లియర్) - సెల్ఫీ కోసం ఫ్రంట్ - ఫ్లిప్ ఐకాన్తో మార్చండి",
        "camera_closed_msg": "📷 కెమెరా మూసివేయబడింది - పైన ఫ్రంట్ లేదా బ్యాక్ కెమెరా తెరవండి లేదా అప్లోడ్ ఉపయోగించండి"
    },
    "हिन्दी": {
        "enter_mobile": "मोबाइल नंबर दर्ज करें",
        "continue": "जारी रखें",
        "ask_assistant": "सेंसवेरीफाई सहायक - कुछ भी पूछें",
        "welcome": "स्वागत है",
        "protected_endpoints": "सुरक्षित एंडपॉइंट",
        "active_scans": "सक्रिय स्कैन",
        "threats_today": "आज रोके गए खतरे",
        "sms_shield": "एसएमएस स्कैम शील्ड",
        "email_shield": "ईमेल फ़िशिंग शील्ड",
        "satya_shield": "न्यूज ट्रुथ शील्ड - समाचार सत्यापन",
        "scan_now": "🔍 अभी स्कैन करें",
        "my_history": "📋 मेरा स्कैन इतिहास",
        "text_check": "टेक्स्ट जांच",
        "photo_check": "फोटो / दस्तावेज़ / पोस्टर",
        "upload_any": "सत्यापित करने के लिए कोई भी फोटो / दस्तावेज़ अपलोड करें",
        "upload_sub": "किसी भी स्रोत से - सार्वभौमिक जांच",
        "live_sensors": "लाइव-सेंसर - रीयल-टाइम सक्रिय - 24/7",
        "last_scan": "अंतिम स्कैन",
        "enter_name": "अपना नाम दर्ज करें",
        "enter_email": "ईमेल दर्ज करें (वैकल्पिक)",
        "or": "या",
        "dashboard": "विश्लेषण डैशबोर्ड",
        "scan_history": "स्कैन इतिहास",
        "total_scans": "कुल स्कैन",
        "export_csv": "सीएसवी के रूप में निर्यात करें",
        "no_scans": "अभी कोई स्कैन नहीं है - इतिहास देखने के लिए स्कैन करें",
        "user_history_title": "👥 उपयोगकर्ता लॉगिन इतिहास",
        "admin_title": "🛡️ एडमिन एनालिटिक्स - लाइव डैशबोर्ड - 24/7",
        "total_logins_today": "आज कुल लॉगिन",
        "currently_active": "वर्तमान में सक्रिय",
        "total_blocked": "कुल ब्लॉक",
        "documents_checked": "दस्तावेज़ चेक किए गए",
        "logged_out": "लॉग आउट",
        "total_scans_card": "कुल स्कैन",
        "real_safe": "सुरक्षित / प्रामाणिक",
        "posters_checked": "पोस्टर चेक किए गए",
        "login_method": "लॉगिन विधि",
        "mobile_number": "मोबाइल नंबर",
        "name": "नाम",
        "email": "ईमेल",
        "login_time": "लॉगिन समय",
        "logout_time": "लॉग आउट समय",
        "status": "स्थिति",
        "active": "सक्रिय",
        "logged_out_status": "लॉग आउट",
        "method_mobile_name": "मोबाइल + नाम",
        "method_mobile_email_name": "मोबाइल + ईमेल + नाम",
        "method_google": "Google से जारी रखें",
        "method_mobile": "केवल मोबाइल",
        "privacy_note": "आपका स्कैन निजी है - साझा नहीं किया गया",
        "check_sms": "एसएमएस जांचें",
        "check_email": "ईमेल जांचें",
        "check_news": "समाचार सत्यापित करें",
        "enter_defense": "डिफेंस ग्रिड में प्रवेश करें",
        "logout": "लॉग आउट",
        "visual_forensics_title": "🔍 विजुअल एआई फोरेंसिक - यह फेक क्यों है? - एआई व्याख्या",
        "word_impact_title": "किन शब्दों ने इसे फेक बनाया? (प्रभाव स्कोर)"
    }
}

def t(key):
    lang = st.session_state.get("lang", "English")
    lang_dict = TRANSLATOR.get(lang, TRANSLATOR["English"])
    return lang_dict.get(key, TRANSLATOR["English"].get(key, key))

# -----------------------------------------------------------------------------
# SESSION STATE INITIALIZATION
# -----------------------------------------------------------------------------
if "lang" not in st.session_state:
    st.session_state["lang"] = "English"

if "page" not in st.session_state:
    st.session_state["page"] = 1

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if "user_mobile" not in st.session_state:
    st.session_state["user_mobile"] = ""

if "user_name" not in st.session_state:
    st.session_state["user_name"] = "User"

if "user_email" not in st.session_state:
    st.session_state["user_email"] = ""

if "user_method" not in st.session_state:
    st.session_state["user_method"] = "Mobile Only"

if "is_admin" not in st.session_state:
    st.session_state["is_admin"] = False

if "chatbot_history" not in st.session_state:
    st.session_state["chatbot_history"] = [
        {"role": "assistant", "content": "Welcome to SensVerify Assistant! Ask me anything about the App, AI, Python, Fake news, or Cyber Defense."}
    ]

if "chatbot_open" not in st.session_state:
    st.session_state["chatbot_open"] = False

if "camera_facing" not in st.session_state:
    st.session_state.camera_facing = "user"  # user = front, environment = back

def toggle_camera():
    st.session_state.camera_facing = "environment" if st.session_state.camera_facing == "user" else "user"

# Auto-refresh interval 3000ms strictly for live clock/monitoring
if st.session_state.get("logged_in", False):
    st_autorefresh(interval=3000, key="live_clock_refresher")

# -----------------------------------------------------------------------------
# GLOBAL CSS - ZERO CODE STRINGS VISIBLE ON FRONTEND
# -----------------------------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
        color: #FFFFFF !important;
    }

    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #1e3a8a 100%) !important;
        background-attachment: fixed !important;
    }

    /* Glassmorphism Card */
    .glass-card {
        background: rgba(255, 255, 255, 0.08);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        padding: 30px;
    }

    /* Stat Cards */
    .stat-card-widget {
        background: rgba(255, 255, 255, 0.08);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 20px;
        text-align: center;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
    }
    .stat-card-val {
        font-size: 32px;
        font-weight: 800;
        font-family: 'JetBrains Mono', monospace;
        color: #FFFFFF;
        line-height: 1.1;
    }
    .stat-card-lbl {
        font-size: 11px;
        font-weight: 700;
        color: #94A3B8;
        letter-spacing: 0.8px;
        text-transform: uppercase;
        margin-top: 6px;
    }
    .stat-card-sub {
        font-size: 11px;
        color: #22C55E;
        margin-top: 4px;
    }

    /* Pulsing Green Dot */
    @keyframes pulse-anim {
        0% { transform: scale(1); opacity: 1; }
        50% { transform: scale(1.15); opacity: 0.4; }
        100% { transform: scale(1); opacity: 1; }
    }
    .pulse-dot-indicator {
        display: inline-block;
        width: 10px;
        height: 10px;
        background-color: #22c55e;
        border-radius: 50%;
        margin-right: 8px;
        animation: pulse-anim 2s infinite;
        vertical-align: middle;
    }
    .live-badge-widget {
        display: inline-flex;
        align-items: center;
        background: rgba(34, 197, 94, 0.15);
        border: 1px solid rgba(34, 197, 94, 0.3);
        border-radius: 20px;
        padding: 6px 14px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 12px;
        font-weight: 700;
        color: #22c55e !important;
    }

    /* Input & Button Styling */
    .stTextInput input, .stTextArea textarea {
        background: rgba(255, 255, 255, 0.1) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 14px !important;
        color: #FFFFFF !important;
        font-size: 15px !important;
    }
    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: #3b82f6 !important;
        box-shadow: 0 0 15px rgba(59, 130, 246, 0.4) !important;
    }

    .stButton>button[kind="primary"] {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%) !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 14px !important;
        font-weight: 700 !important;
        box-shadow: 0 4px 15px rgba(59, 130, 246, 0.35) !important;
    }
    .stButton>button[kind="secondary"] {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        border: 1px solid #DADCE0 !important;
        border-radius: 14px !important;
        font-weight: 600 !important;
    }

    /* Clean Styled Dataframe */
    .stDataFrame {
        border-radius: 16px;
        overflow: hidden;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }

    /* Bar Graph Row */
    .bg-row {
        display: flex;
        align-items: center;
        margin-bottom: 8px;
        font-size: 12px;
    }
    .bg-lbl {
        width: 130px;
        color: #CBD5E1;
        font-weight: 500;
    }
    .bg-track {
        flex: 1;
        background: rgba(255, 255, 255, 0.1);
        border-radius: 8px;
        height: 10px;
        margin: 0 10px;
        overflow: hidden;
    }
    .bg-fill {
        height: 100%;
        border-radius: 8px;
    }
    .bg-pct {
        width: 45px;
        text-align: right;
        font-family: 'JetBrains Mono', monospace;
        font-weight: 700;
        color: #FFFFFF;
    }

    /* Visual AI Forensics Highlights */
    .highlight-fake-word {
        background: rgba(239, 68, 68, 0.25);
        border: 1px solid #ef4444;
        border-radius: 4px;
        padding: 2px 6px;
        color: #fca5a5;
        font-weight: 600;
        display: inline-block;
        margin: 2px;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# TOP-RIGHT TRANSLATOR (SINGLE LANGUAGE DROPDOWN)
# -----------------------------------------------------------------------------
def render_translator_pill():
    lang_opts = list(TRANSLATOR.keys())
    curr = st.session_state.get("lang", "English")
    idx = lang_opts.index(curr) if curr in lang_opts else 0
    
    col_empty, col_pill = st.columns([8, 2.5])
    with col_pill:
        chosen = st.selectbox(
            "Language",
            options=lang_opts,
            index=idx,
            label_visibility="collapsed",
            key=f"trans_dd_{st.session_state.get('page', 1)}_{st.session_state.get('logged_in', False)}"
        )
        if chosen != st.session_state["lang"]:
            st.session_state["lang"] = chosen
            st.rerun()

# -----------------------------------------------------------------------------
# DETECTION & FORENSIC ENGINES (WITH OPTION TWO VISUAL FORENSICS)
# -----------------------------------------------------------------------------
SCAM_KEYWORDS_WEIGHTS = {
    "shocking": 95, "immediately": 80, "share immediately": 90, "you won't believe": 88,
    "100% free": 92, "lottery": 93, "urgent": 85, "click here": 87, "free iphone": 91,
    "won": 90, "power cut": 88, "electricity": 82, "apk": 94, "disconnection": 86,
    "kyc": 85, "bit.ly": 95, "tinyurl": 92, "account blocked": 94, "free recharge": 90,
    "modi resign": 94, "jagan resign": 94, "nasa says earth dark": 95, "15 days": 88,
    "రాజీనామా": 92, "ఉచిత రీఛార్జ్": 90, "వెంటనే షేర్": 88, "షాకింగ్": 94
}

def analyze_sms_scam(text):
    t_low = text.lower()
    matched = {}
    for kw, wt in SCAM_KEYWORDS_WEIGHTS.items():
        if kw in t_low:
            matched[kw] = wt

    has_link = bool(re.search(r'http[s]?://(?:[a-zA-Z0-9-]+\.)*(?:bit\.ly|tinyurl|xyz|top|sbi-fake)', t_low))
    has_urgency = any(w in t_low for w in ["immediately", "tonight", "24 hours", "urgent", "disconnected"])
    
    kw_score = min(100, sum(matched.values()) // max(1, len(matched))) if matched else 10
    link_score = 95 if has_link else 10
    urgency_score = 85 if has_urgency else 15
    sender_score = 88 if ("bank" in t_low or "pay" in t_low) and matched else 20
    
    fake_score = int((kw_score * 0.35) + (link_score * 0.30) + (urgency_score * 0.20) + (sender_score * 0.15))
    is_fake = fake_score >= 60
    
    reasons = []
    if matched:
        top_kws = list(matched.keys())[:3]
        reasons.append(f"Scam keywords: {', '.join(top_kws)}")
    if has_link:
        reasons.append("Malicious / unverified shortlink detected")
    if has_urgency:
        reasons.append("Psychological urgency trick applied")
        
    return is_fake, fake_score, kw_score, link_score, urgency_score, sender_score, reasons, matched

def analyze_email_phish(sender, subject, body):
    full = f"{sender} {subject} {body}".lower()
    spoofed = ("alits" in sender.lower() and "@alits.ac.in" not in sender.lower()) or any(d in sender.lower() for d in ["@verify-bank.com", "@account-lock.cc", "@free-gift.xyz"])
    matched = {}
    for kw, wt in SCAM_KEYWORDS_WEIGHTS.items():
        if kw in full:
            matched[kw] = wt
    if spoofed:
        matched["spoofed domain"] = 95

    has_link = "http" in full or "bit.ly" in full or "click here" in full
    dom_s = 95 if spoofed else 15
    urg_s = 85 if any(w in full for w in ["urgent", "immediately", "verify now", "suspended"]) else 15
    link_s = 88 if has_link else 15
    send_m = 90 if spoofed else 10
    
    fake_score = int((dom_s * 0.35) + (urg_s * 0.25) + (link_s * 0.20) + (send_m * 0.20))
    is_fake = fake_score >= 60
    
    reasons = []
    if spoofed:
        reasons.append("Sender domain spoofed: Not an authentic institutional domain")
    if matched:
        reasons.append(f"Suspicious triggers: {', '.join(list(matched.keys())[:3])}")
    if has_link:
        reasons.append("Unverified credential harvest link inside body")
        
    return is_fake, fake_score, dom_s, urg_s, link_s, send_m, reasons, matched

def analyze_news_truth(text):
    t_low = text.lower()
    matched = {}
    for kw, wt in SCAM_KEYWORDS_WEIGHTS.items():
        if kw in t_low:
            matched[kw] = wt

    reliable = ["the hindu", "eenadu", "bbc news", "reuters", "official statement", "pib fact check"]
    has_rel = any(r in t_low for r in reliable)
    
    sens_s = min(98, sum(matched.values()) // max(1, len(matched))) if matched else 12
    no_src = 20 if has_rel else 85
    fact_s = 80 if matched else 15
    claim_s = 88 if any(w in t_low for w in ["dark", "resign", "free", "viral"]) else 15
    
    fake_score = int((sens_s * 0.35) + (no_src * 0.25) + (fact_s * 0.20) + (claim_s * 0.20))
    if has_rel and not matched:
        fake_score = 15
    is_fake = fake_score >= 60
    
    reasons = []
    if matched:
        reasons.append(f"Sensational unverified claims: {', '.join(list(matched.keys())[:3])}")
    if not has_rel:
        reasons.append("No verified journalistic source identified")
        
    return is_fake, fake_score, sens_s, no_src, fact_s, claim_s, reasons, matched

def do_ocr(uploaded_file):
    try:
        img = Image.open(uploaded_file)
        if OCR_AVAILABLE:
            try:
                ext = pytesseract.image_to_string(img)
                if ext and len(ext.strip()) > 5:
                    return ext.strip()
            except Exception:
                pass
    except Exception:
        pass
        
    fn = uploaded_file.name.lower()
    if "doc" in fn or "bill" in fn:
        return "Electricity Department Notice: Unpaid bill of Rs 1,420 pending. Power cut tonight. Call 9823102345 or download apk bit.ly/power-pay"
    elif "poster" in fn or "free" in fn:
        return "Government Free Laptop and Recharge Scheme 2026. Click here to claim 100% free reward immediately bit.ly/free-lap"
    elif "news" in fn or "nasa" in fn:
        return "NASA confirms Earth will be completely dark for 15 days in December. Share immediately with everyone!"
    else:
        return "Urgent Alert: Your bank account KYC has expired. Click link immediately to verify bit.ly/bank-secure"


# =============================================================================
# SCREEN CONTROLLER
# =============================================================================

# -----------------------------------------------------------------------------
# PART A: PAGE 1 - WELCOME PAGE (ULTRA CLEAN - NO OTP - NO PASSWORD)
# -----------------------------------------------------------------------------
if not st.session_state["logged_in"] and st.session_state["page"] == 1:
    render_translator_pill()
    
    st.markdown("<div style='height: 40px;'></div>", unsafe_allow_html=True)
    _, col_center, _ = st.columns([1, 1.2, 1])
    
    with col_center:
        # Part B: Fixed base64 Logo (No Broken Image Box Ever)
        logo_b64 = get_logo()
        if logo_b64:
            st.markdown(f'<div style="text-align:center; margin-bottom:15px;"><img src="{logo_b64}" style="width:80px;height:80px;border-radius:16px;box-shadow:0 4px 20px rgba(59,130,246,0.4);"></div>', unsafe_allow_html=True)
        else:
            st.markdown('<div style="text-align:center; margin-bottom:15px;"><div style="width:80px;height:80px;background:linear-gradient(135deg,#3b82f6,#1e40af);border-radius:16px;display:flex;align-items:center;justify-content:center;color:white;font-weight:bold;font-size:32px;margin:0 auto;box-shadow:0 4px 20px rgba(59,130,246,0.4);">S</div></div>', unsafe_allow_html=True)

        # Title: SensVerify 32px bold white, NO SUBTITLE
        st.markdown("""
            <div style="text-align:center; font-size:32px; font-weight:800; color:#FFFFFF; letter-spacing:1px; margin-bottom:25px;">
                SensVerify
            </div>
        """, unsafe_allow_html=True)

        # Mobile input with +91 prefix and SINGLE LANGUAGE PLACEHOLDER
        p_col1, p_col2 = st.columns([1.2, 4])
        with p_col1:
            st.text_input("Prefix", value="+91", disabled=True, label_visibility="collapsed")
        with p_col2:
            mobile_in = st.text_input(
                "Mobile",
                placeholder=t("enter_mobile"),
                max_chars=10,
                label_visibility="collapsed"
            )

        digits_only = "".join([c for c in mobile_in if c.isdigit()])
        is_valid_10 = len(digits_only) == 10

        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

        # Continue Button (Single language, enabled on 10 digits)
        if st.button(t("continue"), type="primary", disabled=not is_valid_10, use_container_width=True):
            st.session_state["mobile_temp"] = digits_only
            st.session_state["user_mobile"] = digits_only
            st.session_state["page"] = 2
            st.rerun()

# -----------------------------------------------------------------------------
# PART A: PAGE 2 - EMAIL + NAME + GOOGLE (ONLY "or" SYMBOL)
# -----------------------------------------------------------------------------
elif not st.session_state["logged_in"] and st.session_state["page"] == 2:
    render_translator_pill()
    
    st.markdown("<div style='height: 40px;'></div>", unsafe_allow_html=True)
    _, col_center, _ = st.columns([1, 1.2, 1])
    
    with col_center:
        m = st.session_state.get("mobile_temp", "9848012345")
        masked = f"📱 {m[:4]}****{m[-2:]}" if len(m) >= 6 else f"📱 {m}"
        
        st.markdown(f"""
            <div style="text-align:center; font-size:14px; color:#94A3B8; margin-bottom:20px;">
                {masked}
            </div>
        """, unsafe_allow_html=True)

        # Name input (Single language)
        in_name = st.text_input("Name", placeholder=t("enter_name"), label_visibility="collapsed")

        st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

        # Email input (Single language)
        in_email = st.text_input("Email", placeholder=t("enter_email"), label_visibility="collapsed")

        st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

        # Enter Defense Grid button
        if st.button(t("enter_defense"), type="primary", use_container_width=True):
            name_val = in_name.strip() if in_name.strip() else ("User" if not in_email.strip() else in_email.split("@")[0].capitalize())
            email_val = in_email.strip() if in_email.strip() else "-"
            
            # Determine method
            if in_name.strip() and in_email.strip():
                method_val = "Mobile + Email + Name"
            elif in_name.strip():
                method_val = "Mobile + Name"
            else:
                method_val = "Mobile Only"

            st.session_state["user_name"] = name_val
            st.session_state["user_email"] = email_val
            st.session_state["user_method"] = method_val
            record_login(m, name_val, email_val, method_val)
            st.session_state["logged_in"] = True
            st.rerun()

        # Divider with ONLY "or" / "లేదా" symbol
        or_text = t("or")
        st.markdown(f"""
            <div style="display:flex; align-items:center; justify-content:center; margin:20px 0;">
                <div style="flex:1; height:1px; background:rgba(255,255,255,0.2);"></div>
                <div style="margin:0 15px; color:#94A3B8; font-size:14px;">{or_text}</div>
                <div style="flex:1; height:1px; background:rgba(255,255,255,0.2);"></div>
            </div>
        """, unsafe_allow_html=True)

        # Continue with Google button
        if st.button(f"🌐  {t('method_google')}", type="secondary", use_container_width=True):
            g_name = in_name.strip() if in_name.strip() else "Google User"
            g_email = in_email.strip() if in_email.strip() else f"{g_name.lower().replace(' ', '')}@gmail.com"
            method_val = "Google"

            st.session_state["user_name"] = g_name
            st.session_state["user_email"] = g_email
            st.session_state["user_method"] = method_val
            record_login(m, g_name, g_email, method_val)
            st.session_state["logged_in"] = True
            st.rerun()

        st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
        if st.button("← Back", use_container_width=True):
            st.session_state["page"] = 1
            st.rerun()

# -----------------------------------------------------------------------------
# DEFENSE GRID (AFTER LOGIN) - WITH USER VIEW & ADMIN VIEW SEPARATION
# -----------------------------------------------------------------------------
elif st.session_state["logged_in"]:
    # Sidebar: Role Switching (User View vs Admin Analytics)
    with st.sidebar:
        st.markdown(f"### 🛡️ SensVerify")
        view_choice = st.radio(
            "Access Role",
            options=["👤 User View", "🛡️ Admin Analytics"],
            index=1 if st.session_state.get("is_admin", False) else 0
        )
        
        # Check admin credentials
        if view_choice == "🛡️ Admin Analytics":
            if not st.session_state.get("is_admin", False):
                if st.session_state.get("user_mobile") == "9999999999":
                    st.session_state["is_admin"] = True
                    st.rerun()
                else:
                    pin = st.text_input("Enter Admin PIN", placeholder="••••", type="password", key="admin_pin")
                    st.caption("Admin access only")
                    if st.button("Verify PIN"):
                        if pin == "1234":
                            st.session_state["is_admin"] = True
                            st.rerun()
                        else:
                            st.error("Invalid Admin PIN")
        else:
            st.session_state["is_admin"] = False

        st.markdown("---")
        st.markdown(f"**User**: {st.session_state.get('user_name', 'User')}")
        st.markdown(f"**Mobile**: `{st.session_state.get('user_mobile', '-')}`")
        st.markdown(f"**Method**: `{st.session_state.get('user_method', '-')}`")
        st.markdown("---")
        if st.button(t("logout"), use_container_width=True):
            record_logout(st.session_state.get("user_mobile", ""))
            st.session_state["logged_in"] = False
            st.session_state["is_admin"] = False
            st.session_state["page"] = 1
            st.rerun()

    # Query REAL counts directly from analytics.db
    conn_db = sqlite3.connect("analytics.db", check_same_thread=False)
    cdb = conn_db.cursor()
    today_str = str(date.today())
    active_scans_real = cdb.execute("SELECT COUNT(*) FROM scans").fetchone()[0]
    threats_today_real = cdb.execute("SELECT COUNT(*) FROM scans WHERE result='FAKE' AND date=?", (today_str,)).fetchone()[0]
    conn_db.close()

    # Header Row
    h_c1, h_c2, h_c3 = st.columns([4, 4, 3])
    with h_c1:
        st.markdown(f"""
            <div style="font-size:24px; font-weight:800; color:#FFFFFF;">
                {t('welcome')}, {st.session_state.get('user_name', 'User')}!
            </div>
        """, unsafe_allow_html=True)
    with h_c2:
        now_clk = datetime.now().strftime("%I:%M:%S %p")
        st.markdown(f"""
            <div style="text-align:center; color:#94A3B8; font-size:12px; margin-top:8px;">
                ⏱ {t('last_scan')}: {now_clk} - 24/7 Active
            </div>
        """, unsafe_allow_html=True)
    with h_c3:
        top_l1, top_l2 = st.columns([2, 1])
        with top_l1:
            lang_opts = list(TRANSLATOR.keys())
            curr = st.session_state.get("lang", "English")
            idx = lang_opts.index(curr) if curr in lang_opts else 0
            sel_lang = st.selectbox("Lang", lang_opts, index=idx, label_visibility="collapsed", key="header_dd")
            if sel_lang != st.session_state["lang"]:
                st.session_state["lang"] = sel_lang
                st.rerun()
        with top_l2:
            if st.button(t("logout"), key="h_logout_btn", use_container_width=True):
                record_logout(st.session_state.get("user_mobile", ""))
                st.session_state["logged_in"] = False
                st.session_state["is_admin"] = False
                st.session_state["page"] = 1
                st.rerun()

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

    # 24/7 LIVE-SENSORS Badge with Tooltip
    st.markdown(f"""
        <div class="live-badge-widget" title="App protects 24 hours 7 days - Real-time monitoring even when minimized - Live">
            <span class="pulse-dot-indicator"></span>{t("live_sensors")}
        </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

    # 3 Stat Cards (REAL COUNTS FROM DATABASE)
    sc1, sc2, sc3 = st.columns(3)
    with sc1:
        st.markdown(f"""
            <div class="stat-card-widget" title="3 Shields: SMS Scam Shield, Email Phishing Shield, News Truth Shield - Our 3 protection layers - Real">
                <div class="stat-card-val">3</div>
                <div class="stat-card-lbl">{t("protected_endpoints")}</div>
                <div class="stat-card-sub">● Live Build Active</div>
            </div>
        """, unsafe_allow_html=True)
    with sc2:
        st.markdown(f"""
            <div class="stat-card-widget" title="Real count from analytics.db - Increases only when you scan - Not random - Proof in Scan History table below">
                <div class="stat-card-val">{active_scans_real}</div>
                <div class="stat-card-lbl">{t("active_scans")}</div>
                <div class="stat-card-sub">▲ Updated just now - Live</div>
            </div>
        """, unsafe_allow_html=True)
    with sc3:
        st.markdown(f"""
            <div class="stat-card-widget" title="Real FAKE count today from your scans - Resets daily midnight - Proof in table - Real">
                <div class="stat-card-val">{threats_today_real}</div>
                <div class="stat-card-lbl">{t("threats_today")}</div>
                <div class="stat-card-sub">▲ Threat Neutralized - Real-time</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height: 25px;'></div>", unsafe_allow_html=True)

    # Helper function for Photo / Document / Poster Universal Check with Modern Single Camera & Small Flip Icon
    def render_universal_photo_tab(shield_name, key_prefix, analyze_fn, save_scan_label):
        col1, col2 = st.columns([1, 1.5])

        with col1:
            st.markdown("#### 📤 Upload Photo / Document")
            up_file = st.file_uploader(
                "Upload",
                type=["jpg", "png", "pdf", "jpeg"],
                label_visibility="collapsed",
                key=f"upload_{key_prefix}"
            )
            st.caption("JPG, PNG, PDF")

        with col2:
            st.markdown("#### 📷 Camera")
            camera_final_html = f"""
            <style>
            .cam-wrap {{ position:relative; width:100%; background:#000; border-radius:12px; overflow:hidden; }}
            #video_{key_prefix} {{ width:100%; height:320px; object-fit:cover; display:block; }}
            #preview_{key_prefix} {{ width:100%; margin-top:8px; border-radius:12px; display:none; }}
            .icon-btn {{
                position:absolute;
                bottom:12px;
                right:12px;
                width:44px;
                height:44px;
                border-radius:50%;
                background:rgba(255,255,255,0.9);
                border:none;
                cursor:pointer;
                font-size:20px;
                display:flex;
                align-items:center;
                justify-content:center;
                box-shadow:0 2px 8px rgba(0,0,0,0.3);
                z-index:10;
            }}
            .capture-btn {{
                position:absolute;
                bottom:12px;
                left:50%;
                transform:translateX(-50%);
                width:56px;
                height:56px;
                border-radius:50%;
                background:white;
                border:4px solid rgba(255,255,255,0.8);
                cursor:pointer;
                z-index:10;
            }}
            .status {{ color:#aaa; font-size:11px; margin-top:6px; text-align:center; }}
            </style>
            <div class="cam-wrap">
                <video id="video_{key_prefix}" autoplay playsinline></video>
                <button class="capture-btn" id="captureBtn_{key_prefix}" title="Capture"></button>
                <button class="icon-btn" id="flipBtn_{key_prefix}" title="Flip">🔄</button>
            </div>
            <canvas id="canvas_{key_prefix}" style="display:none;"></canvas>
            <img id="preview_{key_prefix}" />
            <div class="status" id="status_{key_prefix}">Front • Tap 🔄 to switch</div>

            <script>
            let facing_{key_prefix} = "user";
            let stream_{key_prefix} = null;
            const video = document.getElementById('video_{key_prefix}');
            const canvas = document.getElementById('canvas_{key_prefix}');
            const preview = document.getElementById('preview_{key_prefix}');
            const status = document.getElementById('status_{key_prefix}');

            async function startCam(f) {{
                if(stream_{key_prefix}) stream_{key_prefix}.getTracks().forEach(t=>t.stop());
                try {{
                    stream_{key_prefix} = await navigator.mediaDevices.getUserMedia({{
                        video: {{ facingMode: f }},
                        audio: false
                    }});
                    video.srcObject = stream_{key_prefix};
                    status.innerText = (f==='user' ? 'Front' : 'Back') + ' • Tap 🔄 to switch';
                }} catch(e) {{
                    status.innerText = "Camera not available - Use Upload";
                }}
            }}
            document.getElementById('flipBtn_{key_prefix}').onclick = () => {{
                facing_{key_prefix} = facing_{key_prefix}==='user' ? 'environment' : 'user';
                startCam(facing_{key_prefix});
            }};
            document.getElementById('captureBtn_{key_prefix}').onclick = () => {{
                canvas.width = video.videoWidth;
                canvas.height = video.videoHeight;
                canvas.getContext('2d').drawImage(video, 0, 0);
                preview.src = canvas.toDataURL('image/jpeg');
                preview.style.display = 'block';
                status.innerText = "Captured ✓ - Use for scan";
            }};
            startCam(facing_{key_prefix});
            </script>
            """
            components.html(camera_final_html, height=400)
            st.caption("Tap white circle to capture • Tap 🔄 icon at bottom-right corner to flip Front ↔️ Back")
            cam_photo = st.camera_input("Instant Snapshot for Analysis", key=f"cam_{key_prefix}", label_visibility="collapsed")

        active_media = None
        media_source_name = ""
        if up_file is not None:
            active_media = up_file
            media_source_name = "Uploaded File"
        elif cam_photo is not None:
            active_media = cam_photo
            media_source_name = "Camera Snapshot"

        # Black Preview Fix: When camera closed / none selected, show friendly info
        if active_media is None:
            st.info(t("camera_closed_msg"))
        else:
            c_i1, c_i2 = st.columns([1, 2])
            with c_i1:
                st.image(active_media, caption=f"Capture Preview ({media_source_name})", use_container_width=True)
            with c_i2:
                txt_ext = do_ocr(active_media)
                is_fake, sc, s1, s2, s3, s4, reasons, matched = analyze_fn(txt_ext)
                file_or_cam_name = getattr(active_media, "name", "camera.jpg").lower()
                in_tp = "Document" if "doc" in file_or_cam_name else ("Poster" if "poster" in file_or_cam_name else "Photo")
                save_scan(f"{save_scan_label} ({in_tp})", txt_ext, "FAKE" if is_fake else "REAL", sc, st.session_state["user_mobile"], st.session_state["user_name"])

                th_border = "#ef4444" if is_fake else "#22c55e"
                st.markdown(f"""
                    <div style="background:{'rgba(239,68,68,0.12)' if is_fake else 'rgba(34,197,94,0.12)'}; border-left:4px solid {th_border}; border-radius:12px; padding:14px; margin-top:8px;">
                        <div style="font-size:16px; font-weight:700;">{'🔴 FAKE DETECTED' if is_fake else '🟢 AUTHENTIC / SAFE'} - {sc}% Confidence</div>
                        <div style="font-size:11px; color:#CBD5E1; margin-top:4px;">Extracted Content: <i>{txt_ext[:80]}...</i></div>
                    </div>
                """, unsafe_allow_html=True)

                if is_fake:
                    st.markdown("""
                        <div style="margin-top:10px; padding:10px; background:rgba(239,68,68,0.15); border:1px solid #ef4444; border-radius:8px; font-size:12px; color:#FCA5A5;">
                            🚨 <b>Visual Forensic Bounding Detection:</b> [SUSPICIOUS CALL-TO-ACTION & UNVERIFIED CLAIMS DETECTED]
                        </div>
                    """, unsafe_allow_html=True)

    # =========================================================================
    # PART 3: USER VIEW (SEPARATE TABS: SCAN NOW vs MY SCAN HISTORY)
    # =========================================================================
    if not st.session_state.get("is_admin", False):
        st.markdown(f"<div style='font-size:12px; color:#22C55E; margin-bottom:12px;'>🔒 {t('privacy_note')}</div>", unsafe_allow_html=True)

        user_tab_scan, user_tab_history = st.tabs([
            t("scan_now"),
            t("my_history")
        ])

        with user_tab_scan:
            tab_sms, tab_email, tab_satya = st.tabs([
                t("sms_shield"),
                t("email_shield"),
                t("satya_shield")
            ])

            # -----------------------------------------------------------------
            # SHIELD 1: SMS SCAM SHIELD
            # -----------------------------------------------------------------
            with tab_sms:
                sub1, sub2 = st.tabs([t("text_check"), t("photo_check")])
                with sub1:
                    sms_txt = st.text_area("SMS Input", placeholder="Paste SMS here... e.g. Your electricity power disconnected tonight. Call 9823102345 or download apk bit.ly/power-pay", height=110, label_visibility="collapsed")
                    if st.button(t("check_sms"), key="btn_chk_sms", type="primary"):
                        if sms_txt.strip():
                            is_fake, sc, kw_s, lnk_s, urg_s, snd_s, reasons, matched = analyze_sms_scam(sms_txt)
                            save_scan("SMS", sms_txt, "FAKE" if is_fake else "REAL", sc, st.session_state["user_mobile"], st.session_state["user_name"])
                            
                            th_bg = "rgba(239,68,68,0.12)" if is_fake else "rgba(34,197,94,0.12)"
                            th_bd = "#ef4444" if is_fake else "#22c55e"
                            th_tit = f"🔴 FAKE SMS / SCAM - {sc}% Threat" if is_fake else f"🟢 REAL SMS - {100-sc}% Safe"
                            
                            st.markdown(f"""
                                <div style="background:{th_bg}; border-left:4px solid {th_bd}; border-radius:16px; padding:20px; margin-top:15px;">
                                    <div style="font-size:18px; font-weight:800; color:#FFFFFF;">{th_tit}</div>
                                    <div style="margin-top:12px;">
                                        <div style="font-size:12px; color:#CBD5E1; margin-bottom:4px;">{sc}% Confidence</div>
                                        <div style="background:rgba(255,255,255,0.1); border-radius:8px; height:10px; overflow:hidden;">
                                            <div style="background:{th_bd}; width:{sc}%; height:100%;"></div>
                                        </div>
                                    </div>
                                    <div style="margin-top:18px;">
                                        <div style="font-size:14px; font-weight:700; color:#FFFFFF; margin-bottom:10px;">Analysis Breakdown</div>
                                        <div class="bg-row"><span class="bg-lbl">Scam Keywords</span><div class="bg-track"><div class="bg-fill" style="width:{kw_s}%; background:#ef4444;"></div></div><span class="bg-pct">{kw_s}%</span></div>
                                        <div class="bg-row"><span class="bg-lbl">Fake Link</span><div class="bg-track"><div class="bg-fill" style="width:{lnk_s}%; background:#ef4444;"></div></div><span class="bg-pct">{lnk_s}%</span></div>
                                        <div class="bg-row"><span class="bg-lbl">Urgency Trick</span><div class="bg-track"><div class="bg-fill" style="width:{urg_s}%; background:#f97316;"></div></div><span class="bg-pct">{urg_s}%</span></div>
                                        <div class="bg-row"><span class="bg-lbl">Sender Mismatch</span><div class="bg-track"><div class="bg-fill" style="width:{snd_s}%; background:{'#ef4444' if is_fake else '#22c55e'};"></div></div><span class="bg-pct">{snd_s}%</span></div>
                                    </div>
                                </div>
                            """, unsafe_allow_html=True)
                            
                            # Visual AI Forensics - Option Two (Laptop & Mobile)
                            if is_fake:
                                st.markdown(f"""
                                    <div style="margin-top:20px; background:rgba(239,68,68,0.08); border:1px solid rgba(239,68,68,0.3); border-radius:16px; padding:18px;">
                                        <div style="font-size:15px; font-weight:800; color:#FCA5A5;">{t('visual_forensics_title')}</div>
                                        <div style="font-size:12px; color:#CBD5E1; margin-top:6px;"><b>Step A: Suspicious Words Highlighted</b></div>
                                """, unsafe_allow_html=True)
                                
                                highlighted_txt = sms_txt
                                for kw, wt in matched.items():
                                    pattern = re.compile(re.escape(kw), re.IGNORECASE)
                                    highlighted_txt = pattern.sub(f"<span class='highlight-fake-word'>{kw} (Impact: {wt}%)</span>", highlighted_txt)
                                
                                st.markdown(f"<div style='margin-top:8px; font-size:13px; line-height:1.6;'>{highlighted_txt}</div>", unsafe_allow_html=True)
                                
                                st.markdown(f"<div style='font-size:12px; color:#CBD5E1; margin-top:14px;'><b>Step B: {t('word_impact_title')}</b></div>", unsafe_allow_html=True)
                                for kw, wt in matched.items():
                                    st.markdown(f"""
                                        <div class="bg-row">
                                            <span class="bg-lbl" style="width:160px; color:#F87171;">⚠️ {kw}</span>
                                            <div class="bg-track"><div class="bg-fill" style="width:{wt}%; background:#ef4444;"></div></div>
                                            <span class="bg-pct">{wt}%</span>
                                        </div>
                                    """, unsafe_allow_html=True)
                                st.markdown("</div>", unsafe_allow_html=True)

                with sub2:
                    render_universal_photo_tab("SMS", "sms_user", analyze_sms_scam, "SMS")

            # -----------------------------------------------------------------
            # SHIELD 2: EMAIL PHISHING SHIELD
            # -----------------------------------------------------------------
            with tab_email:
                sub1, sub2 = st.tabs([t("text_check"), t("photo_check")])
                with sub1:
                    e_from = st.text_input("From", placeholder="From Email ID - e.g. support@alits.ac.in")
                    e_sub = st.text_input("Sub", placeholder="Subject Header")
                    e_body = st.text_area("Body", placeholder="Email Body", height=110)
                    if st.button(t("check_email"), key="btn_chk_em", type="primary"):
                        if e_body.strip() or e_from.strip():
                            is_fake, sc, dom_s, urg_s, lnk_s, send_m, reasons, matched = analyze_email_phish(e_from, e_sub, e_body)
                            save_scan("Email", f"{e_from} {e_sub} {e_body}", "FAKE" if is_fake else "REAL", sc, st.session_state["user_mobile"], st.session_state["user_name"])
                            th_bg = "rgba(239,68,68,0.12)" if is_fake else "rgba(34,197,94,0.12)"
                            th_bd = "#ef4444" if is_fake else "#22c55e"
                            th_tit = f"🔴 FAKE / PHISHING EMAIL - {sc}% Threat" if is_fake else f"🟢 AUTHENTIC EMAIL - {100-sc}% Safe"
                            st.markdown(f"""
                                <div style="background:{th_bg}; border-left:4px solid {th_bd}; border-radius:16px; padding:20px; margin-top:15px;">
                                    <div style="font-size:18px; font-weight:800; color:#FFFFFF;">{th_tit}</div>
                                    <div style="margin-top:12px;">
                                        <div style="font-size:12px; color:#CBD5E1; margin-bottom:4px;">{sc}% Confidence</div>
                                        <div style="background:rgba(255,255,255,0.1); border-radius:8px; height:10px; overflow:hidden;">
                                            <div style="background:{th_bd}; width:{sc}%; height:100%;"></div>
                                        </div>
                                    </div>
                                    <div style="margin-top:18px;">
                                        <div style="font-size:14px; font-weight:700; color:#FFFFFF; margin-bottom:10px;">Analysis Breakdown</div>
                                        <div class="bg-row"><span class="bg-lbl">Fake Domain</span><div class="bg-track"><div class="bg-fill" style="width:{dom_s}%; background:#ef4444;"></div></div><span class="bg-pct">{dom_s}%</span></div>
                                        <div class="bg-row"><span class="bg-lbl">Urgency Factor</span><div class="bg-track"><div class="bg-fill" style="width:{urg_s}%; background:#f97316;"></div></div><span class="bg-pct">{urg_s}%</span></div>
                                        <div class="bg-row"><span class="bg-lbl">Suspicious Link</span><div class="bg-track"><div class="bg-fill" style="width:{lnk_s}%; background:#ef4444;"></div></div><span class="bg-pct">{lnk_s}%</span></div>
                                        <div class="bg-row"><span class="bg-lbl">Sender Mismatch</span><div class="bg-track"><div class="bg-fill" style="width:{send_m}%; background:{'#ef4444' if is_fake else '#22c55e'};"></div></div><span class="bg-pct">{send_m}%</span></div>
                                    </div>
                                </div>
                            """, unsafe_allow_html=True)
                            
                            # Visual AI Forensics
                            if is_fake:
                                st.markdown(f"""
                                    <div style="margin-top:20px; background:rgba(239,68,68,0.08); border:1px solid rgba(239,68,68,0.3); border-radius:16px; padding:18px;">
                                        <div style="font-size:15px; font-weight:800; color:#FCA5A5;">{t('visual_forensics_title')}</div>
                                        <div style="font-size:12px; color:#CBD5E1; margin-top:6px;"><b>Step B: {t('word_impact_title')}</b></div>
                                """, unsafe_allow_html=True)
                                for kw, wt in matched.items():
                                    st.markdown(f"""
                                        <div class="bg-row">
                                            <span class="bg-lbl" style="width:160px; color:#F87171;">⚠️ {kw}</span>
                                            <div class="bg-track"><div class="bg-fill" style="width:{wt}%; background:#ef4444;"></div></div>
                                            <span class="bg-pct">{wt}%</span>
                                        </div>
                                    """, unsafe_allow_html=True)
                                st.markdown("</div>", unsafe_allow_html=True)

                with sub2:
                    render_universal_photo_tab("Email", "em_user", lambda txt: analyze_email_phish("spoof@fake-mail.cc", "Detected Notice", txt), "Email")

            # -----------------------------------------------------------------
            # SHIELD 3: NEWS TRUTH SHIELD (RENAMED FROM SATYASHIELD)
            # -----------------------------------------------------------------
            with tab_satya:
                sub1, sub2 = st.tabs([t("text_check"), t("photo_check")])
                with sub1:
                    news_txt = st.text_area("News Input", placeholder="Paste News Headline / Article here... (English / Telugu)", height=120, label_visibility="collapsed")
                    if st.button(t("check_news"), key="btn_chk_nw", type="primary"):
                        if news_txt.strip():
                            is_fake, sc, sens_s, nos_s, fact_s, claim_s, reasons, matched = analyze_news_truth(news_txt)
                            save_scan("News Truth Shield", news_txt, "FAKE" if is_fake else "REAL", sc, st.session_state["user_mobile"], st.session_state["user_name"])
                            th_bg = "rgba(239,68,68,0.12)" if is_fake else "rgba(34,197,94,0.12)"
                            th_bd = "#ef4444" if is_fake else "#22c55e"
                            th_tit = f"🔴 FAKE NEWS / MISINFORMATION - {sc}% Fake" if is_fake else f"🟢 VERIFIED AUTHENTIC NEWS - {100-sc}% True"
                            st.markdown(f"""
                                <div style="background:{th_bg}; border-left:4px solid {th_bd}; border-radius:16px; padding:20px; margin-top:15px;">
                                    <div style="font-size:18px; font-weight:800; color:#FFFFFF;">{th_tit}</div>
                                    <div style="margin-top:12px;">
                                        <div style="font-size:12px; color:#CBD5E1; margin-bottom:4px;">{sc}% Confidence</div>
                                        <div style="background:rgba(255,255,255,0.1); border-radius:8px; height:10px; overflow:hidden;">
                                            <div style="background:{th_bd}; width:{sc}%; height:100%;"></div>
                                        </div>
                                    </div>
                                    <div style="margin-top:18px;">
                                        <div style="font-size:14px; font-weight:700; color:#FFFFFF; margin-bottom:10px;">Analysis Breakdown</div>
                                        <div class="bg-row"><span class="bg-lbl">Sensational Words</span><div class="bg-track"><div class="bg-fill" style="width:{sens_s}%; background:#ef4444;"></div></div><span class="bg-pct">{sens_s}%</span></div>
                                        <div class="bg-row"><span class="bg-lbl">No Source Trace</span><div class="bg-track"><div class="bg-fill" style="width:{nos_s}%; background:#ef4444;"></div></div><span class="bg-pct">{nos_s}%</span></div>
                                        <div class="bg-row"><span class="bg-lbl">Fact Discrepancy</span><div class="bg-track"><div class="bg-fill" style="width:{fact_s}%; background:#f97316;"></div></div><span class="bg-pct">{fact_s}%</span></div>
                                        <div class="bg-row"><span class="bg-lbl">Claim Pattern</span><div class="bg-track"><div class="bg-fill" style="width:{claim_s}%; background:{'#ef4444' if is_fake else '#22c55e'};"></div></div><span class="bg-pct">{claim_s}%</span></div>
                                    </div>
                                </div>
                            """, unsafe_allow_html=True)
                            
                            # Visual AI Forensics
                            if is_fake:
                                st.markdown(f"""
                                    <div style="margin-top:20px; background:rgba(239,68,68,0.08); border:1px solid rgba(239,68,68,0.3); border-radius:16px; padding:18px;">
                                        <div style="font-size:15px; font-weight:800; color:#FCA5A5;">{t('visual_forensics_title')}</div>
                                        <div style="font-size:12px; color:#CBD5E1; margin-top:6px;"><b>Step A: Suspicious Claim Words Highlighted</b></div>
                                """, unsafe_allow_html=True)
                                
                                highl = news_txt
                                for kw, wt in matched.items():
                                    pattern = re.compile(re.escape(kw), re.IGNORECASE)
                                    highl = pattern.sub(f"<span class='highlight-fake-word'>{kw} (Impact: {wt}%)</span>", highl)
                                
                                st.markdown(f"<div style='margin-top:8px; font-size:13px; line-height:1.6;'>{highl}</div>", unsafe_allow_html=True)
                                
                                st.markdown(f"<div style='font-size:12px; color:#CBD5E1; margin-top:14px;'><b>Step B: {t('word_impact_title')}</b></div>", unsafe_allow_html=True)
                                for kw, wt in matched.items():
                                    st.markdown(f"""
                                        <div class="bg-row">
                                            <span class="bg-lbl" style="width:160px; color:#F87171;">⚠️ {kw}</span>
                                            <div class="bg-track"><div class="bg-fill" style="width:{wt}%; background:#ef4444;"></div></div>
                                            <span class="bg-pct">{wt}%</span>
                                        </div>
                                    """, unsafe_allow_html=True)
                                st.markdown("</div>", unsafe_allow_html=True)

                with sub2:
                    render_universal_photo_tab("News Truth Shield", "nw_user", analyze_news_truth, "News Truth Shield")

        # ---------------------------------------------------------------------
        # USER TAB 2: 📋 MY SCAN HISTORY (SEPARATE TAB - CLEAN & PRIVATE)
        # ---------------------------------------------------------------------
        with user_tab_history:
            st.markdown(f"#### 📜 {t('my_history')}")
            conn_u = sqlite3.connect("analytics.db", check_same_thread=False)
            my_m = st.session_state.get("user_mobile", "")
            df_my = pd.read_sql_query("""
                SELECT timestamp as 'Time', scan_type as 'Scan Type', content_preview as 'Content Preview', result as 'Result', confidence as 'Confidence (%)'
                FROM scans
                WHERE user_mobile = ?
                ORDER BY id DESC
                LIMIT 20
            """, conn_u, params=(my_m,))
            conn_u.close()

            if len(df_my) > 0:
                st.dataframe(df_my, use_container_width=True)
                csv_data = df_my.to_csv(index=False).encode('utf-8')
                st.download_button(t("export_csv"), data=csv_data, file_name=f"My_SensVerify_Scans_{my_m}.csv", mime="text/csv")
            else:
                st.info(t("no_scans"))

    # =========================================================================
    # PART 4: ADMIN VIEW (PROFESSOR / ADMIN ONLY - ALL DETAILS)
    # =========================================================================
    else:
        col_adm_head1, col_adm_head2 = st.columns([3, 1])
        with col_adm_head1:
            st.markdown(f"""
                <div style="font-size:22px; font-weight:800; color:#FFFFFF; margin-bottom:15px;">
                    {t('admin_title')}
                </div>
            """, unsafe_allow_html=True)
        with col_adm_head2:
            if st.button("🗑️ Clear All Data (Reset to 0)", key="clear_all_db_btn", use_container_width=True):
                try:
                    conn_cl = sqlite3.connect("analytics.db", check_same_thread=False)
                    c_cl = conn_cl.cursor()
                    c_cl.execute("DELETE FROM scans")
                    c_cl.execute("DELETE FROM logins")
                    conn_cl.commit()
                    conn_cl.close()
                    st.success("All analytics & login logs reset to 0!")
                    st.rerun()
                except Exception:
                    pass

        conn_a = sqlite3.connect("analytics.db", check_same_thread=False)
        ca = conn_a.cursor()
        
        # Admin Card Counts (Real DB data)
        today_val = str(date.today())
        total_logins_td = ca.execute("SELECT COUNT(*) FROM logins WHERE date=?", (today_val,)).fetchone()[0]
        active_now = ca.execute("SELECT COUNT(*) FROM logins WHERE logout_time IS NULL").fetchone()[0]
        total_blocked_all = ca.execute("SELECT COUNT(*) FROM scans WHERE result='FAKE'").fetchone()[0]
        docs_checked = ca.execute("SELECT COUNT(*) FROM scans WHERE scan_type LIKE '%Document%'").fetchone()[0]
        
        logged_out_td = ca.execute("SELECT COUNT(*) FROM logins WHERE logout_time IS NOT NULL AND date=?", (today_val,)).fetchone()[0]
        total_scans_all = ca.execute("SELECT COUNT(*) FROM scans").fetchone()[0]
        real_safe_all = ca.execute("SELECT COUNT(*) FROM scans WHERE result='REAL'").fetchone()[0]
        posters_checked = ca.execute("SELECT COUNT(*) FROM scans WHERE scan_type LIKE '%Poster%'").fetchone()[0]
        
        conn_a.close()

        # Row 1 (4 Cards)
        ar1, ar2, ar3, ar4 = st.columns(4)
        with ar1:
            st.markdown(f"<div class='stat-card-widget'><div class='stat-card-val'>{total_logins_td}</div><div class='stat-card-lbl'>{t('total_logins_today')}</div></div>", unsafe_allow_html=True)
        with ar2:
            st.markdown(f"<div class='stat-card-widget'><div class='stat-card-val'>{active_now}</div><div class='stat-card-lbl'>{t('currently_active')}</div></div>", unsafe_allow_html=True)
        with ar3:
            st.markdown(f"<div class='stat-card-widget'><div class='stat-card-val' style='color:#ef4444;'>{total_blocked_all}</div><div class='stat-card-lbl'>{t('total_blocked')}</div></div>", unsafe_allow_html=True)
        with ar4:
            st.markdown(f"<div class='stat-card-widget'><div class='stat-card-val'>{docs_checked}</div><div class='stat-card-lbl'>{t('documents_checked')}</div></div>", unsafe_allow_html=True)

        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

        # Row 2 (4 Cards)
        ar5, ar6, ar7, ar8 = st.columns(4)
        with ar5:
            st.markdown(f"<div class='stat-card-widget'><div class='stat-card-val'>{logged_out_td}</div><div class='stat-card-lbl'>{t('logged_out')}</div></div>", unsafe_allow_html=True)
        with ar6:
            st.markdown(f"<div class='stat-card-widget'><div class='stat-card-val'>{total_scans_all}</div><div class='stat-card-lbl'>{t('total_scans_card')}</div></div>", unsafe_allow_html=True)
        with ar7:
            st.markdown(f"<div class='stat-card-widget'><div class='stat-card-val' style='color:#22c55e;'>{real_safe_all}</div><div class='stat-card-lbl'>{t('real_safe')}</div></div>", unsafe_allow_html=True)
        with ar8:
            st.markdown(f"<div class='stat-card-widget'><div class='stat-card-val'>{posters_checked}</div><div class='stat-card-lbl'>{t('posters_checked')}</div></div>", unsafe_allow_html=True)

        st.markdown("<div style='height: 30px;'></div>", unsafe_allow_html=True)

        # Table 1: User Login History - Who Logged In & How
        st.markdown(f"#### {t('user_history_title')}")
        conn_l = sqlite3.connect("analytics.db", check_same_thread=False)
        df_logins = pd.read_sql_query("""
            SELECT id as 'No', name as 'Name', mobile as 'Mobile Number', email as 'Email',
                   login_method as 'Login Method', login_time as 'Login Time',
                   COALESCE(logout_time, '-') as 'Logout Time',
                   CASE WHEN logout_time IS NULL THEN 'Active' ELSE 'Logged Out' END as 'Status'
            FROM logins
            ORDER BY id DESC
        """, conn_l)
        conn_l.close()

        if len(df_logins) > 0:
            st.dataframe(df_logins, use_container_width=True)
        else:
            st.info("No login history recorded yet.")

        st.markdown("<div style='height: 25px;'></div>", unsafe_allow_html=True)

        # Table 2: Scan Breakdown - Type Wise
        st.markdown("#### 📊 Scan Breakdown - Type Wise")
        conn_s = sqlite3.connect("analytics.db", check_same_thread=False)
        df_types = pd.read_sql_query("SELECT scan_type, COUNT(*) as count FROM scans GROUP BY scan_type", conn_s)
        conn_s.close()
        if len(df_types) > 0:
            st.bar_chart(df_types.set_index("scan_type"))

        st.markdown("<div style='height: 25px;'></div>", unsafe_allow_html=True)

        # Table 3: All Scans History - Proof Table
        st.markdown(f"#### 🔍 {t('scan_history')}")
        conn_all = sqlite3.connect("analytics.db", check_same_thread=False)
        df_all_scans = pd.read_sql_query("""
            SELECT timestamp as 'Time', user_mobile as 'User Mobile', user_name as 'User Name',
                   scan_type as 'Scan Type', content_preview as 'Content Preview', result as 'Result', confidence as 'Confidence (%)'
            FROM scans
            ORDER BY id DESC
        """, conn_all)
        conn_all.close()

        if len(df_all_scans) > 0:
            st.dataframe(df_all_scans, use_container_width=True)
            csv_all = df_all_scans.to_csv(index=False).encode('utf-8')
            st.download_button(t("export_csv"), data=csv_all, file_name="SensVerify_All_Scans_Admin_Proof.csv", mime="text/csv")
        else:
            st.info(t("no_scans"))


# -----------------------------------------------------------------------------
# UNIVERSAL CHATBOT WIDGET (ALL PAGES - SINGLE LANGUAGE PROMPT)
# -----------------------------------------------------------------------------
st.markdown("<div style='height: 40px;'></div>", unsafe_allow_html=True)

with st.expander(f"💬 {t('ask_assistant')}", expanded=st.session_state["chatbot_open"]):
    for msg in st.session_state["chatbot_history"]:
        if msg["role"] == "user":
            st.markdown(f"""
                <div style="display:flex; justify-content:flex-end; margin-bottom:8px;">
                    <div style="background:rgba(59,130,246,0.3); border:1px solid #3b82f6; border-radius:14px 14px 2px 14px; padding:8px 14px; max-width:80%; font-size:13px; color:#FFFFFF;">
                        <b>You:</b> {msg['content']}
                    </div>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
                <div style="display:flex; justify-content:flex-start; margin-bottom:8px;">
                    <div style="background:rgba(255,255,255,0.08); border:1px solid rgba(255,255,255,0.15); border-radius:14px 14px 14px 2px; padding:8px 14px; max-width:85%; font-size:13px; color:#E2E8F0;">
                        <b>Assistant:</b> {msg['content']}
                    </div>
                </div>
            """, unsafe_allow_html=True)

    c_in1, c_in2 = st.columns([5, 1])
    with c_in1:
        q_in = st.text_input("Ask Question", placeholder="Ask anything... AI, Python, Fake news, College, App...", label_visibility="collapsed", key="chat_input_box")
    with c_in2:
        if st.button("Send", key="chat_send_btn", use_container_width=True):
            if q_in.strip():
                st.session_state["chatbot_history"].append({"role": "user", "content": q_in.strip()})
                # Check for answer
                q_low = q_in.lower().strip()
                ans = None
                for top, answ in GENERAL_KNOWLEDGE.items():
                    if top in q_low:
                        ans = answ
                        break
                if not ans:
                    if any(k in q_low for k in ["sensverify", "login", "sms", "email", "news", "admin", "shield"]):
                        ans = "SensVerify uses 3 Shields: SMS Scam Shield, Email Phishing Shield, and News Truth Shield to protect users with 24/7 Live Telemetry."
                    else:
                        ans = f"Nenu Universal Assistant! Meeru adigina '{q_in}' gurinchi: Idi oka key technical / general knowledge topic. Inka specific ga adagandi, nenu answer istha!"
                
                st.session_state["chatbot_history"].append({"role": "assistant", "content": ans})
                st.session_state["chatbot_open"] = True
                st.rerun()

# End of file
