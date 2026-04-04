import streamlit as st
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

st.set_page_config(
    page_title="Connectra · Onchain Talent",
    page_icon="⬡",
    layout="wide",
    initial_sidebar_state="expanded",
)

from styles import GLOBAL_CSS, SIDEBAR_BRAND
from data.sqlite_db import init_db, seed_if_empty

st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

init_db()
seed_if_empty()

defaults = {
    "user_role":        "talent",
    "wallet":           "0x742d35Cc6634C0532925a3b844Bc454e4438f44e",
    "wallet_connected": False,
    "current_page":     "home",
    "prev_page":        "home",
    "wiz_step":         1,
    "wiz_data":         {},
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

def go(page_key):
    st.session_state.prev_page = st.session_state.current_page
    st.session_state.current_page = page_key
    st.rerun()

PAGE_LABELS = {
    "home":      "Home",
    "profile":   "Create Profile",
    "dashboard": "Talent Dashboard",
    "market":    "Marketplace",
    "skilltest": "Skill Tests",
    "postjob":   "Post a Job",
    "employer":  "Employer Hub",
    "analytics": "Analytics",
}

PAGE_ICONS = {
    "home":      "🏠",
    "profile":   "👤",
    "dashboard": "📊",
    "market":    "💼",
    "skilltest": "✅",
    "postjob":   "➕",
    "employer":  "🏢",
    "analytics": "📈",
}

# Inject a single CSS block that highlights whichever nav button is active
# We use the button's aria-label (which Streamlit sets to the button text) to target it
active_page = st.session_state.current_page
active_label = f"{PAGE_ICONS.get(active_page, '')}  {PAGE_LABELS.get(active_page, '')}"
st.markdown(f"""
<style>
/* Active nav button highlight — target by button text content match */
[data-testid="stSidebar"] .stButton > button[title="{active_label}"],
[data-testid="stSidebar"] .stButton > button[aria-label="{active_label}"] {{
  background: rgba(29,158,117,.18) !important;
  color: #4de8b4 !important;
  border-left: 3px solid #1D9E75 !important;
  padding-left: 11px !important;
  font-weight: 600 !important;
}}
</style>
""", unsafe_allow_html=True)

def nav_btn(page_key):
    icon  = PAGE_ICONS[page_key]
    label = PAGE_LABELS[page_key]
    # Plain text only in button label — no HTML/SVG
    if st.button(f"{icon}  {label}", key=f"nav_{page_key}", use_container_width=True):
        go(page_key)

# ══════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════
with st.sidebar:
    st.markdown(SIDEBAR_BRAND, unsafe_allow_html=True)
    st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

    nav_btn("home")

    st.markdown("<div style='font-size:10px;color:#2a4a34;letter-spacing:.1em;text-transform:uppercase;padding:12px 8px 4px;'>Mode</div>", unsafe_allow_html=True)

    prev_role = st.session_state.user_role
    role = st.radio("", ["Talent", "Employer"], horizontal=True,
                    index=0 if prev_role == "talent" else 1,
                    label_visibility="collapsed", key="role_radio")
    new_role = role.lower()
    if new_role != prev_role:
        st.session_state.user_role = new_role
        go("dashboard" if new_role == "talent" else "postjob")

    st.markdown("<div style='height:2px'></div>", unsafe_allow_html=True)

    if st.session_state.user_role == "talent":
        nav_btn("profile")
        nav_btn("dashboard")
        nav_btn("market")
        nav_btn("skilltest")
    else:
        nav_btn("postjob")
        nav_btn("employer")

    st.markdown("<hr style='border:none;border-top:1px solid rgba(29,158,117,.12);margin:6px 0;'>", unsafe_allow_html=True)
    nav_btn("analytics")
    st.markdown("<hr style='border:none;border-top:1px solid rgba(29,158,117,.12);margin:6px 0;'>", unsafe_allow_html=True)

    st.markdown("<div style='font-size:10px;color:#2a4a34;letter-spacing:.1em;text-transform:uppercase;padding:0 8px 4px;'>Demo Wallet</div>", unsafe_allow_html=True)

    if not st.session_state.wallet_connected:
        if st.button("🔗  Connect Wallet", use_container_width=True, key="connect_wallet"):
            st.session_state.wallet_connected = True
            st.rerun()
    else:
        w = st.session_state.wallet
        st.markdown(f"""
<div style='background:rgba(29,158,117,.1);border:1px solid rgba(29,158,117,.22);
            border-radius:10px;padding:10px 12px;font-size:11px;margin:2px 4px;'>
  <div style='color:#2a4a34;font-size:10px;letter-spacing:.05em;margin-bottom:2px;'>CONNECTED</div>
  <div style='font-family:DM Mono,monospace;color:#4de8b4;font-size:11px;'>{w[:10]}...{w[-6:]}</div>
  <div style='color:#1D9E75;font-size:10px;margin-top:3px;'>● Polygon Amoy</div>
</div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

    if st.button("🔄  Reset Demo Data", use_container_width=True, key="reset_data"):
        from data.seed_data import seed_database
        seed_database()
        st.success("Reset!")
        st.rerun()

    st.markdown("""
<div style='margin:10px 4px 0;padding:12px;background:rgba(29,158,117,.05);
            border-radius:10px;border:1px solid rgba(29,158,117,.1);
            font-size:11px;color:#4a6a84;line-height:2.1;'>
  <div style='font-size:10px;color:#2a4a34;letter-spacing:.08em;margin-bottom:6px;'>POWERED BY</div>
  ⬡ Polygon Amoy Testnet<br>
  📦 IPFS / nft.storage<br>
  🤖 Rule-based ML Engine<br>
  🗄️ SQLite (upgradeable)
</div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════
# BACK BUTTON + PAGE ROUTING
# ══════════════════════════════════════════════════════
PAGE_MAP = {
    "home":      "1_Home.py",
    "profile":   "2_Create_Profile.py",
    "dashboard": "3_Talent_Dashboard.py",
    "market":    "4_Marketplace.py",
    "postjob":   "5_Post_Job.py",
    "employer":  "6_Employer_Dashboard.py",
    "analytics": "7_Analytics.py",
    "skilltest": "8_Skill_Tests.py",
}

BACK_MAP = {
    "profile":   "home",
    "dashboard": "home",
    "market":    "dashboard",
    "skilltest": "dashboard",
    "postjob":   "home",
    "employer":  "postjob",
    "analytics": "home",
}

page = st.session_state.current_page

if page in BACK_MAP:
    back_key   = st.session_state.prev_page if (st.session_state.prev_page and st.session_state.prev_page != page) else BACK_MAP[page]
    back_label = PAGE_LABELS.get(back_key, "Back")
    if st.button(f"← {back_label}", key="back_btn"):
        go(back_key)
    st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

filename = PAGE_MAP.get(page, "1_Home.py")
exec(open(ROOT / "pages" / filename).read())
