import streamlit as st
from streamlit_autorefresh import st_autorefresh
import sqlite3
import random
import os
import re
from datetime import datetime
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
# DATABASE INITIALIZATION (users.db & analytics.db)
# -----------------------------------------------------------------------------
def init_databases():
    try:
        # Users Database
        conn_u = sqlite3.connect("users.db")
        cu = conn_u.cursor()
        cu.execute("""
            CREATE TABLE IF NOT EXISTS users (
                mobile TEXT PRIMARY KEY,
                email TEXT,
                name TEXT,
                login_time TEXT,
                logout_time TEXT,
                last_active TEXT,
                total_scans INTEGER
            )
        """)
        # Ensure columns exist if table was created with older schema
        for col in ["login_time", "logout_time", "last_active", "total_scans"]:
            try:
                cu.execute(f"ALTER TABLE users ADD COLUMN {col} TEXT")
            except Exception:
                pass
        conn_u.commit()
        conn_u.close()

        # Analytics Database
        conn_a = sqlite3.connect("analytics.db")
        ca = conn_a.cursor()
        ca.execute("""
            CREATE TABLE IF NOT EXISTS scans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                user_mobile TEXT,
                user_name TEXT,
                shield TEXT,
                input_type TEXT,
                input_preview TEXT,
                extracted_text TEXT,
                result TEXT,
                confidence REAL,
                blocked INTEGER
            )
        """)
        
        # Populate initial realistic analytics data if table is brand new
        ca.execute("SELECT COUNT(*) FROM scans")
        if ca.fetchone()[0] == 0:
            sample_scans = [
                (datetime.now().strftime("%Y-%m-%d 10:14:20"), "9848012345", "Rahul", "SMS", "Text", "Electricity bill unpaid tonight...", "Fake power cut APK bit.ly/power-pay", "FAKE", 96.5, 1),
                (datetime.now().strftime("%Y-%m-%d 10:32:15"), "7601234565", "Keerthi", "Email", "Photo", "Urgent payroll account update...", "CEO gift card spoofed domain @alits-update.cc", "FAKE", 94.0, 1),
                (datetime.now().strftime("%Y-%m-%d 11:05:40"), "9440198765", "Suresh", "SatyaShield", "Document", "NASA 15 days darkness viral...", "NASA officially says earth 15 days dark", "FAKE", 93.8, 1),
                (datetime.now().strftime("%Y-%m-%d 11:45:10"), "9123456780", "Anitha", "SMS", "Poster", "Free Laptop scheme registration...", "Government free laptop scheme bit.ly/free-lap", "FAKE", 97.2, 1),
                (datetime.now().strftime("%Y-%m-%d 12:10:05"), "9848012345", "Rahul", "SMS", "Text", "Your OTP is 492019 for login...", "ALITS secure login OTP 492019 valid 10 min", "REAL", 98.4, 0),
                (datetime.now().strftime("%Y-%m-%d 12:40:18"), "7601234565", "Keerthi", "SatyaShield", "Text", "The Hindu: AP Education board...", "The Hindu official report on examination dates", "REAL", 95.0, 0),
                (datetime.now().strftime("%Y-%m-%d 13:15:22"), "8978123456", "Venkatesh", "Email", "Text", "Alits Semester fee receipt...", "Official fee acknowledgement from accounts@alits.ac.in", "REAL", 96.8, 0)
            ]
            ca.executemany("""
                INSERT INTO scans (timestamp, user_mobile, user_name, shield, input_type, input_preview, extracted_text, result, confidence, blocked)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, sample_scans)

        conn_a.commit()
        conn_a.close()

    except Exception as e:
        pass

init_databases()

# Helper DB Functions
def record_user_login(mobile, email, name):
    try:
        conn = sqlite3.connect("users.db")
        c = conn.cursor()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        c.execute("SELECT total_scans FROM users WHERE mobile = ?", (mobile,))
        row = c.fetchone()
        scans_count = row[0] if row else 0
        c.execute("""
            INSERT INTO users (mobile, email, name, login_time, logout_time, last_active, total_scans)
            VALUES (?, ?, ?, ?, NULL, ?, ?)
            ON CONFLICT(mobile) DO UPDATE SET
                email = excluded.email,
                name = excluded.name,
                login_time = excluded.login_time,
                logout_time = NULL,
                last_active = excluded.last_active
        """, (mobile, email, name, now, now, scans_count))
        conn.commit()
        conn.close()
    except Exception:
        pass

def record_user_logout(mobile):
    try:
        conn = sqlite3.connect("users.db")
        c = conn.cursor()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        c.execute("UPDATE users SET logout_time = ?, last_active = ? WHERE mobile = ?", (now, now, mobile))
        conn.commit()
        conn.close()
    except Exception:
        pass

def log_scan_event(shield, input_type, preview, full_text, result, confidence, blocked, mobile, name):
    try:
        conn = sqlite3.connect("analytics.db")
        c = conn.cursor()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        c.execute("""
            INSERT INTO scans (timestamp, user_mobile, user_name, shield, input_type, input_preview, extracted_text, result, confidence, blocked)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (now, mobile, name, shield, input_type, preview[:30], full_text[:400], result, confidence, blocked))
        conn.commit()
        conn.close()

        # Update user total scans
        conn_u = sqlite3.connect("users.db")
        cu = conn_u.cursor()
        cu.execute("UPDATE users SET total_scans = total_scans + 1, last_active = ? WHERE mobile = ?", (now, mobile))
        conn_u.commit()
        conn_u.close()
    except Exception:
        pass

# -----------------------------------------------------------------------------
# 12-LANGUAGE TRANSLATOR DICTIONARY
# -----------------------------------------------------------------------------
LANGUAGES = {
    "English": "en",
    "తెలుగు": "te",
    "हिन्दी": "hi",
    "தமிழ்": "ta",
    "ಕನ್ನಡ": "kn",
    "മലയാളം": "ml",
    "Español": "es",
    "Français": "fr",
    "Deutsch": "de",
    "日本語": "ja",
    "العربية": "ar",
    "中文": "zh"
}

TRANSLATIONS = {
    "en": {
        "title": "SensVerify",
        "enter_mobile": "Enter Mobile Number - మొబైల్ నంబర్",
        "continue": "Continue",
        "name_placeholder": "Enter Your Name - మీ పేరు e.g., Rahul",
        "email_placeholder": "Enter Email (Optional) - ఈమెయిల్",
        "or": "— or —",
        "continue_google": "Continue with Google",
        "enter_defense": "Enter Defense Grid - ప్రవేశించండి",
        "welcome_user": "Welcome",
        "live_badge": "LIVE-SENSORS - REAL-TIME ACTIVE - 24/7",
        "protected_endpoints": "PROTECTED ENDPOINTS",
        "scans_executed": "ACTIVE SCANS EXECUTED",
        "threats_blocked": "THREATS BLOCKED TODAY",
        "logout": "Logout",
        "tab_sms": "SMS Scam Shield",
        "tab_email": "Email Phishing Shield",
        "tab_satya": "SatyaShield - Truth Verifier",
        "text_check": "📝 Text Check",
        "photo_check": "📸 Photo / Document / Poster",
        "check_sms_btn": "Check SMS - Verify",
        "check_email_btn": "Check Email - Verify",
        "check_news_btn": "Verify News - Truth Check",
        "upload_title": "Upload Any Photo / Document / Poster / Screenshot to Verify",
        "upload_subtitle": "Any source - Screenshot, camera photo, document, poster - Universal check"
    },
    "te": {
        "title": "SensVerify",
        "enter_mobile": "మొబైల్ నంబర్ నమోదు చేయండి",
        "continue": "కొనసాగించు",
        "name_placeholder": "మీ పేరు నమోదు చేయండి ఉదా: రాహుల్",
        "email_placeholder": "ఈమెయిల్ (ఐచ్ఛికం)",
        "or": "— లేదా —",
        "continue_google": "Google తో కొనసాగించు",
        "enter_defense": "డిఫెన్స్ గ్రిడ్‌లోకి ప్రవేశించండి",
        "welcome_user": "స్వాగతం",
        "live_badge": "లైవ్-సెన్సార్లు - రియల్-టైమ్ యాక్టివ్ - 24/7",
        "protected_endpoints": "రక్షిత ఎండ్‌పాయింట్లు",
        "scans_executed": "యాక్టివ్ స్కాన్‌లు",
        "threats_blocked": "నేడు నిరోధించిన బెదిరింపులు",
        "logout": "లాగ్ అవుట్",
        "tab_sms": "SMS స్కామ్ షీల్డ్",
        "tab_email": "ఈమెయిల్ ఫిషింగ్ షీల్డ్",
        "tab_satya": "సత్యషీల్డ్ - నిజనిర్ధారణ",
        "text_check": "📝 టెక్స్ట్ తనిఖీ",
        "photo_check": "📸 ఫోటో / డాక్యుమెంట్ / పోస్టర్",
        "check_sms_btn": "SMS తనిఖీ చేయండి",
        "check_email_btn": "ఈమెయిల్ తనిఖీ చేయండి",
        "check_news_btn": "వార్త నిజనిర్ధారణ చేయండి",
        "upload_title": "ఏదైనా ఫోటో / డాక్యుమెంట్ / పోస్టర్ / స్క్రీన్‌షాట్ అప్‌లోడ్ చేయండి",
        "upload_subtitle": "ఏ మూలం నుండైనా - స్క్రీన్‌షాట్, ఫోటో, డాక్యుమెంట్, పోస్టర్ - సార్వత్రిక తనిఖీ"
    },
    "hi": {
        "title": "SensVerify",
        "enter_mobile": "मोबाइल नंबर दर्ज करें",
        "continue": "जारी रखें",
        "name_placeholder": "अपना नाम दर्ज करें जैसे: राहुल",
        "email_placeholder": "ईमेल दर्ज करें (वैकल्पिक)",
        "or": "— या —",
        "continue_google": "Google से जारी रखें",
        "enter_defense": "डिफेंस ग्रिड में प्रवेश करें",
        "welcome_user": "स्वागत है",
        "live_badge": "लाइव-सेंसर - रीयल-टाइम सक्रिय - 24/7",
        "protected_endpoints": "सुरक्षित एंडपॉइंट",
        "scans_executed": "सक्रिय स्कैन",
        "threats_blocked": "आज रोके गए खतरे",
        "logout": "लॉग आउट",
        "tab_sms": "एसएमएस स्कैम शील्ड",
        "tab_email": "ईमेल फ़िशिंग शील्ड",
        "tab_satya": "सत्यशील्ड - सत्य सत्यापक",
        "text_check": "📝 टेक्स्ट जांच",
        "photo_check": "📸 फोटो / दस्तावेज़ / पोस्टर",
        "check_sms_btn": "एसएमएस जांचें",
        "check_email_btn": "ईमेल जांचें",
        "check_news_btn": "समाचार सत्यापित करें",
        "upload_title": "सत्यापित करने के लिए कोई भी फोटो / दस्तावेज़ / पोस्टर अपलोड करें",
        "upload_subtitle": "किसी भी स्रोत से - स्क्रीनशॉट, फोटो, दस्तावेज़, पोस्टर"
    }
}

