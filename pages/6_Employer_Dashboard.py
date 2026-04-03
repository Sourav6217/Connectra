import streamlit as st
import json, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from styles import GLOBAL_CSS
from data.sqlite_db import (get_all_jobs, get_all_talents, get_applications_for_job,
                             book_interview, get_interviews_for_employer,
                             get_hire_history, add_hire_history, rate_hire)
from utils.matching import rank_talents_for_job, get_success_prob, get_risk_level, score_class
from utils.blockchain import simulate_hire, short_hash
from datetime import date

st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

wallet     = st.session_state.get("wallet","0x742d35Cc6634C0532925a3b844Bc454e4438f44e")
jobs_df    = get_all_jobs()
talents_df = get_all_talents()

st.markdown("""
<div class='ph aup'>
  <div class='ph-title'>Employer Hub</div>
  <div class='ph-sub'>AI-ranked candidates · Interviews · Hire flow · History</div>
</div>
""", unsafe_allow_html=True)

if jobs_df.empty:
    st.markdown("<div style='text-align:center;padding:80px;'><div style='font-size:48px;margin-bottom:16px;'>📢</div><div class='ph-title' style='margin-bottom:8px;'>No Jobs Posted Yet</div></div>", unsafe_allow_html=True)
    if st.button("Post a Job"):
        st.switch_page("pages/5_Post_Job.py")
    st.stop()

