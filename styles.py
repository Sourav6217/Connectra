GLOBAL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@600;700;800&family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap');

/* ── ROOT ─────────────────────────────── */
html, body, [data-testid="stAppViewContainer"] {
  background: #040d1a !important;
  color: #c8d8e8;
  font-family: 'DM Sans', sans-serif;
}

/* ── SIDEBAR ─────────────────────────── */
[data-testid="stSidebar"] {
  min-width: 265px !important;
  max-width: 265px !important;
  width: 265px !important;
  background: #030b16 !important;
  border-right: 1px solid rgba(29,158,117,.15) !important;
}
[data-testid="stSidebarCollapseButton"],
[data-testid="collapsedControl"],
button[kind="header"] { display: none !important; }
[data-testid="stSidebarNav"] { display: none !important; }

/* Brand block sticky */
[data-testid="stSidebar"] [data-testid="stSidebarContent"] {
  padding-top: 0 !important;
}

/* ── SIDEBAR BUTTONS (nav items) ──────── */
[data-testid="stSidebar"] .stButton > button {
  background: transparent !important;
  border: none !important;
  border-radius: 10px !important;
  color: #4a6a84 !important;
  font-family: 'DM Sans', sans-serif !important;
  font-size: 13px !important;
  font-weight: 400 !important;
  padding: 9px 14px !important;
  margin: 1px 4px !important;
  text-align: left !important;
  width: calc(100% - 8px) !important;
  transition: all .15s !important;
  justify-content: flex-start !important;
  letter-spacing: 0.01em !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
  background: rgba(29,158,117,.08) !important;
  color: #c8d8e8 !important;
  border: none !important;
}
[data-testid="stSidebar"] .stButton > button:focus {
  box-shadow: none !important;
  border: none !important;
  outline: none !important;
}

/* ── ROLE RADIO ─────────────────────── */
[data-testid="stSidebar"] [data-testid="stRadio"] > div { gap: 4px !important; }
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

/* ── MAIN CONTENT ─────────────────────── */
.main .block-container { padding: 24px 36px 60px !important; max-width: 100% !important; }

/* ── MAIN AREA BUTTONS ─────────────────── */
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