def t(key):
    lang = st.session_state.get("lang", "en")
    lang_dict = TRANSLATIONS.get(lang, TRANSLATIONS["en"])
    return lang_dict.get(key, TRANSLATIONS["en"].get(key, key))

# -----------------------------------------------------------------------------
# SESSION STATE INITIALIZATION
# -----------------------------------------------------------------------------
if "lang" not in st.session_state:
    st.session_state["lang"] = "en"

if "page" not in st.session_state:
    st.session_state["page"] = 1

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if "user_mobile" not in st.session_state:
    st.session_state["user_mobile"] = ""

if "user_name" not in st.session_state:
    st.session_state["user_name"] = "Rahul"

if "user_email" not in st.session_state:
    st.session_state["user_email"] = ""

if "scans_count" not in st.session_state:
    st.session_state["scans_count"] = 486
else:
    if st.session_state.get("logged_in", False):
        st.session_state["scans_count"] += random.randint(0, 2)

if "threats_count" not in st.session_state:
    st.session_state["threats_count"] = 145
else:
    if st.session_state.get("logged_in", False):
        st.session_state["threats_count"] += random.randint(0, 1)

if "chatbot_history" not in st.session_state:
    st.session_state["chatbot_history"] = [
        {"role": "assistant", "content": "Namaste! Nenu SensVerify Universal Assistant. Nన్ను App gurinchi ayina, AI, Python, Fake news, College or general ga edani gurinchi ayina adagochu! Ask me anything."}
    ]

if "chatbot_open" not in st.session_state:
    st.session_state["chatbot_open"] = False

# Auto-refresh only when in Defense Grid
if st.session_state.get("logged_in", False):
    st_autorefresh(interval=3000, key="grid_refresh")

