import streamlit as st
import plotly.graph_objects as go
import json, sys, os, time
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from styles import GLOBAL_CSS
from data.sqlite_db import (get_talent, get_applications_for_talent, get_all_jobs,
                             get_test_results, save_test_result, has_taken_test,
                             get_interviews_for_talent)
from data.skill_questions import get_questions
from utils.matching import calculate_match, get_risk_level, score_class
from utils.blockchain import format_wallet, short_hash

st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

wallet = st.session_state.get("wallet","0x742d35Cc6634C0532925a3b844Bc454e4438f44e")
df     = get_talent(wallet)

if df.empty:
    st.markdown("""
<div style='text-align:center;padding:80px;'>
  <div style='font-size:48px;margin-bottom:16px;'>👤</div>
  <div class='ph-title' style='margin-bottom:8px;'>No Profile Found</div>
  <div style='font-size:13px;color:#3a4a5c;margin-bottom:24px;'>Create your verified profile to get started.</div>
</div>
""", unsafe_allow_html=True)
    if st.button("Create Profile"):
        st.switch_page("pages/2_Create_Profile.py")
    st.stop()

row   = df.iloc[0]
skills_list = json.loads(row["skills"]) if isinstance(row["skills"],str) else row["skills"]
test_bonus  = float(row.get("test_bonus") or 0)

# Talent score
exp_s  = min(row["years_exp"]/10, 1)*100
rat_s  = row["rating"]/5*100
comp_s = float(row["completion_rate"])
sk_s   = min(len(skills_list)/8, 1)*100
base_s = round(0.30*sk_s + 0.30*exp_s + 0.25*rat_s + 0.15*comp_s)
talent_score = round(base_s * 0.85 + test_bonus * 0.15) if test_bonus > 0 else base_s
risk_label, risk_cls = get_risk_level(row)

