GLOBAL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700;800&family=DM+Sans:ital,wght@0,300;0,400;0,500;0,600;1,400&family=DM+Mono:wght@400;500&display=swap');

/* ══════════════════════════════════════════
   BASE
══════════════════════════════════════════ */
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif !important;
}
.stApp { background: #040d1a !important; }
.block-container {
    padding-top: 1.8rem !important;
    padding-bottom: 3rem !important;
    max-width: 1140px !important;
}
#MainMenu, footer { visibility: hidden; }
header { visibility: hidden; }
/* Keep sidebar collapse/expand arrow visible */
[data-testid="collapsedControl"] { visibility: visible !important; display: flex !important; }
section[data-testid="stSidebarCollapsedControl"] { visibility: visible !important; }

/* ══════════════════════════════════════════
   SIDEBAR
══════════════════════════════════════════ */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #060f20 0%, #071a12 100%) !important;
    border-right: 1px solid rgba(29,158,117,0.18) !important;
}
[data-testid="stSidebar"] * { color: #c8d8e8 !important; }
[data-testid="stSidebarNav"] a {
    border-radius: 10px !important;
    transition: all 0.2s ease !important;
    margin: 2px 0 !important;
}
[data-testid="stSidebarNav"] a:hover {
    background: rgba(29,158,117,0.12) !important;
    padding-left: 1.3rem !important;
}
[data-testid="stSidebarNav"] a[aria-current="page"] {
    background: rgba(29,158,117,0.2) !important;
    border-left: 3px solid #1D9E75 !important;
}

/* ══════════════════════════════════════════
   ANIMATIONS
══════════════════════════════════════════ */
@keyframes fadeUp   { from{opacity:0;transform:translateY(20px)} to{opacity:1;transform:translateY(0)} }
@keyframes fadeIn   { from{opacity:0} to{opacity:1} }
@keyframes glow     { 0%,100%{box-shadow:0 0 0 0 rgba(29,158,117,.35)} 50%{box-shadow:0 0 0 10px rgba(29,158,117,0)} }
@keyframes fillBar  { from{width:0} to{width:var(--w)} }
@keyframes spin     { to{transform:rotate(360deg)} }
@keyframes bounce   { 0%,100%{transform:translateY(0)} 50%{transform:translateY(-6px)} }

.anim-up  { animation: fadeUp  .55s ease both; }
.anim-in  { animation: fadeIn  .4s  ease both; }
.d1 { animation-delay:.08s } .d2 { animation-delay:.16s }
.d3 { animation-delay:.24s } .d4 { animation-delay:.32s }
.d5 { animation-delay:.40s } .d6 { animation-delay:.48s }

/* ══════════════════════════════════════════
   METRIC CARDS
══════════════════════════════════════════ */
.m-card {
    background: linear-gradient(135deg,#0c1e3a 0%,#0a2d1e 100%);
    border: 1px solid rgba(29,158,117,.28);
    border-radius: 18px; padding: 20px 22px;
    position: relative; overflow: hidden;
    transition: transform .25s, box-shadow .25s;
    animation: fadeUp .5s ease both;
}
.m-card::before {
    content:''; position:absolute; top:-35px; right:-35px;
    width:100px; height:100px; border-radius:50%;
    background:rgba(29,158,117,.07);
}
.m-card:hover { transform:translateY(-4px); box-shadow:0 12px 30px rgba(29,158,117,.18); }
.m-lbl { font-size:11px; text-transform:uppercase; letter-spacing:.1em; color:#3d5a7a; margin-bottom:7px; }
.m-val { font-size:28px; font-weight:700; font-family:'Syne',sans-serif; color:#fff; line-height:1; }
.m-delta { font-size:12px; color:#1D9E75; margin-top:5px; }

/* ══════════════════════════════════════════
   HERO
══════════════════════════════════════════ */
.hero {
    background: linear-gradient(135deg,#051224 0%,#0a2d1e 55%,#051224 100%);
    border: 1px solid rgba(29,158,117,.22);
    border-radius: 26px; padding: 52px;
    position: relative; overflow: hidden;
    animation: fadeUp .5s ease both;
}
.hero::before {
    content:''; position:absolute; top:-100px; right:-100px;
    width:380px; height:380px; border-radius:50%;
    background:radial-gradient(circle,rgba(29,158,117,.12) 0%,transparent 70%);
}
.hero::after {
    content:''; position:absolute; bottom:-60px; left:40px;
    width:220px; height:220px; border-radius:50%;
    background:radial-gradient(circle,rgba(56,138,221,.07) 0%,transparent 70%);
}
.hero-title {
    font-family:'Syne',sans-serif; font-size:46px; font-weight:800;
    color:#fff; line-height:1.13; margin-bottom:18px; position:relative; z-index:1;
}
.hero-title .g {
    background:linear-gradient(90deg,#1D9E75,#4de8b4);
    -webkit-background-clip:text; -webkit-text-fill-color:transparent;
}
.hero-sub { font-size:17px; color:#7a9ab8; line-height:1.75; max-width:500px; margin-bottom:30px; position:relative; z-index:1; }

/* ══════════════════════════════════════════
   GLASS CARDS
══════════════════════════════════════════ */
.g-card {
    background: rgba(10,25,48,.72);
    border: 1px solid rgba(29,158,117,.18);
    border-radius: 20px; padding: 24px;
    transition: all .3s ease;
    animation: fadeUp .5s ease both;
}
.g-card:hover {
    border-color: rgba(29,158,117,.4);
    box-shadow: 0 8px 32px rgba(29,158,117,.1);
    transform: translateY(-3px);
}
.g-card-accent { border-left: 3px solid #1D9E75; }

/* ══════════════════════════════════════════
   SECTION HEADINGS
══════════════════════════════════════════ */
.s-title {
    font-family:'Syne',sans-serif; font-size:20px; font-weight:700;
    color:#fff; margin-bottom:4px;
}
.s-sub { font-size:13px; color:#4a6a84; margin-bottom:22px; }

/* ══════════════════════════════════════════
   TAGS / BADGES
══════════════════════════════════════════ */
.tag { display:inline-block; padding:4px 12px; border-radius:50px; font-size:11px;
       font-weight:600; margin:3px; text-transform:uppercase; letter-spacing:.04em; }
.tg  { background:rgba(29,158,117,.18); color:#4de8b4; border:1px solid rgba(29,158,117,.3); }
.tb  { background:rgba(56,138,221,.15); color:#7ab8f5; border:1px solid rgba(56,138,221,.3); }
.ta  { background:rgba(239,159,39,.15); color:#f5c263; border:1px solid rgba(239,159,39,.3); }
.tp  { background:rgba(127,119,221,.15); color:#b3aeef; border:1px solid rgba(127,119,221,.3); }
.tr  { background:rgba(226,75,74,.15); color:#f08080; border:1px solid rgba(226,75,74,.3); }
.tc  { background:rgba(56,189,248,.15); color:#7dd3fc; border:1px solid rgba(56,189,248,.3); }

/* ══════════════════════════════════════════
   PROGRESS BARS
══════════════════════════════════════════ */
.bar-bg  { background:rgba(255,255,255,.06); border-radius:6px; height:8px; overflow:hidden; margin:5px 0 14px; }
.bar     { height:8px; border-radius:6px; background:linear-gradient(90deg,#1D9E75,#4de8b4);
           animation:fillBar 1s ease both; animation-delay:.3s; }
.bar-b   { background:linear-gradient(90deg,#378ADD,#7ab8f5); }
.bar-a   { background:linear-gradient(90deg,#EF9F27,#f5c263); }
.bar-r   { background:linear-gradient(90deg,#E24B4A,#f08080); }

/* ══════════════════════════════════════════
   JOB CARDS
══════════════════════════════════════════ */
.job-card {
    background:rgba(10,25,48,.55); border:1px solid rgba(29,158,117,.14);
    border-radius:16px; padding:20px 22px; margin-bottom:14px;
    transition:all .25s ease; animation:fadeUp .5s ease both;
}
.job-card:hover {
    border-color:rgba(29,158,117,.45);
    background:rgba(10,25,48,.85);
    transform:translateX(5px);
}

/* ══════════════════════════════════════════
   SCORE PILLS
══════════════════════════════════════════ */
.sp { padding:6px 16px; border-radius:50px; font-size:13px; font-weight:700;
      white-space:nowrap; font-family:'Syne',sans-serif; }
.sp-h { background:rgba(29,158,117,.22); color:#4de8b4; border:1px solid rgba(29,158,117,.45); }
.sp-m { background:rgba(239,159,39,.2);  color:#f5c263; border:1px solid rgba(239,159,39,.45); }
.sp-l { background:rgba(226,75,74,.18);  color:#f08080; border:1px solid rgba(226,75,74,.35); }

/* ══════════════════════════════════════════
   RISK BADGES
══════════════════════════════════════════ */
.risk-lo { background:rgba(29,158,117,.15); color:#4de8b4; border:1px solid rgba(29,158,117,.3); padding:5px 14px; border-radius:50px; font-size:12px; font-weight:600; }
.risk-me { background:rgba(239,159,39,.15); color:#f5c263; border:1px solid rgba(239,159,39,.3); padding:5px 14px; border-radius:50px; font-size:12px; font-weight:600; }
.risk-hi { background:rgba(226,75,74,.15);  color:#f08080; border:1px solid rgba(226,75,74,.3);  padding:5px 14px; border-radius:50px; font-size:12px; font-weight:600; }

/* ══════════════════════════════════════════
   NFT CARD
══════════════════════════════════════════ */
.nft-card {
    background:linear-gradient(135deg,#0a2d20,#0c1e3a);
    border:1px solid #1D9E75; border-radius:18px; padding:22px;
    position:relative; overflow:hidden;
}
.nft-card::before {
    content:'⬡'; position:absolute; right:-14px; top:-16px;
    font-size:90px; color:rgba(29,158,117,.06);
}
.nft-hex { font-family:'DM Mono',monospace; font-size:12px; color:#1D9E75; letter-spacing:.05em; }

/* ══════════════════════════════════════════
   AVATAR
══════════════════════════════════════════ */
.av { width:50px; height:50px; border-radius:50%; display:flex; align-items:center;
      justify-content:center; font-weight:700; font-size:16px; flex-shrink:0;
      font-family:'Syne',sans-serif; }
.av-g { background:rgba(29,158,117,.2); color:#4de8b4; border:2px solid rgba(29,158,117,.45); }
.av-b { background:rgba(56,138,221,.2); color:#7ab8f5; border:2px solid rgba(56,138,221,.45); }
.av-a { background:rgba(239,159,39,.2); color:#f5c263; border:2px solid rgba(239,159,39,.45); }
.av-p { background:rgba(127,119,221,.2); color:#b3aeef; border:2px solid rgba(127,119,221,.45); }

/* ══════════════════════════════════════════
   FORMULA BOX
══════════════════════════════════════════ */
.formula {
    background:rgba(4,13,26,.9); border:1px solid rgba(29,158,117,.18);
    border-left:3px solid #1D9E75; border-radius:8px;
    padding:14px 18px; font-family:'DM Mono',monospace; font-size:12px;
    color:#4a6a84; line-height:2;
}
.formula .hl { color:#4de8b4; font-weight:600; }
.formula .num { color:#7ab8f5; }

/* ══════════════════════════════════════════
   DIVIDER
══════════════════════════════════════════ */
.div { border:none; border-top:1px solid rgba(29,158,117,.12); margin:18px 0; }

/* ══════════════════════════════════════════
   STEP CIRCLES
══════════════════════════════════════════ */
.step-n {
    width:34px; height:34px; border-radius:50%;
    background:rgba(29,158,117,.18); border:1px solid rgba(29,158,117,.5);
    display:flex; align-items:center; justify-content:center;
    font-weight:700; font-size:13px; color:#4de8b4; flex-shrink:0;
    font-family:'Syne',sans-serif;
}
.step-n.done { background:rgba(29,158,117,.35); border-color:#1D9E75; }

/* ══════════════════════════════════════════
   CANDIDATE ROW
══════════════════════════════════════════ */
.cand-row {
    display:flex; align-items:center; gap:14px; padding:12px 10px;
    border-bottom:1px solid rgba(29,158,117,.09);
    transition:background .2s;
}
.cand-row:last-child { border-bottom:none; }
.cand-row:hover { background:rgba(29,158,117,.05); border-radius:10px; }

/* ══════════════════════════════════════════
   BUTTON OVERRIDES
══════════════════════════════════════════ */
.stButton > button {
    background:linear-gradient(135deg,#1D9E75,#159060) !important;
    color:white !important; border:none !important;
    border-radius:50px !important; padding:10px 28px !important;
    font-weight:600 !important; font-family:'DM Sans',sans-serif !important;
    letter-spacing:.02em; transition:all .25s ease !important;
}
.stButton > button:hover {
    transform:translateY(-2px) !important;
    box-shadow:0 8px 20px rgba(29,158,117,.4) !important;
}
.stButton > button[kind="secondary"] {
    background:transparent !important;
    border:1px solid rgba(29,158,117,.35) !important;
    color:#4de8b4 !important;
}
.stButton > button[kind="secondary"]:hover {
    background:rgba(29,158,117,.1) !important;
    border-color:#1D9E75 !important;
}

/* ══════════════════════════════════════════
   INPUT / SELECT / SLIDER
══════════════════════════════════════════ */
.stTextInput > div > div > input,
.stTextArea textarea,
.stNumberInput input {
    background:rgba(10,25,48,.8) !important;
    border:1px solid rgba(29,158,117,.25) !important;
    border-radius:10px !important; color:#c8d8e8 !important;
    font-family:'DM Sans',sans-serif !important;
}
.stTextInput > div > div > input:focus,
.stTextArea textarea:focus {
    border-color:#1D9E75 !important;
    box-shadow:0 0 0 2px rgba(29,158,117,.2) !important;
}
.stSelectbox [data-baseweb="select"] > div,
.stMultiSelect [data-baseweb="select"] > div {
    background:rgba(10,25,48,.8) !important;
    border:1px solid rgba(29,158,117,.25) !important;
    border-radius:10px !important;
}
.stSlider [data-baseweb="slider"] [data-testid="stTickBar"] span { color:#4a6a84 !important; }
[data-baseweb="slider"] [role="slider"] { background:#1D9E75 !important; border:none !important; }
[data-baseweb="slider"] div[data-testid] > div:first-child { background:#1D9E75 !important; }

/* ══════════════════════════════════════════
   TABS
══════════════════════════════════════════ */
.stTabs [data-baseweb="tab-list"] {
    background:rgba(10,25,48,.5) !important; border-radius:12px !important;
    gap:4px; padding:4px !important;
}
.stTabs [data-baseweb="tab"] {
    background:transparent !important; color:#4a6a84 !important;
    border-radius:9px !important; padding:8px 18px !important;
    font-family:'DM Sans',sans-serif !important; font-weight:500 !important;
    border:none !important;
    transition:all .2s !important;
}
.stTabs [data-baseweb="tab"][aria-selected="true"] {
    background:rgba(29,158,117,.2) !important; color:#4de8b4 !important;
}
.stTabs [data-baseweb="tab-panel"] { padding-top:20px !important; }

/* ══════════════════════════════════════════
   METRICS (st.metric)
══════════════════════════════════════════ */
[data-testid="stMetric"] {
    background:rgba(10,25,48,.6) !important;
    border:1px solid rgba(29,158,117,.2) !important;
    border-radius:14px !important; padding:16px !important;
}
[data-testid="stMetricValue"] { color:#fff !important; font-family:'Syne',sans-serif !important; }
[data-testid="stMetricDelta"] { color:#1D9E75 !important; }
[data-testid="stMetricLabel"] { color:#4a6a84 !important; }

/* ══════════════════════════════════════════
   DATAFRAME
══════════════════════════════════════════ */
[data-testid="stDataFrame"] {
    border:1px solid rgba(29,158,117,.15) !important;
    border-radius:14px !important; overflow:hidden;
}

/* ══════════════════════════════════════════
   EXPANDER
══════════════════════════════════════════ */
[data-testid="stExpander"] {
    background:rgba(10,25,48,.5) !important;
    border:1px solid rgba(29,158,117,.18) !important;
    border-radius:12px !important;
}

/* ══════════════════════════════════════════
   TOAST / SUCCESS / WARNING
══════════════════════════════════════════ */
[data-testid="stAlert"] {
    border-radius:12px !important;
    border-left:3px solid rgba(29,158,117,.8) !important;
}

/* ══════════════════════════════════════════
   PROGRESS WIZARD
══════════════════════════════════════════ */
.wiz-track {
    display:flex; align-items:center; gap:0; margin-bottom:28px;
}
.wiz-step {
    display:flex; align-items:center; gap:8px; font-size:12px;
    font-weight:600; color:#3d5a7a;
    font-family:'DM Sans',sans-serif;
}
.wiz-step.active { color:#4de8b4; }
.wiz-step.done   { color:#1D9E75; }
.wiz-dot {
    width:28px; height:28px; border-radius:50%; display:flex; align-items:center;
    justify-content:center; font-size:11px; font-weight:700;
    background:rgba(255,255,255,.05); border:1px solid rgba(255,255,255,.1);
    font-family:'Syne',sans-serif; flex-shrink:0;
}
.wiz-step.active .wiz-dot { background:rgba(29,158,117,.25); border-color:#1D9E75; color:#4de8b4; animation:glow 2s infinite; }
.wiz-step.done   .wiz-dot { background:rgba(29,158,117,.4); border-color:#1D9E75; color:#fff; }
.wiz-line { flex:1; height:1px; background:rgba(255,255,255,.07); min-width:24px; max-width:60px; }
.wiz-line.done { background:#1D9E75; }

/* ══════════════════════════════════════════
   INLINE STAT BADGE
══════════════════════════════════════════ */
.stat-b {
    display:inline-flex; align-items:center; gap:6px;
    background:rgba(29,158,117,.1); border:1px solid rgba(29,158,117,.2);
    padding:4px 12px; border-radius:50px;
    font-size:12px; color:#4de8b4; font-weight:500;
}

/* ══════════════════════════════════════════
   LIVE PREVIEW BOX
══════════════════════════════════════════ */
.preview-box {
    background:linear-gradient(135deg,#0a2d20,#0c1e3a);
    border:1px solid rgba(29,158,117,.3); border-radius:14px; padding:16px;
}

/* ══════════════════════════════════════════
   TOGGLE
══════════════════════════════════════════ */
[data-testid="stToggle"] > label { color:#8ba8c4 !important; font-size:13px !important; }

/* ══════════════════════════════════════════
   RADIO
══════════════════════════════════════════ */
.stRadio > div { gap:10px; }
.stRadio label { color:#8ba8c4 !important; font-size:13px !important; }

/* ══════════════════════════════════════════
   SELECTBOX DROPDOWN ITEMS (dark)
══════════════════════════════════════════ */
[data-baseweb="popover"] [role="option"] {
    background:rgba(6,15,30,.97) !important; color:#c8d8e8 !important;
}
[data-baseweb="popover"] [role="option"]:hover { background:rgba(29,158,117,.18) !important; }
[data-baseweb="popover"] [role="option"][aria-selected="true"] { background:rgba(29,158,117,.25) !important; color:#4de8b4 !important; }

/* ══════════════════════════════════════════
   MULTISELECT TAGS
══════════════════════════════════════════ */
[data-baseweb="tag"] {
    background:rgba(29,158,117,.25) !important; color:#4de8b4 !important;
    border:1px solid rgba(29,158,117,.4) !important; border-radius:50px !important;
}
</style>
"""

SIDEBAR_BRAND = """
<div style='padding:16px 8px 20px;text-align:center;'>
  <div style='font-family:Syne,sans-serif;font-size:22px;font-weight:800;
              background:linear-gradient(90deg,#1D9E75,#4de8b4);
              -webkit-background-clip:text;-webkit-text-fill-color:transparent;
              letter-spacing:-0.5px;'>
    ⬡ Connectra
  </div>
  <div style='font-size:10px;color:#2a4a34;letter-spacing:.14em;margin-top:3px;
              text-transform:uppercase;'>Onchain Talent Platform</div>
</div>
"""
