import streamlit as st
import json
import random
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from styles import GLOBAL_CSS
from data.sqlite_db import upsert_talent, update_nft
from utils.blockchain import mint_profile_nft
from utils.ui_components import render_skills

st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

SKILLS_ALL = [
    "Python","SQL","JavaScript","React","AWS","Docker","Excel","Power BI",
    "Machine Learning","Data Analysis","Java","Node.js","MongoDB","Git",
    "TypeScript","Kubernetes","Tableau","Django","Flask","FastAPI",
    "Pandas","NumPy","Scikit-learn","TensorFlow","Blockchain","Solidity",
    "Web3.py","Risk Analytics","Financial Modeling","Streamlit","Figma",
    "Product Management","Swift","Kotlin","Go","Rust","Redis","PostgreSQL",
]

ROLES = [
    "Software Engineer","Data Analyst","Full Stack Developer","Backend Developer",
    "Frontend Developer","Product Manager","Data Scientist","DevOps Engineer",
    "UI/UX Designer","QA Engineer","Risk Analyst","ML Engineer","Quant Analyst",
]

# ── Wizard step state ──
if "wiz_step" not in st.session_state:
    st.session_state.wiz_step = 1
if "wiz_data" not in st.session_state:
    st.session_state.wiz_data = {}
if "skill_test_results" not in st.session_state:
  st.session_state.skill_test_results = {}

step = st.session_state.wiz_step

# ════════════════════════════════════════════════
# HEADER
# ════════════════════════════════════════════════
st.markdown("""
<div class='anim-up' style='margin-bottom:8px;'>
  <div class='s-title' style='font-size:26px;'>✨ Create Your Onchain Profile</div>
  <div class='s-sub'>4 steps to mint your Soulbound NFT identity on Polygon</div>
</div>
""", unsafe_allow_html=True)

# ── Progress wizard ──
steps_meta = [
    ("1","Basic Info",   step > 1, step == 1),
    ("2","Skills",       step > 2, step == 2),
    ("3","Work Proof",   step > 3, step == 3),
    ("4","Review & Mint",step > 4, step == 4),
]
wiz_html = "<div class='wiz-track'>"
for i, (num, label, done, active) in enumerate(steps_meta):
    cls = "done" if done else "active" if active else ""
    tick = "✓" if done else num
    wiz_html += f"""
    <div class='wiz-step {cls}'>
      <div class='wiz-dot'>{tick}</div>
      <span style='display:none;'>{label}</span>
      <span style='font-size:12px;'>{label}</span>
    </div>"""
    if i < len(steps_meta) - 1:
        wiz_html += f"<div class='wiz-line {'done' if done else ''}'></div>"
wiz_html += "</div>"
st.markdown(wiz_html, unsafe_allow_html=True)

