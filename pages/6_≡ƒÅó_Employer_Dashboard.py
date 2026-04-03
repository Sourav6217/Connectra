import streamlit as st
import json, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from styles import GLOBAL_CSS
from data.sqlite_db import get_all_jobs, get_all_talents, get_applications_for_job
from utils.matching import rank_talents_for_job, get_success_prob, get_risk_level, score_class
from utils.blockchain import simulate_hire, short_hash
from utils.ui_components import render_skills, html_bar, render_hbar, render_gauge

st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

jobs_df    = get_all_jobs()
talents_df = get_all_talents()

st.markdown("""
<div class='anim-up' style='margin-bottom:20px;'>
  <div class='s-title' style='font-size:26px;'>🏢 Employer Hub</div>
  <div class='s-sub'>AI-ranked candidates · Onchain hire flow · Full analytics</div>
</div>
""", unsafe_allow_html=True)

if jobs_df.empty:
    st.markdown("""
    <div style='text-align:center;padding:80px;'>
      <div style='font-size:48px;margin-bottom:16px;'>📢</div>
      <div class='s-title' style='margin-bottom:8px;'>No Jobs Posted Yet</div>
      <div style='font-size:13px;color:#4a6a84;margin-bottom:24px;'>Post your first job to start discovering talent.</div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("📢 Post a Job"):
        st.switch_page("pages/5_📢_Post_Job.py")
    st.stop()

tabs = st.tabs(["🔥 Top Candidates", "📋 My Jobs", "🏆 Leaderboard", "⬡ Hire Flow"])

AVATAR_COLS = [
    ("av-g","#1D9E75"), ("av-b","#378ADD"), ("av-a","#EF9F27"),
    ("av-p","#7F77DD"), ("av-g","#4de8b4"), ("av-b","#7ab8f5"),
]

# ════════════════════════════════════════════════
# TAB 1: TOP CANDIDATES
# ════════════════════════════════════════════════
with tabs[0]:
    job_titles = [f"#{r['job_id']} — {r['title']} ({r.get('company','')})"
                  for _, r in jobs_df.iterrows()]
    selected_label = st.selectbox("Select job to analyse:", job_titles)
    selected_job_id = int(selected_label.split("—")[0].replace("#","").strip())
    job_row = jobs_df[jobs_df["job_id"] == selected_job_id].iloc[0]

    st.markdown("<br>", unsafe_allow_html=True)

    top_matches = rank_talents_for_job(talents_df, job_row, top_n=8)

    col_list, col_chart = st.columns([1.3, 1], gap="large")

    with col_list:
        st.markdown(f"""
        <div class='g-card anim-up'>
          <div class='s-title' style='font-size:16px;margin-bottom:4px;'>
            Top Candidates
          </div>
          <div class='s-sub'>Ranked by AI match score · Job: {job_row["title"]}</div>
        """, unsafe_allow_html=True)

        for rank_i, (talent, score) in enumerate(top_matches, 1):
            t_skills = json.loads(talent["skills"]) if isinstance(talent["skills"], str) else talent["skills"]
            req_skills = json.loads(job_row["required_skills"])
            common = set(s.lower() for s in t_skills) & set(s.lower() for s in req_skills)
            prob, emoji = get_success_prob(score)
            risk_label, risk_cls = get_risk_level(talent)
            sc_cls = score_class(score)
            av_cls, av_col = AVATAR_COLS[rank_i % len(AVATAR_COLS)]
            initials = talent["name"][0] + (talent["name"].split()[-1][0] if " " in talent["name"] else "")
            nft_badge = "<span class='tag tp' style='font-size:9px;padding:2px 6px;'>⬡ NFT</span>" if talent.get("nft_token_id") else ""
            highlight = "background:rgba(29,158,117,.06);border-radius:10px;padding:10px 8px;margin:-2px -4px;" if rank_i == 1 else ""

            st.markdown(f"""
            <div class='cand-row' style='{highlight}'>
              <div style='font-family:Syne,sans-serif;font-size:13px;color:#2a4a34;width:20px;'>#{rank_i}</div>
              <div class='av {av_cls}' style='width:38px;height:38px;font-size:13px;'>{initials.upper()}</div>
              <div style='flex:1;min-width:0;'>
                <div style='font-size:13px;font-weight:600;color:#fff;
                            display:flex;align-items:center;gap:6px;flex-wrap:wrap;'>
                  {talent["name"]}
                  {nft_badge}
                  {"<span class='tag tg' style='font-size:9px;padding:1px 6px;'>🥇 Top Pick</span>" if rank_i==1 else ""}
                </div>
                <div style='font-size:11px;color:#4a6a84;margin-top:1px;'>
                  {talent["role"]} · {talent["years_exp"]}yr · ⭐{talent["rating"]} · {len(common)}/{len(req_skills)} skills
                </div>
                <div style='margin-top:4px;display:flex;gap:6px;align-items:center;'>
                  <span class='{risk_cls}' style='font-size:10px;'>{risk_label}</span>
                  <span style='font-size:11px;color:#4a6a84;'>{emoji} {prob:.0f}% success</span>
                </div>
              </div>
              <div class='sp {sc_cls}' style='font-size:12px;'>{score:.0f}%</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    with col_chart:
        names  = [t["name"].split()[0] for t, _ in top_matches]
        scores = [s for _, s in top_matches]
        render_hbar(names, scores, highlight_name=top_matches[0][0]["name"] if top_matches else "",
                    height=280)

        # Job requirements summary
        req_skills_list = json.loads(job_row["required_skills"])
        st.markdown(f"""
        <div class='g-card anim-up d3' style='margin-top:14px;'>
          <div style='font-size:13px;font-weight:600;color:#fff;margin-bottom:10px;'>Job Requirements</div>
          <div style='font-size:12px;color:#4a6a84;line-height:1.8;'>
            💰 Budget: <span style='color:#fff;'>${job_row["budget_usdc"]:,}</span><br>
            🕐 Timeline: <span style='color:#fff;'>{job_row["timeline_days"]} days</span><br>
            📍 Type: <span style='color:#fff;'>{job_row.get("location_type","Remote")}</span><br>
            🎓 Exp: <span style='color:#fff;'>{job_row.get("experience_required",2)}+ years</span>
          </div>
          <div style='margin-top:10px;'>
            {"".join(f"<span class='tag tg' style='font-size:10px;'>{s}</span>" for s in req_skills_list[:6])}
          </div>
        </div>
        """, unsafe_allow_html=True)

# ════════════════════════════════════════════════
# TAB 2: MY JOBS
# ════════════════════════════════════════════════
with tabs[1]:
    for _, job in jobs_df.iterrows():
        apps = get_applications_for_job(int(job["job_id"]))
        n_apps = len(apps)
        top_score = apps["match_score"].max() if not apps.empty else 0

        st.markdown(f"""
        <div class='job-card anim-up' style='margin-bottom:12px;'>
          <div style='display:flex;align-items:center;gap:14px;'>
            <div>
              <div style='font-family:Syne,sans-serif;font-size:15px;font-weight:700;color:#fff;'>
                {job["title"]}
              </div>
              <div style='font-size:12px;color:#4a6a84;margin-top:3px;'>
                {job.get("company","")} · ${job["budget_usdc"]:,} · {job["timeline_days"]}d · {job.get("location_type","Remote")}
              </div>
            </div>
            <div style='margin-left:auto;display:flex;gap:12px;align-items:center;'>
              <div style='text-align:center;'>
                <div style='font-size:18px;font-weight:700;color:#fff;font-family:Syne,sans-serif;'>{n_apps}</div>
                <div style='font-size:10px;color:#2a4a34;'>Applications</div>
              </div>
              <div style='text-align:center;'>
                <div style='font-size:18px;font-weight:700;color:#4de8b4;font-family:Syne,sans-serif;'>{top_score:.0f}%</div>
                <div style='font-size:10px;color:#2a4a34;'>Top Score</div>
              </div>
              <span class='tag tg'>Open</span>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        if n_apps > 0:
            with st.expander(f"View {n_apps} applicants"):
                for _, app in apps.iterrows():
                    sc_cls = score_class(app["match_score"])
                    nft = "<span class='tag tp' style='font-size:10px;'>⬡ NFT</span>" if app.get("nft_token_id") else ""
                    st.markdown(f"""
                    <div style='display:flex;align-items:center;gap:12px;padding:8px 0;
                                border-bottom:1px solid rgba(29,158,117,.08);'>
                      <div style='font-size:13px;color:#fff;font-weight:500;flex:1;'>
                        {app.get("name","Unknown")} {nft}
                      </div>
                      <div style='font-size:11px;color:#4a6a84;'>{app.get("role","")}</div>
                      <div class='sp {sc_cls}' style='font-size:11px;'>{app["match_score"]:.0f}%</div>
                      <span class='tag {"tg" if app["status"]=="Hired" else "tb" if app["status"]=="Shortlisted" else "ta"}'
                            style='font-size:10px;'>{app["status"]}</span>
                    </div>
                    """, unsafe_allow_html=True)

# ════════════════════════════════════════════════
# TAB 3: LEADERBOARD
# ════════════════════════════════════════════════
with tabs[2]:
    st.markdown("""
    <div class='s-title' style='font-size:18px;margin-bottom:6px;'>🏆 Platform Talent Leaderboard</div>
    <div class='s-sub'>Top verified talents ranked by overall score</div>
    """, unsafe_allow_html=True)

    # Compute scores for all talents
    if not talents_df.empty and not jobs_df.empty:
        sample_job = jobs_df.iloc[0]
        all_scored = [(r, rank_talents_for_job(talents_df[:1], sample_job)[0][1] if True else 0)
                      for _, r in talents_df.iterrows()]

        # Use talent_score formula
        def talent_score_fn(r):
            import json as _j
            sl = _j.loads(r["skills"]) if isinstance(r["skills"], str) else r["skills"]
            s  = min(len(sl)/8, 1) * 100
            e  = min(r["years_exp"]/10, 1) * 100
            ra = r["rating"]/5.0 * 100
            c  = r["completion_rate"]
            return round(0.30*s + 0.30*e + 0.25*ra + 0.15*c)

        leaderboard = sorted(
            [(r, talent_score_fn(r)) for _, r in talents_df.iterrows()],
            key=lambda x: x[1], reverse=True
        )[:10]

        for rank_i, (talent, ts) in enumerate(leaderboard, 1):
            av_cls, _ = AVATAR_COLS[rank_i % len(AVATAR_COLS)]
            initials = talent["name"][0] + (talent["name"].split()[-1][0] if " " in talent["name"] else "")
            medal = "🥇" if rank_i==1 else "🥈" if rank_i==2 else "🥉" if rank_i==3 else f"#{rank_i}"
            nft_badge = "<span class='tag tp' style='font-size:9px;padding:2px 6px;'>⬡ NFT</span>" if talent.get("nft_token_id") else ""

            st.markdown(f"""
            <div class='g-card' style='padding:14px 18px;margin-bottom:8px;'>
              <div style='display:flex;align-items:center;gap:14px;'>
                <div style='font-size:18px;width:28px;'>{medal}</div>
                <div class='av {av_cls}' style='width:40px;height:40px;font-size:14px;'>{initials.upper()}</div>
                <div style='flex:1;'>
                  <div style='font-size:14px;font-weight:600;color:#fff;display:flex;gap:6px;align-items:center;'>
                    {talent["name"]} {nft_badge}
                  </div>
                  <div style='font-size:11px;color:#4a6a84;'>{talent["role"]} · {talent["location"]} · {talent["years_exp"]}yr</div>
                </div>
                <div style='text-align:right;'>
                  <div style='font-family:Syne,sans-serif;font-size:20px;font-weight:700;
                              color:{"#4de8b4" if ts>=80 else "#f5c263" if ts>=65 else "#f08080"};'>
                    {ts}
                  </div>
                  <div style='font-size:10px;color:#2a4a34;'>Score</div>
                </div>
              </div>
            </div>
            """, unsafe_allow_html=True)

# ════════════════════════════════════════════════
# TAB 4: HIRE FLOW
# ════════════════════════════════════════════════
with tabs[3]:
    st.markdown("""
    <div class='s-title' style='font-size:18px;margin-bottom:6px;'>⬡ Onchain Hire Flow</div>
    <div class='s-sub'>Select a candidate to initiate escrow & mint a Work Agreement NFT</div>
    """, unsafe_allow_html=True)

    col_sel1, col_sel2 = st.columns(2)
    with col_sel1:
        hire_job_label = st.selectbox("Job:", job_titles, key="hire_job")
        hire_job_id    = int(hire_job_label.split("—")[0].replace("#","").strip())
        hire_job       = jobs_df[jobs_df["job_id"]==hire_job_id].iloc[0]

    top_for_hire = rank_talents_for_job(talents_df, hire_job, top_n=5)
    hire_options = [f"{t['name']} — {s:.0f}% match" for t, s in top_for_hire]
    with col_sel2:
        if hire_options:
            chosen = st.selectbox("Candidate:", hire_options, key="hire_cand")
            chosen_idx = hire_options.index(chosen)
            chosen_talent, chosen_score = top_for_hire[chosen_idx]
        else:
            st.info("No candidates found.")
            st.stop()

    st.markdown("<br>", unsafe_allow_html=True)

    if top_for_hire:
        col_summary, col_action = st.columns([1.4, 1], gap="large")

        with col_summary:
            prob, emoji = get_success_prob(chosen_score)
            risk_label, risk_cls = get_risk_level(chosen_talent)
            initials = chosen_talent["name"][0] + (chosen_talent["name"].split()[-1][0] if " " in chosen_talent["name"] else "")

            st.markdown(f"""
            <div class='g-card anim-up'>
              <div style='display:flex;align-items:center;gap:14px;margin-bottom:16px;'>
                <div class='av av-g' style='width:52px;height:52px;font-size:18px;'>{initials.upper()}</div>
                <div>
                  <div style='font-family:Syne,sans-serif;font-size:18px;font-weight:700;color:#fff;'>{chosen_talent["name"]}</div>
                  <div style='font-size:12px;color:#4a6a84;'>{chosen_talent["role"]} · {chosen_talent["years_exp"]} yrs</div>
                </div>
                <div style='margin-left:auto;'>
                  <div class='sp {"sp-h" if chosen_score>=78 else "sp-m" if chosen_score>=60 else "sp-l"}'>{chosen_score:.0f}%</div>
                </div>
              </div>
              <div style='display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px;margin-bottom:16px;'>
                <div style='text-align:center;padding:10px;background:rgba(29,158,117,.08);border-radius:10px;'>
                  <div style='font-size:16px;font-weight:700;color:#fff;font-family:Syne,sans-serif;'>{emoji} {prob:.0f}%</div>
                  <div style='font-size:10px;color:#4a6a84;'>Success Prob</div>
                </div>
                <div style='text-align:center;padding:10px;background:rgba(56,138,221,.08);border-radius:10px;'>
                  <div style='font-size:16px;font-weight:700;color:#fff;font-family:Syne,sans-serif;'>⭐ {chosen_talent["rating"]}</div>
                  <div style='font-size:10px;color:#4a6a84;'>Rating</div>
                </div>
                <div style='text-align:center;padding:10px;background:rgba(127,119,221,.08);border-radius:10px;'>
                  <div style='font-size:16px;font-weight:700;font-family:Syne,sans-serif;' class='{risk_cls}'>{risk_label}</div>
                  <div style='font-size:10px;color:#4a6a84;'>Risk Level</div>
                </div>
              </div>
              {html_bar("Match Score", chosen_score)}
              {html_bar("Completion Rate", float(chosen_talent["completion_rate"]))}
            </div>
            """, unsafe_allow_html=True)

        with col_action:
            st.markdown(f"""
            <div class='g-card anim-up d2' style='border-color:rgba(29,158,117,.4);'>
              <div class='s-title' style='font-size:16px;margin-bottom:14px;'>Escrow & Hire</div>
              <div style='font-size:13px;color:#4a6a84;line-height:1.8;margin-bottom:16px;'>
                💰 Budget: <span style='color:#fff;font-weight:600;'>${hire_job["budget_usdc"]:,} USDC</span><br>
                🕐 Duration: <span style='color:#fff;'>{hire_job["timeline_days"]} days</span><br>
                ⛓️ Network: <span style='color:#4de8b4;'>Polygon Amoy</span><br>
                🔒 Payment: <span style='color:#fff;'>Milestone-based escrow</span>
              </div>
            """, unsafe_allow_html=True)

            if st.button("⬡ Hire & Escrow USDC", use_container_width=True, key="hire_btn"):
                with st.spinner("⛓️ Creating Work Agreement NFT & escrowing USDC..."):
                    import time; time.sleep(1.2)
                    result = simulate_hire(
                        str(chosen_talent["wallet_address"]),
                        int(hire_job["budget_usdc"])
                    )
                st.success(f"✅ Hired! Escrow locked · Work NFT #{result['work_nft_id']}")
                st.markdown(f"""
                <div style='font-size:12px;margin-top:10px;line-height:2;'>
                  <span class='tag tg'>NFT #{result["work_nft_id"]}</span><br>
                  <span style='font-family:DM Mono,monospace;color:#2a4a34;font-size:10px;'>
                    Tx: {short_hash(result["tx_hash"])}
                  </span><br>
                  <span style='color:#1D9E75;font-size:11px;'>
                    ${result["escrow_amount"]:,} USDC locked in escrow
                  </span>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)
