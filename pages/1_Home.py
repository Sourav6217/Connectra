import streamlit as st
import sys, os, pathlib

from styles import GLOBAL_CSS
from data.sqlite_db import get_platform_stats

st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

stats = get_platform_stats()

# ════════════════════════════════════════════════
# HERO
# ════════════════════════════════════════════════
st.markdown("""
<div class='hero anim-up'>
  <div class='hero-title'>
    Verified Talent.<br>
    <span class='g'>Onchain Trust.</span><br>
    Instant Matches.
  </div>
  <div class='hero-sub'>
    Connectra replaces inflated CVs with tamper-proof on-chain reputation.
    Our AI predicts job success — not keyword matches.
    Every hire is transparent, every profile is portable.
  </div>
  <div style='display:flex;gap:12px;flex-wrap:wrap;margin-bottom:32px;position:relative;z-index:1;'>
    <span class='stat-b'>🔐 Soulbound NFT Identity</span>
    <span class='stat-b'>🤖 AI Match Scoring</span>
    <span class='stat-b'>📊 Predictive Analytics</span>
    <span class='stat-b'>⛓️ Polygon Testnet</span>
  </div>
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ════════════════════════════════════════════════
# LIVE PLATFORM METRICS
# ════════════════════════════════════════════════
c1, c2, c3, c4, c5 = st.columns(5)
mdata = [
    (str(stats["talents"]),    "Verified Talents",   "▲ Live",        "0.05s"),
    (str(stats["jobs"]),       "Active Jobs",         "▲ Open now",    "0.12s"),
    (str(stats["nfts_minted"]),"NFTs Minted",         "On-chain",      "0.19s"),
    (f"{stats['avg_match']}%", "Avg Match Score",     "AI-computed",   "0.26s"),
    (str(stats["hired"]),      "Successful Hires",    "Onchain proof", "0.33s"),
]
for col, (val, lbl, delta, delay) in zip([c1,c2,c3,c4,c5], mdata):
    with col:
        st.markdown(f"""
        <div class='m-card' style='animation-delay:{delay};'>
          <div class='m-lbl'>{lbl}</div>
          <div class='m-val'>{val}</div>
          <div class='m-delta'>{delta}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ════════════════════════════════════════════════
# TWO ENTRY CARDS
# ════════════════════════════════════════════════
col_t, col_e = st.columns(2, gap="large")

with col_t:
    st.markdown("""
    <div class='g-card anim-up d2' style='padding:32px;text-align:center;min-height:280px;
         display:flex;flex-direction:column;align-items:center;justify-content:center;'>
      <div style='font-size:48px;margin-bottom:16px;animation:bounce 2s infinite;'>👤</div>
      <div style='font-family:Syne,sans-serif;font-size:22px;font-weight:700;color:#fff;margin-bottom:8px;'>
        I'm Talent
      </div>
      <div style='font-size:13px;color:#4a6a84;line-height:1.7;margin-bottom:24px;max-width:300px;'>
        Create your verified on-chain identity, showcase your skills,
        get matched to gigs that fit your profile perfectly.
      </div>
      <div style='display:flex;gap:8px;flex-wrap:wrap;justify-content:center;'>
        <span class='tag tg'>Create Profile</span>
        <span class='tag tg'>Mint NFT</span>
        <span class='tag tg'>Apply to Gigs</span>
      </div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("🚀 Enter as Talent", use_container_width=True, key="btn_talent"):
        st.session_state.user_role = "talent"
        st.session_state.current_page = "dashboard"; st.rerun()

with col_e:
    st.markdown("""
    <div class='g-card anim-up d3' style='padding:32px;text-align:center;min-height:280px;
         display:flex;flex-direction:column;align-items:center;justify-content:center;
         border-color:rgba(56,138,221,.25);'>
      <div style='font-size:48px;margin-bottom:16px;animation:bounce 2s infinite;animation-delay:.4s;'>🏢</div>
      <div style='font-family:Syne,sans-serif;font-size:22px;font-weight:700;color:#fff;margin-bottom:8px;'>
        I'm Hiring
      </div>
      <div style='font-size:13px;color:#4a6a84;line-height:1.7;margin-bottom:24px;max-width:300px;'>
        Post jobs on-chain, discover ranked candidates with AI-verified scores,
        hire confidently with transparent reputation data.
      </div>
      <div style='display:flex;gap:8px;flex-wrap:wrap;justify-content:center;'>
        <span class='tag tb'>Post Jobs</span>
        <span class='tag tb'>AI Ranking</span>
        <span class='tag tb'>Hire Onchain</span>
      </div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("🏢 Enter as Employer", use_container_width=True, key="btn_employer"):
        st.session_state.user_role = "employer"
        st.session_state.current_page = "employer"; st.rerun()

st.markdown("<br>", unsafe_allow_html=True)

# ════════════════════════════════════════════════
# HOW IT WORKS
# ════════════════════════════════════════════════
st.markdown("""
<div class='g-card anim-up d4'>
  <div class='s-title' style='text-align:center;font-size:22px;margin-bottom:6px;'>How Connectra Works</div>
  <div class='s-sub' style='text-align:center;margin-bottom:28px;'>End-to-end from profile to placement — all onchain</div>
  <div style='display:grid;grid-template-columns:repeat(4,1fr);gap:20px;'>
""", unsafe_allow_html=True)

steps = [
    ("🪙","Mint Identity","Create a Soulbound NFT with your verified skills and work history stored on Polygon."),
    ("🤖","AI Match Score","Our weighted model scores your fit for every job — skills, experience, ratings, completion."),
    ("🔥","Apply Instantly","One-click apply with onchain receipt. Your match score and success probability shown upfront."),
    ("⛓️","Hire & Escrow","Employers hire onchain. USDC escrowed, released on milestone. Mutual reputation updated."),
]
for icon, title, desc in steps:
    st.markdown(f"""
    <div style='text-align:center;padding:20px 12px;'>
      <div style='font-size:32px;margin-bottom:12px;'>{icon}</div>
      <div style='font-family:Syne,sans-serif;font-size:15px;font-weight:700;color:#fff;margin-bottom:8px;'>{title}</div>
      <div style='font-size:12px;color:#4a6a84;line-height:1.65;'>{desc}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("</div></div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ════════════════════════════════════════════════
# TECH STACK FOOTER
# ════════════════════════════════════════════════
st.markdown("""
<div style='text-align:center;padding:24px;border-top:1px solid rgba(29,158,117,.12);'>
  <div style='font-size:11px;color:#2a4a34;letter-spacing:.1em;text-transform:uppercase;margin-bottom:12px;'>
    Innovation Stack
  </div>
  <div style='display:flex;justify-content:center;gap:16px;flex-wrap:wrap;'>
    <span class='tag tg'>Polygon Amoy</span>
    <span class='tag tb'>IPFS / nft.storage</span>
    <span class='tag tp'>Soulbound NFTs</span>
    <span class='tag ta'>AI Matching Engine</span>
    <span class='tag tc'>SQLite → Upgradeable</span>
    <span class='tag tg'>Streamlit</span>
  </div>
  <div style='font-size:11px;color:#1a2a1a;margin-top:12px;'>
    Zero gas fees on testnet · All data verifiable on Polygon Explorer
  </div>
</div>
""", unsafe_allow_html=True)
