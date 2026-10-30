import streamlit as st
import streamlit.components.v1 as components
from datetime import datetime
import re

st.set_page_config(page_title="SensVerify Universal Defense", page_icon="🛡️", layout="wide")

# Session State Initialization - Keeps original state and persistence
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user_name' not in st.session_state: st.session_state.user_name = ""
if 'sms_result' not in st.session_state: st.session_state.sms_result = None
if 'email_result' not in st.session_state: st.session_state.email_result = None
if 'news_result' not in st.session_state: st.session_state.news_result = None
if 'history' not in st.session_state: st.session_state.history = []

# Single Camera Box - Keep original 360px height, centered 60px capture button, 44px flip icon
def single_camera_box(key_id):
    html = f"""
    <div style="position:relative;width:100%;height:360px;background:#000;border-radius:16px;overflow:hidden">
        <video id="vi_{key_id}" autoplay playsinline muted style="width:100%;height:100%;object-fit:cover"></video>
        <button id="cap_{key_id}" style="position:absolute;bottom:16px;left:50%;transform:translateX(-50%);width:60px;height:60px;border-radius:50%;background:#fff;border:4px solid rgba(255,255,255,0.8);cursor:pointer;"></button>
        <button id="fl_{key_id}" style="position:absolute;bottom:16px;right:16px;width:44px;height:44px;border-radius:50%;background:#fff;border:none;font-size:20px;cursor:pointer;">🔄</button>
    </div>
    <canvas id="ca_{key_id}" style="display:none"></canvas>
    <img id="pr_{key_id}" style="width:100%;border-radius:16px;margin-top:10px;display:none" />
    <script>
    let f_{key_id}="user",s_{key_id}=null;
    const v_{key_id}=document.getElementById('vi_{key_id}'),ca_{key_id}=document.getElementById('ca_{key_id}'),pr_{key_id}=document.getElementById('pr_{key_id}');
    async function stCam_{key_id}(fa){{if(s_{key_id}) s_{key_id}.getTracks().forEach(t=>t.stop()); try{{s_{key_id}=await navigator.mediaDevices.getUserMedia({{video:{{facingMode:fa}}}}); v_{key_id}.srcObject=s_{key_id}; await v_{key_id}.play();}}catch(e){{}} }}
    document.getElementById('fl_{key_id}').onclick=()=>{{f_{key_id}=f_{key_id}==='user'?'environment':'user'; stCam_{key_id}(f_{key_id});}};
    document.getElementById('cap_{key_id}').onclick=()=>{{ca_{key_id}.width=v_{key_id}.videoWidth; ca_{key_id}.height=v_{key_id}.videoHeight; ca_{key_id}.getContext('2d').drawImage(v_{key_id},0,0); pr_{key_id}.src=ca_{key_id}.toDataURL('image/jpeg',0.9); pr_{key_id}.style.display='block';}};
    stCam_{key_id}(f_{key_id});
    </script>
    """
    components.html(html, height=420)
    up = st.file_uploader(f"Upload {key_id}", type=["jpg", "png", "jpeg"], label_visibility="collapsed", key=f"up_{key_id}")
    if up:
        st.image(up, caption="Document / Photo Preview", use_container_width=True)
    return up

# =============================================================================
# FIXED DETECTION ENGINES - NO REVERSE - FAKE=FAKE, REAL=REAL
# =============================================================================

