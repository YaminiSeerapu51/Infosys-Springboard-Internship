import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore, auth as admin_auth
import requests
from streamlit_lottie import st_lottie
import base64
import os

# -----------------------
# CONFIG
# -----------------------
SERVICE_ACCOUNT_PATH = r"D:\project\Tourism and Holiday trends\serviceAccountKey.json"
POWERBI_EMBED_URL = "https://app.powerbi.com/reportEmbed?reportId=9c05147e-a4d8-4786-b6e8-b7e70456abdb&autoAuth=true&ctid=ab0d6933-c2be-4144-ab83-542b2fd6e21e"
FIREBASE_API_KEY = "AIzaSyBGFLI2HCAqv4YY-gyBkpn19vp9gF2x2KU"
LOGIN_BG_PATH = r"D:\project\Tourism and Holiday trends\assets\images (3).jpg"
LOTTIE_URLS = {
    "home": "https://assets4.lottiefiles.com/packages/lf20_yf3k.json",
    "dashboard": "https://assets1.lottiefiles.com/packages/lf20_1tgnpuzo.json",
    "insights": "https://assets4.lottiefiles.com/packages/lf20_uciwcsjl.json",
    "feedback": "https://assets3.lottiefiles.com/packages/lf20_y8g7jnth.json",
    "profile": "https://assets2.lottiefiles.com/packages/lf20_jwhfxnkv.json",
    "travel_home": "https://assets1.lottiefiles.com/packages/lf20_k5hqkx7x.json",
    "insights_data": "https://assets9.lottiefiles.com/packages/lf20_qcz2w4oj.json",
    "world_map": "https://assets2.lottiefiles.com/packages/lf20_ydo1amjm.json"
}

# Firebase init (with mock fallback)
db = None
try:
    if not firebase_admin._apps and os.path.exists(SERVICE_ACCOUNT_PATH):
        cred = credentials.Certificate(SERVICE_ACCOUNT_PATH)
        firebase_admin.initialize_app(cred)
        db = firestore.client()
except Exception:
    db = None

# -----------------------
# HELPER: Load Local Image as Base64
# -----------------------
def get_base64_image(path):
    try:
        if os.path.exists(path):
            with open(path, "rb") as img_file:
                return base64.b64encode(img_file.read()).decode()
    except:
        pass
    return None

