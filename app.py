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
    "prev_page":        None,
    "wiz_step":         1,
    "wiz_data":         {},
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

def go(page_key: str):
    st.session_state.prev_page = st.session_state.current_page
    st.session_state.current_page = page_key
    st.rerun()

# ── SVG icons ─────────────────────────────────────────────────────────────────
ICO = {
    "home":      '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>',
    "profile":   '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>',
    "dashboard": '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></svg>',
    "market":    '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="7" width="20" height="14" rx="2"/><path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/></svg>',
    "test":      '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M9 11l3 3L22 4"/><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/></svg>',
    "postjob":   '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="16"/><line x1="8" y1="12" x2="16" y2="12"/></svg>',
    "employer":  '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="3" width="20" height="14" rx="2"/><line x1="8" y1="21" x2="16" y2="21"/><line x1="12" y1="17" x2="12" y2="21"/></svg>',
    "analytics": '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>',
    "chevron":   '<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 18 15 12 9 6"/></svg>',
    "back":      '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="15 18 9 12 15 6"/></svg>',
}

def nav_btn(page_key: str, label: str, icon_key: str):
    """Single real st.button styled as a nav item via CSS classes."""
    active = st.session_state.current_page == page_key
    icon   = ICO.get(icon_key, "")
    chev   = ICO["chevron"]
    cls    = "nav-active" if active else "nav-item"
    # The label inside the button includes icon + text + chevron via HTML
    btn_label = f"{icon} {label} {chev}"
    # Render button — CSS handles all styling
    if st.button(btn_label, key=f"nav_{page_key}", use_container_width=True):
        go(page_key)

