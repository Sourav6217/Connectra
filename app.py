import streamlit as st
import sys
import os
from pathlib import Path

# ── Ensure project root is on Python path (critical for Streamlit Cloud) ──────
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

# ── Bootstrap DB ──────────────────────────────────────────────────────────────
init_db()
seed_if_empty()

# ── Session defaults ──────────────────────────────────────────────────────────
defaults = {
    "user_role":         "talent",
    "wallet":            "0x742d35Cc6634C0532925a3b844Bc454e4438f44e",
    "wallet_connected":  False,
    "onboarded":         False,
    "wiz_step":          1,
    "wiz_data":          {},
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ═══════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown(SIDEBAR_BRAND, unsafe_allow_html=True)

    # Role toggle
    st.markdown("""
<div style='font-size:10px;color:#2a4a34;letter-spacing:.1em;
            text-transform:uppercase;padding:14px 14px 6px;'>Mode</div>
""", unsafe_allow_html=True)
    role = st.radio(
        "", ["Talent", "Employer"], horizontal=True,
        index=0 if st.session_state.user_role == "talent" else 1,
        label_visibility="collapsed"
    )
    st.session_state.user_role = role.lower()

    st.markdown("<div style='margin:12px 0 6px;'></div>", unsafe_allow_html=True)

    # Wallet connect
    st.markdown("""
<div style='font-size:10px;color:#2a4a34;letter-spacing:.1em;
            text-transform:uppercase;padding:0 14px 6px;'>Demo Wallet</div>
""", unsafe_allow_html=True)

    if not st.session_state.wallet_connected:
        if st.button("Connect Wallet", use_container_width=True):
            st.session_state.wallet_connected = True
            st.rerun()
    else:
        w = st.session_state.wallet
        st.markdown(f"""
<div style='background:rgba(29,158,117,.1);border:1px solid rgba(29,158,117,.22);
            border-radius:10px;padding:10px 12px;font-size:11px;margin:0 4px;'>
  <div style='color:#2a4a34;margin-bottom:3px;font-size:10px;letter-spacing:.05em;'>CONNECTED</div>
  <div style='font-family:DM Mono,monospace;color:#4de8b4;word-break:break-all;'>{w[:10]}...{w[-6:]}</div>
  <div style='color:#1D9E75;font-size:10px;margin-top:4px;display:flex;align-items:center;gap:4px;'>
    <svg width='8' height='8' viewBox='0 0 8 8'><circle cx='4' cy='4' r='4' fill='#1D9E75'/></svg>
    Polygon Amoy
  </div>
</div>
""", unsafe_allow_html=True)

    st.markdown("<hr style='border:none;border-top:1px solid rgba(29,158,117,.1);margin:14px 4px;'>", unsafe_allow_html=True)

    if st.button("Reset Demo Data", use_container_width=True):
        from data.seed_data import seed_database
        seed_database()
        st.success("Data reset!")
        st.rerun()

    st.markdown("""
<div style='margin:16px 4px 0;padding:12px;background:rgba(29,158,117,.05);
            border-radius:10px;border:1px solid rgba(29,158,117,.1);'>
  <div style='font-size:10px;color:#2a4a34;letter-spacing:.08em;margin-bottom:8px;'>POWERED BY</div>
  <div style='font-size:11px;color:#4a6a84;line-height:2;'>
    <div style='display:flex;align-items:center;gap:6px;'>
      <svg width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='#1D9E75' stroke-width='2'><polygon points='12 2 22 8.5 22 15.5 12 22 2 15.5 2 8.5 12 2'/></svg>
      Polygon Amoy Testnet
    </div>
    <div style='display:flex;align-items:center;gap:6px;'>
      <svg width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='#378ADD' stroke-width='2'><path d='M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z'/></svg>
      IPFS / nft.storage
    </div>
    <div style='display:flex;align-items:center;gap:6px;'>
      <svg width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='#7F77DD' stroke-width='2'><circle cx='12' cy='12' r='10'/><line x1='2' y1='12' x2='22' y2='12'/><path d='M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z'/></svg>
      Rule-based ML Engine
    </div>
    <div style='display:flex;align-items:center;gap:6px;'>
      <svg width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='#4a6a84' stroke-width='2'><ellipse cx='12' cy='5' rx='9' ry='3'/><path d='M21 12c0 1.66-4 3-9 3s-9-1.34-9-3'/><path d='M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5'/></svg>
      SQLite (upgradeable)
    </div>
  </div>
</div>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════
# PAGES
# ═══════════════════════════════════════════════════════════
page = st.navigation([
    st.Page("pages/1_Home.py",              title="Home",              icon=":material/home:"),
    st.Page("pages/2_Create_Profile.py",    title="Create Profile",    icon=":material/person_add:"),
    st.Page("pages/3_Talent_Dashboard.py",  title="Talent Dashboard",  icon=":material/dashboard:"),
    st.Page("pages/4_Marketplace.py",       title="Marketplace",       icon=":material/work:"),
    st.Page("pages/5_Post_Job.py",          title="Post a Job",        icon=":material/add_circle:"),
    st.Page("pages/6_Employer_Dashboard.py",title="Employer Hub",      icon=":material/business:"),
    st.Page("pages/7_Analytics.py",         title="Analytics",         icon=":material/analytics:"),
    st.Page("pages/8_Skill_Tests.py",       title="Skill Tests",       icon=":material/quiz:"),
])
page.run()