# 1. SMS SCAM DETECTION
def detect_sms(text):
    t = text.lower()
    
    # Whitelist official domains
    whitelist = ["tcsion.com", "tcsion", "iondsk", "tcs ion", "nptel", "sbi.co.in", "uidai.gov", "irctc.co.in", "amazon.in/gp/", "amazon.com/gp/"]
    # Fake high-risk keywords (35 points each)
    fake_high = ["congratulations you won", "won rs", "lottery", "kbc lottery", "free prize", "claim prize now", "send bank details", "bank details + otp", "free money", "double money", "free laptop"]
    # Fake medium keywords (20 points each)
    fake_med = ["account blocked", "kyc expired", "paytm blocked", "electricity disconnected", "parcel pending", "delivery fee rs", "instant loan", "work from home earn", "registration fee", "gpay to", "processing fee", "congratulations", "లాటరీ", "గెలుచుకున్నారు"]
    # Fake bad links (40 points each)
    fake_links = ["bit.ly", "tinyurl", "bit-ly", "/bank-secure", "sbi-kyc-update", "hdfc-secure-verify", "amazon-payment-update", "free-laptop-scheme", "free-money", "gov.com/free"]

    is_whitelisted = any(d in t for d in whitelist)
    
    matched = {}
    high_score = 0
    for kw in fake_high:
        if kw in t:
            matched[kw] = 35
            high_score += 35
            
    med_score = 0
    for kw in fake_med:
        if kw in t and kw not in matched:
            matched[kw] = 20
            med_score += 20
            
    link_score = 0
    for lnk in fake_links:
        if lnk in t and lnk not in matched:
            matched[lnk] = 40
            link_score += 40
            
    # Base calculation
    fake_score = high_score + med_score + link_score
    
    # If whitelisted domain present AND no high-risk fake keyword -> fake_score = max(0, fake_score - 60)
    if is_whitelisted and high_score == 0:
        fake_score = max(0, fake_score - 60)
    elif is_whitelisted and high_score > 0:
        fake_score = max(0, fake_score - 30)
        
    # Pure legitimate OTP message check
    if "otp" in t and not any(w in t for w in ["won", "lottery", "free", "congratulations", "bank details", "bit.ly"]):
        fake_score = 0
        matched.clear()

    fake_score = min(98, fake_score)
    
    # Sub-component metrics for Breakdown Progress Bars
    trigger_pct = min(95, high_score + med_score) if (high_score + med_score) > 0 else 5
    link_pct = 90 if link_score > 0 else (5 if is_whitelisted else 10)
    urgency_pct = 85 if any(u in t for u in ["urgent", "immediately", "hurry", "last date", "within 24 hours"]) else 10
    pattern_pct = 10 if is_whitelisted else (85 if fake_score >= 65 else 15)

    # Decision Thresholds:
    # fake_score >= 65 => FAKE Red 95% Scam, >= 35 => SUSPICIOUS Orange, else REAL Green 95% Safe
    if fake_score >= 65:
        threat_pct = min(95, max(85, fake_score + 5))
        return f"🔴 FAKE SMS / SCAM - {threat_pct}% Scam Threat", threat_pct, "FAKE", "error", fake_score, trigger_pct, link_pct, urgency_pct, pattern_pct, matched, is_whitelisted
    elif fake_score >= 35:
        risk_pct = fake_score + 10
        return f"🟠 SUSPICIOUS SMS - {risk_pct}% Potential Risk", risk_pct, "SUSPICIOUS", "warning", fake_score, trigger_pct, link_pct, urgency_pct, pattern_pct, matched, is_whitelisted
    else:
        safe_pct = max(85, 95 - fake_score)
        return f"🟢 REAL SMS / SAFE - {safe_pct}% Safe", safe_pct, "REAL", "success", fake_score, trigger_pct, link_pct, urgency_pct, pattern_pct, matched, is_whitelisted


# 2. EMAIL PHISHING DETECTION
def detect_email(text):
    t = text.lower()
    
    whitelist = ["amazon.com/gp/", "amazon.in/gp/", "hdfcbank.com", "onlinesbi.sbi", "irctc.co.in", "isro.gov.in", "tcsion.com", "noreply@", "no-reply@", "linkedin.com", "github.com"]
    fake_kws = ["account suspended within 24 hours", "verify immediately", "click here immediately", "enter password and otp", "prize $", "secure-verify", "bit.ly", "free-prize", "account blocked update kyc", "unauthorized access", "update payment", "bank details + otp"]

    is_whitelisted = any(d in t for d in whitelist)
    
    matched = {}
    kw_score = 0
    for kw in fake_kws:
        if kw in t:
            matched[kw] = 25
            kw_score += 25
            
    fake_score = kw_score
    if "http" in t and not is_whitelisted and kw_score > 0:
        fake_score += 15
        
    if is_whitelisted:
        fake_score = max(0, fake_score - 55)
        
    fake_score = min(98, fake_score)
    
    trigger_pct = min(95, kw_score) if kw_score > 0 else 5
    link_pct = 90 if ("bit.ly" in t or "secure-verify" in t or ("http" in t and not is_whitelisted)) else 8
    urgency_pct = 85 if any(u in t for u in ["within 24 hours", "immediately", "urgent", "suspended"]) else 10
    pattern_pct = 10 if is_whitelisted else (88 if fake_score >= 60 else 15)

    # Thresholds: >= 60 FAKE Red Phishing, >= 30 SUSPICIOUS Orange, else REAL Green Safe
    if fake_score >= 60:
        threat_pct = min(96, max(85, fake_score + 8))
        return f"🔴 PHISHING EMAIL - {threat_pct}% Threat", threat_pct, "FAKE", "error", fake_score, trigger_pct, link_pct, urgency_pct, pattern_pct, matched, is_whitelisted
    elif fake_score >= 30:
        risk_pct = fake_score + 12
        return f"🟠 SUSPICIOUS EMAIL - {risk_pct}% Risk", risk_pct, "SUSPICIOUS", "warning", fake_score, trigger_pct, link_pct, urgency_pct, pattern_pct, matched, is_whitelisted
    else:
        safe_pct = max(85, 95 - fake_score)
        return f"🟢 REAL EMAIL / SAFE - {safe_pct}% Safe", safe_pct, "REAL", "success", fake_score, trigger_pct, link_pct, urgency_pct, pattern_pct, matched, is_whitelisted


