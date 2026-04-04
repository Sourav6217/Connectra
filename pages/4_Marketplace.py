import streamlit as st
import json, sys, os

from styles import GLOBAL_CSS
from data.sqlite_db import get_talent, get_all_jobs, insert_application
from utils.matching import calculate_match, get_breakdown, get_success_prob, score_class
from utils.blockchain import mint_application_nft, short_hash
from utils.ui_components import html_bar

st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

wallet     = st.session_state.get("wallet", "0x742d35Cc6634C0532925a3b844Bc454e4438f44e")
talent_df  = get_talent(wallet)
jobs_df    = get_all_jobs()

st.markdown("""
<div class='anim-up' style='margin-bottom:20px;'>
  <div class='s-title' style='font-size:26px;'>🔥 Job Marketplace</div>
  <div class='s-sub'>Select a gig from the dropdown · AI match score computed from your verified profile</div>
</div>
""", unsafe_allow_html=True)

has_profile = not talent_df.empty
talent_row  = talent_df.iloc[0] if has_profile else None

if not has_profile:
    st.markdown("""
    <div class='g-card' style='text-align:center;padding:32px;border-color:rgba(239,159,39,.3);'>
      <div style='font-size:32px;margin-bottom:10px;'>⚠️</div>
      <div style='font-size:15px;color:#f5c263;font-weight:600;margin-bottom:6px;'>Profile Required</div>
      <div style='font-size:13px;color:#4a6a84;'>Create your profile to see match scores.</div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Create Profile First"):
        st.session_state.current_page = "profile"; st.rerun()

if jobs_df.empty:
    st.info("No jobs posted yet.")
    st.stop()

# Compute scores
job_scores = {}
for _, job in jobs_df.iterrows():
    score = calculate_match(talent_row, job) if has_profile else 0.0
    job_scores[int(job["job_id"])] = score

# Filters
f1, f2, f3 = st.columns([1.5, 1.2, 1.2])
with f1:
    search = st.text_input("", placeholder="Search title or company...", label_visibility="collapsed")
with f2:
    loc_filter = st.selectbox("", ["All Locations","Remote","Hybrid","On-site"], label_visibility="collapsed")
with f3:
    sort_by = st.selectbox("", ["Best Match","Highest Pay","Newest"], label_visibility="collapsed")

# Filter rows
rows = []
for _, job in jobs_df.iterrows():
    jid   = int(job["job_id"])
    score = job_scores.get(jid, 0.0)
    if search:
        q   = search.lower()
        req = json.loads(job["required_skills"])
        if not (q in job["title"].lower() or q in job.get("company","").lower()
                or any(q in s.lower() for s in req)):
            continue
    if loc_filter != "All Locations" and job.get("location_type","") != loc_filter:
        continue
    rows.append((job, score))

if sort_by == "Best Match":
    rows.sort(key=lambda x: x[1], reverse=True)
elif sort_by == "Highest Pay":
    rows.sort(key=lambda x: x[0]["budget_usdc"], reverse=True)
elif sort_by == "Newest":
    rows.sort(key=lambda x: str(x[0].get("posted_date","")), reverse=True)

if not rows:
    st.markdown("<div style='text-align:center;padding:60px;color:#2a4a34;'>No gigs match your filters.</div>", unsafe_allow_html=True)
    st.stop()

# Score emoji helper
def semoji(s):
    return "🟢" if s>=78 else "🟡" if s>=60 else "🔴"

LOC_ICON = {"Remote":"🌐","Hybrid":"🔀","On-site":"📍"}

dropdown_labels = [
    f"{semoji(s)}  {job['title']}  ·  {job.get('company','')}  ·  ${job['budget_usdc']:,}  ·  Match: {s:.0f}%"
    for job, s in rows
]

selected_idx = st.selectbox(
    f"Choose from {len(rows)} gigs:",
    range(len(rows)),
    format_func=lambda i: dropdown_labels[i]
)

selected_job, selected_score = rows[selected_idx]
req_skills = json.loads(selected_job["required_skills"])
prob, emoji = get_success_prob(selected_score)
sc_cls  = score_class(selected_score)
bar_col = "#1D9E75" if selected_score>=78 else "#EF9F27" if selected_score>=60 else "#E24B4A"
loc_type = selected_job.get("location_type","Remote")
initials = "".join(w[0] for w in selected_job["title"].split()[:2]).upper()

AVATAR_PAIRS = [
    ("#0c1e3a","#378ADD"),("#0a2d20","#1D9E75"),("#1a1430","#7F77DD"),
    ("#1a0e0a","#D85A30"),("#130a28","#9F7AEA"),("#0a1a0a","#48BB78"),
]
bg_c, fg_c = AVATAR_PAIRS[selected_idx % len(AVATAR_PAIRS)]

skills_html = " ".join(
    f"<span class='tag tg' style='font-size:10px;'>{s}</span>" for s in req_skills[:7]
)
if len(req_skills) > 7:
    skills_html += f"<span style='font-size:11px;color:#2a4a34;'> +{len(req_skills)-7}</span>"

st.markdown("<br>", unsafe_allow_html=True)

col_detail, col_action = st.columns([1.6, 1], gap="large")

with col_detail:
    st.markdown(f"""
<div class='g-card anim-up'>
  <div style='display:flex;align-items:flex-start;gap:16px;'>
    <div style='width:56px;height:56px;border-radius:14px;background:{bg_c};
                border:1px solid {fg_c}55;display:flex;align-items:center;
                justify-content:center;font-weight:700;font-size:16px;
                color:{fg_c};flex-shrink:0;font-family:Syne,sans-serif;'>
      {initials}
    </div>
    <div style='flex:1;'>
      <div style='font-family:Syne,sans-serif;font-size:20px;font-weight:700;color:#fff;margin-bottom:4px;'>
        {selected_job["title"]}
      </div>
      <div style='font-size:13px;color:#4a6a84;margin-bottom:10px;'>
        {selected_job.get("company","Company")} &nbsp;·&nbsp;
        {LOC_ICON.get(loc_type,"📍")} {loc_type} &nbsp;·&nbsp;
        {selected_job["timeline_days"]}d &nbsp;·&nbsp;
        {selected_job.get("posted_date","—")}
      </div>
      <div style='margin-bottom:14px;'>{skills_html}</div>
      <div style='display:flex;align-items:center;gap:14px;'>
        <div style='flex:1;max-width:240px;'>
          <div style='display:flex;justify-content:space-between;font-size:11px;color:#2a4a34;margin-bottom:4px;'>
            <span>AI Match Score</span>
            <span style='color:{bar_col};font-weight:700;'>{selected_score:.0f}%</span>
          </div>
          <div class='bar-bg' style='margin:0;'>
            <div class='bar' style='width:{selected_score:.1f}%;background:{bar_col};'></div>
          </div>
        </div>
        <div style='font-size:12px;color:#4a6a84;'>
          {emoji} Success: <span style='color:#fff;font-weight:600;'>{prob:.0f}%</span>
        </div>
        <div style='font-family:Syne,sans-serif;font-size:18px;font-weight:700;color:#fff;'>
          ${selected_job["budget_usdc"]:,}
        </div>
      </div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

    desc_txt = selected_job.get("description","")
    exp_req  = selected_job.get("experience_required",2)
    st.markdown(f"""
<div class='g-card anim-up d2' style='margin-top:14px;'>
  <div style='font-size:15px;font-weight:600;color:#fff;margin-bottom:10px;'>Job Description</div>
  <div style='font-size:13px;color:#6b8aaa;line-height:1.75;margin-bottom:16px;'>{desc_txt}</div>
  <hr class='div'>
  <div style='display:grid;grid-template-columns:1fr 1fr;gap:10px;font-size:12px;color:#4a6a84;'>
    <div>Budget: <span style='color:#fff;font-weight:600;'>${selected_job["budget_usdc"]:,}</span></div>
    <div>Timeline: <span style='color:#fff;'>{selected_job["timeline_days"]} days</span></div>
    <div>Type: <span style='color:#fff;'>{loc_type}</span></div>
    <div>Experience: <span style='color:#fff;'>{exp_req}+ yrs</span></div>
  </div>
</div>
""", unsafe_allow_html=True)

with col_action:
    if has_profile:
        breakdown = get_breakdown(talent_row, selected_job)
        bars_html = "".join(
            html_bar(factor, val, "bar" if val>=78 else "bar-a" if val>=55 else "bar-r")
            for factor, val in breakdown.items()
        )
        st.markdown(f"""
<div class='g-card anim-up d2'>
  <div style='font-size:15px;font-weight:600;color:#fff;margin-bottom:14px;'>Match Breakdown</div>
  {bars_html}
  <div class='formula' style='margin-top:12px;'>
    <span class='hl'>Match</span> = 0.45xSkill + 0.25xExp + 0.20xRating + 0.10xCompletion = <span class='hl'>{selected_score:.0f}%</span>
  </div>
</div>
""", unsafe_allow_html=True)
    else:
        st.markdown("""
<div class='g-card' style='text-align:center;padding:24px;'>
  <div style='color:#f5c263;font-size:13px;'>Create a profile to see your match breakdown</div>
</div>
""", unsafe_allow_html=True)

    grad_end = "#4de8b4" if selected_score >= 78 else "#f5c263"
    st.markdown(f"""
<div class='g-card anim-up d3' style='margin-top:14px;border-color:rgba(29,158,117,.4);'>
  <div style='text-align:center;margin-bottom:16px;'>
    <div style='font-size:11px;color:#2a4a34;margin-bottom:6px;'>YOUR MATCH</div>
    <div style='font-family:Syne,sans-serif;font-size:48px;font-weight:800;line-height:1;
                background:linear-gradient(90deg,{bar_col},{grad_end});
                -webkit-background-clip:text;-webkit-text-fill-color:transparent;'>
      {selected_score:.0f}%
    </div>
    <div class='sp {sc_cls}' style='display:inline-block;margin-top:8px;'>
      {emoji} {prob:.0f}% success probability
    </div>
  </div>
  <hr class='div'>
  <div style='font-size:12px;color:#4a6a84;text-align:center;line-height:1.8;'>
    Applying creates an onchain receipt NFT as proof of your application.
  </div>
</div>
""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    if has_profile:
        if st.button("Apply Onchain", use_container_width=True,
                     key=f"apply_btn_{selected_job['job_id']}"):
            with st.spinner("Recording on Polygon Amoy..."):
                import time; time.sleep(0.8)
                nft_result = mint_application_nft(wallet, int(selected_job["job_id"]), selected_score)
                success = insert_application(wallet, int(selected_job["job_id"]), selected_score, nft_result["tx_hash"])
            if success:
                st.success(f"Applied! Match: {selected_score:.0f}%")
                st.markdown(f"""
<div style='font-size:11px;margin-top:8px;line-height:2;'>
  <span class='tag tg'>Receipt NFT #{nft_result["token_id"]}</span><br>
  <span style='font-family:DM Mono,monospace;color:#2a4a34;font-size:10px;'>Tx: {short_hash(nft_result["tx_hash"])}</span>
</div>
""", unsafe_allow_html=True)
            else:
                st.warning("Already applied to this job.")
    else:
        if st.button("Create Profile to Apply", use_container_width=True):
            st.session_state.current_page = "profile"; st.rerun()

# Other recommended gigs
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("""<div style='font-size:13px;font-weight:600;color:#4de8b4;margin-bottom:12px;'>Other Recommended Gigs</div>""", unsafe_allow_html=True)

other_rows = [r for r in rows if int(r[0]["job_id"]) != int(selected_job["job_id"])][:6]
cards_html = ""
for job, score in other_rows:
    sc  = score_class(score)
    bc  = "#1D9E75" if score>=78 else "#EF9F27" if score>=60 else "#E24B4A"
    req = json.loads(job["required_skills"])
    skill_tags = " ".join(f"<span class='tag tg' style='font-size:9px;'>{s}</span>" for s in req[:3])
    cards_html += f"""
<div style='display:flex;align-items:center;gap:12px;padding:12px 14px;
            background:rgba(10,25,48,.55);border:1px solid rgba(29,158,117,.12);
            border-radius:12px;margin-bottom:8px;'>
  <div style='flex:1;min-width:0;'>
    <div style='font-size:13px;font-weight:600;color:#fff;'>{job["title"]}</div>
    <div style='font-size:11px;color:#4a6a84;margin:2px 0;'>{job.get("company","")} · ${job["budget_usdc"]:,} · {job.get("location_type","Remote")}</div>
    <div>{skill_tags}</div>
  </div>
  <div style='text-align:right;flex-shrink:0;'>
    <div class='sp {sc}' style='font-size:12px;'>{score:.0f}%</div>
    <div style='font-size:10px;color:#2a4a34;margin-top:4px;'>{job["timeline_days"]}d</div>
  </div>
</div>
"""

if cards_html:
    st.markdown(cards_html, unsafe_allow_html=True)