TAG_C  = ["tg","tb","ta","tp","tc"]
SCTAG  = {"Pending":"ta","Shortlisted":"tb","Hired":"tg","Rejected":"tr"}
AV_C   = ["av-g","av-b","av-a","av-p"]
DARK   = dict(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")

st.markdown(f"""
<div class='ph aup'>
  <div class='ph-title'>My Dashboard</div>
  <div class='ph-sub'>Verified on-chain identity · {format_wallet(wallet)}</div>
</div>
""", unsafe_allow_html=True)

tabs = st.tabs(["Profile", "AI Insights", "NFT Identity", "Applications", "Skill Tests", "Interviews"])

# ══ TAB 1: PROFILE ══════════════════════════
with tabs[0]:
    initials = (row["name"][0] + (row["name"].split()[-1][0] if " " in row["name"] else "")).upper()
    avail_c  = "tg" if row.get("availability")=="Available" else "ta" if row.get("availability")=="Part-time" else "tr"
    nft_span = "<span class='tag tp' style='font-size:10px;'>⬡ NFT Verified</span>" if row.get("nft_token_id") else ""
    skill_tags = " ".join(f"<span class='tag {TAG_C[i%len(TAG_C)]}'>{s}</span>" for i,s in enumerate(skills_list[:12]))
    bio_html = f"<div style='margin-top:12px;font-size:13px;color:#5a7088;line-height:1.7;padding:12px;background:rgba(255,255,255,.02);border-radius:8px;border-left:2px solid rgba(29,158,117,.3);'>{row['bio']}</div>" if row.get("bio") else ""
    test_note = f"<span style='font-size:11px;color:#4de8b4;margin-left:8px;'>+{test_bonus:.0f}% test bonus</span>" if test_bonus > 0 else ""

    col_l, col_r = st.columns([1.5, 1], gap="large")
    with col_l:
        st.markdown(f"""
<div class='gc aup'>
  <div style='display:flex;align-items:center;gap:14px;margin-bottom:16px;'>
    <div class='av av-g' style='width:56px;height:56px;font-size:18px;'>{initials}</div>
    <div style='flex:1;'>
      <div style='font-size:19px;font-weight:700;color:#fff;'>{row["name"]}</div>
      <div style='font-size:12px;color:#3a4a5c;margin-top:2px;'>{row["role"]} · {row["location"]} · {row["years_exp"]}yr</div>
      <div style='margin-top:6px;display:flex;gap:6px;flex-wrap:wrap;'>
        <span class='tag {avail_c}'>{row.get("availability","Available")}</span>
        {nft_span}
        <span class='tag tb'>${row.get("hourly_rate",30)}/hr</span>
      </div>
    </div>
    <div style='text-align:right;'>
      <div style='font-size:10px;color:#2a3a2a;margin-bottom:2px;letter-spacing:.08em;'>TALENT SCORE</div>
      <div style='font-size:44px;font-weight:700;color:#fff;line-height:1;'>{talent_score}</div>
      <div style='font-size:10px;color:#2a3a2a;'>/ 100{test_note}</div>
    </div>
  </div>
  <div style='background:rgba(255,255,255,.05);border-radius:4px;height:6px;overflow:hidden;margin-bottom:16px;'>
    <div style='height:6px;border-radius:4px;background:linear-gradient(90deg,#1D9E75,#4de8b4);width:{talent_score}%;'></div>
  </div>
  <div style='font-size:10px;color:#2a3a2a;letter-spacing:.1em;text-transform:uppercase;margin-bottom:8px;'>Verified Skills</div>
  <div>{skill_tags}</div>
  {bio_html}
</div>
""", unsafe_allow_html=True)

        c1,c2,c3,c4 = st.columns(4)
        for col,(val,lbl) in zip([c1,c2,c3,c4],[
            (row["projects"],"Projects"), (f"{row['rating']}/5","Rating"),
            (f"{row['completion_rate']}%","Completion"), (f"${row.get('hourly_rate',30)}","Hourly")]):
            with col:
                st.markdown(f"<div class='kpi' style='text-align:center;padding:14px;'><div class='kpi-val' style='font-size:20px;'>{val}</div><div class='kpi-lbl'>{lbl}</div></div>", unsafe_allow_html=True)

    with col_r:
        apps_df = get_applications_for_talent(wallet)
        if apps_df.empty:
            apps_inner = "<div style='text-align:center;padding:20px;color:#2a3a4a;font-size:13px;'>No applications yet.<br>Browse the Marketplace!</div>"
        else:
            apps_inner = ""
            for _, app in apps_df.head(5).iterrows():
                sc_cls = score_class(float(app.get("match_score",0)))
                sc_col = SCTAG.get(str(app.get("status","")), "ta")
                apps_inner += f"""
<div style='padding:9px 0;border-bottom:1px solid rgba(255,255,255,.04);'>
  <div style='display:flex;justify-content:space-between;align-items:center;'>
    <div>
      <div style='font-size:12px;font-weight:600;color:#fff;'>{str(app.get("title","Job"))[:28]}</div>
      <div style='font-size:10px;color:#3a4a5c;margin-top:1px;'>{app.get("company","")}</div>
    </div>
    <div style='display:flex;gap:5px;align-items:center;'>
      <span class='sp {sc_cls}' style='font-size:10px;'>{float(app.get("match_score",0)):.0f}%</span>
      <span class='tag {sc_col}' style='padding:2px 8px;font-size:9px;'>{app.get("status","")}</span>
    </div>
  </div>
</div>"""
        st.markdown(f"""
<div class='gc aup d2'>
  <div class='st2' style='margin-bottom:12px;'>My Applications <span style='font-size:11px;color:#3a4a5c;font-weight:400;'>({len(apps_df)} total)</span></div>
  {apps_inner}
</div>
""", unsafe_allow_html=True)

        bar1 = f"""
<div style='margin-bottom:10px;'>
  <div style='display:flex;justify-content:space-between;font-size:11px;color:#3a4a5c;margin-bottom:3px;'><span>Completion Rate</span><span style='color:#4de8b4;font-weight:600;'>{comp_s:.0f}%</span></div>
  <div style='background:rgba(255,255,255,.05);border-radius:3px;height:5px;'><div style='height:5px;border-radius:3px;background:#1D9E75;width:{comp_s}%;'></div></div>
</div>"""
        proj_pct = min(float(row["projects"])/25*100,100)
        bar2 = f"""
<div style='margin-bottom:0;'>
  <div style='display:flex;justify-content:space-between;font-size:11px;color:#3a4a5c;margin-bottom:3px;'><span>Project Load</span><span style='color:#7ab8f5;font-weight:600;'>{row["projects"]}</span></div>
  <div style='background:rgba(255,255,255,.05);border-radius:3px;height:5px;'><div style='height:5px;border-radius:3px;background:#378ADD;width:{proj_pct}%;'></div></div>
</div>"""
        st.markdown(f"""
<div class='gc aup d3' style='margin-top:12px;'>
  <div class='st2' style='margin-bottom:10px;'>Risk Assessment</div>
  <div class='{risk_cls}' style='margin-bottom:12px;'>{risk_label}</div>
  {bar1}{bar2}
</div>
""", unsafe_allow_html=True)

# ══ TAB 2: AI INSIGHTS ══════════════════════
with tabs[1]:
    c1, c2 = st.columns(2)
    for col, (label, value, color) in zip([c1,c2],[
        ("Overall Talent Score", float(talent_score), "#1D9E75"),
        ("Skill Confidence", float(min(sk_s,100)), "#378ADD"),
    ]):
        with col:
            fig = go.Figure(go.Indicator(
                mode="gauge+number", value=value,
                title={"text": label, "font": {"color":"#6b8aaa","size":13}},
                number={"font":{"color":"#fff","size":42},"suffix":"%"},
                gauge={"axis":{"range":[0,100],"tickcolor":"#2a3a4a","tickfont":{"color":"#2a3a4a","size":10}},
                       "bar":{"color":color,"thickness":.22},
                       "bgcolor":"rgba(0,0,0,0)","bordercolor":"rgba(0,0,0,0)",
                       "steps":[{"range":[0,60],"color":"rgba(226,75,74,.06)"},
                                 {"range":[60,80],"color":"rgba(239,159,39,.06)"},
                                 {"range":[80,100],"color":"rgba(29,158,117,.06)"}],
                       "threshold":{"line":{"color":"#4de8b4","width":2},"thickness":.75,"value":value}}
            ))
            fig.update_layout(**DARK, height=200, margin=dict(l=20,r=20,t=50,b=10))
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})

    col_a, col_b = st.columns(2, gap="large")
    with col_a:
        bars = [("Skill Depth",sk_s,"#1D9E75"),("Experience",exp_s,"#1D9E75"),
                ("Peer Rating",rat_s,"#1D9E75"),("Completion",comp_s,"#1D9E75"),
                ("Test Bonus",min(test_bonus,100),"#378ADD")]
        bars_html = ""
        for lbl,val,col_c in bars:
            bars_html += f"""
<div style='margin-bottom:10px;'>
  <div style='display:flex;justify-content:space-between;font-size:11px;color:#3a4a5c;margin-bottom:3px;'><span>{lbl}</span><span style='color:#c8d8e8;font-weight:600;'>{val:.0f}%</span></div>
  <div style='background:rgba(255,255,255,.05);border-radius:3px;height:5px;'><div style='height:5px;border-radius:3px;background:{col_c};width:{min(val,100):.1f}%;'></div></div>
</div>"""
        st.markdown(f"""
<div class='gc'>
  <div class='st2' style='margin-bottom:14px;'>Score Breakdown</div>
  {bars_html}
  <div class='formula' style='margin-top:12px;'>
    <span class='hl'>Score</span> = 0.85×base + 0.15×test_bonus<br>
    base = 0.30×<span class='num'>{sk_s:.0f}</span> + 0.30×<span class='num'>{exp_s:.0f}</span> + 0.25×<span class='num'>{rat_s:.0f}</span> + 0.15×<span class='num'>{comp_s:.0f}</span><br>
    = <span class='hl'>{talent_score}</span> / 100
  </div>
</div>
""", unsafe_allow_html=True)

    with col_b:
        cats = ["Skill Depth","Experience","Delivery","Communication","Domain","Adaptability"]
        vals = [min(sk_s,100), min(exp_s,100), comp_s, 75, min(exp_s*.9,100), 72]
        fig_r = go.Figure()
        fig_r.add_trace(go.Scatterpolar(
            r=[round(v) for v in vals]+[round(vals[0])], theta=cats+[cats[0]],
            fill="toself", fillcolor="rgba(29,158,117,.15)",
            line=dict(color="#1D9E75",width=2), marker=dict(color="#4de8b4",size=5), name="You"
        ))
        fig_r.add_trace(go.Scatterpolar(
            r=[70]*7, theta=cats+[cats[0]], fill="toself",
            fillcolor="rgba(56,138,221,.07)", line=dict(color="#378ADD",width=1,dash="dot"),
            name="Platform avg"
        ))
        fig_r.update_layout(**DARK,
            polar=dict(bgcolor="rgba(0,0,0,0)",
                radialaxis=dict(visible=True,range=[0,100],tickfont=dict(color="#2a3a4a",size=9),
                    gridcolor="rgba(29,158,117,.1)",linecolor="rgba(29,158,117,.1)"),
                angularaxis=dict(tickfont=dict(color="#8ba8c4",size=11),gridcolor="rgba(29,158,117,.1)")),
            showlegend=True, legend=dict(font=dict(color="#6b8aaa",size=11),bgcolor="rgba(0,0,0,0)"),
            margin=dict(l=30,r=30,t=20,b=30), height=270)
        st.plotly_chart(fig_r, use_container_width=True, config={"displayModeBar":False})

