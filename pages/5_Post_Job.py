import streamlit as st
import json, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from styles import GLOBAL_CSS
from data.sqlite_db import get_all_talents, insert_job
from utils.matching import rank_talents_for_job
from utils.blockchain import simulate_job_post, short_hash

st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

SKILLS_ALL = [
    "Python","SQL","JavaScript","React","AWS","Docker","Excel","Power BI",
    "Machine Learning","Data Analysis","Java","Node.js","MongoDB","Git",
    "TypeScript","Kubernetes","Tableau","Django","Flask","FastAPI",
    "Pandas","NumPy","Scikit-learn","TensorFlow","Blockchain","Solidity",
    "Web3.py","Risk Analytics","Financial Modeling","Streamlit","Figma",
    "Product Management","Go","Rust","Redis","PostgreSQL",
]
ROLES = [
    "Software Engineer","Data Analyst","Full Stack Developer","Backend Developer",
    "Frontend Developer","Product Manager","Data Scientist","DevOps Engineer",
    "UI/UX Designer","QA Engineer","Risk Analyst","ML Engineer","Quant Analyst",
]

st.markdown("""
<div class='anim-up' style='margin-bottom:20px;'>
  <div class='s-title' style='font-size:26px;'>📢 Post a New Job</div>
  <div class='s-sub'>All jobs are recorded on Polygon Amoy · Live candidate preview as you type</div>
</div>
""", unsafe_allow_html=True)

talents_df = get_all_talents()
col_form, col_preview = st.columns([1.3, 1], gap="large")

# ════════════════════════════════════════════════
# FORM
# ════════════════════════════════════════════════
with col_form:
    st.markdown("<div class='g-card anim-up'>", unsafe_allow_html=True)
    st.markdown("""<div class='s-title' style='font-size:17px;margin-bottom:16px;'>Job Details</div>""",
                unsafe_allow_html=True)

    title = st.selectbox("Job Role *", ROLES)
    company = st.text_input("Company Name *", placeholder="e.g. FinEdge Technologies")
    description = st.text_area("Job Description *",
                               placeholder="Describe the role, responsibilities, and ideal candidate...",
                               height=100)

    req_skills = st.multiselect("Required Skills *", SKILLS_ALL,
                                placeholder="Select skills required...")

    c1, c2 = st.columns(2)
    with c1:
        budget = st.slider("Budget (USDC $)", 500, 10000, 3500, 100)
        exp_req = st.slider("Experience Required (years)", 0, 10, 3)
    with c2:
        timeline = st.slider("Timeline (days)", 15, 180, 60)
        loc_type = st.selectbox("Location Type", ["Remote","Hybrid","On-site"])

    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    post_clicked = st.button("⬡ Post Job Onchain", use_container_width=True)