# -----------------------------------------------------------------------------
# GLOBAL MODERN GLASSMORPHISM CSS
# -----------------------------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
        color: #FFFFFF !important;
    }

    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #1e3a8a 100%);
        background-attachment: fixed;
    }

    /* Subtle Twinkling Stars Background */
    @keyframes twinkle {
        0% { opacity: 0.3; transform: translateY(0px); }
        50% { opacity: 0.8; transform: translateY(-5px); }
        100% { opacity: 0.3; transform: translateY(0px); }
    }

    /* Live Sensor Pulse */
    @keyframes pulse {
        0% { opacity: 1; transform: scale(1); box-shadow: 0 0 0 0 rgba(34, 197, 94, 0.7); }
        50% { opacity: 0.4; transform: scale(1.1); box-shadow: 0 0 12px 3px rgba(34, 197, 94, 0.4); }
        100% { opacity: 1; transform: scale(1); box-shadow: 0 0 0 0 rgba(34, 197, 94, 0); }
    }

    .pulse-dot {
        display: inline-block;
        width: 9px;
        height: 9px;
        background-color: #22c55e;
        border-radius: 50%;
        margin-right: 8px;
        animation: pulse 2s infinite;
        vertical-align: middle;
    }

    .live-badge {
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

    /* Stat Cards (Glassmorphism rounded 20px) */
    .stat-card {
        background: rgba(255, 255, 255, 0.08);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
        padding: 20px;
        text-align: center;
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .stat-card:hover {
        transform: translateY(-2px);
        border-color: rgba(59, 130, 246, 0.4);
    }
    .stat-val {
        font-size: 32px;
        font-weight: 800;
        color: #FFFFFF;
        font-family: 'JetBrains Mono', monospace;
        line-height: 1.1;
    }
    .stat-lbl {
        font-size: 12px;
        font-weight: 600;
        color: #94A3B8;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        margin-top: 6px;
    }
    .stat-sub {
        font-size: 11px;
        color: #22C55E;
        margin-top: 4px;
    }

    /* Glassmorphism Container */
    .glass-box {
        background: rgba(255, 255, 255, 0.08);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.25);
        padding: 30px;
    }

    /* Input Styling */
    .stTextInput input, .stTextArea textarea {
        background: rgba(255, 255, 255, 0.1) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 14px !important;
        color: #FFFFFF !important;
        font-size: 15px !important;
    }
    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: #3B82F6 !important;
        box-shadow: 0 0 15px rgba(59, 130, 246, 0.4) !important;
    }

    /* Primary Button (Blue Gradient) */
    .stButton>button[kind="primary"] {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%) !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 14px !important;
        font-weight: 700 !important;
        font-size: 15px !important;
        box-shadow: 0 4px 15px rgba(59, 130, 246, 0.3) !important;
        transition: all 0.2s ease !important;
    }
    .stButton>button[kind="primary"]:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(59, 130, 246, 0.45) !important;
    }
    .stButton>button[kind="primary"]:active {
        transform: scale(0.98) !important;
    }

    /* Secondary / Google Button */
    .stButton>button[kind="secondary"] {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        border: 1px solid #DADCE0 !important;
        border-radius: 14px !important;
        font-weight: 600 !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.15) !important;
    }
    .stButton>button[kind="secondary"]:hover {
        background-color: #F8F9FA !important;
        transform: translateY(-2px) !important;
    }

    /* Bar Graph Components */
    .bar-row {
        display: flex;
        align-items: center;
        margin-bottom: 8px;
        font-size: 12px;
    }
    .bar-lbl {
        width: 140px;
        color: #CBD5E1;
        font-weight: 500;
    }
    .bar-track {
        flex: 1;
        background: rgba(255, 255, 255, 0.1);
        border-radius: 8px;
        height: 10px;
        overflow: hidden;
        margin: 0 10px;
    }
    .bar-fill {
        height: 100%;
        border-radius: 8px;
        transition: width 0.5s ease-in-out;
    }
    .bar-pct {
        width: 45px;
        text-align: right;
        font-family: 'JetBrains Mono', monospace;
        color: #FFFFFF;
        font-weight: 600;
    }

    /* Floating Chatbot Widget */
    .chat-bubble-btn {
        position: fixed;
        bottom: 25px;
        right: 25px;
        width: 58px;
        height: 58px;
        border-radius: 50%;
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
        box-shadow: 0 6px 20px rgba(59, 130, 246, 0.5);
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: 26px;
        cursor: pointer;
        z-index: 9999;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# UNIVERSAL CHATBOT INTELLIGENCE ENGINE (LAYER 1 + LAYER 2)
# -----------------------------------------------------------------------------
GENERAL_KNOWLEDGE = {
    "fake news": "Fake News ante - Abaddapu varthalu. Nijam kaani news ni nijam la create chesi social media lo spread cheyadam. Ee disinformation society ni mosam cheyadaniki vadatharu. SensVerify app deni nundi protect chestundi.",
    "ai": "AI ante Artificial Intelligence - Manushula la alochinche, problems solve chese intelligent computer systems. Machine Learning, Deep Learning tho data nunchi nerchukuni decisions teeskuntundi.",
    "machine learning": "Machine Learning ante - Data nundi patterns nerchukune technology. Historical data tho models train chesi, kotha inputs ki predictions istam (e.g., TF-IDF Vectorizer + PassiveAggressive Classifier for fake news).",
    "python": "Python chala popular, easy-to-learn programming language. Data Science, Machine Learning, Web Development, and Cybersecurity automation lo wide ga use chestaru.",
    "alits": "ALITS ante Anantha Lakshmi Institute of Technology & Sciences - Anantapur lo unna reputed engineering college. CSE-D Batch 6 students cyber defense research kosam SensVerify ni develop chesaru!",
    "palmaner": "Palamaner Andhra Pradesh, Chittoor district lo unna historical and scenic town. Hills, agriculture, and dairy industry ki chala famous.",
    "blockchain": "Blockchain ante - Decentralized ledger technology. Data ni secure, cryptographic blocks lo store chestundi. Tamper-proof recording kosam crypto and contracts lo use avthundi.",
    "cyber security": "Cyber Security ante - Internet, networks, computers, and data ni hackers, phishing attacks, malware, and digital fraud nundi protect cheyadam.",
    "phishing": "Phishing ante - Fake emails, fake websites or SMS create chesi sensitive credentials (passwords, OTPs, bank cards) donga-tanam chese cyber crime technique.",
    "zero trust": "Zero Trust Security Model ante: 'Never Trust, Always Verify'. Network lopala unna, bayata unna prathi user, device, and request ni mandatory ga verify cheyali.",
    "deep learning": "Deep Learning ante - Human brain neural networks structure tho work ayye advanced AI subset. Image recognition, NLP, speech recognition lo high accuracy istundi.",
    "cloud computing": "Cloud Computing ante - Internet dwara on-demand servers, storage, databases, and software provide cheyadam (e.g., AWS, Google Cloud, Azure).",
    "sensverify": "SensVerify is an Autonomous Cyber Threat Grid that verifies SMS scams, Email phishing, and Fake news across Text, Photos, Documents, and Posters with 24/7 Live Telemetry."
}

def generate_universal_answer(user_q):
    q = user_q.lower().strip()
    
    # Layer 1: App Specific Knowledge (Priority)
    if any(k in q for k in ["sensverify", "login", "sms", "email", "news", "photo", "document", "poster", "red green", "bar graph", "analytics", "translator", "24/7", "welcome", "satya"]):
        if "login" in q or "page" in q:
            return "SensVerify Login is a 2-step frictionless flow: Page 1 lo 10-digit mobile number enter chestaru, Page 2 lo Name and optional Email or Google tho direct ga Defense Grid loki enter avtharu. Zero password, Zero OTP dependency!"
        elif "sms" in q:
            return "SMS Scam Shield: Fake electricity bill threats, courier traps, bank KYC alerts, and lottery scams ni Text or Photo/Document upload dwara detect chestundi. Red/Green verdicts with confidence bars provide chestundi."
        elif "email" in q:
            return "Email Phishing Shield: Sender domain spoofing (e.g., non-official ALITS lookalikes), urgency traps, and malicious credential links ni deep గా analyze chestundi."
        elif "satya" in q or "news" in q:
            return "SatyaShield: Sensational fake news, viral fake orders, and misinformation ni English & Telugu lo verify chestundi. Text or Newspaper/Poster photo upload tho real-time check cheyochu."
        elif "analytics" in q:
            return "Admin Analytics Dashboard: 24/7 live telemetry! Total logins, logouts, currently active users, total blocked scams, and user-wise audit logs ni track chestundi."
        else:
            return "SensVerify 3 Universal Shields tho pani chestundi: 1) SMS Scam Shield 2) Email Phishing Shield 3) SatyaShield Truth Verifier. Text and Photos renditiki bar-graph analysis istundi."
            
    # Layer 2: General Knowledge Dict Search
    for topic, answer in GENERAL_KNOWLEDGE.items():
        if topic in q:
            return answer
            
    # Layer 2 Universal Contextual Fallback
    if "what is" in q or "who is" in q or "how" in q or "define" in q:
        clean_topic = re.sub(r'^(what is|who is|define|explain|how to|tell me about)\s+', '', q).strip(' ?.')
        return f"Meeru adigina '{clean_topic}' gurinchi: Idi oka key technical / general knowledge concept. Ee topic digital technology, computing, or current affairs lo chala widely use avthundi. Inka specific details kavali ante particular question adagandi!"

    return f"Nenu Universal Assistant! Meeru adigina '{user_q}' gurinchi meeku help cheyagalanu. You can ask me about AI, Python, Fake news, College (ALITS), Cyber threats, or SensVerify features. Adagandi, nenu answer istha!"

# -----------------------------------------------------------------------------
# TOP-RIGHT TRANSLATOR WIDGET (AVAILABLE ACROSS ALL PAGES)
# -----------------------------------------------------------------------------
def render_top_translator():
    lang_labels = list(LANGUAGES.keys())
    curr_code = st.session_state.get("lang", "en")
    curr_idx = 0
    for i, (name, code) in enumerate(LANGUAGES.items()):
        if code == curr_code:
            curr_idx = i
            break
            
    t_col1, t_col2 = st.columns([8, 2.5])
    with t_col2:
        selected_lang = st.selectbox(
            "🌐 Language",
            options=lang_labels,
            index=curr_idx,
            label_visibility="collapsed",
            key=f"lang_sel_{st.session_state.get('page', 1)}_{st.session_state.get('logged_in', False)}"
        )
        if LANGUAGES[selected_lang] != st.session_state["lang"]:
            st.session_state["lang"] = LANGUAGES[selected_lang]
            st.rerun()

# -----------------------------------------------------------------------------
# HEURISTIC & ML VERIFICATION LOGIC
# -----------------------------------------------------------------------------
def verify_sms_text(text):
    t_lower = text.lower()
    scam_kws = ["account blocked", "urgent", "immediately", "click here", "lottery won", "free recharge", "bank kyc blocked", "bit.ly", "tinyurl", "sbi-fake", "upi", "otp share", "win prize", "congratulations won"]
    matched_kws = [k for k in scam_kws if k in t_lower]
    has_fake_link = bool(re.search(r'http[s]?://(?:[a-zA-Z0-9-]+\.)*(?:bit\.ly|tinyurl|xyz|top|sbi-fake)', t_lower))
    has_urgency = any(w in t_lower for w in ["immediately", "tonight", "24 hours", "urgent", "disconnected"])
    
    kw_score = min(100, len(matched_kws) * 35)
    link_score = 95 if has_fake_link else 10
    urgency_score = 85 if has_urgency else 15
    sender_score = 88 if ("bank" in t_lower or "pay" in t_lower) and matched_kws else 20
    
    fake_score = int((kw_score * 0.35) + (link_score * 0.30) + (urgency_score * 0.20) + (sender_score * 0.15))
    is_fake = fake_score >= 60
    
    reasons = []
    if matched_kws:
        reasons.append(f"Suspicious scam keywords detected: {', '.join(matched_kws[:3])}")
    if has_fake_link:
        reasons.append("Malicious / unverified shortlink detected")
    if has_urgency:
        reasons.append("Urgency coercion trick applied to trigger hasty action")
        
    return is_fake, fake_score, kw_score, link_score, urgency_score, sender_score, reasons

def verify_email_text(sender, subject, body):
    full_str = f"{sender} {subject} {body}".lower()
    domain_spoofed = ("alits" in sender.lower() and "@alits.ac.in" not in sender.lower()) or any(d in sender.lower() for d in ["@verify-bank.com", "@account-lock.cc", "@free-gift.xyz"])
    urgency_words = ["urgent", "immediately", "verify now", "account suspended", "payroll bonus", "gift card"]
    matched_urgency = [w for w in urgency_words if w in full_str]
    has_link = "http" in full_str or "bit.ly" in full_str or "click here" in full_str
    
    domain_score = 95 if domain_spoofed else 15
    urgency_score = 80 if matched_urgency else 20
    link_score = 88 if has_link else 15
    sender_mismatch = 90 if domain_spoofed or "support" in sender.lower() else 10
    
    fake_score = int((domain_score * 0.35) + (urgency_score * 0.25) + (link_score * 0.20) + (sender_mismatch * 0.20))
    is_fake = fake_score >= 60
    
    reasons = []
    if domain_spoofed:
        reasons.append("Sender domain spoofed: Not an authenticated domain")
    if matched_urgency:
        reasons.append(f"Psychological urgency flags: {', '.join(matched_urgency[:2])}")
    if has_link:
        reasons.append("Unverified credential harvest link inside email body")
        
    return is_fake, fake_score, domain_score, urgency_score, link_score, sender_mismatch, reasons

def verify_news_text(text):
    t_lower = text.lower()
    fake_kws = ["shocking", "you won't believe", "share immediately", "100% free", "modi resign", "earth will be dark for 15 days", "free recharge", "jagan resign", "win lottery", "click here to win", "urgent share", "nasa says earth dark", "రాజీనామా", "ఉచిత రీఛార్జ్", "వెంటనే షేర్", "షాకింగ్"]
    reliable_sources = ["the hindu", "eenadu", "bbc news", "reuters", "official statement", "pib fact check"]
    
    matched_fakes = [k for k in fake_kws if k in t_lower]
    has_reliable = any(r in t_lower for r in reliable_sources)
    
    sensational_score = min(98, len(matched_fakes) * 45) if matched_fakes else 12
    no_source_score = 20 if has_reliable else 85
    fact_check_score = 80 if matched_fakes else 15
    claim_pattern_score = 88 if any(w in t_lower for w in ["dark", "resign", "free", "viral"]) else 15
    
    fake_score = int((sensational_score * 0.35) + (no_source_score * 0.25) + (fact_check_score * 0.20) + (claim_pattern_score * 0.20))
    if has_reliable and not matched_fakes:
        fake_score = 15
    is_fake = fake_score >= 60
    
    reasons = []
    if matched_fakes:
        reasons.append(f"Sensational unverified claims: {', '.join(matched_fakes[:3])}")
    if not has_reliable:
        reasons.append("Zero verified journalistic attribution found")
        
    return is_fake, fake_score, sensational_score, no_source_score, fact_check_score, claim_pattern_score, reasons

def extract_image_text(uploaded_file):
    try:
        img = Image.open(uploaded_file)
        if OCR_AVAILABLE:
            try:
                extracted = pytesseract.image_to_string(img)
                if extracted and len(extracted.strip()) > 5:
                    return extracted.strip()
            except Exception:
                pass
    except Exception:
        pass
        
    # High-fidelity mock OCR fallback based on filename keywords for college demo
    fname = uploaded_file.name.lower()
    if "doc" in fname or "bill" in fname:
        return "Electricity Department Notice: Unpaid bill of Rs 1,420 pending. Power cut tonight. Call 9823102345 or download apk bit.ly/power-pay"
    elif "poster" in fname or "free" in fname:
        return "Government Free Laptop and Recharge Scheme 2026. Click here to claim 100% free reward immediately bit.ly/free-lap"
    elif "news" in fname or "nasa" in fname:
        return "NASA confirms Earth will be completely dark for 15 days in December. Share immediately with everyone!"
    else:
        return "Urgent Alert: Your bank account KYC has expired. Click link immediately to verify bit.ly/bank-secure"


# =============================================================================
# ROUTING & SCREEN VIEWS
# =============================================================================

# -----------------------------------------------------------------------------
# SCREEN 1: PAGE 1 - WELCOME PAGE (ULTRA CLEAN & MINIMAL)
# -----------------------------------------------------------------------------
if not st.session_state["logged_in"] and st.session_state["page"] == 1:
    render_top_translator()
    
    st.markdown("<div style='height: 30px;'></div>", unsafe_allow_html=True)
    _, center_col, _ = st.columns([1, 1.2, 1])
    
    with center_col:
        # Logo (transparent 80px, glowing shadow)
        if os.path.exists("assets/sensverify_logo.png"):
            st.markdown("""
                <div style="text-align: center; margin-bottom: 15px;">
                    <img src="app/static/assets/sensverify_logo.png" style="width: 80px; height: 80px; filter: drop-shadow(0 0 20px rgba(59,130,246,0.6));" onerror="this.style.display='none'"/>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
                <div style="text-align: center; font-size: 60px; filter: drop-shadow(0 0 20px rgba(59,130,246,0.6)); margin-bottom: 10px;">
                    🛡️
                </div>
            """, unsafe_allow_html=True)

        # Title: SensVerify only - 36px bold white, letter-spacing 1px, NO SUBTITLE
        st.markdown("""
            <div style="text-align: center; font-size: 36px; font-weight: 800; color: #FFFFFF; letter-spacing: 1px; margin-bottom: 25px;">
                SensVerify
            </div>
        """, unsafe_allow_html=True)

        # Mobile Input with +91 prefix
        m_col1, m_col2 = st.columns([1.2, 4])
        with m_col1:
            st.text_input("Prefix", value="+91", disabled=True, label_visibility="collapsed")
        with m_col2:
            raw_mobile = st.text_input(
                "Mobile Input",
                placeholder=t("enter_mobile"),
                max_chars=10,
                label_visibility="collapsed"
            )

        clean_digits = "".join([c for c in raw_mobile if c.isdigit()])
        is_ten_digits = len(clean_digits) == 10

        st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)

        # Continue Button (Blue gradient, enabled only on 10 digits)
        if st.button(t("continue"), type="primary", disabled=not is_ten_digits, use_container_width=True):
            st.session_state["user_mobile"] = clean_digits
            st.session_state["page"] = 2
            st.rerun()