# ══ TAB 3: NFT ══════════════════════════════
with tabs[2]:
    if row.get("nft_token_id"):
        col_n, col_i = st.columns([1,1.4], gap="large")
        with col_n:
            explorer = f"https://amoy.polygonscan.com/token/0xConnectraNFT?a={row['nft_token_id']}"
            st.markdown(f"""
<div class='nft-card'>
  <div style='font-size:9px;letter-spacing:.12em;color:#1a4a2a;text-transform:uppercase;margin-bottom:12px;'>Soulbound Identity · Polygon Amoy</div>
  <div style='display:flex;align-items:center;gap:12px;margin-bottom:14px;'>
    <div style='width:46px;height:46px;border-radius:10px;background:rgba(29,158,117,.15);border:1px solid #1D9E75;display:flex;align-items:center;justify-content:center;font-size:22px;'>⬡</div>
    <div>
      <div style='font-size:15px;font-weight:700;color:#fff;'>Talent #{row["nft_token_id"]}</div>
      <div style='font-size:11px;color:#3a4a5c;margin-top:1px;'>{row["name"]} · {row["role"]}</div>
    </div>
  </div>
  <hr style='border:none;border-top:1px solid rgba(29,158,117,.15);margin:12px 0;'>
  <div style='display:grid;grid-template-columns:1fr 1fr;gap:8px;font-size:11px;'>
    <div><div style='color:#1a4a2a;margin-bottom:2px;'>Wallet</div><div class='nft-hex-bg'>{format_wallet(wallet)}</div></div>
    <div><div style='color:#1a4a2a;margin-bottom:2px;'>Tx Hash</div><div class='nft-hex-bg'>{short_hash(row.get("nft_tx_hash",""))}</div></div>
    <div><div style='color:#1a4a2a;margin-bottom:2px;'>Network</div><div style='color:#c8d8e8;'>Polygon Amoy</div></div>
    <div><div style='color:#1a4a2a;margin-bottom:2px;'>Type</div><div style='color:#4de8b4;font-weight:600;'>Soulbound</div></div>
  </div>
</div>
<div style='text-align:center;margin-top:12px;'>
  <a href='{explorer}' target='_blank' style='font-size:12px;color:#1D9E75;text-decoration:none;'>View on Polygonscan →</a>
</div>
""", unsafe_allow_html=True)
        with col_i:
            st.markdown("""
<div class='gc'>
  <div class='st2' style='margin-bottom:12px;'>What is a Soulbound NFT?</div>
  <div style='font-size:13px;color:#3a4a5c;line-height:1.85;'>
    <div style='margin-bottom:10px;'>🔐 <span style='color:#c8d8e8;font-weight:500;'>Non-transferable</span> — tied permanently to your wallet. Cannot be sold.</div>
    <div style='margin-bottom:10px;'>📦 <span style='color:#c8d8e8;font-weight:500;'>IPFS Metadata</span> — skills and work history on decentralized storage forever.</div>
    <div style='margin-bottom:10px;'>✅ <span style='color:#c8d8e8;font-weight:500;'>Employer Verifiable</span> — any employer can verify on Polygonscan in one click.</div>
    <div>🔄 <span style='color:#c8d8e8;font-weight:500;'>Portable Reputation</span> — switch platforms without losing your history.</div>
  </div>
</div>
""", unsafe_allow_html=True)
    else:
        st.markdown("<div style='text-align:center;padding:60px;'><div style='font-size:48px;margin-bottom:14px;'>⬡</div><div class='ph-title' style='margin-bottom:8px;'>NFT Not Minted Yet</div><div style='font-size:13px;color:#3a4a5c;'>Go to Create Profile to mint your Soulbound identity.</div></div>", unsafe_allow_html=True)
        if st.button("Mint My NFT"):
            st.switch_page("pages/2_Create_Profile.py")