# -----------------------
# ENHANCED CSS STYLING
# -----------------------
def load_css(is_auth=False, theme="Light"):
    base64_img = get_base64_image(LOGIN_BG_PATH) if is_auth else None
    bg_url = f"data:image/jpeg;base64,{base64_img}" if base64_img else "https://images.unsplash.com/photo-1507525428034-b723cf961d3e"
    
    if theme == "Dark":
        app_bg = "linear-gradient(135deg, #0f0f23 0%, #1a1a2e 50%, #16213e 100%)"
        sidebar_bg = "linear-gradient(145deg, #1e1e2e 0%, #2d2d42 100%)"
        text_color = "#ffffff"
        secondary_text = "#e0e0e0"
        card_bg = "rgba(45, 45, 66, 0.95)"
        button_bg = "linear-gradient(135deg, #667eea 0%, #764ba2 100%)"
        button_hover = "linear-gradient(135deg, #764ba2 0%, #667eea 100%)"
        nav_active = "linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)"
        nav_hover = "rgba(79, 172, 254, 0.2)"
        auth_card_bg = "rgba(30, 30, 46, 0.95)"
        auth_text_color = "#ffffff"
        input_bg = "rgba(45, 45, 66, 0.8)"
        input_border = "rgba(102, 126, 234, 0.5)"
        input_text_color = "#ffffff"
    else:
        # Light theme - proper white/light backgrounds
        if is_auth and base64_img:
            app_bg = f"linear-gradient(rgba(255,255,255,0.95), rgba(255,255,255,0.95)), url('{bg_url}')"
        else:
            app_bg = "linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)"
        sidebar_bg = "linear-gradient(145deg, #ffffff 0%, #f8f9ff 100%)"
        text_color = "#2c3e50"
        secondary_text = "#34495e"
        card_bg = "rgba(255, 255, 255, 0.95)"
        button_bg = "linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)"
        button_hover = "linear-gradient(135deg, #00f2fe 0%, #4facfe 100%)"
        nav_active = "linear-gradient(135deg, #667eea 0%, #764ba2 100%)"
        nav_hover = "rgba(102, 126, 234, 0.1)"
        auth_card_bg = "rgba(255, 255, 255, 0.98)"
        auth_text_color = "#2c3e50"
        input_bg = "rgba(255, 255, 255, 0.95)"
        input_border = "rgba(102, 126, 234, 0.3)"
        input_text_color = "#2c3e50"

    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    /* Global App Styling */
    .stApp {{
        background: {app_bg};
        background-size: cover;
        background-attachment: fixed;
        color: {text_color};
        font-family: 'Inter', sans-serif;
    }}
    
    /* Hide Streamlit Elements */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}
    
    /* Main Content Area */
    .main .block-container {{
        padding-top: 2rem;
        padding-left: 3rem;
        padding-right: 3rem;
        max-width: 100%;
    }}
    
    /* Enhanced Sidebar */
    .stSidebar {{
        background: {sidebar_bg} !important;
        border-radius: 0 25px 25px 0;
        box-shadow: 5px 0 25px rgba(0,0,0,0.1);
        border-right: 3px solid rgba(102, 126, 234, 0.3);
    }}
    
    .stSidebar > div {{
        padding: 2rem 1rem;
    }}
    
    /* Sidebar Header */
    .sidebar-header {{
        text-align: center;
        padding: 1.5rem 0 2rem 0;
        border-bottom: 2px solid rgba(102, 126, 234, 0.2);
        margin-bottom: 2rem;
    }}
    
    .sidebar-header h1 {{
        color: {text_color};
        font-size: 1.8rem;
        font-weight: 700;
        margin: 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }}
    
    .sidebar-header p {{
        color: {secondary_text};
        opacity: 0.8;
        font-size: 0.95rem;
        margin: 0.5rem 0 0 0;
        font-weight: 500;
    }}
    
    /* Headers and Typography */
    h1, h2, h3 {{
        color: {text_color};
        font-weight: 700;
        margin-bottom: 1.5rem;
    }}
    
    h1 {{
        font-size: 3rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-align: center;
        margin-bottom: 2rem;
    }}
    
    h2 {{
        font-size: 2.2rem;
        color: {text_color};
    }}
    
    h3 {{
        font-size: 1.8rem;
        color: {text_color};
    }}
    
    /* Enhanced Buttons */
    .stButton > button {{
        background: {button_bg};
        color: white;
        border: none;
        border-radius: 25px;
        padding: 14px 35px;
        font-weight: 600;
        font-size: 1.1rem;
        box-shadow: 0 6px 20px rgba(79, 172, 254, 0.3);
        transition: all 0.3s ease;
        font-family: 'Inter', sans-serif;
        letter-spacing: 0.5px;
    }}
    
    .stButton > button:hover {{
        background: {button_hover};
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(79, 172, 254, 0.4);
    }}
    
    /* Enhanced Login Button */
    .login-button button {{
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 35px !important;
        padding: 22px 50px !important;
        font-weight: 800 !important;
        font-size: 1.5rem !important;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.5) !important;
        transition: all 0.4s ease !important;
        font-family: 'Inter', sans-serif !important;
        letter-spacing: 2px !important;
        text-transform: uppercase !important;
        cursor: pointer !important;
    }}
    
    .login-button button:hover {{
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%) !important;
        transform: translateY(-4px) scale(1.02) !important;
        box-shadow: 0 15px 40px rgba(102, 126, 234, 0.6) !important;
    }}
    
    .login-button button:active {{
        transform: translateY(-2px) scale(1.01) !important;
    }}
    
    /* Form Elements */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > select {{
        border-radius: 18px;
        border: 3px solid {input_border};
        padding: 20px 25px;
        font-size: 1.3rem;
        background: {input_bg};
        color: {input_text_color};
        font-family: 'Inter', sans-serif;
        transition: all 0.3s ease;
        font-weight: 500;
    }}
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus,
    .stSelectbox > div > div > select:focus {{
        border-color: #667eea;
        box-shadow: 0 0 25px rgba(102, 126, 234, 0.4);
        background: {input_bg};
        color: {input_text_color};
        transform: translateY(-2px);
    }}
    
    /* Enhanced Label Styling */
    .stTextInput label,
    .stTextArea label,
    .stSelectbox label {{
        font-size: 1.3rem !important;
        font-weight: 700 !important;
        color: {auth_text_color} !important;
        margin-bottom: 1rem !important;
    }}
    
    /* Cards and Containers */
    .auth-container {{
        display: flex;
        justify-content: center;
        align-items: center;
        min-height: 100vh;
        padding: 2rem;
    }}
    
    .auth-card {{
        background: {auth_card_bg};
        padding: 4rem;
        border-radius: 30px;
        box-shadow: 0 25px 80px rgba(0,0,0,0.15);
        backdrop-filter: blur(15px);
        border: 2px solid rgba(102, 126, 234, 0.2);
        max-width: 550px;
        width: 100%;
        text-align: center;
        position: relative;
        overflow: hidden;
    }}
    
    .auth-card::before {{
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }}
    
    .auth-card h1 {{
        font-size: 3.5rem;
        font-weight: 800;
        margin-bottom: 1rem;
        color: {auth_text_color};
        text-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }}
    
    .auth-card p {{
        font-size: 1.3rem;
        color: {auth_text_color};
        opacity: 0.8;
        margin-bottom: 3rem;
        font-weight: 500;
    }}
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 10px;
        background: rgba(102, 126, 234, 0.15);
        border-radius: 20px;
        padding: 12px;
        margin-bottom: 2.5rem;
    }}
    
    .stTabs [data-baseweb="tab"] {{
        color: {auth_text_color};
        font-weight: 700;
        font-size: 1.4rem;
        border-radius: 15px;
        padding: 16px 32px;
        transition: all 0.3s ease;
    }}
    
    .stTabs [data-baseweb="tab"]:hover {{
        background: rgba(102, 126, 234, 0.2);
        transform: translateY(-2px);
    }}
    
    .stTabs [aria-selected="true"] {{
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white !important;
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
    }}
    
    .content-card {{
        background: {card_bg};
        padding: 2.5rem;
        border-radius: 25px;
        box-shadow: 0 15px 40px rgba(0,0,0,0.1);
        margin-bottom: 2rem;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(102, 126, 234, 0.1);
        transition: all 0.3s ease;
    }}
    
    .content-card:hover {{
        transform: translateY(-5px);
        box-shadow: 0 20px 50px rgba(0,0,0,0.15);
    }}
    
    .content-card h3 {{
        color: {text_color};
        font-size: 1.6rem;
        font-weight: 700;
        margin-bottom: 1.5rem;
    }}
    
    .content-card p, .content-card li {{
        color: {secondary_text};
        font-size: 1.1rem;
        line-height: 1.7;
        font-weight: 500;
    }}
    
    /* Enhanced Profile Card */
    .profile-container {{
        display: grid;
        grid-template-columns: 1fr 2fr;
        gap: 2rem;
        margin: 2rem 0;
    }}
    
    .profile-main-card {{
        background: {card_bg};
        padding: 3rem;
        border-radius: 30px;
        box-shadow: 0 20px 60px rgba(0,0,0,0.1);
        text-align: center;
        border: 2px solid rgba(102, 126, 234, 0.1);
        position: relative;
        overflow: hidden;
    }}
    
    .profile-main-card::before {{
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 6px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }}
    
    .profile-avatar {{
        width: 120px;
        height: 120px;
        border-radius: 50%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto 2rem auto;
        font-size: 3rem;
        color: white;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
        position: relative;
    }}
    
    .profile-avatar::after {{
        content: '';
        position: absolute;
        top: -4px;
        left: -4px;
        right: -4px;
        bottom: -4px;
        border-radius: 50%;
        border: 3px solid rgba(102, 126, 234, 0.3);
    }}
    
    .profile-name {{
        font-size: 2.5rem;
        font-weight: 700;
        color: {text_color};
        margin-bottom: 0.5rem;
    }}
    
    .profile-role {{
        font-size: 1.3rem;
        color: {secondary_text};
        opacity: 0.8;
        font-weight: 500;
        margin-bottom: 2rem;
    }}
    
    .profile-details {{
        display: grid;
        gap: 1.5rem;
    }}
    
    .profile-info {{
        background: rgba(102, 126, 234, 0.08);
        padding: 1.8rem;
        border-radius: 20px;
        border-left: 5px solid #667eea;
        transition: all 0.3s ease;
    }}
    
    .profile-info:hover {{
        background: rgba(102, 126, 234, 0.12);
        transform: translateX(5px);
    }}
    
    .profile-info-label {{
        font-size: 1rem;
        font-weight: 600;
        color: {secondary_text};
        opacity: 0.8;
        margin-bottom: 0.5rem;
        text-transform: uppercase;
        letter-spacing: 1px;
    }}
    
    .profile-info-value {{
        font-size: 1.3rem;
        font-weight: 600;
        color: {text_color};
    }}
    
    /* Stats Cards */
    .stats-container {{
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
        gap: 2rem;
        margin: 3rem 0;
    }}
    
    .stat-card {{
        background: {card_bg};
        padding: 2.5rem;
        border-radius: 25px;
        text-align: center;
        box-shadow: 0 15px 40px rgba(0,0,0,0.1);
        transition: all 0.4s ease;
        position: relative;
        overflow: hidden;
        border: 2px solid rgba(102, 126, 234, 0.1);
    }}
    
    .stat-card::before {{
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }}
    
    .stat-card:hover {{
        transform: translateY(-10px);
        box-shadow: 0 25px 60px rgba(0,0,0,0.15);
        border-color: rgba(102, 126, 234, 0.3);
    }}
    
    .stat-number {{
        font-size: 3.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 1rem;
    }}
    
    .stat-label {{
        color: {text_color};
        font-size: 1.3rem;
        font-weight: 600;
        opacity: 0.8;
    }}
    
    /* Dashboard iframe */
    .dashboard-container {{
        background: {card_bg};
        border-radius: 25px;
        overflow: hidden;
        box-shadow: 0 20px 50px rgba(0,0,0,0.1);
        margin: 3rem 0;
        border: 2px solid rgba(102, 126, 234, 0.1);
    }}
    
    /* Animation containers */
    .animation-container {{
        display: flex;
        justify-content: center;
        align-items: center;
        margin: 2rem 0;
        padding: 2rem;
        background: {card_bg};
        border-radius: 25px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    }}
    
    /* Home page specific animations */
    .home-hero-section {{
        text-align: center;
        padding: 4rem 0;
    }}
    
    .home-hero-section h1 {{
        font-size: 4rem;
        margin-bottom: 1.5rem;
    }}
    
    .home-hero-section p {{
        font-size: 1.5rem;
        color: {secondary_text};
        font-weight: 500;
        margin-bottom: 3rem;
    }}
    
    /* Insights page animations */
    .insights-grid {{
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
        gap: 2rem;
        margin: 2rem 0;
    }}
    
    /* Enhanced text styling for better readability */
    p, li, span {{
        color: {secondary_text};
        font-size: 1.1rem;
        line-height: 1.8;
        font-weight: 500;
    }}
    
    strong {{
        color: {text_color};
        font-weight: 700;
    }}
    
    /* Responsive Design */
    @media (max-width: 768px) {{
        .main .block-container {{
            padding-left: 1rem;
            padding-right: 1rem;
        }}
        
        h1 {{
            font-size: 2.5rem;
        }}
        
        .auth-card {{
            padding: 2.5rem;
        }}
        
        .profile-container {{
            grid-template-columns: 1fr;
        }}
        
        .stat-number {{
            font-size: 2.5rem;
        }}
        
        .home-hero-section h1 {{
            font-size: 3rem;
        }}
    }}
    </style>
    """, unsafe_allow_html=True)

# -----------------------
# NAVIGATION COMPONENT
# -----------------------
def render_sidebar():
    with st.sidebar:
        st.markdown("""
        <div class="sidebar-header">
            <h1>🌍 Tourism Analytics</h1>
            <p>Data-driven insights</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Navigation menu - Settings removed
        menu_items = [
            ("🏠", "Home", "home"),
            ("📊", "Dashboard", "dashboard"),
            ("💡", "Insights", "insights"),
            ("💬", "Feedback", "feedback"),
            ("👤", "Profile", "profile"),
        ]
        
        if "current_page" not in st.session_state:
            st.session_state.current_page = "home"
        
        st.markdown('<ul class="nav-menu">', unsafe_allow_html=True)
        for icon, label, page_key in menu_items:
            if st.button(f"{icon} {label}", key=f"nav_{page_key}", use_container_width=True):
                st.session_state.current_page = page_key
                st.rerun()
        st.markdown('</ul>', unsafe_allow_html=True)
        
        # Logout button
        st.markdown("<br><br>", unsafe_allow_html=True)
        if st.button("🚪 Logout", key="logout_btn", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

# -----------------------
# LOTTIE HELPER
# -----------------------
@st.cache_data
def load_lottie(url):
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            return r.json()
    except:
        pass
    return None

# -----------------------
# AUTH FUNCTIONS
# -----------------------
def login_user(email, password):
    if not db:
        return {"localId": "demo", "email": email} if email and password else None
    try:
        login_url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_API_KEY}"
        payload = {"email": email, "password": password, "returnSecureToken": True}
        res = requests.post(login_url, json=payload)
        res.raise_for_status()
        return res.json()
    except:
        return None