DARK = dict(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
AV_C = [("av-g","#1D9E75"),("av-b","#378ADD"),("av-a","#EF9F27"),("av-p","#7F77DD")]
job_titles = [f"#{r['job_id']} — {r['title']} ({r.get('company','')})" for _,r in jobs_df.iterrows()]

def ts_fn(r):
    try: sl = json.loads(r["skills"]) if isinstance(r["skills"],str) else r["skills"]
    except: sl = []
    return round(.30*min(len(sl)/8,1)*100 + .30*min(r["years_exp"]/10,1)*100 + .25*r["rating"]/5*100 + .15*float(r["completion_rate"]))

tabs = st.tabs(["🏆 Top Candidates", "📋 My Jobs", "📅 Interviews", "⬡ Hire Flow", "📜 Hiring History"])

# ══ TAB 1: TOP CANDIDATES ═══════════════════
with tabs[0]:
    sel_lbl = st.selectbox("Select job:", job_titles, key="top_job")
    sel_jid = int(sel_lbl.split("—")[0].replace("#","").strip())
    job_row = jobs_df[jobs_df["job_id"]==sel_jid].iloc[0]
    top     = rank_talents_for_job(talents_df, job_row, top_n=8)
    req_sk  = json.loads(job_row["required_skills"])
    st.markdown("<br>", unsafe_allow_html=True)

    col_l, col_r = st.columns([1.3, 1], gap="large")
    with col_l:
        rows_html = ""
        for i,(t,sc) in enumerate(top,1):
            try: tsk = json.loads(t["skills"]) if isinstance(t["skills"],str) else t["skills"]
            except: tsk = []
            common = set(s.lower() for s in tsk) & set(s.lower() for s in req_sk)
            prob,emoji = get_success_prob(sc)
            rl,rc = get_risk_level(t)
            sc_cls = score_class(sc)
            av_c,_ = AV_C[i%len(AV_C)]
            nm = t["name"]
            init = (nm[0]+(nm.split()[-1][0] if " " in nm else "")).upper()
            nft  = "<span class='tag tp' style='font-size:9px;'>NFT</span>" if t.get("nft_token_id") else ""
            top1 = "<span class='tag tg' style='font-size:9px;'>Top Pick</span>" if i==1 else ""
            hi   = "background:rgba(29,158,117,.05);border-radius:8px;padding:8px 6px;margin:-2px -3px;" if i==1 else ""
            rows_html += f"""
<div class='cand-row' style='{hi}'>
  <div style='font-size:12px;color:#2a3a4a;width:18px;'>#{i}</div>
  <div class='av {av_c}' style='width:36px;height:36px;font-size:12px;'>{init}</div>
  <div style='flex:1;min-width:0;'>
    <div style='font-size:12px;font-weight:600;color:#fff;display:flex;align-items:center;gap:5px;flex-wrap:wrap;'>{nm} {nft} {top1}</div>
    <div style='font-size:10px;color:#3a4a5c;'>{t["role"]} · {t["years_exp"]}yr · ★{t["rating"]} · {len(common)}/{len(req_sk)} skills</div>
    <div style='margin-top:3px;display:flex;gap:5px;'><span class='{rc}' style='font-size:9px;'>{rl}</span><span style='font-size:10px;color:#3a4a5c;'>{emoji} {prob:.0f}% success</span></div>
  </div>
  <div class='sp {sc_cls}' style='font-size:11px;'>{sc:.0f}%</div>
</div>"""
        st.markdown(f"<div class='gc aup'><div class='st2' style='margin-bottom:4px;'>Top Candidates</div><div class='st3'>Job: {job_row['title']}</div>{rows_html}</div>", unsafe_allow_html=True)

    with col_r:
        import plotly.graph_objects as go
        names  = [t["name"].split()[0] for t,_ in top]
        scores = [s for _,s in top]
        colors = ["#1D9E75" if i==0 else "#1e4a70" for i in range(len(names))]
        fig = go.Figure(go.Bar(x=scores,y=names,orientation="h",
            marker=dict(color=colors,line=dict(width=0)),
            text=[f"{s:.0f}%" for s in scores],textposition="inside",
            textfont=dict(color="white",size=11),
            hovertemplate="%{y}: %{x:.1f}%<extra></extra>"))
        fig.add_vline(x=75,line_dash="dot",line_color="#2a3a4a",line_width=1,
            annotation_text="Threshold",annotation_font_color="#3a4a5c",annotation_font_size=9)
        fig.update_layout(**DARK, xaxis=dict(range=[0,100],tickfont=dict(color="#3a4a5c",size=10),
            gridcolor="rgba(255,255,255,.03)",zerolinecolor="rgba(0,0,0,0)"),
            yaxis=dict(tickfont=dict(color="#c8d8e8",size=11)),
            margin=dict(l=0,r=20,t=10,b=20),height=240,bargap=0.3)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})

        skill_tags = " ".join(f"<span class='tag tg' style='font-size:10px;'>{s}</span>" for s in req_sk[:6])
        st.markdown(f"""
<div class='gc aup d3' style='margin-top:12px;'>
  <div class='st2' style='margin-bottom:8px;'>Job Requirements</div>
  <div style='font-size:12px;color:#3a4a5c;line-height:1.9;'>Budget: <span style='color:#fff;'>${job_row["budget_usdc"]:,}</span><br>Timeline: <span style='color:#fff;'>{job_row["timeline_days"]}d</span><br>Type: <span style='color:#fff;'>{job_row.get("location_type","Remote")}</span><br>Exp: <span style='color:#fff;'>{job_row.get("experience_required",2)}+ yr</span></div>
  <div style='margin-top:8px;'>{skill_tags}</div>
</div>
""", unsafe_allow_html=True)

