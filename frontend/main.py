import os

import requests
import streamlit as st
from dotenv import load_dotenv
from requests.auth import HTTPBasicAuth

load_dotenv()

API_URL = os.getenv("API_URL")

st.set_page_config(
    page_title="Medical RAG AI",
    page_icon="⚕",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;1,9..40,300&family=JetBrains+Mono:wght@400;500&display=swap');

* { box-sizing: border-box; }

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    color: #cbd5e1;
}

/* ── App Background ─────────────────────────────── */
.stApp {
    background: #040d18;
    background-image:
        radial-gradient(ellipse 60% 40% at 15% 65%, rgba(0,200,232,0.05) 0%, transparent 60%),
        radial-gradient(ellipse 50% 55% at 85% 15%, rgba(14,165,233,0.06) 0%, transparent 60%);
}

.stApp::before {
    content: '';
    position: fixed;
    inset: 0;
    background-image:
        linear-gradient(rgba(0,200,232,0.022) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0,200,232,0.022) 1px, transparent 1px);
    background-size: 48px 48px;
    pointer-events: none;
    z-index: 0;
}

/* ── Hide Streamlit Chrome ──────────────────────── */
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stDecoration"] { display: none; }
.block-container { padding-top: 2rem !important; max-width: 860px !important; }

/* ── Sidebar ────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: rgba(4, 12, 22, 0.97) !important;
    border-right: 1px solid rgba(0, 200, 232, 0.07) !important;
}
[data-testid="stSidebarContent"] {
    padding: 1.75rem 1.25rem !important;
}

/* ── Buttons ────────────────────────────────────── */
.stButton > button {
    width: 100% !important;
    background: linear-gradient(135deg, #0369a1 0%, #00b8d4 100%) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 3px !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.75rem !important;
    letter-spacing: 0.12em !important;
    text-transform: uppercase !important;
    padding: 0.65rem 1.25rem !important;
    transition: all 0.22s ease !important;
    box-shadow: 0 0 20px rgba(0,184,212,0.18) !important;
}

.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 32px rgba(0,184,212,0.38) !important;
}

.stButton > button:active {
    transform: translateY(0px) !important;
}

/* ── Text Inputs ────────────────────────────────── */
.stTextInput > div > div > input {
    background: rgba(255,255,255,0.03) !important;
    border: 1px solid rgba(0,200,232,0.14) !important;
    border-radius: 3px !important;
    color: #e2e8f0 !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.95rem !important;
    padding: 0.65rem 0.9rem !important;
    transition: all 0.2s ease !important;
}

.stTextInput > div > div > input:focus {
    border-color: rgba(0,200,232,0.45) !important;
    background: rgba(0,200,232,0.03) !important;
    box-shadow: 0 0 0 2px rgba(0,200,232,0.07) !important;
    outline: none !important;
}