def signup_user(email, password, full_name, mobile):
    if not db:
        return "demo_uid"
    try:
        user = admin_auth.create_user(email=email, password=password)
        db.collection("users").document(user.uid).set({
            "full_name": full_name, "email": email, "mobile": mobile
        })
        return user.uid
    except Exception as e:
        st.error(f"Error: {e}")
        return None

def get_profile_data(uid):
    if not db:
        return {"full_name": "Demo User", "email": "demo@example.com", "mobile": "123-456-7890"}
    try:
        doc_ref = db.collection("users").document(uid).get()
        return doc_ref.to_dict() if doc_ref.exists else {}
    except:
        return {}

# -----------------------
# AUTH PAGE
# -----------------------
def auth_page():
    if "theme" not in st.session_state:
        st.session_state.theme = "Light"
    
    load_css(is_auth=True, theme=st.session_state.theme)
    
    # Large animated header with lottie
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        lottie_data = load_lottie(LOTTIE_URLS["travel_home"])
        if lottie_data:
            st_lottie(lottie_data, height=300, key="auth_hero_anim", speed=0.8)
    
    st.markdown("""
    <div style="text-align: center; margin: 2rem 0;">
        <h1 style="font-size: 4.5rem; font-weight: 900; margin-bottom: 1rem; 
                   background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                   -webkit-background-clip: text;
                   -webkit-text-fill-color: transparent;">
            🌍 Tourism Analytics
        </h1>
        <p style="font-size: 1.6rem; color: #34495e; font-weight: 500; margin-bottom: 3rem;">
            Unlock insights into global travel trends and discover the future of tourism
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    with st.container():
        col1, col2, col3 = st.columns([1, 2.5, 1])
        with col2:
            # Add welcome message with animation
            st.markdown("""
            <div style="text-align: center; margin-bottom: 2rem;">
                <h2 style="font-size: 2.5rem; font-weight: 700; color: #2c3e50; margin-bottom: 0.5rem;">
                    Welcome Back!
                </h2>
                <p style="font-size: 1.3rem; color: #7f8c8d;">
                    Sign in to access your analytics dashboard
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            tab1, tab2 = st.tabs(["🔐 Login", "📝 Sign Up"])
            
            with tab1:
                with st.form("login_form"):
                    st.markdown("<div style='padding: 1rem 0;'>", unsafe_allow_html=True)
                    email = st.text_input("📧 Email Address", placeholder="Enter your email", key="login_email")
                    password = st.text_input("🔒 Password", type="password", placeholder="Enter your password", key="login_pass")
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    
                    # Custom styled login button
                    st.markdown('<div class="login-button">', unsafe_allow_html=True)
                    login_submit = st.form_submit_button("🚀 SIGN IN NOW", use_container_width=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    if login_submit and email and password:
                        user = login_user(email, password)
                        if user:
                            st.session_state.user = user
                            st.success("✅ Welcome back! Redirecting to dashboard...")
                            st.balloons()
                            st.rerun()
                        else:
                            st.error("❌ Invalid credentials. Try demo@example.com / demo123")
                
                # Demo credentials hint
                st.markdown("""
                <div style="text-align: center; margin-top: 2rem; padding: 1.5rem; 
                            background: rgba(102, 126, 234, 0.1); border-radius: 15px;">
                    <p style="font-size: 1.1rem; color: #667eea; margin: 0; font-weight: 600;">
                        💡 Demo Account
                    </p>
                    <p style="font-size: 1rem; color: #34495e; margin: 0.5rem 0 0 0;">
                        Email: demo@example.com | Password: demo123
                    </p>
                </div>
                """, unsafe_allow_html=True)
            
            with tab2:
                with st.form("signup_form"):
                    st.markdown("<div style='padding: 1rem 0;'>", unsafe_allow_html=True)
                    full_name = st.text_input("👤 Full Name", placeholder="Enter your full name", key="signup_name")
                    email = st.text_input("📧 Email Address", placeholder="Enter your email", key="signup_email")
                    mobile = st.text_input("📱 Mobile Number", placeholder="Enter your mobile number", key="signup_mobile")
                    password = st.text_input("🔒 Password", type="password", placeholder="Create a strong password", key="signup_pass")
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    
                    col1, col2, col3 = st.columns([1, 2, 1])
                    with col2:
                        signup_submit = st.form_submit_button("🎉 CREATE ACCOUNT", use_container_width=True)
                    
                    if signup_submit and all([email, password, full_name, mobile]):
                        uid = signup_user(email, password, full_name, mobile)
                        if uid:
                            st.success("🎊 Account created successfully! Please log in.")
                            st.balloons()
    
    # Footer animation
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        lottie_data = load_lottie(LOTTIE_URLS["world_map"])
        if lottie_data:
            st_lottie(lottie_data, height=250, key="auth_footer_anim", speed=0.5)

# -----------------------
# MAIN PAGES
# -----------------------
def home_page():
    st.markdown("""
    <div class="home-hero-section">
        <h1>🌍 Welcome to Tourism Analytics</h1>
        <p>Discover global travel trends and insights powered by advanced data analytics</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        lottie_data = load_lottie(LOTTIE_URLS["travel_home"])
        if lottie_data:
            st_lottie(lottie_data, height=400, key="home_hero_anim", speed=0.8)
    
    st.markdown('<div class="stats-container">', unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("""
        <div class="stat-card">
            <div class="stat-number">2.8B</div>
            <div class="stat-label">Global Travelers</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="stat-card">
            <div class="stat-number">195</div>
            <div class="stat-label">Countries Covered</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="stat-card">
            <div class="stat-number">$1.4T</div>
            <div class="stat-label">Tourism Revenue</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="stat-card">
            <div class="stat-number">24/7</div>
            <div class="stat-label">Real-time Data</div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    with col1:
        lottie_data = load_lottie(LOTTIE_URLS["world_map"])
        if lottie_data:
            st.markdown('<div class="animation-container">', unsafe_allow_html=True)
            st_lottie(lottie_data, height=350, key="world_map_anim", speed=0.5)
            st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="content-card">
            <h3>🚀 Platform Features</h3>
            <ul style="list-style: none; padding: 0;">
                <li style="margin: 1.5rem 0;"><strong>📊 Interactive Dashboards</strong><br>
                Real-time Power BI visualizations with dynamic filtering</li>
                <li style="margin: 1.5rem 0;"><strong>🔐 Secure Access</strong><br>
                Firebase authentication with enterprise-grade security</li>
                <li style="margin: 1.5rem 0;"><strong>💡 Smart Insights</strong><br>
                AI-powered trend analysis and predictive analytics</li>
                <li style="margin: 1.5rem 0;"><strong>📱 Responsive Design</strong><br>
                Seamless experience across all devices and platforms</li>
                <li style="margin: 1.5rem 0;"><strong>🌐 Global Coverage</strong><br>
                Comprehensive data from 195+ countries worldwide</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        lottie_data = load_lottie(LOTTIE_URLS["home"])
        if lottie_data:
            st.markdown('<div class="animation-container">', unsafe_allow_html=True)
            st_lottie(lottie_data, height=300, key="home_secondary_anim")
            st.markdown('</div>', unsafe_allow_html=True)

def dashboard_page():
    st.markdown("# 📊 Interactive Tourism Dashboard")
    st.markdown("### Real-time analytics and visualizations")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        lottie_data = load_lottie(LOTTIE_URLS["dashboard"])
        if lottie_data:
            st.markdown('<div class="animation-container">', unsafe_allow_html=True)
            st_lottie(lottie_data, height=250, key="dash_anim")
            st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="dashboard-container">
        <iframe title="Tourism Report" width="100%" height="800" 
        src="{}" frameborder="0" allowFullScreen="true"></iframe>
    </div>
    """.format(POWERBI_EMBED_URL), unsafe_allow_html=True)

def insights_page():
    st.markdown("# 💡 Key Tourism Insights")
    st.markdown("### Data-driven discoveries and predictive trends")
    
    col1, col2 = st.columns([1, 1])
    with col1:
        lottie_data = load_lottie(LOTTIE_URLS["insights_data"])
        if lottie_data:
            st.markdown('<div class="animation-container">', unsafe_allow_html=True)
            st_lottie(lottie_data, height=350, key="insights_main_anim", speed=0.8)
            st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        lottie_data = load_lottie(LOTTIE_URLS["insights"])
        if lottie_data:
            st.markdown('<div class="animation-container">', unsafe_allow_html=True)
            st_lottie(lottie_data, height=350, key="insights_secondary_anim")
            st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="content-card">
        <h3>🌍 Global Tourism Recovery Analysis</h3>
        <p>International tourism has demonstrated exceptional resilience, achieving a remarkable 65% recovery rate compared to pre-pandemic levels. This recovery is driven by multiple interconnected factors that reflect changing consumer behaviors and industry adaptations.</p>
        <p><strong>Key Recovery Drivers:</strong></p>
        <ul>
            <li><strong>Pent-up Demand:</strong> Consumers are prioritizing travel experiences after years of restrictions</li>
            <li><strong>Health Security:</strong> Widespread vaccination coverage has restored traveler confidence</li>
            <li><strong>Flexible Policies:</strong> Airlines and hotels offering adaptable booking terms</li>
            <li><strong>Digital Integration:</strong> Seamless health passport and contactless travel technologies</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="insights-grid">', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div class="content-card">
            <h4>🏆 Top Global Destinations</h4>
            <div style="margin: 1.5rem 0;">
                <div style="margin: 1rem 0; padding: 1rem; background: rgba(102, 126, 234, 0.1); border-radius: 10px;">
                    <strong>1. 🇫🇷 France</strong><br>
                    <span style="font-size: 1.2rem; font-weight: 600;">89.4M visitors</span><br>
                    <span style="opacity: 0.8;">+12% YoY growth</span>
                </div>
                <div style="margin: 1rem 0; padding: 1rem; background: rgba(102, 126, 234, 0.1); border-radius: 10px;">
                    <strong>2. 🇪🇸 Spain</strong><br>
                    <span style="font-size: 1.2rem; font-weight: 600;">83.7M visitors</span><br>
                    <span style="opacity: 0.8;">+15% YoY growth</span>
                </div>
                <div style="margin: 1rem 0; padding: 1rem; background: rgba(102, 126, 234, 0.1); border-radius: 10px;">
                    <strong>3. 🇺🇸 United States</strong><br>
                    <span style="font-size: 1.2rem; font-weight: 600;">79.3M visitors</span><br>
                    <span style="opacity: 0.8;">+8% YoY growth</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="content-card">
            <h4>💰 Spending & Trends</h4>
            <div style="margin: 1.5rem 0;">
                <div style="margin: 1rem 0; padding: 1rem; background: rgba(76, 175, 80, 0.1); border-radius: 10px;">
                    <strong>💎 Luxury Travel</strong><br>
                    <span style="font-size: 1.2rem; font-weight: 600; color: #4CAF50;">+25% YoY</span><br>
                    <span style="opacity: 0.8;">$2,847 avg. spending per trip</span>
                </div>
                <div style="margin: 1rem 0; padding: 1rem; background: rgba(76, 175, 80, 0.1); border-radius: 10px;">
                    <strong>🌿 Eco-Tourism</strong><br>
                    <span style="font-size: 1.2rem; font-weight: 600; color: #4CAF50;">+40% YoY</span><br>
                    <span style="opacity: 0.8;">$1,234 avg. spending per trip</span>
                </div>
                <div style="margin: 1rem 0; padding: 1rem; background: rgba(76, 175, 80, 0.1); border-radius: 10px;">
                    <strong>💻 Digital Nomads</strong><br>
                    <span style="font-size: 1.2rem; font-weight: 600; color: #4CAF50;">+60% YoY</span><br>
                    <span style="opacity: 0.8;">$1,856 avg. monthly spending</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="content-card">
            <h4>📈 Emerging Markets</h4>
            <div style="margin: 1.5rem 0;">
                <div style="margin: 1rem 0; padding: 1rem; background: rgba(255, 152, 0, 0.1); border-radius: 10px;">
                    <strong>🌏 Asia-Pacific</strong><br>
                    <span style="font-size: 1.2rem; font-weight: 600; color: #FF9800;">+15% growth</span><br>
                    <span style="opacity: 0.8;">Led by Vietnam, Thailand</span>
                </div>
                <div style="margin: 1rem 0; padding: 1rem; background: rgba(255, 152, 0, 0.1); border-radius: 10px;">
                    <strong>🌎 Latin America</strong><br>
                    <span style="font-size: 1.2rem; font-weight: 600; color: #FF9800;">+12% growth</span><br>
                    <span style="opacity: 0.8;">Mexico, Colombia leading</span>
                </div>
                <div style="margin: 1rem 0; padding: 1rem; background: rgba(255, 152, 0, 0.1); border-radius: 10px;">
                    <strong>🌍 Africa</strong><br>
                    <span style="font-size: 1.2rem; font-weight: 600; color: #FF9800;">+18% growth</span><br>
                    <span style="opacity: 0.8;">Morocco, South Africa surge</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div class="content-card">
        <h3>🔮 Future Predictions & Trends</h3>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 2rem; margin: 2rem 0;">
            <div>
                <h4>🤖 Technology Integration</h4>
                <p>AI-powered personalization, VR previews, and blockchain-based identity verification will reshape the booking experience by 2025.</p>
            </div>
            <div>
                <h4>🌱 Sustainable Tourism</h4>
                <p>Carbon-neutral travel options will become standard, with 70% of travelers willing to pay premium for eco-friendly experiences.</p>
            </div>
            <div>
                <h4>🏠 Workation Boom</h4>
                <p>Extended stays combining work and leisure will grow by 200%, driven by remote work flexibility and lifestyle changes.</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def feedback_page():
    st.markdown("# 💬 Share Your Feedback")
    st.markdown("### Help us improve your experience")
    
    col1, col2 = st.columns([1, 2])
    with col1:
        lottie_data = load_lottie(LOTTIE_URLS["feedback"])
        if lottie_data:
            st.markdown('<div class="animation-container">', unsafe_allow_html=True)
            st_lottie(lottie_data, height=400, key="feedback_anim")
            st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        with st.form("feedback_form"):
            st.markdown("#### Tell us about your experience")
            
            rating = st.select_slider("Rate your overall experience", 
                                    options=['😞 Poor', '😐 Fair', '😊 Good', '😍 Excellent'],
                                    value='😊 Good')
            
            feedback_type = st.selectbox("Feedback Category", 
                                       ['General Experience', 'Dashboard Performance', 'Data Accuracy', 'Feature Request', 'Bug Report', 'UI/UX Feedback'])
            
            message = st.text_area("Your detailed feedback", 
                                 placeholder="Share your thoughts, suggestions, or report any issues you've encountered...",
                                 height=150)
            
            contact_preference = st.checkbox("I would like to be contacted about my feedback")
            
            st.markdown("<br>", unsafe_allow_html=True)
            submitted = st.form_submit_button("🚀 Submit Feedback", use_container_width=True)
            
            if submitted and message:
                st.success("🎉 Thank you for your valuable feedback! Our team will review it and get back to you shortly.")
        st.markdown('</div>', unsafe_allow_html=True)

def profile_page():
    st.markdown("# 👤 User Profile")
    st.markdown("### Manage your account information")
    
    user_data = get_profile_data(st.session_state.user.get("localId", "demo"))
    
    st.markdown('<div class="profile-container">', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        lottie_data = load_lottie(LOTTIE_URLS["profile"])
        if lottie_data:
            st.markdown('<div class="animation-container">', unsafe_allow_html=True)
            st_lottie(lottie_data, height=300, key="profile_anim")
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="profile-main-card">
            <div class="profile-avatar">
                👤
            </div>
            <div class="profile-name">{user_data.get('full_name', 'Demo User')}</div>
            <div class="profile-role">Member</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="profile-details">', unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="profile-info">
            <div class="profile-info-label">👤 Full Name</div>
            <div class="profile-info-value">{user_data.get('full_name', 'Demo User')}</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="profile-info">
            <div class="profile-info-label">📧 Email Address</div>
            <div class="profile-info-value">{user_data.get('email', 'demo@example.com')}</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="profile-info">
            <div class="profile-info-label">📱 Mobile Number</div>
            <div class="profile-info-value">{user_data.get('mobile', 'Not provided')}</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("✏️ Edit Profile", use_container_width=True):
            st.info("Profile editing feature will be available in the next update!")
    
    st.markdown('</div>', unsafe_allow_html=True)

# -----------------------
# MAIN APP LOGIC
# -----------------------
def main():
    if "theme" not in st.session_state:
        st.session_state.theme = "Light"
    
    if "user" not in st.session_state:
        auth_page()
        return
    
    load_css(theme=st.session_state.theme)
    
    render_sidebar()
    
    col1, col2, col3 = st.columns([6, 1, 1])
    with col3:
        if st.button("🌙" if st.session_state.theme == "Light" else "☀️", 
            help="Toggle theme", key="theme_toggle"):
            st.session_state.theme = "Dark" if st.session_state.theme == "Light" else "Light"
            st.rerun()
    
    current_page = st.session_state.get("current_page", "home")
    
    if current_page == "home":
        home_page()
    elif current_page == "dashboard":
        dashboard_page()
    elif current_page == "insights":
        insights_page()
    elif current_page == "feedback":
        feedback_page()
    elif current_page == "profile":
        profile_page()

if __name__ == "__main__":
    st.set_page_config(
        page_title="Tourism Analytics Dashboard",
        page_icon="🌍",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    main()