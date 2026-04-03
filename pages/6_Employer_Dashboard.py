import streamlit as st
import json, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from styles import GLOBAL_CSS
from data.sqlite_db import (
  get_all_jobs, get_all_talents, get_applications_for_job,
  upsert_interview, get_interview, add_chat_message, get_chat_messages,
  set_application_status, upsert_hiring_record, complete_hiring_and_rate,
  get_hiring_history_for_employer, set_job_status,
)
from utils.matching import rank_talents_for_job, get_success_prob, get_risk_level, score_class
from utils.blockchain import simulate_hire, short_hash
from utils.ui_components import html_bar, render_hbar

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
    if st.button("Post a Job"):
        st.switch_page("pages/5_Post_Job.py")
    st.stop()

tabs = st.tabs(["🔥 Top Candidates", "📋 My Jobs", "🏆 Leaderboard", "⬡ Hire Flow", "🕘 Hiring History"])

AVATAR_COLS = [
    ("av-g","#1D9E75"), ("av-b","#378ADD"), ("av-a","#EF9F27"),
    ("av-p","#7F77DD"), ("av-g","#4de8b4"), ("av-b","#7ab8f5"),
]

def talent_score_fn(r):
    try:
        sl = json.loads(r["skills"]) if isinstance(r["skills"], str) else r["skills"]
    except Exception:
        sl = []
    s  = min(len(sl)/8, 1) * 100
    e  = min(r["years_exp"]/10, 1) * 100
    ra = r["rating"]/5.0 * 100
    c  = float(r["completion_rate"])
    ts = float(r.get("skill_test_score", 0) or 0)
    rv = float(r.get("review_score", 0) or 0)
    return round(0.26*s + 0.27*e + 0.19*ra + 0.14*c + 0.09*ts + 0.05*rv)