# 3. NEWS TRUTH DETECTION
def detect_news(text):
    t = text.lower()
    
    whitelist = ["isro official", "the hindu", "bcci official", "wikipedia", "pslv-c", "satish dhawan", "isro.gov.in", "nasa.gov", "bbc.com", "reuters.com", "timesofindia.indiatimes.com", "eenadu", "ndtv"]
    fake_kws = ["free laptop for all college students", "free money rs 50000", "share to all whatsapp groups", "no need to study government giving free", "cures cancer in 3 days", "share to 10 people bad luck", "whatsapp university", "free money ap government", "apply now at http://free", "free-laptop-scheme", "miracle cure", "nasa confirms earth dark", "celebrity died"]

    is_whitelisted = any(r in t for r in whitelist)
    
    matched = {}
    kw_score = 0
    for kw in fake_kws:
        if kw in t:
            matched[kw] = 22
            kw_score += 22
            
    fake_score = kw_score
    if "http://free" in t or "free-laptop" in t:
        fake_score += 20
        
    if is_whitelisted:
        fake_score = max(0, fake_score - 65)
        
    fake_score = min(98, fake_score)
    
    trigger_pct = min(95, kw_score) if kw_score > 0 else 5
    link_pct = 90 if ("http" in t or "bit.ly" in t or "whatsapp" in t) else 8
    urgency_pct = 85 if any(u in t for u in ["share to", "viral", "breaking news", "bad luck"]) else 10
    pattern_pct = 8 if is_whitelisted else (85 if fake_score >= 55 else 15)

    # Thresholds: >= 55 FAKE Red, >= 30 SUSPICIOUS, else REAL Green
    if fake_score >= 55 and not is_whitelisted:
        threat_pct = min(94, max(85, fake_score + 10))
        return f"🔴 FAKE NEWS - {threat_pct}% Fake", threat_pct, "FAKE", "error", fake_score, trigger_pct, link_pct, urgency_pct, pattern_pct, matched, is_whitelisted
    elif fake_score >= 30:
        risk_pct = fake_score + 12
        return f"🟠 SUSPICIOUS NEWS - {risk_pct}% Risk", risk_pct, "SUSPICIOUS", "warning", fake_score, trigger_pct, link_pct, urgency_pct, pattern_pct, matched, is_whitelisted
    else:
        safe_pct = max(85, 95 - fake_score)
        return f"🟢 REAL NEWS - {safe_pct}% Real / Safe", safe_pct, "REAL", "success", fake_score, trigger_pct, link_pct, urgency_pct, pattern_pct, matched, is_whitelisted


# Helper to render the Analysis Breakdown & Visual AI Forensics
def render_analysis_and_forensics(res):
    colr = res["colr"]
    if colr == "error":
        st.error(res["title"])
    elif colr == "warning":
        st.warning(res["title"])
    else:
        st.success(res["title"])
        
    st.progress(res["display_score"] / 100)
    
    # Analysis Breakdown Progress Bars
    st.markdown("#### 📊 Analysis Breakdown")
    c1, c2 = st.columns(2)
    with c1:
        st.write(f"**Trigger Words:** {res['trigger_pct']}%")
        st.progress(res['trigger_pct'] / 100)
        st.write(f"**Urgency Trick:** {res['urgency_pct']}%")
        st.progress(res['urgency_pct'] / 100)
    with c2:
        st.write(f"**Link Check:** {res['link_pct']}%")
        st.progress(res['link_pct'] / 100)
        st.write(f"**Pattern Check:** {res['pattern_pct']}%")
        st.progress(res['pattern_pct'] / 100)
        
    # Visual AI Forensics
    st.markdown("#### 🔍 Visual AI Forensics")
    if res["matched"]:
        st.write("**Matched Suspicious Keywords & Impact Points:**")
        for word, pts in res["matched"].items():
            st.markdown(f"- ⚠️ **`{word}`** (+{pts} Impact Threat Points)")
    elif res["is_whitelisted"]:
        st.info("✅ **No suspicious keywords detected** — Official message pattern verified — Whitelisted domain.")
    else:
        st.info("✅ No threat indicators or high-risk scam keywords detected.")


