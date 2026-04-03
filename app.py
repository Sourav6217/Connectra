import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

st.set_page_config(
    page_title="Connectra · Onchain Talent",
    page_icon="⬡",
    layout="wide",
    initial_sidebar_state="expanded",
)

from styles import GLOBAL_CSS, SIDEBAR_BRAND
from data.sqlite_db import init_db, seed_if_empty

st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

# ── Bootstrap DB ──
init_db()
seed_if_empty()

# ── Session state defaults ──
defaults = {
    "user_role":   "talent",
    "wallet":      "0x742d35Cc6634C0532925a3b844Bc454e4438f44e",
    "wallet_connected": False,
    "onboarded":   False,
    "demo_wallet_set": False,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ═══════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════
with st.sidebar:
    st.markdown(SIDEBAR_BRAND, unsafe_allow_html=True)

    # Role toggle
    st.markdown("""
    <div style='font-size:10px;color:#2a4a34;letter-spacing:.1em;
                text-transform:uppercase;padding:0 4px 6px;'>Mode</div>
    """, unsafe_allow_html=True)
    role = st.radio("", ["Talent", "Employer"], horizontal=True,
                    index=0 if st.session_state.user_role == "talent" else 1,
                    label_visibility="collapsed")
    st.session_state.user_role = role.lower()

    st.markdown("<div style='margin:14px 0 6px;'></div>", unsafe_allow_html=True)

    # Wallet
    st.markdown("""
    <div style='font-size:10px;color:#2a4a34;letter-spacing:.1em;
                text-transform:uppercase;padding:0 4px 6px;'>Demo Wallet</div>
    """, unsafe_allow_html=True)

    if not st.session_state.wallet_connected:
        if st.button("🔗 Connect Wallet", use_container_width=True):
            st.session_state.wallet_connected = True
            st.rerun()
    else:
        st.markdown(f"""
        <div style='background:rgba(29,158,117,.12);border:1px solid rgba(29,158,117,.25);
                    border-radius:10px;padding:10px 12px;font-size:11px;'>
          <div style='color:#2a4a34;margin-bottom:3px;font-size:10px;letter-spacing:.05em;'>CONNECTED</div>
          <div style='font-family:DM Mono,monospace;color:#4de8b4;word-break:break-all;'>
            {st.session_state.wallet[:10]}...{st.session_state.wallet[-6:]}
          </div>
          <div style='color:#1D9E75;font-size:10px;margin-top:4px;'>● Polygon Amoy</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='margin:14px 0;'></div>", unsafe_allow_html=True)
    st.markdown("""<hr style='border:none;border-top:1px solid rgba(29,158,117,.12);margin:0;'>""", unsafe_allow_html=True)
    st.markdown("<div style='margin:10px 0 4px;'></div>", unsafe_allow_html=True)

    # Reset
    if st.button("🔄 Reset Demo Data", use_container_width=True):
        from data.seed_data import seed_database
        seed_database()
        st.success("Data reset!")
        st.rerun()

    st.markdown("""
    <div style='margin-top:20px;padding:12px;background:rgba(29,158,117,.06);
                border-radius:10px;border:1px solid rgba(29,158,117,.12);'>
      <div style='font-size:10px;color:#2a4a34;letter-spacing:.08em;margin-bottom:6px;'>POWERED BY</div>
      <div style='font-size:11px;color:#4a6a84;line-height:1.8;'>
        ⬡ Polygon Amoy Testnet<br>
        📦 IPFS / nft.storage<br>
        🤖 Rule-based ML Engine<br>
        🗄️ SQLite (upgradeable)
      </div>
    </div>
    """, unsafe_allow_html=True)

# ═══════════════════════════════════════════
# PAGES
# ═══════════════════════════════════════════
page = st.navigation([
    st.Page("pages/1_Home.py",              title="Home",              icon="🏠"),
    st.Page("pages/2_Create_Profile.py",    title="Create Profile",    icon="✨"),
    st.Page("pages/3_Talent_Dashboard.py",  title="Talent Dashboard",  icon="📊"),
    st.Page("pages/4_Marketplace.py",       title="Marketplace",       icon="🔥"),
    st.Page("pages/5_Post_Job.py",          title="Post a Job",        icon="📢"),
    st.Page("pages/6_Employer_Dashboard.py",title="Employer Hub",      icon="🏢"),
    st.Page("pages/7_Analytics.py",         title="Analytics",         icon="📈"),
])
page.run()
