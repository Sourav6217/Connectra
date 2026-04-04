import streamlit as st
import sys
import os
from pathlib import Path

# ── Ensure project root is on Python path ─────────────────────────────────────
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

# ── Bootstrap DB ───────────────────────────────────────────────────────────────
init_db()
seed_if_empty()

# ── Session defaults ───────────────────────────────────────────────────────────
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

# ── SVG icon helpers ───────────────────────────────────────────────────────────
ICONS = {
    "home":      '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>',
    "profile":   '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>',
    "dashboard": '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></svg>',
    "market":    '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="7" width="20" height="14" rx="2"/><path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/></svg>',
    "test":      '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="M9 11l3 3L22 4"/><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/></svg>',
    "postjob":   '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="16"/><line x1="8" y1="12" x2="16" y2="12"/></svg>',
    "employer":  '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="3" width="20" height="14" rx="2"/><line x1="8" y1="21" x2="16" y2="21"/><line x1="12" y1="17" x2="12" y2="21"/></svg>',
    "analytics": '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>',
    "chevron":   '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 18 15 12 9 6"/></svg>',
}

def nav_item(page_key: str, label: str, icon_key: str):
    """Render a sidebar nav button and handle click."""
    active = st.session_state.current_page == page_key
    active_class = "nav-item-active" if active else "nav-item"
    # We use a real st.button for click handling, but style it with markdown
    col_icon, col_label, col_arrow = st.columns([1, 6, 1])
    clicked = st.button(
        f"{label}",
        key=f"nav_{page_key}",
        use_container_width=True,
        help=label,
    )
    if clicked:
        st.session_state.current_page = page_key
        st.rerun()

# ── Better approach: full custom nav with st.markdown links ────────────────────
def render_nav_item(page_key: str, label: str, icon_key: str):
    active = st.session_state.current_page == page_key
    cls = "snav-active" if active else "snav-item"
    icon_svg = ICONS.get(icon_key, "")
    chevron  = ICONS["chevron"]
    btn_key  = f"navbtn_{page_key}"
    st.markdown(f"""
<div class='{cls}' id='nav_{page_key}'>
  <span class='snav-icon'>{icon_svg}</span>
  <span class='snav-label'>{label}</span>
  <span class='snav-arrow'>{chevron}</span>
</div>
""", unsafe_allow_html=True)
    # Invisible button overlay for click (zero-width space label)
    if st.button("\u200b", key=btn_key, use_container_width=True):
        st.session_state.current_page = page_key
        st.rerun()

# ══════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════
with st.sidebar:
    # ── Pinned brand ──────────────────────────────────────────────────
    st.markdown(SIDEBAR_BRAND, unsafe_allow_html=True)

    # ── HOME (always visible) ─────────────────────────────────────────
    st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
    render_nav_item("home", "Home", "home")

    # ── Role toggle ───────────────────────────────────────────────────
    st.markdown("""
<div style='font-size:10px;color:#2a4a34;letter-spacing:.1em;
            text-transform:uppercase;padding:16px 14px 6px;'>Mode</div>
""", unsafe_allow_html=True)

    prev_role = st.session_state.user_role
    role = st.radio(
        "", ["Talent", "Employer"], horizontal=True,
        index=0 if st.session_state.user_role == "talent" else 1,
        label_visibility="collapsed",
        key="role_radio",
    )
    new_role = role.lower()
    if new_role != prev_role:
        st.session_state.user_role = new_role
        # Reset to role's default page on toggle
        st.session_state.current_page = "dashboard" if new_role == "talent" else "postjob"
        st.rerun()

    st.markdown("<div style='height:6px;'></div>", unsafe_allow_html=True)

    # ── Role-specific nav items ───────────────────────────────────────
    if st.session_state.user_role == "talent":
        render_nav_item("profile",   "Create Profile",   "profile")
        render_nav_item("dashboard", "Talent Dashboard", "dashboard")
        render_nav_item("market",    "Marketplace",      "market")
        render_nav_item("skilltest", "Skill Tests",      "test")
    else:
        render_nav_item("postjob",  "Post a Job",    "postjob")
        render_nav_item("employer", "Employer Hub",  "employer")

    # ── Analytics (always visible, separated) ────────────────────────
    st.markdown("<hr style='border:none;border-top:1px solid rgba(29,158,117,.1);margin:10px 8px;'>",
                unsafe_allow_html=True)
    render_nav_item("analytics", "Analytics", "analytics")

    # ── Wallet ────────────────────────────────────────────────────────
    st.markdown("<hr style='border:none;border-top:1px solid rgba(29,158,117,.1);margin:10px 8px;'>",
                unsafe_allow_html=True)
    st.markdown("""
<div style='font-size:10px;color:#2a4a34;letter-spacing:.1em;
            text-transform:uppercase;padding:0 14px 6px;'>Demo Wallet</div>
""", unsafe_allow_html=True)

    if not st.session_state.wallet_connected:
        if st.button("Connect Wallet", use_container_width=True, key="connect_wallet"):
            st.session_state.wallet_connected = True
            st.rerun()
    else:
        w = st.session_state.wallet
        st.markdown(f"""
<div style='background:rgba(29,158,117,.1);border:1px solid rgba(29,158,117,.22);
            border-radius:10px;padding:10px 12px;font-size:11px;margin:0 4px;'>
  <div style='color:#2a4a34;margin-bottom:3px;font-size:10px;letter-spacing:.05em;'>CONNECTED</div>
  <div style='font-family:DM Mono,monospace;color:#4de8b4;word-break:break-all;font-size:11px;'>
    {w[:10]}...{w[-6:]}
  </div>
  <div style='color:#1D9E75;font-size:10px;margin-top:4px;display:flex;align-items:center;gap:4px;'>
    <svg width='8' height='8' viewBox='0 0 8 8'><circle cx='4' cy='4' r='4' fill='#1D9E75'/></svg>
    Polygon Amoy
  </div>
</div>
""", unsafe_allow_html=True)

    st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
    if st.button("Reset Demo Data", use_container_width=True, key="reset_data"):
        from data.seed_data import seed_database
        seed_database()
        st.success("Reset!")
        st.rerun()

    st.markdown("""
<div style='margin:12px 4px 0;padding:12px;background:rgba(29,158,117,.05);
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


# ══════════════════════════════════════════════════════════════════════
# PAGE ROUTING  (no st.navigation — we control it via session_state)
# ══════════════════════════════════════════════════════════════════════
page = st.session_state.current_page

if page == "home":
    exec(open(ROOT / "pages" / "1_Home.py").read())
elif page == "profile":
    exec(open(ROOT / "pages" / "2_Create_Profile.py").read())
elif page == "dashboard":
    exec(open(ROOT / "pages" / "3_Talent_Dashboard.py").read())
elif page == "market":
    exec(open(ROOT / "pages" / "4_Marketplace.py").read())
elif page == "postjob":
    exec(open(ROOT / "pages" / "5_Post_Job.py").read())
elif page == "employer":
    exec(open(ROOT / "pages" / "6_Employer_Dashboard.py").read())
elif page == "analytics":
    exec(open(ROOT / "pages" / "7_Analytics.py").read())
elif page == "skilltest":
    exec(open(ROOT / "pages" / "8_Skill_Tests.py").read())
else:
    exec(open(ROOT / "pages" / "1_Home.py").read())