# ══════════════════════════════════════════
# TAB 1: TOP CANDIDATES
# ══════════════════════════════════════════
with tabs[0]:
    job_titles = [f"#{r['job_id']} — {r['title']} ({r.get('company','')})"
                  for _, r in jobs_df.iterrows()]
    selected_label = st.selectbox("Select job to analyse:", job_titles, key="top_cand_job")
    selected_job_id = int(selected_label.split("—")[0].replace("#","").strip())
    job_row = jobs_df[jobs_df["job_id"] == selected_job_id].iloc[0]

    st.markdown("<br>", unsafe_allow_html=True)

    top_matches = rank_talents_for_job(talents_df, job_row, top_n=8)

    col_list, col_chart = st.columns([1.3, 1], gap="large")

    with col_list:
        # Build entire candidate list HTML as one string — no split st.markdown calls
        req_skills = json.loads(job_row["required_skills"])
        rows_html  = ""
        for rank_i, (talent, score) in enumerate(top_matches, 1):
            try:
                t_skills = json.loads(talent["skills"]) if isinstance(talent["skills"], str) else talent["skills"]
            except Exception:
                t_skills = []
            common = set(s.lower() for s in t_skills) & set(s.lower() for s in req_skills)
            prob, emoji = get_success_prob(score)
            risk_label, risk_cls = get_risk_level(talent)
            sc_cls = score_class(score)
            av_cls, _ = AVATAR_COLS[rank_i % len(AVATAR_COLS)]
            nm = talent["name"]
            initials = nm[0] + (nm.split()[-1][0] if " " in nm else "")
            nft_badge = "<span class='tag tp' style='font-size:9px;padding:2px 6px;'>NFT</span>" if talent.get("nft_token_id") else ""
            top_badge = "<span class='tag tg' style='font-size:9px;padding:1px 6px;'>Top Pick</span>" if rank_i == 1 else ""
            hi_style  = "background:rgba(29,158,117,.06);border-radius:10px;padding:10px 8px;margin:-2px -4px;" if rank_i == 1 else ""

            rows_html += f"""
<div class='cand-row' style='{hi_style}'>
  <div style='font-family:Syne,sans-serif;font-size:13px;color:#2a4a34;width:20px;'>#{rank_i}</div>
  <div class='av {av_cls}' style='width:38px;height:38px;font-size:13px;'>{initials.upper()}</div>
  <div style='flex:1;min-width:0;'>
    <div style='font-size:13px;font-weight:600;color:#fff;display:flex;align-items:center;gap:6px;flex-wrap:wrap;'>
      {nm} {nft_badge} {top_badge}
    </div>
    <div style='font-size:11px;color:#4a6a84;margin-top:1px;'>
      {talent["role"]} · {talent["years_exp"]}yr · {talent["rating"]} · {len(common)}/{len(req_skills)} skills
    </div>
    <div style='margin-top:4px;display:flex;gap:6px;align-items:center;'>
      <span class='{risk_cls}' style='font-size:10px;'>{risk_label}</span>
      <span style='font-size:11px;color:#4a6a84;'>{emoji} {prob:.0f}% success</span>
    </div>
  </div>
  <div class='sp {sc_cls}' style='font-size:12px;'>{score:.0f}%</div>
</div>
"""

        full_card = f"""
<div class='g-card anim-up'>
  <div class='s-title' style='font-size:16px;margin-bottom:4px;'>Top Candidates</div>
  <div class='s-sub'>Ranked by AI match score · Job: {job_row["title"]}</div>
  {rows_html}
</div>
"""
        st.markdown(full_card, unsafe_allow_html=True)

    with col_chart:
        names  = [t["name"].split()[0] for t, _ in top_matches]
        scores = [s for _, s in top_matches]
        render_hbar(names, scores,
                    highlight_name=top_matches[0][0]["name"] if top_matches else "",
                    height=280)

        req_skills_list = json.loads(job_row["required_skills"])
        skill_tags = " ".join(f"<span class='tag tg' style='font-size:10px;'>{s}</span>" for s in req_skills_list)
        st.markdown(f"""
<div class='g-card anim-up d3' style='margin-top:14px;'>
  <div style='font-size:13px;font-weight:600;color:#fff;margin-bottom:10px;'>Job Requirements</div>
  <div style='font-size:12px;color:#4a6a84;line-height:1.8;'>
    Budget: <span style='color:#fff;'>${job_row["budget_usdc"]:,}</span><br>
    Timeline: <span style='color:#fff;'>{job_row["timeline_days"]} days</span><br>
    Type: <span style='color:#fff;'>{job_row.get("location_type","Remote")}</span><br>
    Exp: <span style='color:#fff;'>{job_row.get("experience_required",2)}+ years</span>
  </div>
  <div style='margin-top:10px;'>{skill_tags}</div>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════
# TAB 2: MY JOBS
# ══════════════════════════════════════════
with tabs[1]:
    for _, job in jobs_df.iterrows():
        apps    = get_applications_for_job(int(job["job_id"]))
        n_apps  = len(apps)
        top_sc  = apps["match_score"].max() if not apps.empty else 0

        st.markdown(f"""
<div class='job-card anim-up' style='margin-bottom:12px;'>
  <div style='display:flex;align-items:center;gap:14px;'>
    <div style='flex:1;'>
      <div style='font-family:Syne,sans-serif;font-size:15px;font-weight:700;color:#fff;'>
        {job["title"]}
      </div>
      <div style='font-size:12px;color:#4a6a84;margin-top:3px;'>
        {job.get("company","")} · ${job["budget_usdc"]:,} · {job["timeline_days"]}d · {job.get("location_type","Remote")}
      </div>
    </div>
    <div style='display:flex;gap:14px;align-items:center;'>
      <div style='text-align:center;'>
        <div style='font-size:18px;font-weight:700;color:#fff;font-family:Syne,sans-serif;'>{n_apps}</div>
        <div style='font-size:10px;color:#2a4a34;'>Applications</div>
      </div>
      <div style='text-align:center;'>
        <div style='font-size:18px;font-weight:700;color:#4de8b4;font-family:Syne,sans-serif;'>{top_sc:.0f}%</div>
        <div style='font-size:10px;color:#2a4a34;'>Top Score</div>
      </div>
      <span class='tag tg'>{job.get("status","Open")}</span>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

        if n_apps > 0:
            with st.expander(f"View {n_apps} applicants"):
                # Build applicant table as one HTML string
                rows_html = ""
                for _, app in apps.iterrows():
                    sc_cls = score_class(app["match_score"])
                    nft    = "<span class='tag tp' style='font-size:10px;'>NFT</span>" if app.get("nft_token_id") else ""
                    st_cl  = "tg" if app["status"]=="Hired" else "tb" if app["status"]=="Shortlisted" else "ta"
                    rows_html += f"""
<div style='display:flex;align-items:center;gap:12px;padding:8px 0;
            border-bottom:1px solid rgba(29,158,117,.08);'>
  <div style='font-size:13px;color:#fff;font-weight:500;flex:1;'>{app.get("name","Unknown")} {nft}</div>
  <div style='font-size:11px;color:#4a6a84;'>{app.get("role","")}</div>
  <div class='sp {sc_cls}' style='font-size:11px;'>{app["match_score"]:.0f}%</div>
  <span class='tag {st_cl}' style='font-size:10px;'>{app["status"]}</span>
</div>
"""
                st.markdown(rows_html, unsafe_allow_html=True)

# ══════════════════════════════════════════
# TAB 3: LEADERBOARD
# ══════════════════════════════════════════
with tabs[2]:
    st.markdown("""
<div class='s-title' style='font-size:18px;margin-bottom:6px;'>Platform Talent Leaderboard</div>
<div class='s-sub'>Top verified talents ranked by overall score</div>
""", unsafe_allow_html=True)

    leaderboard = sorted(
        [(r, talent_score_fn(r)) for _, r in talents_df.iterrows()],
        key=lambda x: x[1], reverse=True
    )[:10]

    # Build entire leaderboard as one HTML string
    lb_html = ""
    for rank_i, (talent, ts) in enumerate(leaderboard, 1):
        av_cls, _  = AVATAR_COLS[rank_i % len(AVATAR_COLS)]
        nm         = talent["name"]
        initials   = nm[0] + (nm.split()[-1][0] if " " in nm else "")
        medal      = "🥇" if rank_i==1 else "🥈" if rank_i==2 else "🥉" if rank_i==3 else f"#{rank_i}"
        nft_badge  = "<span class='tag tp' style='font-size:9px;padding:2px 6px;'>NFT</span>" if talent.get("nft_token_id") else ""
        score_col  = "#4de8b4" if ts>=80 else "#f5c263" if ts>=65 else "#f08080"
        lb_html += f"""
<div class='g-card' style='padding:14px 18px;margin-bottom:8px;'>
  <div style='display:flex;align-items:center;gap:14px;'>
    <div style='font-size:18px;width:28px;'>{medal}</div>
    <div class='av {av_cls}' style='width:40px;height:40px;font-size:14px;'>{initials.upper()}</div>
    <div style='flex:1;'>
      <div style='font-size:14px;font-weight:600;color:#fff;display:flex;gap:6px;align-items:center;'>
        {nm} {nft_badge}
      </div>
      <div style='font-size:11px;color:#4a6a84;'>{talent["role"]} · {talent.get("location","")} · {talent["years_exp"]}yr</div>
    </div>
    <div style='text-align:right;'>
      <div style='font-family:Syne,sans-serif;font-size:20px;font-weight:700;color:{score_col};'>{ts}</div>
      <div style='font-size:10px;color:#2a4a34;'>Score</div>
    </div>
  </div>
</div>
"""
    st.markdown(lb_html, unsafe_allow_html=True)

# ══════════════════════════════════════════
# TAB 4: HIRE FLOW
# ══════════════════════════════════════════
with tabs[3]:
    st.markdown("""
<div class='s-title' style='font-size:18px;margin-bottom:6px;'>Onchain Hire Flow</div>
<div class='s-sub'>Book interview + chat for credibility before escrow hiring</div>
""", unsafe_allow_html=True)

    col_sel1, col_sel2 = st.columns(2)
    with col_sel1:
        hire_job_label = st.selectbox(
            "Job:", job_titles, key="hire_job"
        )
        hire_job_id = int(hire_job_label.split("—")[0].replace("#","").strip())
        hire_job = jobs_df[jobs_df["job_id"] == hire_job_id].iloc[0]

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

    employer_wallet = st.session_state.get("wallet", "0xDemoEmployerWallet")
    chosen_wallet = str(chosen_talent["wallet_address"])

    st.markdown("<br>", unsafe_allow_html=True)
    col_summary, col_action = st.columns([1.4, 1], gap="large")

    with col_summary:
        prob, emoji = get_success_prob(chosen_score)
        risk_label, risk_cls = get_risk_level(chosen_talent)
        nm = chosen_talent["name"]
        initials = nm[0] + (nm.split()[-1][0] if " " in nm else "")
        sc_cls = score_class(chosen_score)
        bars_html = (
            html_bar("Match Score", chosen_score)
            + html_bar("Completion Rate", float(chosen_talent["completion_rate"]))
            + html_bar("Skill Test", float(chosen_talent.get("skill_test_score", 0) or 0))
            + html_bar("Employer Review", float(chosen_talent.get("review_score", 0) or 0))
        )

        st.markdown(f"""
<div class='g-card anim-up'>
  <div style='display:flex;align-items:center;gap:14px;margin-bottom:16px;'>
    <div class='av av-g' style='width:52px;height:52px;font-size:18px;'>{initials.upper()}</div>
    <div>
      <div style='font-family:Syne,sans-serif;font-size:18px;font-weight:700;color:#fff;'>{nm}</div>
      <div style='font-size:12px;color:#4a6a84;'>{chosen_talent["role"]} · {chosen_talent["years_exp"]} yrs</div>
    </div>
    <div style='margin-left:auto;'>
      <div class='sp {sc_cls}'>{chosen_score:.0f}%</div>
    </div>
  </div>
  <div style='display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px;margin-bottom:16px;'>
    <div style='text-align:center;padding:10px;background:rgba(29,158,117,.08);border-radius:10px;'>
      <div style='font-size:16px;font-weight:700;color:#fff;font-family:Syne,sans-serif;'>{emoji} {prob:.0f}%</div>
      <div style='font-size:10px;color:#4a6a84;'>Success Prob</div>
    </div>
    <div style='text-align:center;padding:10px;background:rgba(56,138,221,.08);border-radius:10px;'>
      <div style='font-size:16px;font-weight:700;color:#fff;font-family:Syne,sans-serif;'>{chosen_talent["rating"]}</div>
      <div style='font-size:10px;color:#4a6a84;'>Rating</div>
    </div>
    <div style='text-align:center;padding:10px;background:rgba(127,119,221,.08);border-radius:10px;'>
      <div style='font-size:16px;font-weight:700;font-family:Syne,sans-serif;' class='{risk_cls}'>{risk_label}</div>
      <div style='font-size:10px;color:#4a6a84;'>Risk</div>
    </div>
  </div>
  {bars_html}
</div>
""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("**Credibility Actions Before Hire**")

        interview_df = get_interview(hire_job_id, chosen_wallet)
        with st.expander("📅 Book Interview", expanded=interview_df.empty):
            c1, c2 = st.columns(2)
            with c1:
                i_date = st.date_input("Interview date", key=f"i_date_{hire_job_id}_{chosen_wallet}")
                i_time = st.time_input("Interview time", key=f"i_time_{hire_job_id}_{chosen_wallet}")
            with c2:
                i_mode = st.selectbox(
                    "Mode", ["Video", "Audio", "Chat"],
                    key=f"i_mode_{hire_job_id}_{chosen_wallet}"
                )
                i_notes = st.text_input("Notes", key=f"i_note_{hire_job_id}_{chosen_wallet}")
            if st.button("Book Interview", key=f"book_interview_{hire_job_id}_{chosen_wallet}"):
                scheduled_at = f"{i_date} {i_time.strftime('%H:%M')}"
                upsert_interview(hire_job_id, chosen_wallet, employer_wallet, scheduled_at, i_mode, i_notes)
                set_application_status(chosen_wallet, hire_job_id, "Interview Scheduled")
                st.success("Interview booked.")
                st.rerun()

            if not interview_df.empty:
                irow = interview_df.iloc[0]
                st.info(f"Scheduled: {irow['scheduled_at']} · {irow['mode']} · {irow['status']}")

        with st.expander("💬 Employer Chat", expanded=False):
            msgs = get_chat_messages(hire_job_id, chosen_wallet, employer_wallet)
            if msgs.empty:
                st.caption("No messages yet.")
            else:
                for _, msg in msgs.tail(8).iterrows():
                    label = "You" if msg["sender_role"] == "Employer" else "Talent"
                    st.markdown(
                        f"<div style='font-size:12px;padding:8px 10px;margin-bottom:6px;border-radius:10px;"
                        f"background:{'rgba(29,158,117,.12)' if label == 'You' else 'rgba(56,138,221,.12)'};'>"
                        f"<strong>{label}</strong> · <span style='color:#4a6a84;'>{msg['sent_at']}</span><br>{msg['message']}</div>",
                        unsafe_allow_html=True,
                    )
            chat_msg = st.text_input("Type a message", key=f"chat_box_{hire_job_id}_{chosen_wallet}")
            if st.button("Send", key=f"chat_send_{hire_job_id}_{chosen_wallet}") and chat_msg.strip():
                add_chat_message(hire_job_id, chosen_wallet, employer_wallet, "Employer", chat_msg.strip())
                st.rerun()

    with col_action:
        st.markdown(f"""
<div class='g-card anim-up d2' style='border-color:rgba(29,158,117,.4);'>
  <div class='s-title' style='font-size:16px;margin-bottom:14px;'>Escrow and Hire</div>
  <div style='font-size:13px;color:#4a6a84;line-height:1.8;margin-bottom:16px;'>
    Budget: <span style='color:#fff;font-weight:600;'>${hire_job["budget_usdc"]:,} USDC</span><br>
    Duration: <span style='color:#fff;'>{hire_job["timeline_days"]} days</span><br>
    Network: <span style='color:#4de8b4;'>Polygon Amoy</span><br>
    Payment: <span style='color:#fff;'>Milestone-based escrow</span>
  </div>
</div>
""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Hire and Escrow USDC", use_container_width=True, key="hire_btn"):
            with st.spinner("Creating Work Agreement NFT and escrowing USDC..."):
                import time
                time.sleep(1.2)
                result = simulate_hire(chosen_wallet, int(hire_job["budget_usdc"]))
            set_application_status(chosen_wallet, hire_job_id, "Hired")
            upsert_hiring_record(
                hire_job_id,
                chosen_wallet,
                employer_wallet,
                status="Ongoing",
                fees_paid_usdc=0,
                skills_used=hire_job.get("required_skills", "[]"),
                duration_days=int(hire_job["timeline_days"]),
                notes=f"Work NFT #{result['work_nft_id']} created",
            )
            set_job_status(hire_job_id, "In Progress")
            st.success(f"Hired! Escrow locked · Work NFT #{result['work_nft_id']}")
            st.markdown(f"""
<div style='font-size:12px;margin-top:10px;line-height:2;'>
  <span class='tag tg'>NFT #{result["work_nft_id"]}</span><br>
  <span style='font-family:DM Mono,monospace;color:#2a4a34;font-size:10px;'>Tx: {short_hash(result["tx_hash"])}</span><br>
  <span style='color:#1D9E75;font-size:11px;'>${result["escrow_amount"]:,} USDC locked</span>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════
# TAB 5: HIRING HISTORY
# ══════════════════════════════════════════
with tabs[4]:
    st.markdown("""
<div class='s-title' style='font-size:18px;margin-bottom:6px;'>Past Hiring / Hiring History</div>
<div class='s-sub'>Track ongoing vs ended engagements, paid amount, and rate delivered talent</div>
""", unsafe_allow_html=True)

    employer_wallet = st.session_state.get("wallet", "0xDemoEmployerWallet")
    history_df = get_hiring_history_for_employer(employer_wallet)

    if history_df.empty:
        st.info("No hiring records yet. Hire from the Hire Flow tab to populate history.")
    else:
        ongoing = history_df[history_df["status"] == "Ongoing"]
        ended = history_df[history_df["status"] == "Ended & Paid"]
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Engagements", len(history_df))
        c2.metric("Ongoing", len(ongoing))
        c3.metric("Ended & Paid", len(ended))

        st.markdown("<br>", unsafe_allow_html=True)
        for _, h in history_df.iterrows():
            status_tag = "tg" if h["status"] == "Ended & Paid" else "tb"
            rating_txt = f"{h['rating_by_employer']}/5" if h.get("rating_by_employer") else "Not rated"
            fees_paid = float(h.get("fees_paid_usdc", 0) or 0)

            st.markdown(f"""
<div class='g-card' style='margin-bottom:10px;'>
  <div style='display:flex;align-items:center;gap:12px;'>
    <div style='flex:1;'>
      <div style='font-size:15px;font-weight:700;color:#fff;'>{h['job_title']} · {h['company']}</div>
      <div style='font-size:12px;color:#4a6a84;margin-top:2px;'>
        Talent: {h['name']} ({h['role']}) · {h['years_exp']} yrs
      </div>
      <div style='font-size:11px;color:#4a6a84;margin-top:6px;'>
        Duration: {int(h.get('duration_days', 0) or 0)} days · Fees Paid: ${fees_paid:,.0f} · Rating: {rating_txt}
      </div>
    </div>
    <span class='tag {status_tag}'>{h['status']}</span>
  </div>
</div>
""", unsafe_allow_html=True)

            if h["status"] == "Ongoing":
                with st.expander(f"Close & Rate: {h['name']} for job #{int(h['job_id'])}"):
                    rc1, rc2 = st.columns(2)
                    with rc1:
                        end_fee = st.number_input(
                            "Fees paid (USDC)",
                            min_value=0,
                            value=int(h.get("fees_paid_usdc", 0) or 0),
                            key=f"fee_{int(h['id'])}",
                        )
                        end_duration = st.number_input(
                            "Duration (days)",
                            min_value=1,
                            value=max(1, int(h.get("duration_days", 1) or 1)),
                            key=f"dur_{int(h['id'])}",
                        )
                    with rc2:
                        end_rating = st.slider("Rate talent", 1.0, 5.0, 4.0, 0.1, key=f"rate_{int(h['id'])}")
                        skills_used = st.text_area(
                            "Skills used (comma separated)",
                            value=", ".join(json.loads(h.get("skills_used", "[]"))) if str(h.get("skills_used", "")).startswith("[") else str(h.get("skills_used", "")),
                            key=f"skills_{int(h['id'])}",
                        )
                    end_notes = st.text_input("Notes", key=f"notes_{int(h['id'])}")
                    if st.button("Mark Ended & Paid", key=f"close_{int(h['id'])}"):
                        complete_hiring_and_rate(
                            int(h["job_id"]),
                            str(h["talent_wallet"]),
                            employer_wallet,
                            float(end_fee),
                            int(end_duration),
                            float(end_rating),
                            skills_used,
                            end_notes,
                        )
                        set_job_status(int(h["job_id"]), "Closed")
                        st.success("Hiring record completed and talent rating saved.")
                        st.rerun()
