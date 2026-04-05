# -*- coding: utf-8 -*-
GLOBAL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@600;700;800&family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap');

/* ── ROOT ─────────────────────────────── */
html, body, [data-testid="stAppViewContainer"] {
  background: #040d1a !important;
  color: #c8d8e8;
  font-family: 'DM Sans', sans-serif;
}

/* ── FORCE SIDEBAR ALWAYS OPEN ─────────── */
[data-testid="stSidebar"] {
  min-width: 280px !important;
  max-width: 280px !important;
  width: 280px !important;
  background: #030b16 !important;
  border-right: 1px solid rgba(29,158,117,.14) !important;
}
[data-testid="stSidebarCollapseButton"],
[data-testid="collapsedControl"],
button[kind="header"] { display: none !important; }

/* Sidebar header strip (top fixed area above content) */
[data-testid="stSidebarHeader"] {
  height: 124px !important;
  min-height: 124px !important;
}

/* ── SIDEBAR: brand pinned, content scrollable ── */
[data-testid="stSidebar"] > div:first-child {
  display: flex !important;
  flex-direction: column !important;
  height: 100vh !important;
  overflow: hidden !important;
}

[data-testid="stSidebar"] [data-testid="stSidebarContent"] {
  display: flex !important;
  flex-direction: column !important;
  height: 100% !important;
  overflow: hidden !important;
  padding-top: 0 !important;
}

/* Brand block — pinned, never scrolls */
[data-testid="stSidebar"] [data-testid="stSidebarContent"] > div:first-child {
  flex-shrink: 0 !important;
  position: sticky !important;
  top: 0 !important;
  z-index: 10 !important;
  background: #030b16 !important;
}

/* Scrollable area below brand */
[data-testid="stSidebar"] [data-testid="stSidebarContent"] > div:not(:first-child) {
  flex: 1 1 auto !important;
  overflow-y: auto !important;
  overflow-x: hidden !important;
  padding-bottom: 24px !important;
}

/* Hide default sidebar nav */
[data-testid="stSidebarNav"] { display: none !important; }

/* ── SIDEBAR NAV ITEMS ──────────────────── */
[data-testid="stSidebarNav"] a {
  display: flex !important;
  align-items: center !important;
  gap: 10px !important;
  padding: 9px 14px !important;
  border-radius: 10px !important;
  font-size: 13px !important;
  color: #4a6a84 !important;
  font-family: 'DM Sans', sans-serif !important;
  text-decoration: none !important;
  transition: all .15s !important;
  margin: 2px 8px !important;
  position: relative !important;
}
[data-testid="stSidebarNav"] a:hover {
  color: #c8d8e8 !important;
  background: rgba(29,158,117,.08) !important;
}
[data-testid="stSidebarNav"] a[aria-current="page"] {
  color: #4de8b4 !important;
  background: rgba(29,158,117,.14) !important;
  font-weight: 600 !important;
}
[data-testid="stSidebarNav"] a::after {
  content: '';
  display: block;
  width: 5px; height: 9px;
  border-right: 1.5px solid currentColor;
  border-top: 1.5px solid currentColor;
  transform: rotate(45deg);
  position: absolute; right: 14px; top: 50%; margin-top: -4.5px;
  opacity: 0.4;
}
[data-testid="stSidebarNav"] a[aria-current="page"]::after { opacity: 1; }

/* ── MAIN CONTENT PADDING ───────────────── */
.main .block-container { padding: 8px 36px 60px !important; max-width: 100% !important; }

/* Keep Streamlit top header layer visible */

/* ── CENTERED NATIVE HEADER TEXT ───────────────── */
/* Native top header subtitle */
[data-testid="stHeader"] {
  position: relative !important;
}