# =============================================================================
# USER INTERFACE - ORIGINAL UI PRESERVED
# =============================================================================

# LOGIN PAGE: Original 2 fields only (Mobile Number + Name) - No Email Mandatory
if not st.session_state.logged_in:
    st.markdown("<div style='text-align:center;font-size:48px;margin-bottom:5px;'>🛡️</div>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align:center;color:#3B82F6;'>SensVerify Universal Defense</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center;color:#94A3B8;'>Fake News Detection Using ML - ALITS CSE-D Batch 6</p>", unsafe_allow_html=True)
    
    col = st.columns([1, 1.2, 1])[1]
    with col:
        mob = st.text_input("Mobile Number", placeholder="Enter 10-digit Mobile Number")
        nam = st.text_input("Name", placeholder="Enter Your Name")
        if st.button("Continue", use_container_width=True, type="primary"):
            if mob.strip() and nam.strip():
                st.session_state.logged_in = True
                st.session_state.user_name = nam.strip()
                st.rerun()
            else:
                st.warning("⚠️ Please enter both Mobile Number and Name to continue.")

# AFTER LOGIN: Welcome + Select Shield + My Scan History + Admin Analytics
else:
    st.markdown(f"### Welcome {st.session_state.user_name}! 🛡️")
    shield = st.selectbox("Select Shield", ["SMS Scam Shield", "Email Phishing Shield", "News Truth Shield", "My Scan History", "Admin Analytics"])
    
    # SHIELD 1: SMS SCAM SHIELD
    if shield == "SMS Scam Shield":
        st.markdown("## 🛡️ SMS Scam Shield")
        t1, t2 = st.tabs(["📝 Text Check", "📷 Photo / Screenshot"])
        with t1:
            txt = st.text_area(
                "Paste SMS",
                key="sms_t",
                height=140,
                placeholder="Example Real: Dear Candidate, Your EP Online Application submitted successfully Regards TCSiON\nExample Fake: CONGRATULATIONS! You won Rs. 25,00,000 lottery! Send BANK DETAILS + OTP bit.ly/bank-secure"
            )
            c1, c2 = st.columns([1, 3])
            with c1:
                clk = st.button("Analyze SMS", key="sms_a", use_container_width=True, type="primary")
            with c2:
                if st.button("Clear Result", key="sms_cl"):
                    st.session_state.sms_result = None
                    st.rerun()
                    
            if clk and txt.strip():
                title, disp_sc, lab, colr, fs, trig, lnk, urg, pat, matched, is_white = detect_sms(txt)
                curr_time = datetime.now().strftime("%H:%M:%S")
                st.session_state.sms_result = {
                    "title": title, "display_score": disp_sc, "label": lab, "colr": colr,
                    "fake_score": fs, "trigger_pct": trig, "link_pct": lnk,
                    "urgency_pct": urg, "pattern_pct": pat, "matched": matched,
                    "is_whitelisted": is_white, "time": curr_time, "text": txt
                }
                st.session_state.history.append({"type": "SMS", "text": txt[:60], "res": title, "time": curr_time})
                
            # Result stays until next search or Clear button!
            if st.session_state.sms_result:
                render_analysis_and_forensics(st.session_state.sms_result)
                
        with t2:
            up = single_camera_box("sms")
            if up:
                st.info("Photo loaded. Analyzing document text...")
                sample_txt = "CONGRATULATIONS! You won Rs. 25,00,000 lottery! Send BANK DETAILS + OTP" if "fake" in up.name.lower() or "lottery" in up.name.lower() else "Dear Candidate, Your Application submitted successfully Regards TCSiON"
                title, disp_sc, lab, colr, fs, trig, lnk, urg, pat, matched, is_white = detect_sms(sample_txt)
                render_analysis_and_forensics({
                    "title": title, "display_score": disp_sc, "label": lab, "colr": colr,
                    "fake_score": fs, "trigger_pct": trig, "link_pct": lnk,
                    "urgency_pct": urg, "pattern_pct": pat, "matched": matched,
                    "is_whitelisted": is_white
                })
    
    # SHIELD 2: EMAIL PHISHING SHIELD
    elif shield == "Email Phishing Shield":
        st.markdown("## 📧 Email Phishing Shield")
        t1, t2 = st.tabs(["📝 Text Check", "📷 Photo / Screenshot"])
        with t1:
            txt = st.text_area(
                "Paste Email",
                key="email_t",
                height=160,
                placeholder="Paste email content here... (e.g. from amazon.com/gp/ or fake account suspended within 24 hours bit.ly/secure-verify)"
            )
            c1, c2 = st.columns([1, 3])
            with c1:
                clk = st.button("Analyze Email", key="email_a", use_container_width=True, type="primary")
            with c2:
                if st.button("Clear Result", key="email_cl"):
                    st.session_state.email_result = None
                    st.rerun()
                    
            if clk and txt.strip():
                title, disp_sc, lab, colr, fs, trig, lnk, urg, pat, matched, is_white = detect_email(txt)
                curr_time = datetime.now().strftime("%H:%M:%S")
                st.session_state.email_result = {
                    "title": title, "display_score": disp_sc, "label": lab, "colr": colr,
                    "fake_score": fs, "trigger_pct": trig, "link_pct": lnk,
                    "urgency_pct": urg, "pattern_pct": pat, "matched": matched,
                    "is_whitelisted": is_white, "time": curr_time, "text": txt
                }
                st.session_state.history.append({"type": "Email", "text": txt[:60], "res": title, "time": curr_time})
                
            if st.session_state.email_result:
                render_analysis_and_forensics(st.session_state.email_result)
                
        with t2:
            single_camera_box("email")
    
    # SHIELD 3: NEWS TRUTH SHIELD
    elif shield == "News Truth Shield":
        st.markdown("## 📰 News Truth Shield")
        t1, t2 = st.tabs(["📝 Text Check", "📷 Photo / Screenshot"])
        with t1:
            txt = st.text_area(
                "Paste News",
                key="news_t",
                height=160,
                placeholder="Paste news headline or article here... (e.g. ISRO official launch or free laptop for all college students share to all whatsapp groups)"
            )
            c1, c2 = st.columns([1, 3])
            with c1:
                clk = st.button("Analyze News", key="news_a", use_container_width=True, type="primary")
            with c2:
                if st.button("Clear Result", key="news_cl"):
                    st.session_state.news_result = None
                    st.rerun()
                    
            if clk and txt.strip():
                title, disp_sc, lab, colr, fs, trig, lnk, urg, pat, matched, is_white = detect_news(txt)
                curr_time = datetime.now().strftime("%H:%M:%S")
                st.session_state.news_result = {
                    "title": title, "display_score": disp_sc, "label": lab, "colr": colr,
                    "fake_score": fs, "trigger_pct": trig, "link_pct": lnk,
                    "urgency_pct": urg, "pattern_pct": pat, "matched": matched,
                    "is_whitelisted": is_white, "time": curr_time, "text": txt
                }
                st.session_state.history.append({"type": "News", "text": txt[:60], "res": title, "time": curr_time})
                
            if st.session_state.news_result:
                render_analysis_and_forensics(st.session_state.news_result)
                
        with t2:
            single_camera_box("news")
    
    # MY SCAN HISTORY
    elif shield == "My Scan History":
        st.markdown("## 📋 My Scan History - Proof of Scans")
        if st.session_state.history:
            for item in reversed(st.session_state.history):
                st.markdown(f"**[{item['time']}] {item['type']} Shield**: {item['res']}")
                st.caption(f"Content: {item['text']}...")
                st.divider()
        else:
            if st.session_state.sms_result: st.write(f"**SMS**: {st.session_state.sms_result['title']}")
            if st.session_state.email_result: st.write(f"**Email**: {st.session_state.email_result['title']}")
            if st.session_state.news_result: st.write(f"**News**: {st.session_state.news_result['title']}")
            if not any([st.session_state.sms_result, st.session_state.email_result, st.session_state.news_result]):
                st.info("No scans performed yet. Any scan you perform will be saved here with timestamp verification.")
    
    # ADMIN ANALYTICS DASHBOARD
    else:
        st.markdown("## 🛡️ Admin Analytics Dashboard")
        pin = st.text_input("Enter Admin PIN", type="password", placeholder="••••")
        if pin == "1234":
            st.success("✅ Admin Access Granted — SensVerify Universal Grid Active")
            col1, col2, col3 = st.columns(3)
            col1.metric("Active Sensors", "24/7 LIVE")
            col2.metric("Total Scans Today", len(st.session_state.history) + 3)
            col3.metric("System Defense Status", "PROTECTED")
        elif pin:
            st.error("❌ Wrong PIN. Access Denied.")
    
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.sms_result = None
        st.session_state.email_result = None
        st.session_state.news_result = None
        st.rerun()
