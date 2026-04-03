import streamlit as st
import json, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from styles import GLOBAL_CSS
from data.sqlite_db import get_talent, get_all_jobs, insert_application
from utils.matching import calculate_match, get_breakdown, get_success_prob, score_class
from utils.blockchain import mint_application_nft, short_hash
from utils.ui_components import render_skills, html_bar

st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

wallet = st.session_state.get("wallet", "0x742d35Cc6634C0532925a3b844Bc454e4438f44e")
talent_df = get_talent(wallet)
jobs_df   = get_all_jobs()

# ════════════════════════════════════════════════
# HEADER
# ════════════════════════════════════════════════
st.markdown("""
<div class='anim-up' style='margin-bottom:20px;'>
  <div class='s-title' style='font-size:26px;'>🔥 Job Marketplace</div>
  <div class='s-sub'>AI-ranked gigs · Match score computed instantly from your verified profile</div>
</div>
""", unsafe_allow_html=True)

# ── Talent check ──
has_profile = not talent_df.empty
talent_row  = talent_df.iloc[0] if has_profile else None

if not has_profile:
    st.markdown("""
    <div class='g-card' style='text-align:center;padding:32px;border-color:rgba(239,159,39,.3);'>
      <div style='font-size:32px;margin-bottom:10px;'>⚠️</div>
      <div style='font-size:15px;color:#f5c263;font-weight:600;margin-bottom:6px;'>Profile Required</div>
      <div style='font-size:13px;color:#4a6a84;'>Create your profile to see match scores and apply to gigs.</div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("✨ Create Profile First"):
        st.switch_page("pages/2_✨_Create_Profile.py")

# ════════════════════════════════════════════════
# FILTERS
# ════════════════════════════════════════════════
f1, f2, f3, f4, f5 = st.columns([2, 1.2, 1.2, 1, 0.8])
with f1:
    search = st.text_input("", placeholder="🔍 Search title, skills, company...",
                           label_visibility="collapsed")
with f2:
    loc_filter = st.selectbox("", ["All Locations","Remote","Hybrid","On-site"],
                              label_visibility="collapsed")
with f3:
    sort_by = st.selectbox("", ["Best Match","Highest Pay","Newest","Lowest Competition"],
                           label_visibility="collapsed")
with f4:
    budget_min = st.number_input("Min $", value=0, step=500, label_visibility="visible")
with f5:
    st.markdown("<br>", unsafe_allow_html=True)
    remote_only = st.toggle("Remote", value=False)

# ════════════════════════════════════════════════
# COMPUTE SCORES + FILTER
# ════════════════════════════════════════════════
jobs_with_scores = []
for _, job in jobs_df.iterrows():
    score = calculate_match(talent_row, job) if has_profile else 0.0
    jobs_with_scores.append((job, score))

# Apply filters
filtered = jobs_with_scores
if search:
    q = search.lower()
    filtered = [(j, s) for j, s in filtered
                if q in j["title"].lower() or q in j.get("company","").lower()
                or any(q in sk.lower() for sk in json.loads(j["required_skills"]))]
if loc_filter != "All Locations":
    filtered = [(j, s) for j, s in filtered if j.get("location_type","") == loc_filter]
if remote_only:
    filtered = [(j, s) for j, s in filtered if j.get("location_type","") == "Remote"]
if budget_min > 0:
    filtered = [(j, s) for j, s in filtered if j["budget_usdc"] >= budget_min]

# Sort
if sort_by == "Best Match":
    filtered.sort(key=lambda x: x[1], reverse=True)
elif sort_by == "Highest Pay":
    filtered.sort(key=lambda x: x[0]["budget_usdc"], reverse=True)
elif sort_by == "Newest":
    filtered.sort(key=lambda x: str(x[0].get("posted_date", "")), reverse=True)

st.markdown(f"""
<div style='font-size:12px;color:#2a4a34;margin:12px 0 16px;'>
  Showing <span style='color:#4de8b4;font-weight:600;'>{len(filtered)}</span> gigs
  {("· sorted by " + sort_by) if sort_by else ""}
</div>
""", unsafe_allow_html=True)

# ════════════════════════════════════════════════
# JOB CARDS
# ════════════════════════════════════════════════
AVATAR_PAIRS = [
    ("#0c1e3a","#378ADD"), ("#0a2d20","#1D9E75"), ("#1a1430","#7F77DD"),
    ("#1a0e0a","#D85A30"), ("#130a28","#9F7AEA"), ("#0a1a0a","#48BB78"),
    ("#1a1a10","#EF9F27"), ("#1a0a18","#D4537E"),
]

if "apply_modal" not in st.session_state:
    st.session_state.apply_modal = None

for idx, (job, score) in enumerate(filtered):
    bg, col = AVATAR_PAIRS[idx % len(AVATAR_PAIRS)]
    sc_cls  = score_class(score)
    prob, emoji = get_success_prob(score)
    initials = "".join(w[0] for w in job["title"].split()[:2]).upper()
    req_skills = json.loads(job["required_skills"])
    bar_color = "#1D9E75" if score >= 78 else "#EF9F27" if score >= 60 else "#E24B4A"
    loc_tag  = "tg" if job.get("location_type")=="Remote" else "tb" if job.get("location_type")=="Hybrid" else "ta"

    with st.container():
        st.markdown(f"""
        <div class='job-card anim-up' style='animation-delay:{idx*0.04:.2f}s;'>
          <div style='display:flex;align-items:flex-start;gap:16px;'>
            <div style='width:52px;height:52px;border-radius:13px;background:{bg};
                        border:1px solid {col}50;display:flex;align-items:center;
                        justify-content:center;font-weight:700;font-size:14px;color:{col};
                        flex-shrink:0;font-family:Syne,sans-serif;'>
              {initials}
            </div>
            <div style='flex:1;min-width:0;'>
              <div style='display:flex;align-items:center;gap:8px;flex-wrap:wrap;margin-bottom:2px;'>
                <div style='font-family:Syne,sans-serif;font-size:16px;font-weight:700;color:#fff;'>
                  {job["title"]}
                </div>
                {f"<span class='tag tp' style='font-size:10px;'>⬡ NFT Req</span>" if score > 80 else ""}
              </div>
              <div style='font-size:12px;color:#4a6a84;margin-bottom:8px;'>
                {job.get("company","Company")} ·
                <span class='tag {loc_tag}' style='padding:2px 8px;font-size:10px;margin:0 3px;'>{job.get("location_type","Remote")}</span>
                · {job["timeline_days"]}d · Posted {job.get("posted_date","recently")}
              </div>
              <div style='margin-bottom:10px;'>
                {"".join(f"<span class='tag tg' style='font-size:10px;'>{s}</span>" for s in req_skills[:5])}
                {"<span style='font-size:11px;color:#2a4a34;'>+" + str(len(req_skills)-5) + " more</span>" if len(req_skills)>5 else ""}
              </div>
              <div style='display:flex;align-items:center;gap:12px;'>
                <div style='flex:1;max-width:200px;'>
                  <div style='display:flex;justify-content:space-between;font-size:10px;color:#2a4a34;margin-bottom:3px;'>
                    <span>Match</span><span style='color:{bar_color};font-weight:600;'>{score:.0f}%</span>
                  </div>
                  <div class='bar-bg' style='margin:0;'>
                    <div class='bar' style='width:{score}%;background:{bar_color};'></div>
                  </div>
                </div>
                <div style='font-size:11px;color:#4a6a84;'>
                  {emoji} Success: <span style='color:#fff;font-weight:600;'>{prob:.0f}%</span>
                </div>
              </div>
            </div>
            <div style='text-align:right;flex-shrink:0;display:flex;flex-direction:column;gap:8px;align-items:flex-end;'>
              <div style='font-family:Syne,sans-serif;font-size:18px;font-weight:700;color:#fff;'>
                ${job["budget_usdc"]:,}
              </div>
              <div class='sp {sc_cls}'>{score:.0f}% match</div>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        col_exp, col_apply = st.columns([3, 1])
        with col_exp:
            with st.expander("📄 View Details"):
                st.markdown(f"""
                <div style='font-size:13px;color:#6b8aaa;line-height:1.7;'>{job["description"]}</div>
                <div style='margin-top:12px;display:flex;gap:12px;font-size:12px;color:#4a6a84;'>
                  <span>🕐 {job["timeline_days"]} days</span>
                  <span>📍 {job.get("location_type","Remote")}</span>
                  <span>🎓 {job.get("experience_required",2)}+ yrs exp</span>
                  <span>💰 ${job["budget_usdc"]:,}</span>
                </div>
                """, unsafe_allow_html=True)

                if has_profile:
                    st.markdown("**Match Breakdown:**")
                    breakdown = get_breakdown(talent_row, job)
                    for factor, val in breakdown.items():
                        col_cls = "bar" if val >= 78 else "bar-a" if val >= 55 else "bar-r"
                        st.markdown(html_bar(factor, val, col_cls), unsafe_allow_html=True)

        with col_apply:
            if has_profile:
                if st.button(f"Apply ⬡", key=f"apply_{job['job_id']}_{idx}", use_container_width=True):
                    with st.spinner("Recording on Polygon..."):
                        import time; time.sleep(0.8)
                        nft_result = mint_application_nft(wallet, int(job["job_id"]), score)
                        success = insert_application(
                            wallet, int(job["job_id"]), score, nft_result["tx_hash"]
                        )
                    if success:
                        st.success(f"✅ Applied! Match: {score:.0f}%")
                        st.markdown(f"""
                        <div style='font-size:11px;margin-top:6px;'>
                          <span class='tag tg'>Receipt NFT #{nft_result["token_id"]}</span><br>
                          <span style='font-family:DM Mono,monospace;color:#2a4a34;font-size:10px;'>
                            Tx: {short_hash(nft_result["tx_hash"])}
                          </span>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.warning("Already applied to this job.")

if not filtered:
    st.markdown("""
    <div style='text-align:center;padding:60px;color:#2a4a34;'>
      <div style='font-size:32px;margin-bottom:12px;'>🔍</div>
      <div style='font-size:16px;'>No gigs match your filters.</div>
      <div style='font-size:13px;margin-top:6px;'>Try clearing filters or broadening your search.</div>
    </div>
    """, unsafe_allow_html=True)
