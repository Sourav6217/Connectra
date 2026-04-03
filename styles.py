GLOBAL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=DM+Mono:wght@400;500&display=swap');

/* ══ BASE ══════════════════════════════════ */
html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }
.stApp { background: #0b0f1a !important; }
.block-container {
    padding-top: 2rem !important;
    padding-bottom: 3rem !important;
    max-width: 1160px !important;
}
#MainMenu, footer { visibility: hidden; }
header { visibility: hidden; height: 0 !important; }

/* ══ NUCLEAR SIDEBAR LOCK ═══════════════════ */
[data-testid="stSidebar"] {
    position: fixed !important;
    top: 0 !important; left: 0 !important;
    height: 100vh !important;
    width: 260px !important;
    min-width: 260px !important;
    max-width: 260px !important;
    z-index: 9999 !important;
    transform: translateX(0px) !important;
    visibility: visible !important;
    background: #080c17 !important;
    border-right: 1px solid rgba(255,255,255,.06) !important;
    transition: none !important;
    overflow: hidden !important;
}
[data-testid="stSidebar"] > div:first-child {
    width: 260px !important;
    background: transparent !important;
    padding: 0 !important;
}
[data-testid="stSidebarContent"] {
    padding: 0 !important;
    overflow-y: auto !important;
    overflow-x: hidden !important;
    height: 100vh !important;
}
/* Kill every collapse control */
[data-testid="stSidebarCollapsedControl"],
[data-testid="collapsedControl"],
button[data-testid="baseButton-headerNoPadding"],
button[aria-label="Close sidebar"],
button[aria-label="Open sidebar"],
.st-emotion-cache-zq5wmm { display: none !important; visibility: hidden !important; }
/* Compensate main area */
.stMainBlockContainer { padding-left: 280px !important; }
section.main > div.stMainBlockContainer { margin-left: 0 !important; }

/* ══ SIDEBAR INNER STYLES ═════════════════ */
/* Hide default nav completely */
[data-testid="stSidebarNav"] { display: none !important; }

/* ── Branding ── */
.sb-brand {
    padding: 24px 20px 20px;
    border-bottom: 1px solid rgba(255,255,255,.05);
    margin-bottom: 6px;
    position: sticky; top: 0; z-index: 10;
    background: #080c17;
}
.sb-logo-row {
    display: flex; align-items: center; gap: 10px; margin-bottom: 2px;
}
.sb-hex {
    width: 32px; height: 32px;
    background: linear-gradient(135deg, #1D9E75, #0d7a5a);
    border-radius: 8px;
    display: flex; align-items: center; justify-content: center;
    font-size: 16px; color: #fff; flex-shrink: 0;
}
.sb-name {
    font-size: 17px; font-weight: 700; color: #fff;
    letter-spacing: -0.3px;
    font-family: 'Inter', sans-serif;
}
.sb-sub {
    font-size: 10px; color: #3a4a5c;
    letter-spacing: .06em; text-transform: uppercase;
    margin-left: 42px;
}

/* ── Nav Section Label ── */
.sb-section {
    font-size: 10px; font-weight: 600;
    color: #2a3a4a; letter-spacing: .12em;
    text-transform: uppercase;
    padding: 16px 20px 6px;
}

/* ── Nav Items ── */
.sb-nav-item {
    display: flex; align-items: center; gap: 12px;
    padding: 10px 20px; margin: 1px 8px;
    border-radius: 8px; cursor: pointer;
    transition: background .15s, color .15s;
    text-decoration: none;
    color: #5a7088 !important;
}
.sb-nav-item:hover {
    background: rgba(255,255,255,.05);
    color: #c8d8e8 !important;
    text-decoration: none;
}
.sb-nav-item.active {
    background: rgba(29,158,117,.15);
    color: #4de8b4 !important;
    border: 1px solid rgba(29,158,117,.2);
}
.sb-nav-item.active .sb-icon svg { stroke: #4de8b4 !important; }
.sb-nav-icon {
    width: 18px; height: 18px; flex-shrink: 0;
    display: flex; align-items: center; justify-content: center;
}
.sb-nav-icon svg {
    stroke: currentColor; fill: none;
    stroke-width: 1.5; stroke-linecap: round; stroke-linejoin: round;
}
.sb-nav-label { flex: 1; font-size: 13px; font-weight: 500; }
.sb-chevron {
    width: 14px; height: 14px; opacity: .35;
    display: flex; align-items: center; justify-content: center; flex-shrink: 0;
}
.sb-chevron svg {
    stroke: currentColor; fill: none;
    stroke-width: 1.5; stroke-linecap: round;
}

/* ── Sidebar bottom info ── */
.sb-footer {
    position: absolute; bottom: 0; left: 0; right: 0;
    padding: 16px 20px;
    border-top: 1px solid rgba(255,255,255,.05);
    background: #080c17;
}
.sb-footer-item {
    font-size: 10px; color: #2a3a4a;
    display: flex; align-items: center; gap: 6px;
    margin-bottom: 4px;
}
.sb-footer-dot {
    width: 6px; height: 6px; border-radius: 50%;
    background: #1D9E75; flex-shrink: 0;
}

/* ══ ANIMATIONS ════════════════════════════ */
@keyframes fadeUp { from{opacity:0;transform:translateY(18px)} to{opacity:1;transform:none} }
@keyframes fadeIn { from{opacity:0} to{opacity:1} }
@keyframes fillBar { from{width:0} to{width:var(--w,100%)} }
@keyframes pulse { 0%,100%{box-shadow:0 0 0 0 rgba(29,158,117,.3)} 50%{box-shadow:0 0 0 8px rgba(29,158,117,0)} }
@keyframes spin { to{transform:rotate(360deg)} }

.aup { animation: fadeUp .5s ease both; }
.d1{animation-delay:.07s} .d2{animation-delay:.14s}
.d3{animation-delay:.21s} .d4{animation-delay:.28s}

/* ══ METRIC CARDS ══════════════════════════ */
.kpi {
    background: #0e1525;
    border: 1px solid rgba(255,255,255,.07);
    border-radius: 14px; padding: 20px;
    transition: border-color .2s, transform .2s;
    animation: fadeUp .45s ease both;
    position: relative; overflow: hidden;
}
.kpi::after {
    content:''; position:absolute; top:0; right:0;
    width:60px; height:60px; border-radius:0 14px 0 60px;
    background: rgba(29,158,117,.04);
}
.kpi:hover { border-color: rgba(29,158,117,.3); transform: translateY(-2px); }
.kpi-icon { font-size:18px; margin-bottom:10px; opacity:.7; }
.kpi-val {
    font-size:26px; font-weight:700; color:#fff;
    letter-spacing:-0.5px; line-height:1;
    font-family:'Inter',sans-serif;
}
.kpi-lbl { font-size:12px; color:#3a4a5c; margin-top:4px; font-weight:500; }
.kpi-delta { font-size:11px; color:#1D9E75; margin-top:6px; font-weight:500; }
.kpi-delta.neg { color:#e55; }

/* ══ GLASS CARDS ════════════════════════════ */
.gc {
    background: #0e1525;
    border: 1px solid rgba(255,255,255,.07);
    border-radius: 14px; padding: 22px;
    animation: fadeUp .5s ease both;
    transition: border-color .2s;
}
.gc:hover { border-color: rgba(255,255,255,.12); }
.gc-accent { border-left: 2px solid #1D9E75; }

/* ══ PAGE HEADERS ══════════════════════════ */
.ph {
    margin-bottom: 24px;
    padding-bottom: 18px;
    border-bottom: 1px solid rgba(255,255,255,.05);
}
.ph-title {
    font-size: 24px; font-weight: 700; color: #fff;
    letter-spacing: -0.4px; margin-bottom: 4px;
}
.ph-sub { font-size: 13px; color: #3a4a5c; }

/* ══ SECTION TITLES ═════════════════════════ */
.st2 { font-size: 15px; font-weight: 600; color: #fff; margin-bottom: 3px; }
.st3 { font-size: 13px; color: #3a4a5c; margin-bottom: 16px; }

/* ══ TAGS ════════════════════════════════════ */
.tag { display:inline-block; padding:3px 10px; border-radius:6px; font-size:11px; font-weight:600; margin:2px; }
.tg  { background:rgba(29,158,117,.14); color:#4de8b4; border:1px solid rgba(29,158,117,.22); }
.tb  { background:rgba(56,138,221,.12); color:#7ab8f5; border:1px solid rgba(56,138,221,.22); }
.ta  { background:rgba(239,159,39,.12); color:#f5c263; border:1px solid rgba(239,159,39,.22); }
.tp  { background:rgba(127,119,221,.12); color:#b3aeef; border:1px solid rgba(127,119,221,.22); }
.tr  { background:rgba(226,75,74,.12); color:#f08080; border:1px solid rgba(226,75,74,.22); }
.tc  { background:rgba(56,189,248,.12); color:#7dd3fc; border:1px solid rgba(56,189,248,.22); }

/* ══ SCORE PILLS ════════════════════════════ */
.sp { padding:5px 14px; border-radius:6px; font-size:12px; font-weight:700; white-space:nowrap; }
.sp-h { background:rgba(29,158,117,.18); color:#4de8b4; border:1px solid rgba(29,158,117,.3); }
.sp-m { background:rgba(239,159,39,.15); color:#f5c263; border:1px solid rgba(239,159,39,.3); }
.sp-l { background:rgba(226,75,74,.12); color:#f08080; border:1px solid rgba(226,75,74,.25); }

/* ══ RISK BADGES ════════════════════════════ */
.risk-lo { background:rgba(29,158,117,.12);  color:#4de8b4; border:1px solid rgba(29,158,117,.25);  padding:4px 12px; border-radius:6px; font-size:11px; font-weight:600; display:inline-block; }
.risk-me { background:rgba(239,159,39,.12);  color:#f5c263; border:1px solid rgba(239,159,39,.25);  padding:4px 12px; border-radius:6px; font-size:11px; font-weight:600; display:inline-block; }
.risk-hi { background:rgba(226,75,74,.12);   color:#f08080; border:1px solid rgba(226,75,74,.22);   padding:4px 12px; border-radius:6px; font-size:11px; font-weight:600; display:inline-block; }

/* ══ NFT CARD ════════════════════════════════ */
.nft-card {
    background: linear-gradient(135deg, #0a2010, #0d1830);
    border: 1px solid rgba(29,158,117,.4);
    border-radius: 14px; padding: 20px; position: relative; overflow: hidden;
}
.nft-hex-bg { font-family:'DM Mono',monospace; font-size:11px; color:#1D9E75; }

/* ══ AVATAR ══════════════════════════════════ */
.av { border-radius:50%; display:flex; align-items:center; justify-content:center; font-weight:700; flex-shrink:0; font-family:'Inter',sans-serif; }
.av-g { background:rgba(29,158,117,.18); color:#4de8b4; border:1.5px solid rgba(29,158,117,.35); }
.av-b { background:rgba(56,138,221,.18); color:#7ab8f5; border:1.5px solid rgba(56,138,221,.35); }
.av-a { background:rgba(239,159,39,.18); color:#f5c263; border:1.5px solid rgba(239,159,39,.35); }
.av-p { background:rgba(127,119,221,.18); color:#b3aeef; border:1.5px solid rgba(127,119,221,.35); }

/* ══ CANDIDATE ROW ═══════════════════════════ */
.cand-row { display:flex; align-items:center; gap:12px; padding:10px 6px; border-bottom:1px solid rgba(255,255,255,.04); }
.cand-row:last-child { border-bottom:none; }
.cand-row:hover { background:rgba(255,255,255,.02); border-radius:8px; }

/* ══ FORMULA BOX ═════════════════════════════ */
.formula {
    background:#060a12; border:1px solid rgba(29,158,117,.15);
    border-left:2px solid #1D9E75; border-radius:6px;
    padding:12px 14px; font-family:'DM Mono',monospace;
    font-size:11px; color:#3a5a3a; line-height:1.9;
}
.formula .hl { color:#4de8b4; font-weight:600; }
.formula .num { color:#7ab8f5; }

/* ══ DIVIDER ══════════════════════════════════ */
.divx { border:none; border-top:1px solid rgba(255,255,255,.06); margin:16px 0; }

/* ══ STREAMLIT OVERRIDES ══════════════════════ */
.stButton > button {
    background: linear-gradient(135deg,#1D9E75,#15855f) !important;
    color: #fff !important; border: none !important;
    border-radius: 8px !important; padding: 9px 22px !important;
    font-weight: 600 !important; font-size: 13px !important;
    font-family: 'Inter', sans-serif !important;
    transition: all .2s !important; letter-spacing: .01em;
}
.stButton > button:hover { transform: translateY(-1px) !important; box-shadow: 0 6px 16px rgba(29,158,117,.35) !important; }
.stButton > button[kind="secondary"] {
    background: rgba(255,255,255,.05) !important;
    border: 1px solid rgba(255,255,255,.1) !important;
    color: #8ba8c4 !important;
}
.stButton > button[kind="secondary"]:hover { border-color: rgba(29,158,117,.4) !important; color: #4de8b4 !important; }
.stTextInput > div > div > input,
.stTextArea textarea, .stNumberInput input {
    background: #0e1525 !important;
    border: 1px solid rgba(255,255,255,.1) !important;
    border-radius: 8px !important; color: #c8d8e8 !important;
    font-family: 'Inter', sans-serif !important;
}
.stTextInput > div > div > input:focus, .stTextArea textarea:focus {
    border-color: rgba(29,158,117,.5) !important;
    box-shadow: 0 0 0 2px rgba(29,158,117,.1) !important;
}
.stSelectbox [data-baseweb="select"] > div,
.stMultiSelect [data-baseweb="select"] > div {
    background: #0e1525 !important;
    border: 1px solid rgba(255,255,255,.1) !important;
    border-radius: 8px !important;
}
[data-baseweb="popover"] [role="option"] { background: #0e1525 !important; color: #c8d8e8 !important; }
[data-baseweb="popover"] [role="option"]:hover { background: rgba(29,158,117,.12) !important; }
[data-baseweb="popover"] [role="option"][aria-selected="true"] { background: rgba(29,158,117,.2) !important; color: #4de8b4 !important; }
[data-baseweb="tag"] { background:rgba(29,158,117,.2) !important; color:#4de8b4 !important; border:1px solid rgba(29,158,117,.3) !important; border-radius:6px !important; }
[data-baseweb="slider"] [role="slider"] { background:#1D9E75 !important; border:none !important; }
.stTabs [data-baseweb="tab-list"] {
    background: rgba(14,21,37,.8) !important;
    border: 1px solid rgba(255,255,255,.06) !important;
    border-radius: 10px !important; padding: 3px !important; gap: 2px;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important; color: #3a4a5c !important;
    border-radius: 8px !important; font-weight: 500 !important;
    font-size: 13px !important; border: none !important; padding: 7px 16px !important;
    transition: all .15s !important;
}
.stTabs [data-baseweb="tab"][aria-selected="true"] {
    background: rgba(29,158,117,.18) !important; color: #4de8b4 !important;
}
[data-testid="stMetric"] {
    background: #0e1525 !important; border: 1px solid rgba(255,255,255,.07) !important;
    border-radius: 12px !important; padding: 14px !important;
}
[data-testid="stMetricValue"] { color: #fff !important; }
[data-testid="stMetricDelta"] { color: #1D9E75 !important; }
[data-testid="stMetricLabel"] { color: #3a4a5c !important; }
[data-testid="stExpander"] {
    background: #0e1525 !important;
    border: 1px solid rgba(255,255,255,.07) !important;
    border-radius: 10px !important;
}
[data-testid="stAlert"] { border-radius: 10px !important; }
</style>
"""

SIDEBAR_BRAND = ""  # Brand injected in sidebar HTML now