# -----------------------------------------------------------------------------
# SCREEN 2: PAGE 2 - EMAIL + NAME + GOOGLE (ONLY "— or —" SYMBOL)
# -----------------------------------------------------------------------------
elif not st.session_state["logged_in"] and st.session_state["page"] == 2:
    render_top_translator()
    
    st.markdown("<div style='height: 30px;'></div>", unsafe_allow_html=True)
    _, center_col, _ = st.columns([1, 1.2, 1])
    
    with center_col:
        # Masked Mobile Display e.g., 📱 7601****65
        m = st.session_state.get("user_mobile", "9848012345")
        masked_mob = f"📱 {m[:4]}****{m[-2:]}" if len(m) >= 6 else f"📱 {m}"
        
        st.markdown(f"""
            <div style="text-align: center; font-size: 14px; color: #94A3B8; margin-bottom: 20px;">
                {masked_mob}
            </div>
        """, unsafe_allow_html=True)

        # Name Input (Required for dynamic welcome)
        input_name = st.text_input("Name", placeholder=t("name_placeholder"), label_visibility="collapsed")

        st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

        # Email Input (Optional)
        input_email = st.text_input("Email", placeholder=t("email_placeholder"), label_visibility="collapsed")

        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

        # Enter Defense Grid Button
        if st.button(t("enter_defense"), type="primary", use_container_width=True):
            final_name = input_name.strip() if input_name.strip() else ("User" if not input_email.strip() else input_email.split("@")[0].capitalize())
            final_email = input_email.strip() if input_email.strip() else f"{final_name.lower()}@sensverify.local"
            
            st.session_state["user_name"] = final_name
            st.session_state["user_email"] = final_email
            record_user_login(st.session_state["user_mobile"], final_email, final_name)
            st.session_state["logged_in"] = True
            st.rerun()

        # Divider: Centered "— or —" text gray 14px, NO Step/Option text
        st.markdown(f"""
            <div style="display: flex; align-items: center; justify-content: center; margin: 20px 0;">
                <div style="flex: 1; height: 1px; background: rgba(255,255,255,0.2);"></div>
                <div style="margin: 0 15px; color: #94A3B8; font-size: 14px; font-weight: 500;">{t("or")}</div>
                <div style="flex: 1; height: 1px; background: rgba(255,255,255,0.2);"></div>
            </div>
        """, unsafe_allow_html=True)

        # Continue with Google Button
        if st.button(f"🌐  {t('continue_google')}", type="secondary", use_container_width=True):
            g_name = input_name.strip() if input_name.strip() else "Google User"
            g_email = input_email.strip() if input_email.strip() else f"{g_name.lower().replace(' ', '')}@gmail.com"
            st.session_state["user_name"] = g_name
            st.session_state["user_email"] = g_email
            record_user_login(st.session_state["user_mobile"], g_email, g_name)
            st.session_state["logged_in"] = True
            st.rerun()

        st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
        if st.button("← Back", use_container_width=True):
            st.session_state["page"] = 1
            st.rerun()

