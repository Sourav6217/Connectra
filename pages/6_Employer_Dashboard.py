import streamlit as st
import json, sys, os
from datetime import date, timedelta

from styles import GLOBAL_CSS
from data.sqlite_db import (
    get_all_jobs, get_all_talents, get_applications_for_job,
    insert_interview, get_interviews_for_employer, get_hiring_history,
    insert_hiring_record, rate_past_hire, insert_message, get_messages
)
from utils.matching import rank_talents_for_job, get_success_prob, get_risk_level, score_class, calculate_talent_score
from utils.blockchain import simulate_hire, short_hash
from utils.ui_components import html_bar, render_hbar

st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

# ── Back navigation ─────────────────────────────────────────────────────────
def _back_button(label="← Back"):
    if st.button(label, key="_back_btn"):
        target = st.session_state.get("prev_page", "home")
        st.session_state.prev_page = st.session_state.current_page
        st.session_state.current_page = target
        st.rerun()

_back_button()

jobs_df    = get_all_jobs()
talents_df = get_all_talents()
employer_wallet = st.session_state.get("wallet", "0xDemoEmployerWallet")

st.markdown("""
<div class='anim-up' style='margin-bottom:20px;'>
  <div class='s-title' style='font-size:26px;'>Employer Hub</div>
  <div class='s-sub'>AI-ranked candidates · Interview booking · Onchain hire flow</div>
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
        st.session_state.current_page = "postjob"; st.rerun()
    st.stop()

tabs = st.tabs(["Top Candidates", "My Jobs", "Leaderboard", "Hire Flow", "Hiring History"])

AVATAR_COLS = [
    ("av-g","#1D9E75"), ("av-b","#378ADD"), ("av-a","#EF9F27"),
    ("av-p","#7F77DD"), ("av-g","#4de8b4"), ("av-b","#7ab8f5"),
]

# ══════════════════════════════════════════════════════════════
# TAB 1: TOP CANDIDATES + INTERVIEW BOOKING + CHAT
# ══════════════════════════════════════════════════════════════
with tabs[0]:
    job_titles = [f"#{r['job_id']} — {r['title']} ({r.get('company','')})"
                  for _, r in jobs_df.iterrows()]
    selected_label = st.selectbox("Select job to analyse:", job_titles, key="top_cand_job")
    selected_job_id = int(selected_label.split("—")[0].replace("#","").strip())
    job_row = jobs_df[jobs_df["job_id"] == selected_job_id].iloc[0]

    st.markdown("<br>", unsafe_allow_html=True)
    top_matches = rank_talents_for_job(talents_df, job_row, top_n=8)

    col_list, col_action = st.columns([1.3, 1], gap="large")

    with col_list:
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
            test_bonus = float(talent.get("test_score_bonus", 0))
            test_badge = f"<span class='tag tc' style='font-size:9px;padding:2px 6px;'>Tested</span>" if test_bonus > 0 else ""
            hi_style = "background:rgba(29,158,117,.06);border-radius:10px;padding:10px 8px;margin:-2px -4px;" if rank_i == 1 else ""

            rows_html += f"""
<div class='cand-row' style='{hi_style}' id='cand_{rank_i}'>
  <div style='font-family:Syne,sans-serif;font-size:13px;color:#2a4a34;width:20px;'>#{rank_i}</div>
  <div class='av {av_cls}' style='width:38px;height:38px;font-size:13px;'>{initials.upper()}</div>
  <div style='flex:1;min-width:0;'>
    <div style='font-size:13px;font-weight:600;color:#fff;display:flex;align-items:center;gap:5px;flex-wrap:wrap;'>
      {nm} {nft_badge} {top_badge} {test_badge}
    </div>
    <div style='font-size:11px;color:#4a6a84;margin-top:1px;'>
      {talent["role"]} · {talent["years_exp"]}yr · ⭐{talent["rating"]} · {len(common)}/{len(req_skills)} skills
    </div>
    <div style='margin-top:3px;display:flex;gap:6px;align-items:center;'>
      <span class='{risk_cls}' style='font-size:10px;'>{risk_label}</span>
      <span style='font-size:11px;color:#4a6a84;'>{emoji} {prob:.0f}% success</span>
    </div>
  </div>
  <div class='sp {sc_cls}' style='font-size:12px;'>{score:.0f}%</div>
</div>
"""
        st.markdown(f"""
<div class='g-card anim-up'>
  <div class='s-title' style='font-size:16px;margin-bottom:4px;'>Top Candidates</div>
  <div class='s-sub'>Ranked by AI match score · {job_row["title"]}</div>
  {rows_html}
</div>
""", unsafe_allow_html=True)

    with col_action:
        names  = [t["name"].split()[0] for t, _ in top_matches]
        scores = [s for _, s in top_matches]
        render_hbar(names, scores,
                    highlight_name=top_matches[0][0]["name"] if top_matches else "",
                    height=240)

        # ── Interview Booking Panel ─────────────────────────────
        st.markdown("""
<div class='g-card anim-up d2' style='margin-top:14px;border-color:rgba(56,138,221,.25);'>
  <div style='display:flex;align-items:center;gap:8px;margin-bottom:14px;'>
    <svg width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='#378ADD' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'><rect x='3' y='4' width='18' height='18' rx='2' ry='2'/><line x1='16' y1='2' x2='16' y2='6'/><line x1='8' y1='2' x2='8' y2='6'/><line x1='3' y1='10' x2='21' y2='10'/></svg>
    <div style='font-size:15px;font-weight:600;color:#fff;'>Book Interview</div>
  </div>
""", unsafe_allow_html=True)

        # Select candidate from top matches
        candidate_options = [f"#{i+1} — {t['name']}" for i, (t, _) in enumerate(top_matches[:5])]
        selected_cand_label = st.selectbox("Select candidate:", candidate_options, key="interview_cand")
        cand_idx = int(selected_cand_label.split("—")[0].replace("#","").strip()) - 1
        selected_talent, selected_score = top_matches[cand_idx]

        interview_date = st.date_input(
            "Interview date",
            value=date.today() + timedelta(days=3),
            min_value=date.today(),
            key="interview_date"
        )
        interview_time = st.selectbox(
            "Time slot",
            ["10:00 AM", "11:00 AM", "2:00 PM", "3:00 PM", "4:00 PM", "5:00 PM"],
            key="interview_time"
        )
        interview_notes = st.text_input(
            "Notes (optional)",
            placeholder="e.g. Video call via Google Meet",
            key="interview_notes"
        )

        if st.button("Schedule Interview", use_container_width=True, key="book_interview"):
            try:
                iid = insert_interview(
                    talent_wallet=selected_talent["wallet_address"],
                    job_id=int(job_row["job_id"]),
                    employer_wallet=employer_wallet,
                    scheduled_date=str(interview_date),
                    scheduled_time=interview_time,
                    notes=interview_notes
                )
                st.success(f"Interview scheduled! ID #{iid}")
            except Exception as e:
                st.error(f"Could not schedule interview: {e}")

        st.markdown("</div>", unsafe_allow_html=True)

        # ── Quick Chat Panel ─────────────────────────────────────
        st.markdown("""
<div class='g-card anim-up d3' style='margin-top:0;border-color:rgba(127,119,221,.2);'>
  <div style='display:flex;align-items:center;gap:8px;margin-bottom:12px;'>
    <svg width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='#7F77DD' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'><path d='M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z'/></svg>
    <div style='font-size:15px;font-weight:600;color:#fff;'>Message Candidate</div>
  </div>
""", unsafe_allow_html=True)

        # Use a fake interview_id based on job+talent combination (demo mode)
        demo_iid = (int(job_row["job_id"]) * 1000) + cand_idx
        msgs_df = get_messages(demo_iid)

        if not msgs_df.empty:
            for _, msg in msgs_df.tail(4).iterrows():
                is_me = msg["sender_role"] == "employer"
                align = "flex-end" if is_me else "flex-start"
                bg = "rgba(29,158,117,.15)" if is_me else "rgba(56,138,221,.1)"
                name_color = "#4de8b4" if is_me else "#7ab8f5"
                st.markdown(f"""
<div style='display:flex;flex-direction:column;align-items:{align};margin-bottom:6px;'>
  <div style='font-size:10px;color:{name_color};margin-bottom:2px;'>
    {"You" if is_me else msg["sender_wallet"][:8]+"..."}
  </div>
  <div style='max-width:85%;padding:8px 12px;background:{bg};
              border-radius:12px;font-size:12px;color:#c8d8e8;line-height:1.5;'>
    {msg["message"]}
  </div>
</div>
""", unsafe_allow_html=True)
        else:
            st.markdown("""
<div style='text-align:center;padding:12px;font-size:12px;color:#2a4a34;'>
  No messages yet. Start the conversation.
</div>
""", unsafe_allow_html=True)

        chat_msg = st.text_input(
            "Type a message...",
            placeholder="Hello! I reviewed your profile...",
            key=f"chat_input_{cand_idx}_{selected_job_id}",
            label_visibility="collapsed"
        )
        if st.button("Send", key=f"send_msg_{cand_idx}", use_container_width=False):
            if chat_msg.strip():
                insert_message(demo_iid, employer_wallet, "employer", chat_msg.strip())
                st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# TAB 2: MY JOBS
# ══════════════════════════════════════════════════════════════
with tabs[1]:
    for _, job in jobs_df.iterrows():
        apps    = get_applications_for_job(int(job["job_id"]))
        n_apps  = len(apps)
        top_sc  = apps["match_score"].max() if not apps.empty else 0

        st.markdown(f"""
<div class='job-card anim-up' style='margin-bottom:12px;'>
  <div style='display:flex;align-items:center;gap:14px;'>
    <div style='flex:1;'>
      <div style='font-family:Syne,sans-serif;font-size:15px;font-weight:700;color:#fff;'>{job["title"]}</div>
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
      <span class='tag tg'>Open</span>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

        if n_apps > 0:
            with st.expander(f"View {n_apps} applicants"):
                rows_html = ""
                for _, app in apps.iterrows():
                    sc_cls = score_class(app["match_score"])
                    nft    = "<span class='tag tp' style='font-size:10px;'>NFT</span>" if app.get("nft_token_id") else ""
                    test_b = float(app.get("test_score_bonus", 0))
                    test_t = f"<span class='tag tc' style='font-size:10px;'>Tested +{test_b:.1f}</span>" if test_b > 0 else ""
                    st_cl  = "tg" if app["status"]=="Hired" else "tb" if app["status"]=="Shortlisted" else "ta"
                    rows_html += f"""
<div style='display:flex;align-items:center;gap:12px;padding:8px 0;
            border-bottom:1px solid rgba(29,158,117,.08);'>
  <div style='font-size:13px;color:#fff;font-weight:500;flex:1;'>{app.get("name","Unknown")} {nft} {test_t}</div>
  <div style='font-size:11px;color:#4a6a84;'>{app.get("role","")}</div>
  <div class='sp {sc_cls}' style='font-size:11px;'>{app["match_score"]:.0f}%</div>
  <span class='tag {st_cl}' style='font-size:10px;'>{app["status"]}</span>
</div>
"""
                st.markdown(rows_html, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# TAB 3: LEADERBOARD
# ══════════════════════════════════════════════════════════════
with tabs[2]:
    st.markdown("""
<div class='s-title' style='font-size:18px;margin-bottom:6px;'>Platform Talent Leaderboard</div>
<div class='s-sub'>Top verified talents ranked by overall talent score</div>
""", unsafe_allow_html=True)

    scored = []
    for _, t in talents_df.iterrows():
        scored.append((t, calculate_talent_score(t)))
    scored.sort(key=lambda x: x[1], reverse=True)
    top_talents = scored[:12]

    MEDAL = {1:"🥇", 2:"🥈", 3:"🥉"}
    lb_html = ""
    for rank_i, (talent, ts) in enumerate(top_talents, 1):
        try:
            t_skills = json.loads(talent["skills"]) if isinstance(talent["skills"], str) else talent["skills"]
        except Exception:
            t_skills = []
        nft_b  = "<span class='tag tp' style='font-size:9px;'>NFT</span>" if talent.get("nft_token_id") else ""
        test_b = float(talent.get("test_score_bonus", 0))
        test_t = f"<span class='tag tc' style='font-size:9px;'>+{test_b:.1f} test</span>" if test_b > 0 else ""
        medal  = MEDAL.get(rank_i, f"#{rank_i}")
        av_cls = AVATAR_COLS[rank_i % len(AVATAR_COLS)][0]
        initials = talent["name"][0] + (talent["name"].split()[-1][0] if " " in talent["name"] else "")
        sc_cls = score_class(ts)
        lb_html += f"""
<div class='cand-row'>
  <div style='font-size:14px;width:28px;text-align:center;'>{medal}</div>
  <div class='av {av_cls}' style='width:36px;height:36px;font-size:12px;'>{initials.upper()}</div>
  <div style='flex:1;min-width:0;'>
    <div style='font-size:13px;font-weight:600;color:#fff;display:flex;align-items:center;gap:5px;'>
      {talent["name"]} {nft_b} {test_t}
    </div>
    <div style='font-size:11px;color:#4a6a84;'>{talent["role"]} · {talent["years_exp"]}yr · {talent["location"]}</div>
  </div>
  <div class='sp {sc_cls}'>{ts:.0f}</div>
</div>
"""
    st.markdown(f"<div class='g-card anim-up'>{lb_html}</div>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# TAB 4: HIRE FLOW
# ══════════════════════════════════════════════════════════════
with tabs[3]:
    st.markdown("""
<div class='s-title' style='font-size:18px;margin-bottom:6px;'>Onchain Hire Flow</div>
<div class='s-sub'>Escrow USDC · Mint Work Agreement NFT · Both parties get onchain proof</div>
""", unsafe_allow_html=True)

    col_sel, col_detail = st.columns([1, 1.4], gap="large")

    with col_sel:
        hire_job_label = st.selectbox("Job:", job_titles, key="hire_job")
        hire_job_id = int(hire_job_label.split("—")[0].replace("#","").strip())
        hire_job = jobs_df[jobs_df["job_id"] == hire_job_id].iloc[0]

        apps = get_applications_for_job(hire_job_id)
        if apps.empty:
            st.info("No applications for this job yet.")
        else:
            cand_opts = [f"{r['name']} — {r['match_score']:.0f}% match" for _, r in apps.iterrows()]
            selected_app_label = st.selectbox("Candidate:", cand_opts, key="hire_cand")
            selected_app_row = apps.iloc[cand_opts.index(selected_app_label)]

            escrowed = int(hire_job["budget_usdc"])
            st.markdown(f"""
<div class='g-card' style='text-align:center;margin-top:10px;'>
  <div style='font-size:11px;color:#2a4a34;margin-bottom:4px;'>ESCROW AMOUNT</div>
  <div style='font-family:Syne,sans-serif;font-size:32px;font-weight:800;color:#fff;'>${escrowed:,}</div>
  <div style='font-size:11px;color:#1D9E75;'>USDC · Polygon Amoy</div>
</div>
""", unsafe_allow_html=True)

            if st.button("Hire Onchain", use_container_width=True, key="hire_btn"):
                import time
                with st.spinner("Recording on Polygon Amoy..."):
                    time.sleep(0.8)
                    result = simulate_hire(selected_app_row["talent_wallet"], escrowed)
                    # Record in hiring history
                    insert_hiring_record({
                        "employer_wallet": employer_wallet,
                        "talent_wallet": selected_app_row["talent_wallet"],
                        "job_id": hire_job_id,
                        "job_title": hire_job["title"],
                        "company": hire_job.get("company", ""),
                        "amount_paid_usdc": escrowed,
                        "skills_used": hire_job["required_skills"],
                        "tx_hash": result["tx_hash"],
                    })

                st.success(f"Hired! Work Agreement NFT #{result['work_nft_id']}")
                st.markdown(f"""
<div class='g-card' style='border-color:rgba(29,158,117,.5);margin-top:10px;font-size:12px;'>
  <div>Tx: <span style='font-family:DM Mono,monospace;color:#4de8b4;'>{short_hash(result["tx_hash"])}</span></div>
  <div style='margin-top:6px;'>Escrow: <span style='color:#fff;'>${escrowed:,} USDC locked</span></div>
  <a href='{result["explorer"]}' target='_blank' style='color:#1D9E75;font-size:11px;display:block;margin-top:8px;'>
    View on Polygonscan →
  </a>
</div>
""", unsafe_allow_html=True)

    with col_detail:
        st.markdown("""
<div class='g-card anim-up d2'>
  <div class='s-title' style='font-size:16px;margin-bottom:14px;'>How the Hire Flow Works</div>
  <div style='font-size:13px;color:#4a6a84;line-height:1.9;'>
    <div style='margin-bottom:12px;display:flex;align-items:flex-start;gap:8px;'>
      <svg width='14' height='14' viewBox='0 0 24 24' fill='none' stroke='#1D9E75' stroke-width='2' style='margin-top:2px;flex-shrink:0;'><circle cx='12' cy='12' r='10'/><polyline points='12 6 12 12 16 14'/></svg>
      <span><strong style='color:#c8d8e8;'>Schedule Interview</strong> first via the Top Candidates tab to shortlist the candidate.</span>
    </div>
    <div style='margin-bottom:12px;display:flex;align-items:flex-start;gap:8px;'>
      <svg width='14' height='14' viewBox='0 0 24 24' fill='none' stroke='#378ADD' stroke-width='2' style='margin-top:2px;flex-shrink:0;'><rect x='3' y='11' width='18' height='11' rx='2' ry='2'/><path d='M7 11V7a5 5 0 0 1 10 0v4'/></svg>
      <span><strong style='color:#c8d8e8;'>USDC Escrowed</strong> automatically on Polygon. Funds locked until milestone release.</span>
    </div>
    <div style='margin-bottom:12px;display:flex;align-items:flex-start;gap:8px;'>
      <svg width='14' height='14' viewBox='0 0 24 24' fill='none' stroke='#7F77DD' stroke-width='2' style='margin-top:2px;flex-shrink:0;'><polygon points='12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2'/></svg>
      <span><strong style='color:#c8d8e8;'>Work Agreement NFT</strong> minted for both parties as tamper-proof proof of engagement.</span>
    </div>
    <div style='display:flex;align-items:flex-start;gap:8px;'>
      <svg width='14' height='14' viewBox='0 0 24 24' fill='none' stroke='#EF9F27' stroke-width='2' style='margin-top:2px;flex-shrink:0;'><polyline points='9 11 12 14 22 4'/><path d='M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11'/></svg>
      <span><strong style='color:#c8d8e8;'>Rate after completion</strong> from Hiring History tab — ratings update talent score onchain.</span>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# TAB 5: HIRING HISTORY
# ══════════════════════════════════════════════════════════════
with tabs[4]:
    st.markdown("""
<div class='s-title' style='font-size:18px;margin-bottom:6px;'>Hiring History</div>
<div class='s-sub'>All past and ongoing hires · Rate completed work to update talent reputation</div>
""", unsafe_allow_html=True)

    history_df = get_hiring_history(employer_wallet)

    if history_df.empty:
        st.markdown("""
<div style='text-align:center;padding:60px;'>
  <div style='font-size:40px;margin-bottom:14px;'>
    <svg width='40' height='40' viewBox='0 0 24 24' fill='none' stroke='#2a4a34' stroke-width='1.5'><path d='M12 20h9'/><path d='M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z'/></svg>
  </div>
  <div style='font-size:14px;color:#2a4a34;'>No hires recorded yet.</div>
  <div style='font-size:12px;color:#1a2a1a;margin-top:4px;'>Use the Hire Flow tab to make your first hire.</div>
</div>
""", unsafe_allow_html=True)
    else:
        # Summary stats
        ongoing = len(history_df[history_df["status"] == "Ongoing"])
        completed = len(history_df[history_df["status"] == "Completed"])
        total_paid = int(history_df["amount_paid_usdc"].sum())

        c1, c2, c3 = st.columns(3)
        for col, (val, lbl) in zip([c1, c2, c3], [
            (ongoing, "Ongoing"),
            (completed, "Completed"),
            (f"${total_paid:,}", "Total Paid (USDC)"),
        ]):
            with col:
                st.markdown(f"""
<div class='m-card' style='text-align:center;'>
  <div class='m-lbl'>{lbl}</div>
  <div class='m-val' style='font-size:22px;'>{val}</div>
</div>
""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        for _, hire in history_df.iterrows():
            is_ongoing = hire["status"] == "Ongoing"
            status_cls = "ta" if is_ongoing else "tg"
            try:
                skills_used = json.loads(hire["skills_used"]) if hire["skills_used"] else []
            except Exception:
                skills_used = []
            skill_tags = " ".join(f"<span class='tag tg' style='font-size:10px;'>{s}</span>" for s in skills_used[:5])

            with st.expander(f"{'🔄' if is_ongoing else '✅'} {hire['job_title']} — {hire['talent_name']}"):
                col_info, col_rate = st.columns([1.4, 1], gap="large")

                with col_info:
                    st.markdown(f"""
<div style='font-size:13px;line-height:2;color:#4a6a84;'>
  <div><strong style='color:#c8d8e8;'>Talent:</strong> {hire["talent_name"]} · {hire.get("talent_role","")}</div>
  <div><strong style='color:#c8d8e8;'>Role:</strong> {hire["job_title"]}</div>
  <div><strong style='color:#c8d8e8;'>Company:</strong> {hire.get("company","—")}</div>
  <div><strong style='color:#c8d8e8;'>Amount Paid:</strong> <span style='color:#4de8b4;'>${hire["amount_paid_usdc"]:,} USDC</span></div>
  <div><strong style='color:#c8d8e8;'>Start Date:</strong> {hire.get("start_date","—")}</div>
  <div><strong style='color:#c8d8e8;'>Status:</strong> <span class='tag {status_cls}'>{hire["status"]}</span></div>
</div>
<div style='margin-top:10px;'><strong style='font-size:12px;color:#2a4a34;'>Skills Used:</strong><br>{skill_tags}</div>
""", unsafe_allow_html=True)

                with col_rate:
                    if is_ongoing:
                        st.markdown("""
<div style='font-size:12px;color:#f5c263;padding:10px;background:rgba(239,159,39,.08);
            border-radius:10px;border:1px solid rgba(239,159,39,.2);'>
  Contract is ongoing. Complete the work and mark it done to leave a rating.
</div>
""", unsafe_allow_html=True)
                    elif hire.get("employer_rating") is not None:
                        st.markdown(f"""
<div style='font-size:13px;color:#4a6a84;'>
  <strong style='color:#fff;'>Your Rating:</strong>
  <span style='color:#f5c263;font-size:20px;margin-left:6px;'>{'⭐' * int(hire["employer_rating"])}</span>
  <span style='color:#4de8b4;font-size:14px;font-weight:600;margin-left:4px;'>{hire["employer_rating"]}/5</span>
</div>
<div style='font-size:12px;color:#4a6a84;margin-top:6px;font-style:italic;'>
  "{hire.get("employer_feedback","")}"
</div>
""", unsafe_allow_html=True)
                    else:
                        st.markdown("""
<div style='font-size:13px;font-weight:600;color:#fff;margin-bottom:10px;'>Rate this hire</div>
""", unsafe_allow_html=True)
                        rating_val = st.slider(
                            "Rating", 1.0, 5.0, 4.0, 0.5,
                            key=f"rate_{hire['id']}", format="%.1f"
                        )
                        feedback_val = st.text_area(
                            "Feedback",
                            placeholder="How was the collaboration?",
                            key=f"fb_{hire['id']}",
                            height=80
                        )
                        if st.button("Submit Rating", key=f"rate_btn_{hire['id']}"):
                            rate_past_hire(
                                int(hire["id"]), rating_val,
                                feedback_val, hire["talent_wallet"]
                            )
                            st.success("Rating submitted! Talent score updated.")
                            st.rerun()