# ══ TAB 2: MY JOBS ══════════════════════════
with tabs[1]:
    for _,job in jobs_df.iterrows():
        apps = get_applications_for_job(int(job["job_id"]))
        n_apps = len(apps)
        top_sc = apps["match_score"].max() if not apps.empty else 0

        st.markdown(f"""
<div class='gc aup' style='padding:16px 20px;margin-bottom:10px;'>
  <div style='display:flex;align-items:center;gap:12px;'>
    <div style='flex:1;'>
      <div style='font-size:14px;font-weight:600;color:#fff;'>{job["title"]}</div>
      <div style='font-size:11px;color:#3a4a5c;margin-top:2px;'>{job.get("company","")} · ${job["budget_usdc"]:,} · {job["timeline_days"]}d · {job.get("location_type","Remote")}</div>
    </div>
    <div style='display:flex;gap:16px;align-items:center;'>
      <div style='text-align:center;'><div style='font-size:17px;font-weight:700;color:#fff;'>{n_apps}</div><div style='font-size:9px;color:#2a3a4a;'>Apps</div></div>
      <div style='text-align:center;'><div style='font-size:17px;font-weight:700;color:#4de8b4;'>{top_sc:.0f}%</div><div style='font-size:9px;color:#2a3a4a;'>Top</div></div>
      <span class='tag tg'>Open</span>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)
        if n_apps > 0:
            with st.expander(f"View {n_apps} applicants"):
                rows_html = ""
                for _,app in apps.iterrows():
                    sc_cls = score_class(float(app.get("match_score",0)))
                    nft = "<span class='tag tp' style='font-size:9px;'>NFT</span>" if app.get("nft_token_id") else ""
                    st_c = "tg" if app.get("status")=="Hired" else "tb" if app.get("status")=="Shortlisted" else "ta"
                    rows_html += f"""
<div style='display:flex;align-items:center;gap:10px;padding:7px 0;border-bottom:1px solid rgba(255,255,255,.04);'>
  <div style='font-size:12px;color:#fff;font-weight:500;flex:1;'>{app.get("name","Unknown")} {nft}</div>
  <div style='font-size:10px;color:#3a4a5c;'>{app.get("role","")}</div>
  <div class='sp {sc_cls}' style='font-size:10px;'>{float(app.get("match_score",0)):.0f}%</div>
  <span class='tag {st_c}' style='font-size:9px;'>{app.get("status","")}</span>
</div>"""
                st.markdown(rows_html, unsafe_allow_html=True)

# ══ TAB 3: INTERVIEWS ═══════════════════════
with tabs[2]:
    st.markdown("<div class='ph-title' style='font-size:18px;margin-bottom:6px;'>Book & Manage Interviews</div><div class='st3' style='margin-bottom:20px;'>Schedule interviews with top candidates before committing to hire</div>", unsafe_allow_html=True)

    col_book, col_list = st.columns([1.2, 1.4], gap="large")

    with col_book:
        st.markdown("<div class='st2' style='margin-bottom:12px;'>Book New Interview</div>", unsafe_allow_html=True)

        iv_job_lbl = st.selectbox("Job:", job_titles, key="iv_job")
        iv_job_id  = int(iv_job_lbl.split("—")[0].replace("#","").strip())
        iv_job_row = jobs_df[jobs_df["job_id"]==iv_job_id].iloc[0]
        iv_top     = rank_talents_for_job(talents_df, iv_job_row, top_n=5)
        cand_opts  = [f"{t['name']} — {sc:.0f}% match" for t,sc in iv_top]

        if cand_opts:
            iv_cand   = st.selectbox("Candidate:", cand_opts, key="iv_cand")
            iv_idx    = cand_opts.index(iv_cand)
            iv_talent = iv_top[iv_idx][0]

            iv_date = st.date_input("Preferred Date:", value=date.today())
            iv_note = st.text_area("Note / Agenda:", placeholder="Topics to cover, expectations...", height=80)

            if st.button("📅 Book Interview", use_container_width=True):
                book_interview(
                    wallet, str(iv_talent["wallet_address"]),
                    int(iv_job_id), str(iv_talent["name"]), str(iv_job_row["title"]),
                    str(iv_date), iv_note
                )
                st.success(f"Interview booked with {iv_talent['name']}!")

    with col_list:
        st.markdown("<div class='st2' style='margin-bottom:12px;'>Upcoming Interviews</div>", unsafe_allow_html=True)
        ivs = get_interviews_for_employer(wallet)
        if ivs.empty:
            st.markdown("<div style='text-align:center;padding:30px;color:#2a3a4a;font-size:13px;'>No interviews booked yet.</div>", unsafe_allow_html=True)
        else:
            rows_html = ""
            for _,iv in ivs.iterrows():
                st_col = "tg" if iv.get("status")=="Confirmed" else "tb"
                rows_html += f"""
<div class='gc' style='padding:12px 16px;margin-bottom:8px;'>
  <div style='display:flex;align-items:center;gap:10px;'>
    <div style='flex:1;'>
      <div style='font-size:13px;font-weight:600;color:#fff;'>{iv.get("talent_name","")}</div>
      <div style='font-size:11px;color:#3a4a5c;'>{iv.get("job_title","")} · {iv.get("preferred_date","")}</div>
      <div style='font-size:11px;color:#5a7088;margin-top:2px;'>{(str(iv.get("note","")) or "")[:60]}</div>
    </div>
    <span class='tag {st_col}'>{iv.get("status","")}</span>
  </div>
</div>"""
            st.markdown(rows_html, unsafe_allow_html=True)

# ══ TAB 4: HIRE FLOW ════════════════════════
with tabs[3]:
    st.markdown("<div class='ph-title' style='font-size:18px;margin-bottom:6px;'>Onchain Hire Flow</div><div class='st3' style='margin-bottom:20px;'>Select candidate → escrow USDC → mint Work Agreement NFT</div>", unsafe_allow_html=True)

    col_s1, col_s2 = st.columns(2)
    with col_s1:
        h_job_lbl = st.selectbox("Job:", job_titles, key="hire_job")
        h_job_id  = int(h_job_lbl.split("—")[0].replace("#","").strip())
        h_job     = jobs_df[jobs_df["job_id"]==h_job_id].iloc[0]
    h_top    = rank_talents_for_job(talents_df, h_job, top_n=6)
    h_opts   = [f"{t['name']} — {sc:.0f}% match" for t,sc in h_top]
    with col_s2:
        if h_opts:
            h_cand  = st.selectbox("Candidate:", h_opts, key="hire_cand")
            h_idx   = h_opts.index(h_cand)
            h_tal, h_sc = h_top[h_idx]
        else:
            st.info("No candidates."); st.stop()

    st.markdown("<br>", unsafe_allow_html=True)
    col_sum, col_act = st.columns([1.4, 1], gap="large")

    with col_sum:
        prob,emoji = get_success_prob(h_sc)
        rl,rc = get_risk_level(h_tal)
        nm  = h_tal["name"]
        init = (nm[0]+(nm.split()[-1][0] if " " in nm else "")).upper()
        sc_cls = score_class(h_sc)
        b1 = f"""<div style='margin-bottom:8px;'><div style='display:flex;justify-content:space-between;font-size:11px;color:#3a4a5c;margin-bottom:3px;'><span>Match Score</span><span style='color:#4de8b4;font-weight:600;'>{h_sc:.0f}%</span></div><div style='background:rgba(255,255,255,.05);border-radius:3px;height:5px;'><div style='height:5px;border-radius:3px;background:#1D9E75;width:{h_sc:.1f}%;'></div></div></div>"""
        comp_v = float(h_tal["completion_rate"])
        b2 = f"""<div><div style='display:flex;justify-content:space-between;font-size:11px;color:#3a4a5c;margin-bottom:3px;'><span>Completion Rate</span><span style='color:#4de8b4;font-weight:600;'>{comp_v:.0f}%</span></div><div style='background:rgba(255,255,255,.05);border-radius:3px;height:5px;'><div style='height:5px;border-radius:3px;background:#1D9E75;width:{comp_v:.1f}%;'></div></div></div>"""

        st.markdown(f"""
<div class='gc aup'>
  <div style='display:flex;align-items:center;gap:12px;margin-bottom:14px;'>
    <div class='av av-g' style='width:48px;height:48px;font-size:16px;'>{init}</div>
    <div style='flex:1;'>
      <div style='font-size:17px;font-weight:700;color:#fff;'>{nm}</div>
      <div style='font-size:11px;color:#3a4a5c;'>{h_tal["role"]} · {h_tal["years_exp"]}yr</div>
    </div>
    <div class='sp {sc_cls}'>{h_sc:.0f}%</div>
  </div>
  <div style='display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px;margin-bottom:14px;'>
    <div style='text-align:center;padding:9px;background:rgba(29,158,117,.07);border-radius:8px;'>
      <div style='font-size:14px;font-weight:700;color:#fff;'>{emoji} {prob:.0f}%</div>
      <div style='font-size:9px;color:#3a4a5c;'>Success Prob</div>
    </div>
    <div style='text-align:center;padding:9px;background:rgba(56,138,221,.07);border-radius:8px;'>
      <div style='font-size:14px;font-weight:700;color:#fff;'>★ {h_tal["rating"]}</div>
      <div style='font-size:9px;color:#3a4a5c;'>Rating</div>
    </div>
    <div style='text-align:center;padding:9px;background:rgba(127,119,221,.07);border-radius:8px;'>
      <div class='{rc}' style='font-size:12px;'>{rl}</div>
      <div style='font-size:9px;color:#3a4a5c;margin-top:2px;'>Risk</div>
    </div>
  </div>
  {b1}{b2}
</div>
""", unsafe_allow_html=True)

    with col_act:
        st.markdown(f"""
<div class='gc aup d2' style='border-color:rgba(29,158,117,.3);'>
  <div class='st2' style='margin-bottom:12px;'>Escrow and Hire</div>
  <div style='font-size:12px;color:#3a4a5c;line-height:2;'>
    Budget: <span style='color:#fff;font-weight:600;'>${h_job["budget_usdc"]:,} USDC</span><br>
    Duration: <span style='color:#fff;'>{h_job["timeline_days"]} days</span><br>
    Network: <span style='color:#4de8b4;'>Polygon Amoy</span><br>
    Payment: <span style='color:#fff;'>Milestone escrow</span>
  </div>
</div>
""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Hire and Escrow USDC", use_container_width=True, key="hire_btn"):
            import time
            with st.spinner("Creating Work Agreement NFT..."):
                time.sleep(1)
                result = simulate_hire(str(h_tal["wallet_address"]), int(h_job["budget_usdc"]))
                # Add to hire history
                try:
                    tsk = json.loads(h_tal["skills"]) if isinstance(h_tal["skills"],str) else h_tal["skills"]
                except: tsk = []
                add_hire_history({
                    "employer_wallet": wallet,
                    "talent_wallet": str(h_tal["wallet_address"]),
                    "job_id": int(h_job["job_id"]),
                    "job_title": str(h_job["title"]),
                    "talent_name": str(h_tal["name"]),
                    "talent_role": str(h_tal["role"]),
                    "skills_used": ", ".join(tsk[:5]),
                    "start_date": str(date.today()),
                    "amount_paid": int(h_job["budget_usdc"]),
                    "status": "Ongoing",
                })
            st.success(f"Hired! Work NFT #{result['work_nft_id']}")
            st.markdown(f"""
<div style='font-size:11px;margin-top:8px;line-height:2;'>
  <span class='tag tg'>NFT #{result["work_nft_id"]}</span><br>
  <span style='font-family:DM Mono,monospace;color:#2a3a4a;font-size:9px;'>Tx: {short_hash(result["tx_hash"])}</span><br>
  <span style='color:#1D9E75;'>${result["escrow_amount"]:,} USDC locked</span>
</div>
""", unsafe_allow_html=True)

# ══ TAB 5: HIRING HISTORY ═══════════════════
with tabs[4]:
    st.markdown("<div class='ph-title' style='font-size:18px;margin-bottom:6px;'>Hiring History</div><div class='st3' style='margin-bottom:16px;'>Past and ongoing engagements. Rate completed hires to update their Talent Score.</div>", unsafe_allow_html=True)

    history_df = get_hire_history(wallet)

    if history_df.empty:
        st.markdown("<div style='text-align:center;padding:60px;color:#2a3a4a;'>No hiring history yet. Complete a hire using the Hire Flow tab.</div>", unsafe_allow_html=True)
    else:
        # Summary
        ongoing   = len(history_df[history_df["status"]=="Ongoing"]) if "status" in history_df.columns else 0
        completed = len(history_df[history_df["status"]=="Completed"]) if "status" in history_df.columns else 0
        total_amt = history_df["amount_paid"].sum() if "amount_paid" in history_df.columns else 0

        c1,c2,c3 = st.columns(3)
        for col,(val,lbl) in zip([c1,c2,c3],[
            (ongoing,"Ongoing Hires"), (completed,"Completed"), (f"${int(total_amt):,}","Total Paid")]):
            with col:
                st.markdown(f"<div class='kpi' style='text-align:center;padding:14px;'><div class='kpi-val' style='font-size:22px;'>{val}</div><div class='kpi-lbl'>{lbl}</div></div>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        for _, h in history_df.iterrows():
            status_col = "tg" if h.get("status")=="Completed" else "tb"
            rated = h.get("employer_rating") not in [None, ""]
            rating_disp = f"★ {float(h['employer_rating']):.1f}" if rated else "Not rated"
            rating_col  = "#f5c263" if rated else "#2a3a4a"
            skills_disp = str(h.get("skills_used",""))[:50]

            with st.expander(f"{h.get('talent_name','—')} · {h.get('job_title','—')} · {h.get('status','')}"):
                col_info, col_rate = st.columns([1.4, 1], gap="large")
                with col_info:
                    st.markdown(f"""
<div class='gc'>
  <div style='display:grid;grid-template-columns:1fr 1fr;gap:10px;font-size:12px;'>
    <div><div style='color:#2a3a4a;margin-bottom:2px;'>Talent</div><div style='color:#fff;font-weight:600;'>{h.get("talent_name","")}</div></div>
    <div><div style='color:#2a3a4a;margin-bottom:2px;'>Role</div><div style='color:#fff;'>{h.get("talent_role","")}</div></div>
    <div><div style='color:#2a3a4a;margin-bottom:2px;'>Job</div><div style='color:#fff;'>{h.get("job_title","")}</div></div>
    <div><div style='color:#2a3a4a;margin-bottom:2px;'>Amount Paid</div><div style='color:#4de8b4;font-weight:600;'>${int(h.get("amount_paid",0)):,}</div></div>
    <div><div style='color:#2a3a4a;margin-bottom:2px;'>Start Date</div><div style='color:#fff;'>{h.get("start_date","—")}</div></div>
    <div><div style='color:#2a3a4a;margin-bottom:2px;'>End Date</div><div style='color:#fff;'>{h.get("end_date","—") or "Ongoing"}</div></div>
  </div>
  <div style='margin-top:10px;font-size:11px;color:#3a4a5c;'><span style='color:#2a3a4a;'>Skills used:</span> {skills_disp}</div>
  <div style='margin-top:6px;font-size:11px;color:{rating_col};'>{rating_disp}</div>
  {('<div style="margin-top:6px;font-size:11px;color:#5a7088;">' + str(h.get("employer_notes","")) + '</div>') if h.get("employer_notes") else ""}
</div>
""", unsafe_allow_html=True)

                with col_rate:
                    if h.get("status") != "Completed":
                        st.markdown("<div class='st2' style='margin-bottom:10px;'>Complete & Rate</div>", unsafe_allow_html=True)
                        end_d  = st.date_input("End Date:", value=date.today(), key=f"end_{h['id']}")
                        rating = st.slider("Rating:", 1.0, 5.0, 4.0, 0.5, key=f"rat_{h['id']}")
                        notes  = st.text_area("Notes:", placeholder="Performance notes...", height=70, key=f"note_{h['id']}")
                        if st.button("Complete Engagement", key=f"complete_{h['id']}", use_container_width=True):
                            rate_hire(int(h["id"]), rating, notes, str(end_d))
                            st.success("Engagement completed! Talent Score updated.")
                            st.rerun()
                    else:
                        st.markdown(f"""
<div class='gc' style='text-align:center;padding:20px;'>
  <div style='font-size:28px;font-weight:700;color:#f5c263;'>★ {float(h.get("employer_rating",0)):.1f}</div>
  <div style='font-size:11px;color:#3a4a5c;margin-top:4px;'>Your Rating</div>
  <div style='margin-top:8px;'><span class='tag tg'>Completed</span></div>
  <div style='font-size:11px;color:#5a7088;margin-top:8px;'>This rating has been applied to the talent's profile score.</div>
</div>
""", unsafe_allow_html=True)