/* ── TYPOGRAPHY ──────────────────────── */
.s-title { font-family: 'Syne', sans-serif; font-size: 20px; font-weight: 700; color: #ffffff; margin-bottom: 4px; }
.s-sub   { font-size: 13px; color: #4a6a84; margin-bottom: 18px; }
.hero-title { font-family: 'Syne', sans-serif; font-size: clamp(28px,4vw,48px); font-weight: 800; color: #fff; line-height: 1.18; margin-bottom: 16px; }
.hero-sub   { font-size: 15px; color: #4a6a84; line-height: 1.75; max-width: 560px; margin-bottom: 28px; }
.g { background: linear-gradient(90deg,#1D9E75,#4de8b4); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }

/* ── CARDS ────────────────────────────── */
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

/* ── HERO ─────────────────────────────── */
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

/* ── FORM INPUTS ──────────────────────── */
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

/* ── TABS ─────────────────────────────── */
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

/* ── METRIC PILLS ─────────────────────── */
.sp { display: inline-flex; align-items: center; gap: 5px; font-size: 12px; font-weight: 600; padding: 3px 10px; border-radius: 50px; }
.sp-h { background: rgba(29,158,117,.15); color: #4de8b4; border: 1px solid rgba(29,158,117,.3); }
.sp-m { background: rgba(239,159,39,.12); color: #f5c263; border: 1px solid rgba(239,159,39,.25); }
.sp-l { background: rgba(226,75,74,.12); color: #f08080; border: 1px solid rgba(226,75,74,.2); }

/* ── TAGS ─────────────────────────────── */
.tag { display: inline-block; font-size: 11px; padding: 3px 9px; border-radius: 6px; font-weight: 500; margin: 2px 2px; }
.tg { background: rgba(29,158,117,.14); color: #4de8b4; border: 1px solid rgba(29,158,117,.2); }
.tb { background: rgba(56,138,221,.14); color: #7ab8f5; border: 1px solid rgba(56,138,221,.2); }
.ta { background: rgba(239,159,39,.14); color: #f5c263; border: 1px solid rgba(239,159,39,.2); }
.tp { background: rgba(127,119,221,.14); color: #b3aeef; border: 1px solid rgba(127,119,221,.2); }
.tc { background: rgba(77,232,180,.08); color: #4de8b4; border: 1px solid rgba(77,232,180,.15); }
.tr { background: rgba(226,75,74,.12); color: #f08080; border: 1px solid rgba(226,75,74,.18); }
.stat-b { font-size: 12px; padding: 4px 10px; border-radius: 50px; background: rgba(29,158,117,.1); color: #1D9E75; border: 1px solid rgba(29,158,117,.2); }

/* ── RISK PILLS ───────────────────────── */
.risk-lo { display:inline-flex;align-items:center;gap:5px;font-size:11px;padding:3px 10px;border-radius:50px;background:rgba(29,158,117,.15);color:#4de8b4;border:1px solid rgba(29,158,117,.3); }
.risk-me { display:inline-flex;align-items:center;gap:5px;font-size:11px;padding:3px 10px;border-radius:50px;background:rgba(239,159,39,.12);color:#f5c263;border:1px solid rgba(239,159,39,.2); }
.risk-hi { display:inline-flex;align-items:center;gap:5px;font-size:11px;padding:3px 10px;border-radius:50px;background:rgba(226,75,74,.12);color:#f08080;border:1px solid rgba(226,75,74,.2); }

/* ── PROGRESS BARS ────────────────────── */
.bar-bg { background: rgba(29,158,117,.08); border-radius: 50px; height: 6px; overflow: hidden; }
.bar    { background: linear-gradient(90deg,#1D9E75,#4de8b4); height: 100%; border-radius: 50px; }
.bar-a  { background: linear-gradient(90deg,#EF9F27,#f5c263); height: 100%; border-radius: 50px; }
.bar-r  { background: linear-gradient(90deg,#E24B4A,#f08080); height: 100%; border-radius: 50px; }
.bar-b  { background: linear-gradient(90deg,#378ADD,#7ab8f5); height: 100%; border-radius: 50px; }

/* ── CANDIDATE ROW ────────────────────── */
.cand-row { display: flex; align-items: center; gap: 10px; padding: 10px 0; border-bottom: 1px solid rgba(29,158,117,.08); }
.cand-row:last-child { border-bottom: none; }

/* ── AVATAR ───────────────────────────── */
.av { display:flex;align-items:center;justify-content:center;border-radius:10px;font-family:'Syne',sans-serif;font-weight:700;flex-shrink:0; }
.av-g { background:rgba(29,158,117,.18);color:#4de8b4;border:1px solid rgba(29,158,117,.3); }
.av-b { background:rgba(56,138,221,.18);color:#7ab8f5;border:1px solid rgba(56,138,221,.3); }
.av-a { background:rgba(239,159,39,.18);color:#f5c263;border:1px solid rgba(239,159,39,.3); }
.av-p { background:rgba(127,119,221,.18);color:#b3aeef;border:1px solid rgba(127,119,221,.3); }

/* ── FORMULA ──────────────────────────── */
.formula { font-size: 11px; color: #2a4a34; font-family: 'DM Mono', monospace; background: rgba(29,158,117,.04); border-radius: 8px; padding: 10px 12px; border: 1px solid rgba(29,158,117,.1); line-height: 1.8; }
.hl { color: #4de8b4; }
.num{ color: #7ab8f5; }
.nft-hex { font-family: 'DM Mono', monospace; color: #4de8b4; font-size: 12px; word-break: break-all; }
hr.div { border: none; border-top: 1px solid rgba(29,158,117,.1); margin: 14px 0; }

/* ── WIZARD ───────────────────────────── */
.wiz-track { display:flex;align-items:center;gap:0;margin:20px 0 24px; }
.wiz-step  { display:flex;flex-direction:column;align-items:center;gap:6px;flex:1; }
.wiz-dot   { width:32px;height:32px;border-radius:50%;background:rgba(29,158,117,.08);border:2px solid rgba(29,158,117,.2);display:flex;align-items:center;justify-content:center;font-size:13px;font-weight:600;color:#2a4a34;font-family:'Syne',sans-serif; }
.wiz-step.active .wiz-dot { background:rgba(29,158,117,.2);border-color:#1D9E75;color:#4de8b4; }
.wiz-step.done   .wiz-dot { background:#1D9E75;border-color:#1D9E75;color:#fff; }
.wiz-line  { flex:1;height:2px;background:rgba(29,158,117,.1);margin: 0 -4px;position:relative;top:-12px; }
.wiz-line.done { background:#1D9E75; }

/* ── ANIMATIONS ───────────────────────── */
@keyframes anim-up { from{opacity:0;transform:translateY(12px)} to{opacity:1;transform:translateY(0)} }
@keyframes bounce   { 0%,100%{transform:translateY(0)} 50%{transform:translateY(-5px)} }
.anim-up { animation: anim-up .4s cubic-bezier(.22,1,.36,1) both; }
.d2 { animation-delay:.1s; }
.d3 { animation-delay:.2s; }
.d4 { animation-delay:.3s; }

/* ── EXPANDER ─────────────────────────── */
[data-testid="stExpander"] {
  background: rgba(8,20,42,.7) !important;
  border: 1px solid rgba(29,158,117,.12) !important;
  border-radius: 10px !important;
}

/* ── SCROLLBAR ────────────────────────── */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(29,158,117,.2); border-radius: 4px; }

/* ── ALERTS ───────────────────────────── */
[data-testid="stAlert"] { border-radius: 10px !important; }
</style>
"""

NAV_CSS = ""

SIDEBAR_BRAND = """
<div style="padding:16px 14px 12px;border-bottom:1px solid rgba(29,158,117,.12);
            background:#030b16;position:sticky;top:0;z-index:999;">
  <div style="display:flex;align-items:center;gap:10px;">
    <div style="width:34px;height:34px;background:linear-gradient(135deg,#1D9E75,#4de8b4);
                border-radius:9px;display:flex;align-items:center;justify-content:center;
                font-size:18px;color:#030b16;font-weight:800;flex-shrink:0;">⬡</div>
    <div>
      <div style="font-family:Syne,sans-serif;font-size:17px;font-weight:800;
                  background:linear-gradient(90deg,#1D9E75,#4de8b4);
                  -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                  line-height:1.1;">Connectra</div>
      <div style="font-size:10px;color:#1D9E75;letter-spacing:.08em;">ONCHAIN TALENT</div>
    </div>
  </div>
</div>
"""