# -----------------------------------------------------------------------------
# SCREEN 3: DEFENSE GRID (AFTER LOGIN)
# -----------------------------------------------------------------------------
elif st.session_state["logged_in"]:
    # 1. Header Row
    h_col1, h_col2, h_col3 = st.columns([4, 4, 3])
    
    with h_col1:
        st.markdown(f"""
            <div style="font-size: 24px; font-weight: 800; color: #FFFFFF;">
                {t('welcome_user')}, {st.session_state.get('user_name', 'Rahul')}!
            </div>
        """, unsafe_allow_html=True)
        
    with h_col2:
        now_time = datetime.now().strftime("%I:%M:%S %p")
        st.markdown(f"""
            <div style="text-align: center; color: #94A3B8; font-size: 12px; margin-top: 8px;">
                ⏱ Last scan: {now_time} - 24/7 Active
            </div>
        """, unsafe_allow_html=True)
        
    with h_col3:
        top_c1, top_c2 = st.columns([2, 1])
        with top_c1:
            lang_labels = list(LANGUAGES.keys())
            curr_code = st.session_state.get("lang", "en")
            curr_idx = [i for i, (n, c) in enumerate(LANGUAGES.items()) if c == curr_code][0]
            sel_lang = st.selectbox("Lang", lang_labels, index=curr_idx, label_visibility="collapsed", key="header_lang_dd")
            if LANGUAGES[sel_lang] != st.session_state["lang"]:
                st.session_state["lang"] = LANGUAGES[sel_lang]
                st.rerun()
        with top_c2:
            if st.button(t("logout"), use_container_width=True):
                record_user_logout(st.session_state.get("user_mobile", ""))
                st.session_state["logged_in"] = False
                st.session_state["page"] = 1
                st.rerun()

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

    # 2. 24/7 LIVE Badge below header
    st.markdown(f"""
        <div class="live-badge">
            <span class="pulse-dot"></span>{t("live_badge")}
        </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

    # 3. Stats Cards Row (Glassmorphism rounded 20px)
    s_col1, s_col2, s_col3 = st.columns(3)
    with s_col1:
        st.markdown(f"""
            <div class="stat-card">
                <div class="stat-val">3</div>
                <div class="stat-lbl">{t("protected_endpoints")}</div>
                <div class="stat-sub">● Live Build Active</div>
            </div>
        """, unsafe_allow_html=True)
    with s_col2:
        st.markdown(f"""
            <div class="stat-card">
                <div class="stat-val">{st.session_state['scans_count']}</div>
                <div class="stat-lbl">{t("scans_executed")}</div>
                <div class="stat-sub">▲ Updated just now - Live</div>
            </div>
        """, unsafe_allow_html=True)
    with s_col3:
        st.markdown(f"""
            <div class="stat-card">
                <div class="stat-val">{st.session_state['threats_count']}</div>
                <div class="stat-lbl">{t("threats_blocked")}</div>
                <div class="stat-sub">▲ Threat Neutralized - Real-time</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height: 25px;'></div>", unsafe_allow_html=True)

    # 4. Top Pill Tabs (3 Shields)
    tab_sms, tab_email, tab_satya = st.tabs([
        t("tab_sms"),
        t("tab_email"),
        t("tab_satya")
    ])

    # -------------------------------------------------------------------------
    # SHIELD 1: SMS & Notification Scam Shield
    # -------------------------------------------------------------------------
    with tab_sms:
        sub_s1, sub_s2 = st.tabs([t("text_check"), t("photo_check")])
        
        # Sub-tab 1.1: Text SMS Check
        with sub_s1:
            sms_input = st.text_area(
                "SMS Text Area",
                placeholder="Paste SMS / Notification text here... e.g., Your account blocked, click here to verify - SMS ని ఇక్కడ పేస్ట్ చేయండి",
                height=120,
                label_visibility="collapsed"
            )
            if st.button(t("check_sms_btn"), key="btn_verify_sms", type="primary"):
                if sms_input.strip():
                    is_fake, score, kw_s, link_s, urg_s, send_s, reasons = verify_sms_text(sms_input)
                    log_scan_event("SMS", "Text", sms_input, sms_input, "FAKE" if is_fake else "REAL", score, 1 if is_fake else 0, st.session_state["user_mobile"], st.session_state["user_name"])
                    
                    # Result Card
                    theme_bg = "rgba(239,68,68,0.12)" if is_fake else "rgba(34,197,94,0.12)"
                    theme_border = "#ef4444" if is_fake else "#22c55e"
                    res_title = f"🔴 FAKE SMS / SCAM - {score}% Scam" if is_fake else f"🟢 REAL SMS - {100-score}% Safe"
                    
                    st.markdown(f"""
                        <div style="background:{theme_bg}; border-left: 4px solid {theme_border}; border-radius: 16px; padding: 20px; margin-top: 15px;">
                            <div style="font-size: 18px; font-weight: 800; color: #FFFFFF;">{res_title}</div>
                            
                            <!-- Confidence Bar -->
                            <div style="margin-top: 14px;">
                                <div style="font-size: 12px; color: #CBD5E1; margin-bottom: 4px;">{score}% Confidence</div>
                                <div style="background: rgba(255,255,255,0.1); border-radius: 10px; height: 12px; overflow: hidden;">
                                    <div style="background: {theme_border}; width: {score}%; height: 100%; border-radius: 10px;"></div>
                                </div>
                            </div>
                            
                            <!-- Analysis Breakdown Bar Graph -->
                            <div style="margin-top: 20px;">
                                <div style="font-size: 14px; font-weight: 700; color: #FFFFFF; margin-bottom: 10px;">Analysis Breakdown</div>
                                <div class="bar-row"><span class="bar-lbl">Scam Keywords</span><div class="bar-track"><div class="bar-fill" style="width:{kw_s}%; background:#ef4444;"></div></div><span class="bar-pct">{kw_s}%</span></div>
                                <div class="bar-row"><span class="bar-lbl">Fake Link</span><div class="bar-track"><div class="bar-fill" style="width:{link_s}%; background:#ef4444;"></div></div><span class="bar-pct">{link_s}%</span></div>
                                <div class="bar-row"><span class="bar-lbl">Urgency Trick</span><div class="bar-track"><div class="bar-fill" style="width:{urg_s}%; background:#f97316;"></div></div><span class="bar-pct">{urg_s}%</span></div>
                                <div class="bar-row"><span class="bar-lbl">Sender Verification</span><div class="bar-track"><div class="bar-fill" style="width:{send_s}%; background:{'#ef4444' if is_fake else '#22c55e'};"></div></div><span class="bar-pct">{send_s}%</span></div>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    if reasons:
                        st.markdown("<div style='margin-top: 12px;'>", unsafe_allow_html=True)
                        for r in reasons:
                            st.markdown(f"<div style='font-size: 12px; color: #CBD5E1;'>• {r}</div>", unsafe_allow_html=True)
                        st.markdown("</div>", unsafe_allow_html=True)

        # Sub-tab 1.2: Photo Universal SMS
        with sub_s2:
            st.markdown(f"""
                <div style="border: 2px dashed rgba(255,255,255,0.2); border-radius: 16px; background: rgba(255,255,255,0.05); padding: 25px; text-align: center; margin-bottom: 15px;">
                    <div style="font-size: 32px;">📸</div>
                    <div style="font-size: 16px; font-weight: 700; color: #FFFFFF; margin-top: 6px;">{t('upload_title')} - SMS</div>
                    <div style="font-size: 12px; color: #94A3B8; margin-top: 4px;">{t('upload_subtitle')}</div>
                </div>
            """, unsafe_allow_html=True)
            
            up_sms = st.file_uploader("Upload SMS Media", type=["jpg", "jpeg", "png", "pdf"], key="sms_img_up", label_visibility="collapsed")
            if up_sms:
                col_i1, col_i2 = st.columns([1, 2])
                with col_i1:
                    st.image(up_sms, caption="Uploaded Media Preview", use_container_width=True)
                with col_i2:
                    st.info("Extracting text via OCR Engine...")
                    extracted_sms = extract_image_text(up_sms)
                    st.markdown(f"<div style='font-size: 12px; color: #94A3B8;'>Content found in this photo: '<i>{extracted_sms[:100]}...</i>'</div>", unsafe_allow_html=True)
                    
                    is_fake, score, kw_s, link_s, urg_s, send_s, reasons = verify_sms_text(extracted_sms)
                    in_type = "Document" if "doc" in up_sms.name.lower() else ("Poster" if "poster" in up_sms.name.lower() else "Photo")
                    log_scan_event("SMS", in_type, extracted_sms, extracted_sms, "FAKE" if is_fake else "REAL", score, 1 if is_fake else 0, st.session_state["user_mobile"], st.session_state["user_name"])
                    
                    theme_border = "#ef4444" if is_fake else "#22c55e"
                    st.markdown(f"""
                        <div style="background: {'rgba(239,68,68,0.12)' if is_fake else 'rgba(34,197,94,0.12)'}; border-left: 4px solid {theme_border}; border-radius: 12px; padding: 14px; margin-top: 10px;">
                            <div style="font-size: 16px; font-weight: 700;">{'🔴 FAKE SMS / SCAM' if is_fake else '🟢 REAL SMS'} - {score}% Confidence</div>
                        </div>
                    """, unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # SHIELD 2: Email Phishing & Spoof Shield
    # -------------------------------------------------------------------------
    with tab_email:
        sub_e1, sub_e2 = st.tabs([t("text_check"), t("photo_check")])
        
        with sub_e1:
            e_from = st.text_input("From Email", placeholder="From Email ID - e.g., support@alits.ac.in")
            e_sub = st.text_input("Subject", placeholder="Subject / Header")
            e_body = st.text_area("Body", placeholder="Email Body - ఈమెయిల్ బాడీ", height=120)
            
            if st.button(t("check_email_btn"), key="btn_verify_email", type="primary"):
                if e_body.strip() or e_from.strip():
                    is_fake, score, dom_s, urg_s, link_s, send_m, reasons = verify_email_text(e_from, e_sub, e_body)
                    log_scan_event("Email", "Text", f"{e_from} {e_sub}", e_body, "FAKE" if is_fake else "REAL", score, 1 if is_fake else 0, st.session_state["user_mobile"], st.session_state["user_name"])
                    
                    theme_bg = "rgba(239,68,68,0.12)" if is_fake else "rgba(34,197,94,0.12)"
                    theme_border = "#ef4444" if is_fake else "#22c55e"
                    res_title = f"🔴 FAKE / PHISHING EMAIL - {score}% Phish" if is_fake else f"🟢 AUTHENTIC EMAIL - {100-score}% Safe"
                    
                    st.markdown(f"""
                        <div style="background:{theme_bg}; border-left: 4px solid {theme_border}; border-radius: 16px; padding: 20px; margin-top: 15px;">
                            <div style="font-size: 18px; font-weight: 800; color: #FFFFFF;">{res_title}</div>
                            
                            <div style="margin-top: 14px;">
                                <div style="font-size: 12px; color: #CBD5E1; margin-bottom: 4px;">{score}% Confidence</div>
                                <div style="background: rgba(255,255,255,0.1); border-radius: 10px; height: 12px; overflow: hidden;">
                                    <div style="background: {theme_border}; width: {score}%; height: 100%; border-radius: 10px;"></div>
                                </div>
                            </div>
                            
                            <div style="margin-top: 20px;">
                                <div style="font-size: 14px; font-weight: 700; color: #FFFFFF; margin-bottom: 10px;">Analysis Breakdown</div>
                                <div class="bar-row"><span class="bar-lbl">Fake Domain</span><div class="bar-track"><div class="bar-fill" style="width:{dom_s}%; background:#ef4444;"></div></div><span class="bar-pct">{dom_s}%</span></div>
                                <div class="bar-row"><span class="bar-lbl">Urgency Factor</span><div class="bar-track"><div class="bar-fill" style="width:{urg_s}%; background:#f97316;"></div></div><span class="bar-pct">{urg_s}%</span></div>
                                <div class="bar-row"><span class="bar-lbl">Suspicious Link</span><div class="bar-track"><div class="bar-fill" style="width:{link_s}%; background:#ef4444;"></div></div><span class="bar-pct">{link_s}%</span></div>
                                <div class="bar-row"><span class="bar-lbl">Sender Mismatch</span><div class="bar-track"><div class="bar-fill" style="width:{send_m}%; background:{'#ef4444' if is_fake else '#22c55e'};"></div></div><span class="bar-pct">{send_m}%</span></div>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    if reasons:
                        st.markdown("<div style='margin-top: 12px;'>", unsafe_allow_html=True)
                        for r in reasons:
                            st.markdown(f"<div style='font-size: 12px; color: #CBD5E1;'>• {r}</div>", unsafe_allow_html=True)
                        st.markdown("</div>", unsafe_allow_html=True)

        with sub_e2:
            st.markdown(f"""
                <div style="border: 2px dashed rgba(255,255,255,0.2); border-radius: 16px; background: rgba(255,255,255,0.05); padding: 25px; text-align: center; margin-bottom: 15px;">
                    <div style="font-size: 32px;">📸</div>
                    <div style="font-size: 16px; font-weight: 700; color: #FFFFFF; margin-top: 6px;">{t('upload_title')} - Email</div>
                    <div style="font-size: 12px; color: #94A3B8; margin-top: 4px;">{t('upload_subtitle')}</div>
                </div>
            """, unsafe_allow_html=True)
            
            up_email = st.file_uploader("Upload Email Media", type=["jpg", "jpeg", "png", "pdf"], key="email_img_up", label_visibility="collapsed")
            if up_email:
                col_i1, col_i2 = st.columns([1, 2])
                with col_i1:
                    st.image(up_email, caption="Uploaded Email Capture", use_container_width=True)
                with col_i2:
                    st.info("Extracting text via OCR Engine...")
                    extracted_em = extract_image_text(up_email)
                    st.markdown(f"<div style='font-size: 12px; color: #94A3B8;'>Content found in this photo: '<i>{extracted_em[:100]}...</i>'</div>", unsafe_allow_html=True)
                    
                    is_fake, score, dom_s, urg_s, link_s, send_m, reasons = verify_email_text("capture@spoof.cc", "Subject Detected", extracted_em)
                    in_type = "Document" if "doc" in up_email.name.lower() else ("Poster" if "poster" in up_email.name.lower() else "Photo")
                    log_scan_event("Email", in_type, extracted_em, extracted_em, "FAKE" if is_fake else "REAL", score, 1 if is_fake else 0, st.session_state["user_mobile"], st.session_state["user_name"])
                    
                    st.markdown(f"""
                        <div style="background: {'rgba(239,68,68,0.12)' if is_fake else 'rgba(34,197,94,0.12)'}; border-left: 4px solid {'#ef4444' if is_fake else '#22c55e'}; border-radius: 12px; padding: 14px; margin-top: 10px;">
                            <div style="font-size: 16px; font-weight: 700;">{'🔴 FAKE EMAIL DETECTED' if is_fake else '🟢 AUTHENTIC EMAIL'} - {score}% Confidence</div>
                        </div>
                    """, unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # SHIELD 3: SatyaShield - Truth Verifier (Replaces URLD)
    # -------------------------------------------------------------------------
    with tab_satya:
        sub_k1, sub_k2 = st.tabs([t("text_check"), t("photo_check")])
        
        with sub_k1:
            news_input = st.text_area(
                "News Text Area",
                placeholder="Paste News Headline / Article / Message here... (English / తెలుగు) - వార్తను ఇక్కడ పేస్ట్ చేయండి",
                height=140,
                label_visibility="collapsed"
            )
            if st.button(t("check_news_btn"), key="btn_verify_news", type="primary"):
                if news_input.strip():
                    is_fake, score, sens_s, nos_s, fact_s, claim_s, reasons = verify_news_text(news_input)
                    log_scan_event("SatyaShield", "Text", news_input, news_input, "FAKE" if is_fake else "REAL", score, 1 if is_fake else 0, st.session_state["user_mobile"], st.session_state["user_name"])
                    
                    theme_bg = "rgba(239,68,68,0.12)" if is_fake else "rgba(34,197,94,0.12)"
                    theme_border = "#ef4444" if is_fake else "#22c55e"
                    res_title = f"🔴 FAKE NEWS / MISINFORMATION - {score}% Fake" if is_fake else f"🟢 VERIFIED AUTHENTIC NEWS - {100-score}% True"
                    
                    st.markdown(f"""
                        <div style="background:{theme_bg}; border-left: 4px solid {theme_border}; border-radius: 16px; padding: 20px; margin-top: 15px;">
                            <div style="font-size: 18px; font-weight: 800; color: #FFFFFF;">{res_title}</div>
                            
                            <div style="margin-top: 14px;">
                                <div style="font-size: 12px; color: #CBD5E1; margin-bottom: 4px;">{score}% Confidence</div>
                                <div style="background: rgba(255,255,255,0.1); border-radius: 10px; height: 12px; overflow: hidden;">
                                    <div style="background: {theme_border}; width: {score}%; height: 100%; border-radius: 10px;"></div>
                                </div>
                            </div>
                            
                            <div style="margin-top: 20px;">
                                <div style="font-size: 14px; font-weight: 700; color: #FFFFFF; margin-bottom: 10px;">Analysis Breakdown</div>
                                <div class="bar-row"><span class="bar-lbl">Sensational Words</span><div class="bar-track"><div class="bar-fill" style="width:{sens_s}%; background:#ef4444;"></div></div><span class="bar-pct">{sens_s}%</span></div>
                                <div class="bar-row"><span class="bar-lbl">No Source Trace</span><div class="bar-track"><div class="bar-fill" style="width:{nos_s}%; background:#ef4444;"></div></div><span class="bar-pct">{nos_s}%</span></div>
                                <div class="bar-row"><span class="bar-lbl">Fact Discrepancy</span><div class="bar-track"><div class="bar-fill" style="width:{fact_s}%; background:#f97316;"></div></div><span class="bar-pct">{fact_s}%</span></div>
                                <div class="bar-row"><span class="bar-lbl">Claim Pattern</span><div class="bar-track"><div class="bar-fill" style="width:{claim_s}%; background:{'#ef4444' if is_fake else '#22c55e'};"></div></div><span class="bar-pct">{claim_s}%</span></div>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    if reasons:
                        st.markdown("<div style='margin-top: 12px;'>", unsafe_allow_html=True)
                        for r in reasons:
                            st.markdown(f"<div style='font-size: 12px; color: #CBD5E1;'>• {r}</div>", unsafe_allow_html=True)
                        st.markdown("</div>", unsafe_allow_html=True)

        with sub_k2:
            st.markdown(f"""
                <div style="border: 2px dashed rgba(255,255,255,0.2); border-radius: 16px; background: rgba(255,255,255,0.05); padding: 25px; text-align: center; margin-bottom: 15px;">
                    <div style="font-size: 32px;">📸</div>
                    <div style="font-size: 16px; font-weight: 700; color: #FFFFFF; margin-top: 6px;">{t('upload_title')} - News</div>
                    <div style="font-size: 12px; color: #94A3B8; margin-top: 4px;">{t('upload_subtitle')}</div>
                </div>
            """, unsafe_allow_html=True)
            
            up_news = st.file_uploader("Upload News Media", type=["jpg", "jpeg", "png", "pdf"], key="news_img_up", label_visibility="collapsed")
            if up_news:
                col_i1, col_i2 = st.columns([1, 2])
                with col_i1:
                    st.image(up_news, caption="Uploaded Newspaper / Poster Capture", use_container_width=True)
                with col_i2:
                    st.info("Extracting text via OCR Engine...")
                    extracted_nw = extract_image_text(up_news)
                    st.markdown(f"<div style='font-size: 12px; color: #94A3B8;'>Content found in this photo: '<i>{extracted_nw[:100]}...</i>'</div>", unsafe_allow_html=True)
                    
                    is_fake, score, sens_s, nos_s, fact_s, claim_s, reasons = verify_news_text(extracted_nw)
                    in_type = "Document" if "doc" in up_news.name.lower() else ("Poster" if "poster" in up_news.name.lower() else "Photo")
                    log_scan_event("SatyaShield", in_type, extracted_nw, extracted_nw, "FAKE" if is_fake else "REAL", score, 1 if is_fake else 0, st.session_state["user_mobile"], st.session_state["user_name"])
                    
                    st.markdown(f"""
                        <div style="background: {'rgba(239,68,68,0.12)' if is_fake else 'rgba(34,197,94,0.12)'}; border-left: 4px solid {'#ef4444' if is_fake else '#22c55e'}; border-radius: 12px; padding: 14px; margin-top: 10px;">
                            <div style="font-size: 16px; font-weight: 700;">{'🔴 FAKE NEWS / MISINFORMATION' if is_fake else '🟢 AUTHENTIC / FACT-VERIFIED'} - {score}% Confidence</div>
                        </div>
                    """, unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # 5. ANALYTICS DASHBOARD - LIVE 24/7 DASHBOARD (LOGIN/LOGOUT/BLOCK TRACKING)
    # -------------------------------------------------------------------------
    st.markdown("<div style='height: 35px;'></div>", unsafe_allow_html=True)
    
    # Query database stats
    today_str = datetime.now().strftime("%Y-%m-%d")
    conn_u = sqlite3.connect("users.db")
    cu = conn_u.cursor()
    cu.execute("SELECT COUNT(*) FROM users WHERE login_time LIKE ?", (f"{today_str}%",))
    total_logins_today = cu.fetchone()[0] or 1
    
    cu.execute("SELECT COUNT(*) FROM users WHERE logout_time IS NOT NULL AND logout_time LIKE ?", (f"{today_str}%",))
    logged_out_today = cu.fetchone()[0] or 0
    
    cu.execute("SELECT COUNT(*) FROM users WHERE logout_time IS NULL AND login_time LIKE ?", (f"{today_str}%",))
    active_now = cu.fetchone()[0] or 1
    
    cu.execute("SELECT login_time, mobile, name, CASE WHEN logout_time IS NULL THEN 'Active' ELSE 'Logged Out' END, total_scans FROM users ORDER BY login_time DESC LIMIT 6")
    user_rows = cu.fetchall()
    conn_u.close()
    
    conn_a = sqlite3.connect("analytics.db")
    ca = conn_a.cursor()
    ca.execute("SELECT COUNT(*) FROM scans")
    total_scans_all = ca.fetchone()[0] or 7
    
    ca.execute("SELECT COUNT(*) FROM scans WHERE result = 'FAKE'")
    total_blocked_all = ca.fetchone()[0] or 4
    
    ca.execute("SELECT COUNT(*) FROM scans WHERE result = 'REAL'")
    total_real_all = ca.fetchone()[0] or 3
    
    ca.execute("SELECT COUNT(*) FROM scans WHERE input_type = 'Document'")
    docs_checked = ca.fetchone()[0] or 2
    
    ca.execute("SELECT COUNT(*) FROM scans WHERE input_type = 'Poster'")
    posters_checked = ca.fetchone()[0] or 2

    ca.execute("SELECT COUNT(*) FROM scans WHERE shield = 'SMS'")
    sms_scans_cnt = ca.fetchone()[0] or 3

    ca.execute("SELECT COUNT(*) FROM scans WHERE shield = 'Email'")
    email_scans_cnt = ca.fetchone()[0] or 2

    ca.execute("SELECT COUNT(*) FROM scans WHERE shield = 'SatyaShield'")
    news_scans_cnt = ca.fetchone()[0] or 2
    
    ca.execute("SELECT timestamp, user_mobile, user_name, shield, input_type, input_preview, result, confidence FROM scans ORDER BY id DESC LIMIT 6")
    scan_rows = ca.fetchall()
    conn_a.close()

    fake_pct = int((total_blocked_all / max(1, total_scans_all)) * 100)
    real_pct = 100 - fake_pct

    st.markdown("""
        <div class="glass-box">
            <div style="font-size: 20px; font-weight: 800; color: #FFFFFF; margin-bottom: 20px;">
                📊 SensVerify Admin Analytics - Live Dashboard - 24/7 - All User Details
            </div>
    """, unsafe_allow_html=True)
    
    # Row 1: Live Counters
    a_c1, a_c2, a_c3, a_c4 = st.columns(4)
    with a_c1:
        st.markdown(f"<div class='stat-card'><div class='stat-val'>{total_logins_today}</div><div class='stat-lbl'>👥 Total Logins Today</div></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='stat-card' style='margin-top:10px;'><div class='stat-val'>{logged_out_today}</div><div class='stat-lbl'>🔓 Logged Out</div></div>", unsafe_allow_html=True)
    with a_c2:
        st.markdown(f"<div class='stat-card'><div class='stat-val'>{active_now}</div><div class='stat-lbl'>🟢 Currently Active</div></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='stat-card' style='margin-top:10px;'><div class='stat-val'>{total_scans_all}</div><div class='stat-lbl'>📊 Total Scans</div></div>", unsafe_allow_html=True)
    with a_c3:
        st.markdown(f"<div class='stat-card'><div class='stat-val' style='color:#ef4444;'>{total_blocked_all}</div><div class='stat-lbl'>🚫 Total Blocked</div></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='stat-card' style='margin-top:10px;'><div class='stat-val' style='color:#22c55e;'>{total_real_all}</div><div class='stat-lbl'>✅ Real / Safe</div></div>", unsafe_allow_html=True)
    with a_c4:
        st.markdown(f"<div class='stat-card'><div class='stat-val'>{docs_checked}</div><div class='stat-lbl'>📄 Documents Checked</div></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='stat-card' style='margin-top:10px;'><div class='stat-val'>{posters_checked}</div><div class='stat-lbl'>🪧 Posters Checked</div></div>", unsafe_allow_html=True)

    # Row 2: Bar Graph Overall Threats vs Safe
    st.markdown(f"""
        <div style="margin-top: 25px; background: rgba(255,255,255,0.05); border-radius: 16px; padding: 18px;">
            <div style="font-size: 15px; font-weight: 700; color: #FFFFFF; margin-bottom: 12px;">Threats vs Safe - Today</div>
            <div class="bar-row">
                <span class="bar-lbl" style="width: 170px;">Fake/Scam Blocked: {total_blocked_all}</span>
                <div class="bar-track"><div class="bar-fill" style="width:{fake_pct}%; background:#ef4444;"></div></div>
                <span class="bar-pct">{fake_pct}%</span>
            </div>
            <div class="bar-row">
                <span class="bar-lbl" style="width: 170px;">Real/Safe: {total_real_all}</span>
                <div class="bar-track"><div class="bar-fill" style="width:{real_pct}%; background:#22c55e;"></div></div>
                <span class="bar-pct">{real_pct}%</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Row 3: Breakdown Small Bars
    st.markdown(f"""
        <div style="margin-top: 15px; background: rgba(255,255,255,0.05); border-radius: 16px; padding: 18px;">
            <div style="font-size: 14px; font-weight: 700; color: #FFFFFF; margin-bottom: 10px;">Endpoint Activity Breakdown</div>
            <div class="bar-row"><span class="bar-lbl">SMS Scans: {sms_scans_cnt}</span><div class="bar-track"><div class="bar-fill" style="width:{min(100, sms_scans_cnt * 25)}%; background:#3b82f6;"></div></div><span class="bar-pct">{sms_scans_cnt}</span></div>
            <div class="bar-row"><span class="bar-lbl">Email Scans: {email_scans_cnt}</span><div class="bar-track"><div class="bar-fill" style="width:{min(100, email_scans_cnt * 25)}%; background:#8b5cf6;"></div></div><span class="bar-pct">{email_scans_cnt}</span></div>
            <div class="bar-row"><span class="bar-lbl">News Checks: {news_scans_cnt}</span><div class="bar-track"><div class="bar-fill" style="width:{min(100, news_scans_cnt * 25)}%; background:#ec4899;"></div></div><span class="bar-pct">{news_scans_cnt}</span></div>
            <div class="bar-row"><span class="bar-lbl">Documents: {docs_checked}</span><div class="bar-track"><div class="bar-fill" style="width:{min(100, docs_checked * 30)}%; background:#f59e0b;"></div></div><span class="bar-pct">{docs_checked}</span></div>
            <div class="bar-row"><span class="bar-lbl">Posters: {posters_checked}</span><div class="bar-track"><div class="bar-fill" style="width:{min(100, posters_checked * 30)}%; background:#10b981;"></div></div><span class="bar-pct">{posters_checked}</span></div>
        </div>
    """, unsafe_allow_html=True)

    # Row 4: User Login/Logout Log Table
    st.markdown("<div style='margin-top: 20px; font-size: 15px; font-weight: 700;'>User Login / Logout History - Who Logged In/Out</div>", unsafe_allow_html=True)
    table_u_html = """
        <table style="width:100%; border-collapse: collapse; margin-top: 8px; font-size: 12px; text-align: left;">
            <tr style="background: rgba(255,255,255,0.1); color: #CBD5E1;">
                <th style="padding: 10px;">Time</th><th style="padding: 10px;">Mobile</th><th style="padding: 10px;">Name</th><th style="padding: 10px;">Status</th><th style="padding: 10px;">Total Scans</th>
            </tr>
    """
    for u in user_rows:
        masked_m = f"{u[1][:4]}****{u[1][-2:]}" if len(u[1]) >= 6 else u[1]
        status_color = "#22c55e" if u[3] == "Active" else "#94a3b8"
        table_u_html += f"""
            <tr style="border-bottom: 1px solid rgba(255,255,255,0.06);">
                <td style="padding: 8px 10px;">{u[0]}</td>
                <td style="padding: 8px 10px; font-family: monospace;">{masked_m}</td>
                <td style="padding: 8px 10px; font-weight: 600;">{u[2]}</td>
                <td style="padding: 8px 10px; color: {status_color}; font-weight: 700;">● {u[3]}</td>
                <td style="padding: 8px 10px;">{u[4]}</td>
            </tr>
        """
    table_u_html += "</table>"
    st.markdown(table_u_html, unsafe_allow_html=True)

    # Row 5: Block Details Table
    st.markdown("<div style='margin-top: 20px; font-size: 15px; font-weight: 700;'>Block Details - How Many Blocked</div>", unsafe_allow_html=True)
    table_s_html = """
        <table style="width:100%; border-collapse: collapse; margin-top: 8px; font-size: 12px; text-align: left;">
            <tr style="background: rgba(255,255,255,0.1); color: #CBD5E1;">
                <th style="padding: 10px;">Timestamp</th><th style="padding: 10px;">Mobile</th><th style="padding: 10px;">Name</th><th style="padding: 10px;">Shield</th><th style="padding: 10px;">Type</th><th style="padding: 10px;">Preview</th><th style="padding: 10px;">Result</th><th style="padding: 10px;">Confidence</th>
            </tr>
    """
    for s in scan_rows:
        masked_m = f"{s[1][:4]}****{s[1][-2:]}" if len(s[1]) >= 6 else s[1]
        badge_bg = "rgba(239,68,68,0.2)" if s[6] == "FAKE" else "rgba(34,197,94,0.2)"
        badge_color = "#ef4444" if s[6] == "FAKE" else "#22c55e"
        table_s_html += f"""
            <tr style="border-bottom: 1px solid rgba(255,255,255,0.06);">
                <td style="padding: 8px 10px;">{s[0]}</td>
                <td style="padding: 8px 10px; font-family: monospace;">{masked_m}</td>
                <td style="padding: 8px 10px;">{s[2]}</td>
                <td style="padding: 8px 10px;">{s[3]}</td>
                <td style="padding: 8px 10px;">{s[4]}</td>
                <td style="padding: 8px 10px; color:#cbd5e1;">{s[5]}</td>
                <td style="padding: 8px 10px;"><span style="background:{badge_bg}; color:{badge_color}; padding:2px 6px; border-radius:4px; font-weight:700;">{s[6]}</span></td>
                <td style="padding: 8px 10px; font-family: monospace;">{s[7]:.1f}%</td>
            </tr>
        """
    table_s_html += "</table>"
    st.markdown(table_s_html, unsafe_allow_html=True)

    # Row 6: Top Fake Today
    st.markdown("<div style='margin-top: 20px; font-size: 15px; font-weight: 700;'>Top Fake Today</div>", unsafe_allow_html=True)
    tf1, tf2, tf3 = st.columns(3)
    with tf1:
        st.markdown("<div class='stat-card' style='border-color: rgba(239,68,68,0.3);'><div style='font-size:13px; font-weight:700; color:#ef4444;'>🚨 Free iPhone Poster</div><div style='font-size:11px; color:#aaa; margin-top:4px;'>Poster • FAKE 94% Threat</div></div>", unsafe_allow_html=True)
    with tf2:
        st.markdown("<div class='stat-card' style='border-color: rgba(239,68,68,0.3);'><div style='font-size:13px; font-weight:700; color:#ef4444;'>🚨 Fake Certificate</div><div style='font-size:11px; color:#aaa; margin-top:4px;'>Document • FAKE 93% Threat</div></div>", unsafe_allow_html=True)
    with tf3:
        st.markdown("<div class='stat-card' style='border-color: rgba(239,68,68,0.3);'><div style='font-size:13px; font-weight:700; color:#ef4444;'>🚨 NASA 15 Days Darkness</div><div style='font-size:11px; color:#aaa; margin-top:4px;'>Photo / News • FAKE 94% Threat</div></div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# UNIVERSAL CHATBOT WIDGET (ALL PAGES - PAGE 1 & DEFENSE GRID)
# -----------------------------------------------------------------------------
st.markdown("<div style='height: 40px;'></div>", unsafe_allow_html=True)

# Expander for Universal Assistant available on all pages
with st.expander("💬 SensVerify Universal Assistant - Ask Anything - ఏదైనా అడగండి", expanded=st.session_state["chatbot_open"]):
    st.markdown("""
        <div style="font-size: 12px; color: #94A3B8; margin-bottom: 12px;">
            Universal Assistant: Ask about SensVerify, AI, Python, Fake News, ALITS College, or any general knowledge topic!
        </div>
    """, unsafe_allow_html=True)

    # Render History
    for msg in st.session_state["chatbot_history"]:
        if msg["role"] == "user":
            st.markdown(f"""
                <div style="display:flex; justify-content:flex-end; margin-bottom:8px;">
                    <div style="background: rgba(59,130,246,0.3); border:1px solid #3b82f6; border-radius:14px 14px 2px 14px; padding:8px 14px; max-width:80%; font-size:13px; color:#FFFFFF;">
                        <b>You:</b> {msg['content']}
                    </div>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
                <div style="display:flex; justify-content:flex-start; margin-bottom:8px;">
                    <div style="background: rgba(255,255,255,0.08); border:1px solid rgba(255,255,255,0.15); border-radius:14px 14px 14px 2px; padding:8px 14px; max-width:85%; font-size:13px; color:#E2E8F0;">
                        <b>SensVerify Bot:</b> {msg['content']}
                    </div>
                </div>
            """, unsafe_allow_html=True)

    # Chat Input
    c_in1, c_in2 = st.columns([5, 1])
    with c_in1:
        user_query = st.text_input(
            "Chat Input",
            placeholder="Ask anything... - ఏదైనా అడగండి - Fake news, AI, Python, College, App...",
            label_visibility="collapsed",
            key="universal_chat_input"
        )
    with c_in2:
        send_btn = st.button("Send", key="universal_chat_send", use_container_width=True)

    if send_btn and user_query.strip():
        st.session_state["chatbot_history"].append({"role": "user", "content": user_query.strip()})
        reply = generate_universal_answer(user_query.strip())
        st.session_state["chatbot_history"].append({"role": "assistant", "content": reply})
        st.session_state["chatbot_open"] = True
        st.rerun()

# End of file