/* Create centered title */
[data-testid="stHeader"]::after {
  content: "⬡ Connectra • Onchain • Talent Marketplace";
  
  position: absolute;
  left: 60%;
  top: 50%;
  transform: translate(-50%, -50%);
  
  font-family: 'DM Mono', monospace;
  font-size: 14px;
  font-weight: 500;
  letter-spacing: 0.12em;
  
  color: rgba(200,216,232,0.3);
  
  white-space: nowrap;
  pointer-events: none;
}


section[data-testid="stMain"],
[data-testid="stAppViewContainer"] .main {
  padding-top: 0 !important;
  margin-top: 0 !important;
}

section[data-testid="stMain"] > div,
[data-testid="stMainBlockContainer"],
[data-testid="stAppViewContainer"] .main .block-container {
  padding-top: 28px !important;
  margin-top: 0 !important;
}

/* ── TYPOGRAPHY ──────────────────────────── */
.s-title { font-family: 'Syne', sans-serif; font-size: 20px; font-weight: 700; color: #ffffff; margin-bottom: 4px; }
.s-sub   { font-size: 13px; color: #4a6a84; margin-bottom: 18px; }
.hero-title { font-family: 'Syne', sans-serif; font-size: clamp(22px,3.2vw,38px); font-weight: 800; color: #fff; line-height: 1.18; margin-bottom: 16px; }
.hero-sub   { font-size: 15px; color: #4a6a84; line-height: 1.75; max-width: 560px; margin-bottom: 28px; }
.g { background: linear-gradient(90deg,#1D9E75,#4de8b4); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }

/* ── CARDS ───────────────────────────────── */
.g-card {
  background: rgba(10,25,48,.6);
  border: 1px solid rgba(29,158,117,.15);
  border-radius: 14px;
  padding: 20px;
  margin-bottom: 14px;
  backdrop-filter: blur(4px);
}
.nft-card {
  background: linear-gradient(135deg,rgba(0,12,32,.95) 0%,rgba(10,30,18,.95) 100%);
  border: 1px solid rgba(29,158,117,.4);
  border-radius: 16px;
  padding: 20px;
  margin-bottom: 14px;
  box-shadow: 0 0 28px rgba(29,158,117,.06);
}
.job-card { background: rgba(8,20,42,.7); border: 1px solid rgba(29,158,117,.12); border-radius: 12px; padding: 16px 18px; }
.m-card { background: rgba(10,20,40,.8); border: 1px solid rgba(29,158,117,.1); border-radius: 12px; padding: 14px 12px; text-align: center; }
.m-lbl  { font-size: 11px; color: #2a4a34; letter-spacing: .06em; text-transform: uppercase; margin-bottom: 4px; }
.m-val  { font-family: 'Syne', sans-serif; font-size: 26px; font-weight: 700; color: #fff; }
.m-delta{ font-size: 10px; color: #1D9E75; margin-top: 3px; }

/* ── HERO ────────────────────────────────── */
.hero {
  background: linear-gradient(135deg,rgba(4,13,26,.98) 0%,rgba(10,25,18,.98) 100%);
  border: 1px solid rgba(29,158,117,.15);
  border-radius: 18px;
  padding: 44px 44px 36px;
  position: relative; overflow: hidden;
}
.hero::before {
  content: ''; position: absolute; top: -40px; right: -40px;
  width: 280px; height: 280px;
  background: radial-gradient(circle,rgba(29,158,117,.07) 0%,transparent 70%);
  pointer-events: none;
}

/* ── BUTTONS ─────────────────────────────── */
.stButton > button {
  background: rgba(29,158,117,.12) !important;
  border: 1px solid rgba(29,158,117,.35) !important;
  color: #4de8b4 !important;
  border-radius: 10px !important;
  font-family: 'DM Sans', sans-serif !important;
  font-size: 13px !important;
  font-weight: 500 !important;
  padding: 8px 18px !important;
  transition: all .18s !important;
}
.stButton > button:hover {
  background: rgba(29,158,117,.22) !important;
  border-color: rgba(29,158,117,.6) !important;
  color: #fff !important;
}

/* ── FORM INPUTS ─────────────────────────── */
.stTextInput > div > input,
.stTextArea > div > textarea,
.stNumberInput > div > input {
  background: rgba(10,25,48,.8) !important;
  border: 1px solid rgba(29,158,117,.2) !important;
  border-radius: 9px !important;
  color: #c8d8e8 !important;
  font-family: 'DM Sans', sans-serif !important;
}
.stTextInput > div > input:focus,
.stTextArea > div > textarea:focus {
  border-color: rgba(29,158,117,.6) !important;
  box-shadow: 0 0 0 2px rgba(29,158,117,.1) !important;
}
.stSelectbox > div > div,
.stMultiSelect > div > div {
  background: rgba(10,25,48,.8) !important;
  border: 1px solid rgba(29,158,117,.2) !important;
  border-radius: 9px !important;
  color: #c8d8e8 !important;
}
.stSlider > div { color: #4a6a84 !important; }
.stSlider [data-testid="stThumbValue"] { color: #4de8b4 !important; }

/* ── TABS ────────────────────────────────── */
.stTabs [data-testid="stTabBar"] {
  background: transparent !important;
  border-bottom: 1px solid rgba(29,158,117,.12) !important;
  gap: 4px;
}
.stTabs [data-testid="stTabBar"] button {
  background: transparent !important;
  border: none !important;
  color: #4a6a84 !important;
  font-size: 13px !important;
  font-family: 'DM Sans', sans-serif !important;
  padding: 8px 14px !important;
  border-radius: 8px 8px 0 0 !important;
  transition: all .15s !important;
}
.stTabs [data-testid="stTabBar"] button[aria-selected="true"] {
  color: #4de8b4 !important;
  border-bottom: 2px solid #1D9E75 !important;
  background: rgba(29,158,117,.06) !important;
}

/* ── METRIC / SCORE PILLS ────────────────── */
.sp { display: inline-flex; align-items: center; gap: 5px; font-size: 12px; font-weight: 600; padding: 3px 10px; border-radius: 50px; }
.sp-h { background: rgba(29,158,117,.15); color: #4de8b4; border: 1px solid rgba(29,158,117,.3); }
.sp-m { background: rgba(239,159,39,.12); color: #f5c263; border: 1px solid rgba(239,159,39,.25); }
.sp-l { background: rgba(226,75,74,.12); color: #f08080; border: 1px solid rgba(226,75,74,.2); }

/* ── TAGS ────────────────────────────────── */
.tag { display: inline-block; font-size: 11px; padding: 3px 9px; border-radius: 6px; font-weight: 500; margin: 2px 2px; }
.tg { background: rgba(29,158,117,.14); color: #4de8b4; border: 1px solid rgba(29,158,117,.2); }
.tb { background: rgba(56,138,221,.14); color: #7ab8f5; border: 1px solid rgba(56,138,221,.2); }
.ta { background: rgba(239,159,39,.14); color: #f5c263; border: 1px solid rgba(239,159,39,.2); }
.tp { background: rgba(127,119,221,.14); color: #b3aeef; border: 1px solid rgba(127,119,221,.2); }
.tc { background: rgba(77,232,180,.08); color: #4de8b4; border: 1px solid rgba(77,232,180,.15); }
.tr { background: rgba(226,75,74,.12); color: #f08080; border: 1px solid rgba(226,75,74,.18); }
.stat-b { font-size: 12px; padding: 4px 10px; border-radius: 50px; background: rgba(29,158,117,.1); color: #1D9E75; border: 1px solid rgba(29,158,117,.2); }

/* ── RISK PILLS ──────────────────────────── */
.risk-lo { display:inline-flex;align-items:center;gap:5px;font-size:11px;padding:3px 10px;border-radius:50px;background:rgba(29,158,117,.15);color:#4de8b4;border:1px solid rgba(29,158,117,.3); }
.risk-me { display:inline-flex;align-items:center;gap:5px;font-size:11px;padding:3px 10px;border-radius:50px;background:rgba(239,159,39,.12);color:#f5c263;border:1px solid rgba(239,159,39,.2); }
.risk-hi { display:inline-flex;align-items:center;gap:5px;font-size:11px;padding:3px 10px;border-radius:50px;background:rgba(226,75,74,.12);color:#f08080;border:1px solid rgba(226,75,74,.2); }

/* ── PROGRESS BARS ───────────────────────── */
.bar-bg { background: rgba(29,158,117,.08); border-radius: 50px; height: 6px; overflow: hidden; }
.bar    { background: linear-gradient(90deg,#1D9E75,#4de8b4); height: 100%; border-radius: 50px; transition: width .7s cubic-bezier(.22,1,.36,1); }
.bar-a  { background: linear-gradient(90deg,#EF9F27,#f5c263); height: 100%; border-radius: 50px; }
.bar-r  { background: linear-gradient(90deg,#E24B4A,#f08080); height: 100%; border-radius: 50px; }
.bar-b  { background: linear-gradient(90deg,#378ADD,#7ab8f5); height: 100%; border-radius: 50px; }

/* ── CANDIDATE ROW ───────────────────────── */
.cand-row { display: flex; align-items: center; gap: 10px; padding: 10px 0; border-bottom: 1px solid rgba(29,158,117,.08); }
.cand-row:last-child { border-bottom: none; }

/* ── AVATAR ──────────────────────────────── */
.av { display:flex;align-items:center;justify-content:center;border-radius:10px;font-family:'Syne',sans-serif;font-weight:700;flex-shrink:0; }
.av-g { background:rgba(29,158,117,.18);color:#4de8b4;border:1px solid rgba(29,158,117,.3); }
.av-b { background:rgba(56,138,221,.18);color:#7ab8f5;border:1px solid rgba(56,138,221,.3); }
.av-a { background:rgba(239,159,39,.18);color:#f5c263;border:1px solid rgba(239,159,39,.3); }
.av-p { background:rgba(127,119,221,.18);color:#b3aeef;border:1px solid rgba(127,119,221,.3); }

/* ── FORMULA ─────────────────────────────── */
.formula { font-size: 11px; color: #2a4a34; font-family: 'DM Mono', monospace; background: rgba(29,158,117,.04); border-radius: 8px; padding: 10px 12px; border: 1px solid rgba(29,158,117,.1); line-height: 1.8; }
.hl { color: #4de8b4; }
.num{ color: #7ab8f5; }

/* ── NFT HEX ─────────────────────────────── */
.nft-hex { font-family: 'DM Mono', monospace; color: #4de8b4; font-size: 12px; word-break: break-all; }

/* ── DIVIDER ─────────────────────────────── */
hr.div { border: none; border-top: 1px solid rgba(29,158,117,.1); margin: 14px 0; }

/* ── WIZARD ──────────────────────────────── */
.wiz-track { display:flex;align-items:center;gap:0;margin:20px 0 24px; }
.wiz-step  { display:flex;flex-direction:column;align-items:center;gap:6px;flex:1; }
.wiz-dot   { width:32px;height:32px;border-radius:50%;background:rgba(29,158,117,.08);border:2px solid rgba(29,158,117,.2);display:flex;align-items:center;justify-content:center;font-size:13px;font-weight:600;color:#2a4a34;font-family:'Syne',sans-serif; }
.wiz-step.active .wiz-dot { background:rgba(29,158,117,.2);border-color:#1D9E75;color:#4de8b4; }
.wiz-step.done   .wiz-dot { background:#1D9E75;border-color:#1D9E75;color:#fff; }
.wiz-line  { flex:1;height:2px;background:rgba(29,158,117,.1);margin: 0 -4px;position:relative;top:-12px; }
.wiz-line.done { background:#1D9E75; }

/* ── ANIMATIONS ──────────────────────────── */
@keyframes anim-up { from{opacity:0;transform:translateY(12px)} to{opacity:1;transform:translateY(0)} }
@keyframes bounce   { 0%,100%{transform:translateY(0)} 50%{transform:translateY(-5px)} }
.anim-up { animation: anim-up .4s cubic-bezier(.22,1,.36,1) both; }
.d2 { animation-delay:.1s; }
.d3 { animation-delay:.2s; }
.d4 { animation-delay:.3s; }

/* ── EXPANDER ────────────────────────────── */
[data-testid="stExpander"] {
  background: rgba(8,20,42,.7) !important;
  border: 1px solid rgba(29,158,117,.12) !important;
  border-radius: 10px !important;
}

/* ── SCROLLBAR ───────────────────────────── */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(29,158,117,.2); border-radius: 4px; }

/* ── SUCCESS/INFO/ERROR MSGS ─────────────── */
[data-testid="stAlert"] { border-radius: 10px !important; }

/* ── Nav decorative row (icon+label+arrow visual) hidden behind button ── */
.snav-btn, .snav-btn-active {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 9px 14px;
  margin: 2px 8px 0 8px;
  border-radius: 10px 10px 0 0;
  font-size: 13px;
  font-family: 'DM Sans', sans-serif;
  pointer-events: none;
  position: relative;
}
.snav-btn { color: #4a6a84; background: transparent; }
.snav-btn-active { color: #4de8b4; background: rgba(29,158,117,.13);
  border: 1px solid rgba(29,158,117,.25); border-bottom: none; font-weight: 600; }
.snav-icon { display: flex; align-items: center; flex-shrink: 0; opacity: 0.75; }
.snav-btn-active .snav-icon { opacity: 1; }
.snav-label { flex: 1; }
.snav-arrow { display: flex; align-items: center; opacity: 0.35; }
.snav-btn-active .snav-arrow { opacity: 0.9; }

/* ── Sidebar nav buttons: transparent overlay, sized to cover the snav div ── */
[data-testid="stSidebar"] .stButton > button {
  background: transparent !important;
  border: none !important;
  color: transparent !important;
  padding: 0 !important;
  margin-top: -39px !important;
  height: 39px !important;
  width: 100% !important;
  cursor: pointer !important;
  border-radius: 10px !important;
  box-shadow: none !important;
  font-size: 1px !important;
  position: relative !important;
  z-index: 5 !important;
  display: block !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
  background: rgba(29,158,117,.07) !important;
  border: none !important;
}
[data-testid="stSidebar"] .stButton > button:focus {
  box-shadow: none !important; outline: none !important; border: none !important;
}
[data-testid="stSidebar"] .stButton > button:active {
  background: rgba(29,158,117,.15) !important;
}

/* ── Role radio toggle ── */
[data-testid="stSidebar"] [data-testid="stRadio"] > div { gap: 6px !important; }
[data-testid="stSidebar"] [data-testid="stRadio"] label {
  font-size: 13px !important;
  color: #4a6a84 !important;
  padding: 5px 14px !important;
  border-radius: 8px !important;
  background: rgba(29,158,117,.05) !important;
  border: 1px solid rgba(29,158,117,.12) !important;
  cursor: pointer !important;
}
[data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) {
  color: #4de8b4 !important;
  background: rgba(29,158,117,.15) !important;
  border-color: rgba(29,158,117,.4) !important;
  font-weight: 600 !important;
}

/* ── Wallet/Reset/Connect buttons: restore normal styling ── */
[data-testid="stSidebar"] .stButton > button[kind="secondary"],
[data-testid="stSidebar"] div:has(> .stButton > button#connect_wallet) .stButton > button,
[data-testid="stSidebar"] div:has(> .stButton > button#reset_data) .stButton > button {
  margin-top: 0 !important;
  height: auto !important;
  color: #4de8b4 !important;
  font-size: 13px !important;
  padding: 8px 18px !important;
  background: rgba(29,158,117,.12) !important;
  border: 1px solid rgba(29,158,117,.35) !important;
  display: block !important;
  z-index: 1 !important;
}

/* ── Back navigation button ─────────────────────────────── */
button[data-testid="baseButton-secondary"][kind="secondary"]:has(+ *),
div:has(> button[key="_back_btn"]) .stButton > button,
.stButton > button[kind="secondary"] {
  background: transparent !important;
  border: 1px solid rgba(29,158,117,.2) !important;
  color: #4a6a84 !important;
  font-size: 12px !important;
  padding: 5px 14px !important;
  border-radius: 8px !important;
  margin-bottom: 12px !important;
}
.stButton > button[kind="secondary"]:hover {
  background: rgba(29,158,117,.06) !important;
  color: #c8d8e8 !important;
  border-color: rgba(29,158,117,.4) !important;
}

/* ── Fixed top-left logo ─────────────────────────────── */
#connectra-top-logo {
  position: fixed;
  top: 0;
  left: 0;
  z-index: 9999;
  width: 280px;
  height: 124px;
  background: transparent;
  border-bottom: none;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0;
  pointer-events: none;
  box-shadow: none;
}
#connectra-top-logo img {
  width: 104px;
  height: 104px;
  border-radius: 14px;
  object-fit: cover;
  box-shadow: 0 0 20px rgba(77,232,180,.32);
  flex-shrink: 0;
}
#connectra-top-logo .logo-text {
  font-family: 'Syne', sans-serif;
  font-size: 16px;
  font-weight: 800;
  background: linear-gradient(90deg,#1D9E75,#4de8b4);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  line-height: 1.1;
}
#connectra-top-logo .logo-sub {
  font-size: 9px;
  color: #1D9E75;
  letter-spacing: .1em;
}
/* Fine-tuned top gap for all pages */
.main .block-container { padding-top: 0 !important; }

/* Remove extra top margin on first rendered block */
[data-testid="stMain"] [data-testid="stMainBlockContainer"] > div:first-child {
  margin-top: 0 !important;
  padding-top: 0 !important;
}

/* ── Mode slider toggle ──────────────────────────────── */
.mode-slider-wrap {
  padding: 6px 14px 10px;
}
.mode-slider-track {
  position: relative;
  display: flex;
  align-items: center;
  width: 100%;
  height: 40px;
  background: rgba(4,13,26,.7);
  border: 1px solid rgba(29,158,117,.2);
  border-radius: 12px;
  overflow: hidden;
  cursor: pointer;
  user-select: none;
}
.mode-slider-thumb {
  position: absolute;
  top: 3px;
  bottom: 3px;
  width: calc(50% - 4px);
  background: linear-gradient(135deg, #1D9E75, #4de8b4);
  border-radius: 9px;
  transition: left 0.28s cubic-bezier(.4,0,.2,1);
  box-shadow: 0 2px 10px rgba(29,158,117,.4);
  z-index: 0;
}
.mode-slider-thumb.talent  { left: 3px; }
.mode-slider-thumb.employer { left: calc(50% + 1px); }
.mode-slider-option {
  position: relative;
  z-index: 1;
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  font-size: 12px;
  font-weight: 600;
  font-family: 'DM Sans', sans-serif;
  letter-spacing: .03em;
  transition: color .2s;
  height: 100%;
}
.mode-slider-option.active  { color: #030b16; }
.mode-slider-option.inactive { color: #4a6a84; }

</style>
"""

# Alias so app.py can import NAV_CSS separately if needed (kept for compatibility)
NAV_CSS = ""   # now merged into GLOBAL_CSS above

SIDEBAR_BRAND = """
<div style='height:62px;flex-shrink:0;background:#030b16;border-bottom:1px solid rgba(29,158,117,.18);'></div>
"""