# ══ TAB 4: APPLICATIONS ═════════════════════
with tabs[3]:
    apps_df2 = get_applications_for_talent(wallet)
    if apps_df2.empty:
        st.markdown("<div style='text-align:center;padding:60px;color:#2a3a4a;'>No applications yet. Head to the Marketplace!</div>", unsafe_allow_html=True)
    else:
        c1,c2,c3,c4 = st.columns(4)
        for col,status,color in zip([c1,c2,c3,c4],
                                     ["Pending","Shortlisted","Hired","Rejected"],
                                     ["ta","tb","tg","tr"]):
            cnt = len(apps_df2[apps_df2["status"]==status]) if "status" in apps_df2.columns else 0
            with col:
                st.markdown(f"<div class='kpi' style='text-align:center;padding:14px;'><div class='kpi-val' style='font-size:22px;'>{cnt}</div><div class='kpi-lbl'>{status}</div></div>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        rows_html = ""
        for _, app in apps_df2.iterrows():
            sc_cls = score_class(float(app.get("match_score",0)))
            st_col = SCTAG.get(str(app.get("status","")), "ta")
            tx_span = f"<span style='font-family:DM Mono,monospace;color:#2a3a4a;font-size:9px;'>Tx:{short_hash(str(app.get('tx_hash','') or ''))}</span>" if app.get("tx_hash") else ""
            rows_html += f"""
<div class='gc' style='padding:14px 18px;margin-bottom:8px;'>
  <div style='display:flex;align-items:center;gap:12px;'>
    <div style='flex:1;'>
      <div style='font-size:13px;font-weight:600;color:#fff;'>{app.get("title","Job")}</div>
      <div style='font-size:11px;color:#3a4a5c;margin-top:2px;'>{app.get("company","")} · ${int(app.get("budget_usdc",0)):,} · Applied {app.get("applied_date","—")}</div>
    </div>
    <div style='display:flex;gap:6px;align-items:center;flex-wrap:wrap;'>
      <span class='sp {sc_cls}'>{float(app.get("match_score",0)):.0f}% match</span>
      <span class='tag {st_col}'>{app.get("status","")}</span>
      {tx_span}
    </div>
  </div>
</div>"""
        st.markdown(rows_html, unsafe_allow_html=True)

# ══ TAB 5: SKILL TESTS ══════════════════════
with tabs[4]:
    st.markdown("""
<div class='ph' style='border:none;'>
  <div class='ph-title' style='font-size:20px;'>🧪 Skill Verification Tests</div>
  <div class='ph-sub'>Take timed tests to verify your skills. Scores boost your Talent Score by up to +15 points. Tests are optional but differentiate you from unverified profiles.</div>
</div>
""", unsafe_allow_html=True)

    test_df   = get_test_results(wallet)
    best_map  = {}
    if not test_df.empty and "skill" in test_df.columns:
        for _, r in test_df.iterrows():
            best_map[r["skill"]] = float(r.get("best_score",0))

    # Skill grid
    st.markdown("<div class='st2' style='margin-bottom:14px;'>Your Skills — Click to Take Test</div>", unsafe_allow_html=True)

    # Show test results summary
    if best_map:
        summary_html = ""
        for sk, sc in best_map.items():
            sc_col = "#4de8b4" if sc>=75 else "#f5c263" if sc>=55 else "#f08080"
            summary_html += f"""
<div style='display:flex;align-items:center;gap:10px;padding:8px 0;border-bottom:1px solid rgba(255,255,255,.04);'>
  <span class='tag tg'>{sk}</span>
  <div style='flex:1;background:rgba(255,255,255,.04);border-radius:3px;height:4px;'>
    <div style='height:4px;border-radius:3px;background:{sc_col};width:{sc:.0f}%;'></div>
  </div>
  <span style='font-size:12px;font-weight:700;color:{sc_col};font-family:DM Mono,monospace;'>{sc:.0f}%</span>
  <span class='tag tg' style='font-size:9px;'>Verified</span>
</div>"""
        st.markdown(f"<div class='gc' style='margin-bottom:16px;'><div class='st2' style='margin-bottom:10px;'>Completed Tests</div>{summary_html}</div>", unsafe_allow_html=True)
        if test_bonus > 0:
            st.markdown(f"<div style='padding:10px 14px;background:rgba(29,158,117,.1);border:1px solid rgba(29,158,117,.2);border-radius:8px;font-size:13px;color:#4de8b4;margin-bottom:16px;'>Test bonus applied to Talent Score: <strong>+{test_bonus:.1f}%</strong> → Score = {talent_score}/100</div>", unsafe_allow_html=True)

    # Skill selector for test
    st.markdown("<div class='st2' style='margin-bottom:8px;'>Take a New Test</div>", unsafe_allow_html=True)
    skill_to_test = st.selectbox("Select skill to test:", ["— Choose a skill —"] + skills_list, label_visibility="collapsed")

    if skill_to_test and skill_to_test != "— Choose a skill —":
        prev_best = best_map.get(skill_to_test)
        if prev_best is not None:
            st.markdown(f"<div style='font-size:12px;color:#f5c263;margin-bottom:8px;'>You have taken this test before. Best score: <strong>{prev_best:.0f}%</strong>. You can retake to improve.</div>", unsafe_allow_html=True)

        if st.button(f"Start {skill_to_test} Test (5 questions · 90 sec)", key="start_test"):
            st.session_state["active_test"] = skill_to_test
            st.session_state["test_answers"] = {}
            st.session_state["test_start"]   = time.time()
            st.rerun()

    # Active test
    if st.session_state.get("active_test"):
        skill = st.session_state["active_test"]
        questions = get_questions(skill)
        elapsed = time.time() - st.session_state.get("test_start", time.time())
        remaining = max(0, 90 - int(elapsed))

        time_col = "#4de8b4" if remaining > 45 else "#f5c263" if remaining > 15 else "#f08080"
        st.markdown(f"""
<div style='padding:12px 16px;background:#0e1525;border:1px solid rgba(255,255,255,.1);
            border-radius:10px;margin-bottom:16px;display:flex;align-items:center;gap:16px;'>
  <div style='font-size:14px;font-weight:700;color:#fff;'>{skill} Verification Test</div>
  <div style='margin-left:auto;font-family:DM Mono,monospace;font-size:16px;font-weight:700;color:{time_col};'>
    {remaining}s remaining
  </div>
</div>
""", unsafe_allow_html=True)

        answers = {}
        with st.form("test_form"):
            for i, q in enumerate(questions):
                st.markdown(f"<div style='font-size:13px;font-weight:600;color:#c8d8e8;margin-bottom:6px;margin-top:14px;'>Q{i+1}. {q['q']}</div>", unsafe_allow_html=True)
                answers[i] = st.radio("", q["opts"], key=f"q_{i}", label_visibility="collapsed", index=None)

            submitted = st.form_submit_button("Submit Test", use_container_width=False)

        if submitted or remaining == 0:
            correct = 0
            for i, q in enumerate(questions):
                if answers.get(i) == q["opts"][q["ans"]]:
                    correct += 1
            score = round(correct / len(questions) * 100, 1)
            save_test_result(wallet, skill, score, correct, len(questions))

            result_col = "#4de8b4" if score >= 75 else "#f5c263" if score >= 55 else "#f08080"
            st.markdown(f"""
<div style='text-align:center;padding:24px;background:#0e1525;border:1px solid rgba(29,158,117,.2);border-radius:12px;'>
  <div style='font-size:13px;color:#3a4a5c;margin-bottom:8px;'>Your Score</div>
  <div style='font-size:52px;font-weight:700;color:{result_col};font-family:DM Mono,monospace;'>{score:.0f}%</div>
  <div style='font-size:13px;color:#3a4a5c;margin-top:6px;'>{correct}/{len(questions)} correct</div>
  {"<div style='margin-top:10px;font-size:13px;color:#4de8b4;'>Excellent! This boosts your Talent Score.</div>" if score >= 75 else "<div style='margin-top:10px;font-size:13px;color:#f5c263;'>Good effort. Practice and retake to improve!</div>"}
</div>
""", unsafe_allow_html=True)
            del st.session_state["active_test"]
            del st.session_state["test_start"]
            if st.button("View Updated Score"):
                st.rerun()

# ══ TAB 6: INTERVIEWS ═══════════════════════
with tabs[5]:
    interviews_df = get_interviews_for_talent(wallet)
    st.markdown("<div class='ph-title' style='font-size:18px;margin-bottom:16px;'>Interview Requests</div>", unsafe_allow_html=True)
    if interviews_df.empty:
        st.markdown("<div style='text-align:center;padding:40px;color:#2a3a4a;'>No interview requests yet.</div>", unsafe_allow_html=True)
    else:
        rows_html = ""
        for _, iv in interviews_df.iterrows():
            st_col = "tg" if iv.get("status")=="Confirmed" else "tb" if iv.get("status")=="Requested" else "ta"
            rows_html += f"""
<div class='gc' style='padding:14px 18px;margin-bottom:8px;'>
  <div style='display:flex;align-items:center;gap:12px;'>
    <div style='flex:1;'>
      <div style='font-size:13px;font-weight:600;color:#fff;'>{iv.get("job_title","")}</div>
      <div style='font-size:11px;color:#3a4a5c;'>Requested: {iv.get("preferred_date","—")} · Booked: {iv.get("created_at","—")}</div>
      <div style='font-size:11px;color:#5a7088;margin-top:3px;'>{iv.get("note","")}</div>
    </div>
    <span class='tag {st_col}'>{iv.get("status","")}</span>
  </div>
</div>"""
        st.markdown(rows_html, unsafe_allow_html=True)
