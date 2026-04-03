import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

st.set_page_config(
    page_title="Connectra · Onchain Talent",
    page_icon="⬡", layout="wide",
    initial_sidebar_state="expanded",
)

from styles import GLOBAL_CSS
from data.sqlite_db import init_db, seed_if_empty

st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

init_db()
seed_if_empty()

defaults = {
    "user_role": "talent",
    "wallet": "0x742d35Cc6634C0532925a3b844Bc454e4438f44e",
    "wallet_connected": False,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ══════════════════════════════════════════════════════
# PREMIUM SIDEBAR
# ══════════════════════════════════════════════════════
ICON = {
    "overview":    '<svg viewBox="0 0 24 24" width="16" height="16"><rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/></svg>',
    "profile":     '<svg viewBox="0 0 24 24" width="16" height="16"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>',
    "dashboard":   '<svg viewBox="0 0 24 24" width="16" height="16"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>',
    "market":      '<svg viewBox="0 0 24 24" width="16" height="16"><path d="M6 2L3 6v14a2 2 0 002 2h14a2 2 0 002-2V6l-3-4z"/><line x1="3" y1="6" x2="21" y2="6"/><path d="M16 10a4 4 0 01-8 0"/></svg>',
    "postjob":     '<svg viewBox="0 0 24 24" width="16" height="16"><rect x="2" y="7" width="20" height="14" rx="2"/><path d="M16 21V5a2 2 0 00-2-2h-4a2 2 0 00-2 2v16"/></svg>',
    "employer":    '<svg viewBox="0 0 24 24" width="16" height="16"><path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 00-3-3.87"/><path d="M16 3.13a4 4 0 010 7.75"/></svg>',
    "analytics":   '<svg viewBox="0 0 24 24" width="16" height="16"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>',
    "chevron":     '<svg viewBox="0 0 24 24" width="12" height="12"><polyline points="9 18 15 12 9 6"/></svg>',
}

nav_items = [
    ("pages/1_Home.py",              "Overview",          ICON["overview"]),
    ("pages/2_Create_Profile.py",    "Create Profile",    ICON["profile"]),
    ("pages/3_Talent_Dashboard.py",  "My Dashboard",      ICON["dashboard"]),
    ("pages/4_Marketplace.py",       "Marketplace",       ICON["market"]),
    ("pages/5_Post_Job.py",          "Post a Job",        ICON["postjob"]),
    ("pages/6_Employer_Dashboard.py","Employer Hub",      ICON["employer"]),
    ("pages/7_Analytics.py",         "Analytics",         ICON["analytics"]),
]

with st.sidebar:
    # ── Branding ──
    st.markdown(f"""
<div class='sb-brand'>
  <div class='sb-logo-row'>
    <div class='sb-hex'>⬡</div>
    <div class='sb-name'>Connectra</div>
  </div>
  <div class='sb-sub'>Onchain Talent Marketplace</div>
</div>
""", unsafe_allow_html=True)

    # ── Navigation ──
    st.markdown("<div class='sb-section'>Navigation</div>", unsafe_allow_html=True)

    for path, label, icon in nav_items:
        st.page_link(path, label=f"  {label}")

    # ── Divider ──
    st.markdown("<hr style='border:none;border-top:1px solid rgba(255,255,255,.05);margin:12px 8px;'>", unsafe_allow_html=True)
    st.markdown("<div class='sb-section'>Settings</div>", unsafe_allow_html=True)

    # ── Mode + Wallet ──
    role = st.radio("", ["Talent", "Employer"], horizontal=True,
                    index=0 if st.session_state.user_role == "talent" else 1,
                    label_visibility="collapsed")
    st.session_state.user_role = role.lower()

    st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)

    if not st.session_state.wallet_connected:
        if st.button("⬡  Connect Wallet", use_container_width=True):
            st.session_state.wallet_connected = True
            st.rerun()
    else:
        w = st.session_state.wallet
        st.markdown(f"""
<div style='background:rgba(29,158,117,.08);border:1px solid rgba(29,158,117,.18);
            border-radius:8px;padding:10px 12px;font-size:11px;'>
  <div style='color:#2a4a34;font-size:9px;letter-spacing:.08em;margin-bottom:3px;'>CONNECTED</div>
  <div style='font-family:DM Mono,monospace;color:#4de8b4;word-break:break-all;'>{w[:10]}...{w[-6:]}</div>
  <div style='color:#1D9E75;font-size:10px;margin-top:3px;'>● Polygon Amoy</div>
</div>
""", unsafe_allow_html=True)

    st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
    if st.button("↺  Reset Demo Data", use_container_width=True, key="reset_btn"):
        from data.seed_data import seed_database
        seed_database()
        st.success("Reset!")
        st.rerun()

    # ── Footer ──
    st.markdown("""
<div style='margin-top:20px;padding:12px;border-top:1px solid rgba(255,255,255,.05);'>
  <div style='font-size:9px;color:#1a2a1a;letter-spacing:.08em;text-transform:uppercase;margin-bottom:6px;'>Powered by</div>
  <div style='font-size:10px;color:#2a3a4a;line-height:1.9;'>
    ◎ Polygon Amoy Testnet<br>◎ IPFS / nft.storage<br>◎ SQLite → upgradeable
  </div>
</div>
""", unsafe_allow_html=True)

# Custom styling to make page_link items look like premium nav
st.markdown("""
<style>
/* Style page_link as premium nav items */
[data-testid="stPageLink"] a {
    display: flex !important; align-items: center !important;
    padding: 9px 12px 9px 20px !important; margin: 1px 8px !important;
    border-radius: 8px !important; text-decoration: none !important;
    color: #5a7088 !important; font-size: 13px !important; font-weight: 500 !important;
    transition: background .15s, color .15s !important;
}
[data-testid="stPageLink"] a:hover {
    background: rgba(255,255,255,.05) !important; color: #c8d8e8 !important;
}
[data-testid="stPageLink"] a[aria-current="page"] {
    background: rgba(29,158,117,.15) !important; color: #4de8b4 !important;
    border: 1px solid rgba(29,158,117,.2) !important;
}
[data-testid="stPageLink"] { margin: 0 !important; }
</style>
""", unsafe_allow_html=True)

# ══ Pages ══
page = st.navigation([
    st.Page("pages/1_Home.py",              title="Overview",       icon="◈"),
    st.Page("pages/2_Create_Profile.py",    title="Create Profile", icon="◈"),
    st.Page("pages/3_Talent_Dashboard.py",  title="My Dashboard",   icon="◈"),
    st.Page("pages/4_Marketplace.py",       title="Marketplace",    icon="◈"),
    st.Page("pages/5_Post_Job.py",          title="Post a Job",     icon="◈"),
    st.Page("pages/6_Employer_Dashboard.py",title="Employer Hub",   icon="◈"),
    st.Page("pages/7_Analytics.py",         title="Analytics",      icon="◈"),
])
page.run()