# ════════════════════════════════════════════════
# STEP 1: BASIC INFO
# ════════════════════════════════════════════════
if step == 1:
    st.markdown("<div class='g-card anim-up'>", unsafe_allow_html=True)
    st.markdown("""
    <div class='s-title' style='font-size:18px;margin-bottom:4px;'>Step 1 · Basic Information</div>
    <div class='s-sub'>Tell us about yourself</div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        name = st.text_input("Full Name *", placeholder="e.g. Sourav Rana",
                             value=st.session_state.wiz_data.get("name", ""))
        role = st.selectbox("Primary Role *", ROLES,
                            index=ROLES.index(st.session_state.wiz_data.get("role", ROLES[0])))
        location = st.selectbox("Location",
                                ["Mumbai","Bangalore","Delhi","Hyderabad","Pune","Chennai","Remote"],
                                index=0)
    with c2:
        years = st.slider("Years of Experience", 0, 15,
                          int(st.session_state.wiz_data.get("years_exp", 3)))
        availability = st.selectbox("Availability",
                                    ["Available","Part-time","Not Available"])
        hourly = st.slider("Hourly Rate (USD $)", 5, 150,
                           int(st.session_state.wiz_data.get("hourly_rate", 30)))

    bio = st.text_area("Short Bio", placeholder="2–3 sentences about yourself...",
                       value=st.session_state.wiz_data.get("bio", ""),
                       height=90)
    github = st.text_input("GitHub / Portfolio URL", placeholder="https://github.com/you",
                           value=st.session_state.wiz_data.get("github", ""))

    st.markdown("</div>", unsafe_allow_html=True)

    if st.button("Next → Skills", use_container_width=False):
        if not name:
            st.error("Name is required.")
        else:
            st.session_state.wiz_data.update(
                name=name, role=role, years_exp=years,
                location=location, availability=availability,
                hourly_rate=hourly, bio=bio, github=github
            )
            st.session_state.wiz_step = 2
            st.rerun()

# ════════════════════════════════════════════════
# STEP 2: SKILLS
# ════════════════════════════════════════════════
elif step == 2:
    st.markdown("<div class='g-card anim-up'>", unsafe_allow_html=True)
    st.markdown("""
    <div class='s-title' style='font-size:18px;margin-bottom:4px;'>Step 2 · Skills</div>
    <div class='s-sub'>Select all skills you're proficient in (min 3)</div>
    """, unsafe_allow_html=True)

    prev_skills = st.session_state.wiz_data.get("skills", [])
    skills = st.multiselect("Your Skills *", SKILLS_ALL, default=prev_skills,
                            placeholder="Start typing to search skills...")

    if skills:
        st.markdown("<div style='margin-top:8px;'>", unsafe_allow_html=True)
        st.markdown("**Preview:**", unsafe_allow_html=False)
        render_skills(skills)
        st.markdown("</div>", unsafe_allow_html=True)

        # Optional, time-bound demo tests to increase credibility.
        st.markdown("<hr class='div'>", unsafe_allow_html=True)
        st.markdown("**Skill Test (Optional, 60s demo):**")
        st.caption("Taking tests is optional, but strong scores increase your Talent Score and verification credibility.")

        chosen_skill = st.selectbox(
            "Pick one selected skill to attempt",
            skills,
            key="skill_test_pick"
        )
        if st.button("Run 60s Demo Test", key="run_skill_test"):
            score = random.randint(48, 97)
            st.session_state.skill_test_results[chosen_skill] = score
            st.success(f"{chosen_skill} test completed: {score}/100")

        if st.session_state.skill_test_results:
            verified_count = len([x for x in st.session_state.skill_test_results.values() if x >= 60])
            avg_score = round(sum(st.session_state.skill_test_results.values()) / len(st.session_state.skill_test_results), 1)
            chips = " ".join([
                f"<span class='tag {'tg' if v >= 60 else 'ta'}'>{k}: {v}</span>"
                for k, v in st.session_state.skill_test_results.items()
            ])
            st.markdown(f"""
            <div style='margin-top:8px;'>
              {chips}
              <div style='font-size:11px;color:#4a6a84;margin-top:8px;'>
                Avg test score: <span style='color:#fff;'>{avg_score}</span>
                · Verified skills (>=60): <span style='color:#4de8b4;'>{verified_count}</span>
              </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown(f"""
        <div style='margin-top:16px;padding:12px;background:rgba(29,158,117,.08);
                    border-radius:10px;border:1px solid rgba(29,158,117,.2);'>
          <div style='font-size:12px;color:#4a6a84;'>
            🤖 <strong style='color:#4de8b4;'>AI Insight:</strong>
            Based on your selected skills, you match best with
            <span style='color:#fff;font-weight:600;'>
              {"Data Science & ML" if any(s in skills for s in ["Python","Machine Learning","Scikit-learn"]) else
               "Full Stack Development" if any(s in skills for s in ["React","Node.js","JavaScript"]) else
               "Data Analytics" if any(s in skills for s in ["SQL","Excel","Tableau","Power BI"]) else
               "Backend Engineering"}
            </span> roles.
          </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    col_back, col_next = st.columns([1, 3])
    with col_back:
        if st.button("← Back", key="back2"):
            st.session_state.wiz_step = 1; st.rerun()
    with col_next:
        if st.button("Next → Work Proof", use_container_width=True):
            if len(skills) < 3:
                st.error("Please select at least 3 skills.")
            else:
                st.session_state.wiz_data["skills"] = skills
                st.session_state.wiz_step = 3; st.rerun()

# ════════════════════════════════════════════════
# STEP 3: WORK PROOF
# ════════════════════════════════════════════════
elif step == 3:
    st.markdown("<div class='g-card anim-up'>", unsafe_allow_html=True)
    st.markdown("""
    <div class='s-title' style='font-size:18px;margin-bottom:4px;'>Step 3 · Work Proof & Ratings</div>
    <div class='s-sub'>Self-declared now · Verifiable onchain later</div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        projects = st.number_input("Number of Completed Projects",
                                   min_value=0, max_value=100,
                                   value=int(st.session_state.wiz_data.get("projects", 5)))
        rating = st.slider("Self Rating (out of 5.0)", 1.0, 5.0,
                           float(st.session_state.wiz_data.get("rating", 4.2)), 0.1,
                           format="%.1f")
    with c2:
        completion = st.slider("Project Completion Rate %", 0, 100,
                               int(st.session_state.wiz_data.get("completion_rate", 85)))
        st.markdown(f"""
        <div style='margin-top:12px;font-size:12px;color:#4a6a84;'>
          Completion: <span style='color:{"#4de8b4" if completion>=80 else "#f5c263" if completion>=65 else "#f08080"};
          font-weight:600;'>{completion}%</span> ·
          Rating: <span style='color:#4de8b4;font-weight:600;'>{rating}/5.0</span>
        </div>
        """, unsafe_allow_html=True)

    # Quick score preview
    from utils.matching import WEIGHTS
    skill_score = min(len(st.session_state.wiz_data.get("skills", [])) / 8, 1.0) * 100
    test_score = 0
    review_score = 0
    if st.session_state.skill_test_results:
        test_score = sum(st.session_state.skill_test_results.values()) / len(st.session_state.skill_test_results)
    preview_score = round(
        WEIGHTS["skill"] * skill_score / 100 * 100 +
        WEIGHTS["experience"] * min(st.session_state.wiz_data.get("years_exp", 3) / 8, 1.0) * 100 +
        WEIGHTS["rating"] * (rating / 5.0) * 100 +
        WEIGHTS["completion"] * (completion / 100) * 100 +
        WEIGHTS["skill_test"] * test_score +
        WEIGHTS["reviews"] * review_score
    )
    st.markdown(f"""
    <hr class='div'>
    <div style='text-align:center;padding:12px 0;'>
      <div style='font-size:12px;color:#4a6a84;margin-bottom:6px;'>Estimated Talent Score</div>
      <div style='font-family:Syne,sans-serif;font-size:40px;font-weight:800;
                  background:linear-gradient(90deg,#1D9E75,#4de8b4);
                  -webkit-background-clip:text;-webkit-text-fill-color:transparent;'>
        {preview_score}
      </div>
      <div style='font-size:11px;color:#2a4a34;'>out of 100 · Updates with real data</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    col_back, col_next = st.columns([1, 3])
    with col_back:
        if st.button("← Back", key="back3"):
            st.session_state.wiz_step = 2; st.rerun()
    with col_next:
        if st.button("Next → Review & Mint", use_container_width=True):
            st.session_state.wiz_data.update(
                projects=projects, rating=rating, completion_rate=completion
            )
            st.session_state.wiz_step = 4; st.rerun()

# ════════════════════════════════════════════════
# STEP 4: REVIEW & MINT
# ════════════════════════════════════════════════
elif step == 4:
    d = st.session_state.wiz_data
    skills_list = d.get("skills", [])

    col_l, col_r = st.columns([1.4, 1], gap="large")
    with col_l:
        st.markdown("<div class='g-card anim-up'>", unsafe_allow_html=True)
        st.markdown("""
        <div class='s-title' style='font-size:18px;margin-bottom:14px;'>Step 4 · Review Your Profile</div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div style='display:flex;align-items:center;gap:14px;margin-bottom:18px;'>
          <div class='av av-g' style='width:56px;height:56px;font-size:18px;'>
            {d.get("name","?")[0].upper()}{d.get("name","?").split()[-1][0].upper() if " " in d.get("name","?") else ""}
          </div>
          <div>
            <div style='font-family:Syne,sans-serif;font-size:18px;font-weight:700;color:#fff;'>{d.get("name","")}</div>
            <div style='font-size:12px;color:#4a6a84;margin-top:2px;'>{d.get("role","")} · {d.get("location","")} · {d.get("years_exp",0)} yrs exp</div>
            <div style='margin-top:6px;'>
              <span class='tag tg'>{"Available" if d.get("availability")=="Available" else "Part-time"}</span>
              <span class='tag tb'>${d.get("hourly_rate",30)}/hr</span>
            </div>
          </div>
        </div>
        <hr class='div'>
        """, unsafe_allow_html=True)

        st.markdown("**Skills:**")
        render_skills(skills_list)

        st.markdown(f"""
        <div style='margin-top:14px;display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px;'>
          <div style='text-align:center;padding:10px;background:rgba(29,158,117,.08);border-radius:10px;'>
            <div style='font-size:18px;font-weight:700;color:#fff;font-family:Syne,sans-serif;'>{d.get("projects",0)}</div>
            <div style='font-size:11px;color:#4a6a84;'>Projects</div>
          </div>
          <div style='text-align:center;padding:10px;background:rgba(56,138,221,.08);border-radius:10px;'>
            <div style='font-size:18px;font-weight:700;color:#fff;font-family:Syne,sans-serif;'>{d.get("rating",0)}/5</div>
            <div style='font-size:11px;color:#4a6a84;'>Rating</div>
          </div>
          <div style='text-align:center;padding:10px;background:rgba(127,119,221,.08);border-radius:10px;'>
            <div style='font-size:18px;font-weight:700;color:#fff;font-family:Syne,sans-serif;'>{d.get("completion_rate",0)}%</div>
            <div style='font-size:11px;color:#4a6a84;'>Completion</div>
          </div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col_r:
        st.markdown(f"""
        <div class='nft-card anim-up d2'>
          <div style='font-size:10px;letter-spacing:.14em;color:#2a4a34;
                      text-transform:uppercase;margin-bottom:12px;'>Will be minted as</div>
          <div style='display:flex;align-items:center;gap:12px;margin-bottom:14px;'>
            <div style='width:48px;height:48px;border-radius:14px;
                        background:rgba(29,158,117,.15);border:1px solid #1D9E75;
                        display:flex;align-items:center;justify-content:center;font-size:24px;'>
              ⬡
            </div>
            <div>
              <div style='font-family:Syne,sans-serif;font-size:15px;font-weight:700;color:#fff;'>
                Talent NFT
              </div>
              <div style='font-size:11px;color:#4de8b4;'>Soulbound · Non-transferable</div>
            </div>
          </div>
          <div style='font-size:12px;color:#4a6a84;line-height:1.8;'>
            Network: <span style='color:#fff;'>Polygon Amoy</span><br>
            Type: <span style='color:#4de8b4;'>ERC-5192 Soulbound</span><br>
            Metadata: <span style='color:#fff;'>Stored on IPFS</span><br>
            Gas: <span style='color:#4de8b4;'>~0 (Testnet)</span>
          </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("""
        <div class='g-card anim-up d3'>
          <div style='font-size:12px;color:#4a6a84;line-height:1.7;'>
            🔐 Your profile will be stored immutably on Polygon.<br>
            ⚡ NFT metadata uploaded to IPFS via nft.storage.<br>
            🌐 Viewable on Polygonscan explorer.<br>
            🚫 Non-transferable — tied to your wallet only.
          </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col_back, _, col_mint = st.columns([1, 1, 2])
    with col_back:
        if st.button("← Back", key="back4"):
            st.session_state.wiz_step = 3; st.rerun()
    with col_mint:
        if st.button("⬡ Create Profile & Mint NFT", use_container_width=True, key="mint_btn"):
            with st.spinner("⛓️ Minting your Soulbound NFT on Polygon Amoy..."):
                import time; time.sleep(1.2)

                wallet = st.session_state.get("wallet", "0xDemoWallet")
                result = mint_profile_nft(
                    wallet, d["name"], d["role"], skills_list,
                    score=round(d.get("rating", 4.0) / 5.0 * 100)
                )
                row = {
                    "wallet_address": wallet,
                    "name": d["name"], "role": d["role"],
                    "years_exp": d["years_exp"], "location": d["location"],
                    "skills": json.dumps(skills_list),
                    "projects": d["projects"], "rating": d["rating"],
                    "completion_rate": d["completion_rate"],
                    "bio": d.get("bio", ""), "github": d.get("github", ""),
                    "nft_token_id": result["token_id"],
                    "nft_tx_hash": result["tx_hash"],
                    "availability": d["availability"],
                    "hourly_rate": d["hourly_rate"],
                    "skill_test_score": round(
                        sum(st.session_state.skill_test_results.values()) / len(st.session_state.skill_test_results), 1
                    ) if st.session_state.skill_test_results else 0,
                    "verified_skills_count": len([x for x in st.session_state.skill_test_results.values() if x >= 60]),
                    "review_score": 0,
                }
                upsert_talent(row)

            st.success(f"✅ Profile created! NFT Minted → Token #{result['token_id']}")
            st.markdown(f"""
            <div class='g-card' style='border-color:rgba(29,158,117,.5);margin-top:12px;'>
              <div style='display:grid;grid-template-columns:1fr 1fr;gap:12px;font-size:12px;'>
                <div>
                  <div style='color:#2a4a34;margin-bottom:3px;'>Token ID</div>
                  <div style='font-family:DM Mono,monospace;color:#4de8b4;font-size:14px;font-weight:600;'>#{result["token_id"]}</div>
                </div>
                <div>
                  <div style='color:#2a4a34;margin-bottom:3px;'>Block</div>
                  <div style='color:#fff;font-family:DM Mono,monospace;'>{result["block"]}</div>
                </div>
                <div>
                  <div style='color:#2a4a34;margin-bottom:3px;'>Gas Used</div>
                  <div style='color:#7ab8f5;font-family:DM Mono,monospace;'>{result["gas_used"]}</div>
                </div>
                <div>
                  <div style='color:#2a4a34;margin-bottom:3px;'>Network</div>
                  <div style='color:#4de8b4;'>Polygon Amoy</div>
                </div>
              </div>
              <hr class='div'>
              <a href='{result["explorer"]}' target='_blank'
                 style='font-size:12px;color:#1D9E75;text-decoration:none;'>
                🔗 View on Polygonscan →
              </a>
            </div>
            """, unsafe_allow_html=True)

            st.session_state.wiz_step = 1
            st.session_state.wiz_data = {}
            st.session_state.skill_test_results = {}

            import time; time.sleep(1.5)
            st.switch_page("pages/3_Talent_Dashboard.py")