# ══════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════
with st.sidebar:
    # ── PINNED brand (only this is sticky via CSS) ────────────────────
    st.markdown(SIDEBAR_BRAND, unsafe_allow_html=True)

    # Everything below scrolls normally
    st.markdown("<div style='height:6px;'></div>", unsafe_allow_html=True)
    nav_btn("home", "Home", "home")

    # ── Role toggle ───────────────────────────────────────────────────
    st.markdown("""<div style='font-size:10px;color:#2a4a34;letter-spacing:.1em;
        text-transform:uppercase;padding:14px 4px 4px;'>Mode</div>""",
        unsafe_allow_html=True)

    prev_role = st.session_state.user_role
    role = st.radio("", ["Talent", "Employer"], horizontal=True,
                    index=0 if prev_role == "talent" else 1,
                    label_visibility="collapsed", key="role_radio")
    new_role = role.lower()
    if new_role != prev_role:
        st.session_state.user_role = new_role
        st.session_state.current_page = "dashboard" if new_role == "talent" else "postjob"
        st.rerun()

    st.markdown("<div style='height:4px;'></div>", unsafe_allow_html=True)

    # ── Role-specific pages ───────────────────────────────────────────
    if st.session_state.user_role == "talent":
        nav_btn("profile",   "Create Profile",   "profile")
        nav_btn("dashboard", "Talent Dashboard", "dashboard")
        nav_btn("market",    "Marketplace",      "market")
        nav_btn("skilltest", "Skill Tests",      "test")
    else:
        nav_btn("postjob",  "Post a Job",   "postjob")
        nav_btn("employer", "Employer Hub", "employer")

    # ── Analytics always at bottom ────────────────────────────────────
    st.markdown("<hr style='border:none;border-top:1px solid rgba(29,158,117,.1);margin:8px 0;'>",
                unsafe_allow_html=True)
    nav_btn("analytics", "Analytics", "analytics")

    # ── Wallet & utility ──────────────────────────────────────────────
    st.markdown("<hr style='border:none;border-top:1px solid rgba(29,158,117,.1);margin:8px 0;'>",
                unsafe_allow_html=True)
    st.markdown("""<div style='font-size:10px;color:#2a4a34;letter-spacing:.1em;
        text-transform:uppercase;padding:0 4px 4px;'>Demo Wallet</div>""",
        unsafe_allow_html=True)

    if not st.session_state.wallet_connected:
        if st.button("Connect Wallet", use_container_width=True, key="connect_wallet"):
            st.session_state.wallet_connected = True
            st.rerun()
    else:
        w = st.session_state.wallet
        st.markdown(f"""
<div style='background:rgba(29,158,117,.1);border:1px solid rgba(29,158,117,.22);
            border-radius:10px;padding:10px 12px;font-size:11px;margin:2px 0;'>
  <div style='color:#2a4a34;font-size:10px;letter-spacing:.05em;'>CONNECTED</div>
  <div style='font-family:DM Mono,monospace;color:#4de8b4;word-break:break-all;font-size:11px;margin-top:3px;'>
    {w[:10]}...{w[-6:]}
  </div>
  <div style='color:#1D9E75;font-size:10px;margin-top:4px;display:flex;align-items:center;gap:4px;'>
    <svg width='7' height='7' viewBox='0 0 8 8'><circle cx='4' cy='4' r='4' fill='#1D9E75'/></svg>
    Polygon Amoy
  </div>
</div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:6px;'></div>", unsafe_allow_html=True)
    if st.button("Reset Demo Data", use_container_width=True, key="reset_data"):
        from data.seed_data import seed_database
        seed_database()
        st.success("Reset!")
        st.rerun()

    st.markdown("""
<div style='margin:10px 0 0;padding:12px;background:rgba(29,158,117,.05);
            border-radius:10px;border:1px solid rgba(29,158,117,.1);'>
  <div style='font-size:10px;color:#2a4a34;letter-spacing:.08em;margin-bottom:8px;'>POWERED BY</div>
  <div style='font-size:11px;color:#4a6a84;line-height:2.1;'>
    <div style='display:flex;align-items:center;gap:6px;'>
      <svg width='11' height='11' viewBox='0 0 24 24' fill='none' stroke='#1D9E75' stroke-width='2'><polygon points='12 2 22 8.5 22 15.5 12 22 2 15.5 2 8.5 12 2'/></svg>
      Polygon Amoy Testnet
    </div>
    <div style='display:flex;align-items:center;gap:6px;'>
      <svg width='11' height='11' viewBox='0 0 24 24' fill='none' stroke='#378ADD' stroke-width='2'><path d='M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z'/></svg>
      IPFS / nft.storage
    </div>
    <div style='display:flex;align-items:center;gap:6px;'>
      <svg width='11' height='11' viewBox='0 0 24 24' fill='none' stroke='#7F77DD' stroke-width='2'><circle cx='12' cy='12' r='10'/><line x1='2' y1='12' x2='22' y2='12'/><path d='M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z'/></svg>
      Rule-based ML Engine
    </div>
    <div style='display:flex;align-items:center;gap:6px;'>
      <svg width='11' height='11' viewBox='0 0 24 24' fill='none' stroke='#4a6a84' stroke-width='2'><ellipse cx='12' cy='5' rx='9' ry='3'/><path d='M21 12c0 1.66-4 3-9 3s-9-1.34-9-3'/><path d='M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5'/></svg>
      SQLite (upgradeable)
    </div>
  </div>
</div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════
# PAGE ROUTING
# ══════════════════════════════════════════════════════════════════════
page = st.session_state.current_page

# ── Back button helper (rendered at top of main area when applicable) ─
BACK_PAGES = {
    "profile":   ("home",      "Home"),
    "dashboard": ("home",      "Home"),
    "market":    ("dashboard", "Talent Dashboard"),
    "skilltest": ("dashboard", "Talent Dashboard"),
    "postjob":   ("home",      "Home"),
    "employer":  ("postjob",   "Post a Job"),
    "analytics": ("home",      "Home"),
}
if page in BACK_PAGES:
    back_target, back_label = BACK_PAGES[page]
    # Use prev_page if available for smarter back navigation
    if st.session_state.prev_page and st.session_state.prev_page != page:
        back_target = st.session_state.prev_page
        # Get label for prev_page
        PAGE_LABELS = {
            "home":"Home","profile":"Create Profile","dashboard":"Talent Dashboard",
            "market":"Marketplace","skilltest":"Skill Tests","postjob":"Post a Job",
            "employer":"Employer Hub","analytics":"Analytics"
        }
        back_label = PAGE_LABELS.get(back_target, "Back")
    back_svg = ICO["back"]
    if st.button(f"{back_svg} {back_label}", key="back_btn"):
        go(back_target)

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
filename = PAGE_MAP.get(page, "1_Home.py")
exec(open(ROOT / "pages" / filename).read())