# ════════════════════════════════════════════════
# LIVE PREVIEW
# ════════════════════════════════════════════════
with col_preview:
    st.markdown("""
    <div style='font-size:13px;font-weight:600;color:#4de8b4;margin-bottom:10px;
                display:flex;align-items:center;gap:6px;'>
      🤖 Live Candidate Preview
      <span style='font-size:10px;color:#2a4a34;font-weight:400;'>updates as you select skills</span>
    </div>
    """, unsafe_allow_html=True)

    if req_skills:
        mock_job = {
            "required_skills": json.dumps(req_skills),
            "experience_required": exp_req,
        }
        top_matches = rank_talents_for_job(talents_df, mock_job, top_n=6)

        AVATAR_COLS = ["av-g","av-b","av-a","av-p","av-g","av-b"]
        for rank_i, (t, score) in enumerate(top_matches, 1):
            t_skills = json.loads(t["skills"]) if isinstance(t["skills"], str) else t["skills"]
            common = set(s.lower() for s in t_skills) & set(s.lower() for s in req_skills)
            initials = t["name"][0] + (t["name"].split()[-1][0] if " " in t["name"] else "")
            av_cls = AVATAR_COLS[rank_i % len(AVATAR_COLS)]
            sc_col = "#4de8b4" if score>=78 else "#f5c263" if score>=60 else "#f08080"
            nft_badge = "<span class='tag tp' style='font-size:9px;padding:2px 6px;'>⬡</span>" if t.get("nft_token_id") else ""

            st.markdown(f"""
            <div class='cand-row'>
              <div style='font-size:12px;color:#2a4a34;width:18px;font-family:Syne,sans-serif;'>
                {rank_i}
              </div>
              <div class='av {av_cls}' style='width:36px;height:36px;font-size:12px;'>{initials.upper()}</div>
              <div style='flex:1;min-width:0;'>
                <div style='font-size:13px;font-weight:600;color:#fff;display:flex;align-items:center;gap:6px;'>
                  {t["name"]} {nft_badge}
                </div>
                <div style='font-size:11px;color:#4a6a84;'>{t["role"]} · {t["years_exp"]}yr · ⭐{t["rating"]}</div>
                <div style='font-size:10px;color:#2a4a34;margin-top:2px;'>
                  {len(common)}/{len(req_skills)} skills matched
                </div>
              </div>
              <div style='font-family:Syne,sans-serif;font-size:14px;font-weight:700;color:{sc_col};'>
                {score:.0f}%
              </div>
            </div>
            """, unsafe_allow_html=True)

        # Budget sanity check
        avg_rate = int(talents_df["hourly_rate"].mean()) if not talents_df.empty else 30
        est_cost = avg_rate * 8 * (timeline / 5)
        if budget < est_cost * 0.6:
            st.markdown(f"""
            <div style='margin-top:12px;padding:10px;background:rgba(239,159,39,.1);
                        border:1px solid rgba(239,159,39,.3);border-radius:10px;font-size:12px;'>
              ⚠️ Budget <span style='color:#f5c263;'>${budget:,}</span> may be below market rate
              (~${int(est_cost):,} estimated for {timeline}d). May reduce applicant quality.
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style='margin-top:12px;padding:10px;background:rgba(29,158,117,.08);
                        border:1px solid rgba(29,158,117,.2);border-radius:10px;font-size:12px;color:#4de8b4;'>
              ✅ Competitive budget · Expected {len([x for x in top_matches if x[1]>=65])} strong applicants
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style='text-align:center;padding:40px 20px;border:1px dashed rgba(29,158,117,.2);
                    border-radius:14px;color:#2a4a34;'>
          <div style='font-size:24px;margin-bottom:10px;'>👆</div>
          <div style='font-size:13px;'>Select required skills<br>to see live candidate preview</div>
        </div>
        """, unsafe_allow_html=True)

# ════════════════════════════════════════════════
# HANDLE POST
# ════════════════════════════════════════════════
if post_clicked:
    if not title or not company.strip() or not req_skills:
        st.error("Please fill in Role, Company, and at least one Required Skill.")
    elif len(description.strip()) < 20:
        st.error("Please add a richer job description (minimum 20 characters).")
    else:
        with st.spinner("⛓️ Posting job to Polygon Amoy..."):
            import time; time.sleep(0.9)
            wallet = st.session_state.get("wallet", "0xDemoEmployerWallet")
            tx_result = simulate_job_post(wallet, title, budget)
            job_id = insert_job({
                "title": title, "company": company, "description": description,
                "required_skills": json.dumps(req_skills),
                "budget_usdc": budget, "timeline_days": timeline,
                "posted_by_wallet": wallet, "location_type": loc_type,
                "experience_required": exp_req,
            })

        st.success(f"✅ Job posted on Polygon! Job #{job_id}")
        st.markdown(f"""
        <div class='g-card' style='border-color:rgba(29,158,117,.5);margin-top:10px;'>
          <div style='display:grid;grid-template-columns:1fr 1fr;gap:12px;font-size:12px;'>
            <div>
              <div style='color:#2a4a34;margin-bottom:3px;'>Job ID</div>
              <div style='font-family:DM Mono,monospace;color:#4de8b4;font-size:14px;font-weight:600;'>#{job_id}</div>
            </div>
            <div>
              <div style='color:#2a4a34;margin-bottom:3px;'>Tx Hash</div>
              <div style='font-family:DM Mono,monospace;color:#fff;font-size:12px;'>{short_hash(tx_result["tx_hash"])}</div>
            </div>
            <div>
              <div style='color:#2a4a34;margin-bottom:3px;'>Block</div>
              <div style='color:#7ab8f5;font-family:DM Mono,monospace;'>{tx_result["block"]}</div>
            </div>
            <div>
              <div style='color:#2a4a34;margin-bottom:3px;'>Gas Used</div>
              <div style='color:#fff;font-family:DM Mono,monospace;'>{tx_result["gas_used"]}</div>
            </div>
          </div>
          <hr class='div'>
          <a href='{tx_result["explorer"]}' target='_blank'
             style='font-size:12px;color:#1D9E75;text-decoration:none;'>
            🔗 View on Polygonscan →
          </a>
        </div>
        """, unsafe_allow_html=True)
        import time; time.sleep(1.2)
        st.switch_page("pages/6_Employer_Dashboard.py")