.stTextInput > div > div > input::placeholder { color: #1e3a4a !important; }

/* ── Labels ─────────────────────────────────────── */
.stTextInput label,
.stSelectbox label,
[data-testid="stFileUploader"] label {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.65rem !important;
    font-weight: 500 !important;
    color: #00b8d4 !important;
    letter-spacing: 0.14em !important;
    text-transform: uppercase !important;
}

/* ── Selectbox ──────────────────────────────────── */
.stSelectbox > div > div {
    background: rgba(255,255,255,0.03) !important;
    border: 1px solid rgba(0,200,232,0.14) !important;
    border-radius: 3px !important;
    color: #e2e8f0 !important;
}

/* ── Tabs ───────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    background: transparent !important;
    border-bottom: 1px solid rgba(0,200,232,0.08) !important;
    gap: 0 !important;
    padding: 0 !important;
}

.stTabs [data-baseweb="tab"] {
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.72rem !important;
    letter-spacing: 0.12em !important;
    text-transform: uppercase !important;
    color: #334155 !important;
    background: transparent !important;
    border: none !important;
    border-bottom: 2px solid transparent !important;
    padding: 0.75rem 1.75rem !important;
    transition: all 0.2s !important;
}

.stTabs [aria-selected="true"] {
    color: #00b8d4 !important;
    border-bottom: 2px solid #00b8d4 !important;
    background: transparent !important;
}

.stTabs [data-baseweb="tab-panel"] { padding: 1.5rem 0 !important; }

/* ── Alerts ─────────────────────────────────────── */
.stSuccess > div {
    background: rgba(0,200,80,0.07) !important;
    border: 1px solid rgba(0,200,80,0.22) !important;
    border-radius: 3px !important;
    color: #4ade80 !important;
}

.stError > div {
    background: rgba(239,68,68,0.07) !important;
    border: 1px solid rgba(239,68,68,0.22) !important;
    border-radius: 3px !important;
    color: #f87171 !important;
}

/* ── Divider ────────────────────────────────────── */
hr {
    border: none !important;
    border-top: 1px solid rgba(0,200,232,0.07) !important;
    margin: 1.25rem 0 !important;
}

/* ── Spinner ────────────────────────────────────── */
.stSpinner > div { border-top-color: #00b8d4 !important; }

/* ── File uploader ──────────────────────────────── */
[data-testid="stFileUploader"] > div {
    background: rgba(255,255,255,0.02) !important;
    border: 1px dashed rgba(0,200,232,0.16) !important;
    border-radius: 3px !important;
    transition: all 0.2s !important;
}

[data-testid="stFileUploader"] > div:hover {
    border-color: rgba(0,200,232,0.38) !important;
    background: rgba(0,200,232,0.02) !important;
}

/* ── Animations ─────────────────────────────────── */
@keyframes blink {
    0%, 100% { opacity: 1; }
    50%       { opacity: 0.25; }
}

.dot-blink { animation: blink 2.2s ease-in-out infinite; }
</style>
""", unsafe_allow_html=True)


# ── Helpers ────────────────────────────────────────────────────────────────────

def page_header(title: str, subtitle: str = "") -> None:
    sub_html = (
        f'<div style="font-family:JetBrains Mono,monospace;font-size:0.65rem;'
        f'color:#1e3a4a;letter-spacing:0.16em;text-transform:uppercase;margin-top:0.35rem;">'
        f'{subtitle}</div>'
    ) if subtitle else ""
    st.markdown(f"""
    <div style="margin-bottom:2.25rem;padding-bottom:1.5rem;border-bottom:1px solid rgba(0,200,232,0.07);">
        <div style="
            font-family:'Syne',sans-serif;font-size:2rem;font-weight:800;
            background:linear-gradient(130deg,#f8fafc 25%,#00b8d4 100%);
            -webkit-background-clip:text;-webkit-text-fill-color:transparent;
            background-clip:text;letter-spacing:-0.03em;line-height:1.1;
        ">⚕ {title}</div>
        {sub_html}
    </div>
    """, unsafe_allow_html=True)


def role_badge(role: str) -> str:
    palette = {
        "admin":  ("#f59e0b", "245,158,11"),
        "doctor": ("#00b8d4", "0,184,212"),
        "user":   ("#8b5cf6", "139,92,246"),
    }
    color, rgb = palette.get(role, ("#64748b", "100,116,139"))
    return (
        f'<span style="display:inline-block;background:rgba({rgb},0.12);'
        f'border:1px solid rgba({rgb},0.32);color:{color};'
        f'font-family:JetBrains Mono,monospace;font-size:0.65rem;'
        f'letter-spacing:0.1em;padding:0.2rem 0.65rem;border-radius:2px;'
        f'text-transform:uppercase;">{role}</span>'
    )


def parse_error(res: requests.Response, fallback: str = "Unknown error") -> str:
    try:
        detail = res.json().get("detail", fallback)
        if isinstance(detail, list):
            return "; ".join(e.get("msg", str(e)) for e in detail)
        return detail
    except Exception:
        return fallback


def get_auth() -> HTTPBasicAuth:
    return HTTPBasicAuth(st.session_state["username"], st.session_state["password"])


# ── Guards ─────────────────────────────────────────────────────────────────────

if not API_URL:
    st.error("API_URL is not configured. Please set the API_URL environment variable.")
    st.stop()

if "username" not in st.session_state:
    st.session_state.update({"username": "", "password": "", "role": "", "logged_in": False})


# ── Auth UI ────────────────────────────────────────────────────────────────────

def auth_ui() -> None:
    _, col, _ = st.columns([1, 1.5, 1])
    with col:
        page_header("Medical RAG AI", "Role-based medical intelligence platform")

        tab_login, tab_signup = st.tabs(["Login", "Sign Up"])

        with tab_login:
            username = st.text_input("Username", key="login_user", placeholder="your username")
            password = st.text_input("Password", type="password", key="login_pass", placeholder="••••••••")
            if st.button("Login", key="btn_login"):
                try:
                    res = requests.get(
                        f"{API_URL}/login",
                        auth=HTTPBasicAuth(username, password),
                        timeout=30,
                    )
                    if res.status_code == 200:
                        user_data = res.json()
                        st.session_state.update({
                            "username": username,
                            "password": password,
                            "role": user_data["role"],
                            "logged_in": True,
                        })
                        st.rerun()
                    else:
                        st.error(f"Login failed: {parse_error(res)}")
                except requests.exceptions.ConnectionError:
                    st.error("Cannot reach the backend. Is the server running?")

        with tab_signup:
            new_user = st.text_input("Username", key="signup_user", placeholder="choose a username")
            new_pass = st.text_input("Password", type="password", key="signup_pass", placeholder="choose a password")
            new_role = st.selectbox("Role", ["doctor", "admin", "user"], key="signup_role")
            if st.button("Create Account", key="btn_signup"):
                try:
                    res = requests.post(
                        f"{API_URL}/signup",
                        json={"username": new_user, "password": new_pass, "role": new_role},
                        timeout=30,
                    )
                    if res.status_code == 200:
                        st.success(f"Account created for {new_user} — please log in.")
                    else:
                        st.error(f"Signup failed: {parse_error(res)}")
                except requests.exceptions.ConnectionError:
                    st.error("Cannot reach the backend. Is the server running?")


# ── Chat UI ────────────────────────────────────────────────────────────────────

def chat_ui() -> None:
    # Sidebar ──────────────────────────────────────────
    with st.sidebar:
        st.markdown(f"""
        <div style="margin-bottom:1.5rem;">
            <div style="font-family:'JetBrains Mono',monospace;font-size:0.6rem;color:#1e3a4a;
                letter-spacing:0.16em;text-transform:uppercase;margin-bottom:0.5rem;">
                Authenticated as
            </div>
            <div style="font-family:'Syne',sans-serif;font-weight:700;font-size:1.05rem;
                color:#f8fafc;margin-bottom:0.5rem;">
                {st.session_state["username"]}
            </div>
            {role_badge(st.session_state["role"])}
        </div>
        """, unsafe_allow_html=True)

        if st.button("Logout", key="btn_logout"):
            st.session_state.clear()
            st.rerun()

        if st.session_state.get("role") == "admin":
            st.markdown("<hr/>", unsafe_allow_html=True)
            st.markdown("""
            <div style="font-family:'JetBrains Mono',monospace;font-size:0.62rem;color:#00b8d4;
                letter-spacing:0.14em;text-transform:uppercase;margin-bottom:0.9rem;">
                Upload Document
            </div>
            """, unsafe_allow_html=True)
            uploaded_file = st.file_uploader("PDF", type=["pdf"], label_visibility="collapsed")
            target_role = st.selectbox("Assign to role", ["doctor", "admin", "user"], key="upload_role")
            if st.button("Upload & Index", key="btn_upload") and uploaded_file:
                with st.spinner("Indexing document…"):
                    try:
                        res = requests.post(
                            f"{API_URL}/upload",
                            auth=get_auth(),
                            files={"file": (uploaded_file.name, uploaded_file, "application/pdf")},
                            data={"role": target_role},
                            timeout=120,
                        )
                        if res.status_code == 200:
                            st.success(f"Indexed: {uploaded_file.name}")
                        else:
                            st.error(f"Upload failed: {parse_error(res)}")
                    except requests.exceptions.ConnectionError:
                        st.error("Cannot reach the backend.")

    # Main area ────────────────────────────────────────
    page_header("Medical RAG AI", "Ask questions from documents matched to your role")

    question = st.text_input(
        "Question",
        placeholder="e.g. What is the recommended dosage for amoxicillin?",
        label_visibility="collapsed",
    )
    st.markdown("""
    <div style="font-family:'JetBrains Mono',monospace;font-size:0.62rem;color:#1e3a4a;
        letter-spacing:0.12em;text-transform:uppercase;margin-top:-0.6rem;margin-bottom:0.9rem;">
        Ask a question — answers are scoped to your role's documents
    </div>
    """, unsafe_allow_html=True)

    if st.button("Submit", key="btn_submit") and question:
        with st.spinner("Retrieving context and generating answer…"):
            try:
                res = requests.post(
                    f"{API_URL}/chat",
                    auth=get_auth(),
                    json={"question": question},
                    timeout=60,
                )
            except requests.exceptions.ConnectionError:
                st.error("Cannot reach the backend.")
                return

        if res.status_code == 200:
            data = res.json()
            st.markdown(f"""
            <div style="
                background:rgba(0,184,212,0.04);
                border:1px solid rgba(0,184,212,0.14);
                border-left:3px solid #00b8d4;
                border-radius:3px;
                padding:1.5rem 1.75rem;
                margin:1rem 0;
                line-height:1.8;
                font-size:0.96rem;
                color:#e2e8f0;
            ">
                <div style="font-family:'JetBrains Mono',monospace;font-size:0.62rem;color:#00b8d4;
                    letter-spacing:0.14em;text-transform:uppercase;margin-bottom:0.85rem;">
                    <span class="dot-blink" style="color:#00b8d4;">●</span>&nbsp; Answer
                </div>
                {data["answer"]}
            </div>
            """, unsafe_allow_html=True)

            if data.get("sources"):
                tags = "".join(
                    f'<span style="display:inline-block;background:rgba(14,165,233,0.1);'
                    f'border:1px solid rgba(14,165,233,0.22);color:#38bdf8;font-size:0.75rem;'
                    f'font-family:JetBrains Mono,monospace;padding:0.2rem 0.55rem;'
                    f'border-radius:2px;margin:0.15rem 0.15rem 0 0;">{s}</span>'
                    for s in data["sources"]
                )
                st.markdown(f"""
                <div style="
                    background:rgba(14,165,233,0.03);
                    border:1px solid rgba(14,165,233,0.1);
                    border-radius:3px;
                    padding:0.85rem 1.25rem;
                    margin-top:0.5rem;
                ">
                    <div style="font-family:'JetBrains Mono',monospace;font-size:0.6rem;color:#0ea5e9;
                        letter-spacing:0.14em;text-transform:uppercase;margin-bottom:0.6rem;">
                        Sources
                    </div>
                    {tags}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.error(f"Error: {parse_error(res)}")


# ── Router ─────────────────────────────────────────────────────────────────────

if st.session_state.get("logged_in"):
    chat_ui()
else:
    auth_ui()
