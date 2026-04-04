import streamlit as st
import plotly.graph_objects as go
import json, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from styles import GLOBAL_CSS
from data.sqlite_db import get_talent, get_applications_for_talent, get_all_jobs, get_skill_test_results, get_interviews_for_talent
from utils.matching import calculate_match, get_breakdown, get_risk_level, score_class, calculate_talent_score
from utils.blockchain import format_wallet, short_hash
from utils.ui_components import render_gauge, render_radar, render_skills, html_bar, nft_card_html

st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

wallet = st.session_state.get("wallet", "0x742d35Cc6634C0532925a3b844Bc454e4438f44e")
df = get_talent(wallet)

if df.empty:
    st.markdown("""
<div style='text-align:center;padding:80px 20px;'>
  <div style='font-size:48px;margin-bottom:16px;'>
    <svg width='48' height='48' viewBox='0 0 24 24' fill='none' stroke='#2a4a34' stroke-width='1.5'><path d='M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2'/><circle cx='12' cy='7' r='4'/></svg>
  </div>
  <div class='s-title' style='font-size:24px;margin-bottom:8px;'>No Profile Found</div>
  <div style='font-size:14px;color:#4a6a84;margin-bottom:24px;'>Create your verified on-chain profile to get started.</div>
</div>
""", unsafe_allow_html=True)
    if st.button("Create Your Profile"):
        st.switch_page("pages/2_Create_Profile.py")
    st.stop()

row = df.iloc[0]
skills_list = json.loads(row["skills"]) if isinstance(row["skills"], str) else row["skills"]

talent_score = calculate_talent_score(row)
skill_s  = min(len(skills_list) / 8, 1.0) * 100
exp_s    = min(row["years_exp"] / 10, 1.0) * 100
rat_s    = row["rating"] / 5.0 * 100
comp_s   = float(row["completion_rate"])
test_b   = float(row.get("test_score_bonus", 0))
risk_label, risk_cls = get_risk_level(row)

st.markdown(f"""
<div class='anim-up' style='margin-bottom:20px;'>
  <div class='s-title' style='font-size:26px;'>Talent Dashboard</div>
  <div class='s-sub'>Your verified on-chain identity · {format_wallet(wallet)}</div>
</div>
""", unsafe_allow_html=True)

tabs = st.tabs(["Profile", "AI Insights", "NFT Identity", "Applications", "Skill Tests", "Skill Gaps"])

# ════════════════════════════════════════════════
# TAB 1: PROFILE
# ════════════════════════════════════════════════
with tabs[0]:
    col_l, col_r = st.columns([1.5, 1], gap="large")

    with col_l:
        initials = row["name"][0] + (row["name"].split()[-1][0] if " " in row["name"] else "")
        avail_tag = ("tg" if row.get("availability") == "Available"
                     else "ta" if row.get("availability") == "Part-time" else "tr")
        TAG_C = ["tg","tb","ta","tp","tc","tg","tb"]
        skills_tags_html = " ".join(
            f"<span class='tag {TAG_C[i%len(TAG_C)]}'>{s}</span>"
            for i, s in enumerate(skills_list[:12])
        )
        nft_span  = "<span class='tag tp'>NFT Verified</span>" if row.get("nft_token_id") else ""
        bio_block = f"""
<div style='margin-top:14px;font-size:13px;color:#6b8aaa;line-height:1.7;
            padding:12px;background:rgba(255,255,255,.03);border-radius:10px;
            border-left:2px solid rgba(29,158,117,.3);'>{row["bio"]}</div>
""" if row.get("bio") else ""
        test_bonus_badge = f"<span class='tag tc'>+{test_b:.1f} test bonus</span>" if test_b > 0 else ""

        st.markdown(f"""
<div class='g-card anim-up'>
  <div style='display:flex;align-items:center;gap:16px;margin-bottom:18px;'>
    <div class='av av-g' style='width:60px;height:60px;font-size:20px;'>{initials.upper()}</div>
    <div style='flex:1;'>
      <div style='font-family:Syne,sans-serif;font-size:20px;font-weight:700;color:#fff;'>{row["name"]}</div>
      <div style='font-size:13px;color:#4a6a84;margin-top:2px;'>{row["role"]} · {row["location"]} · {row["years_exp"]} yrs exp</div>
      <div style='margin-top:8px;display:flex;gap:8px;flex-wrap:wrap;'>
        <span class='tag {avail_tag}'>{row.get("availability","Available")}</span>
        {nft_span} {test_bonus_badge}
        <span class='tag tb'>${row.get("hourly_rate",30)}/hr</span>
      </div>
    </div>
    <div style='text-align:right;'>
      <div style='font-size:10px;color:#2a4a34;margin-bottom:4px;letter-spacing:.08em;'>TALENT SCORE</div>
      <div style='font-family:Syne,sans-serif;font-size:44px;font-weight:800;line-height:1;
                  background:linear-gradient(90deg,#1D9E75,#4de8b4);
                  -webkit-background-clip:text;-webkit-text-fill-color:transparent;'>{talent_score:.0f}</div>
      <div style='font-size:10px;color:#2a4a34;'>/ 100</div>
    </div>
  </div>
  <div class='bar-bg'><div class='bar' style='width:{min(talent_score,100)}%;'></div></div>
  <hr class='div'>
  <div style='font-size:11px;color:#2a4a34;letter-spacing:.1em;text-transform:uppercase;margin-bottom:10px;'>Verified Skills</div>
  <div>{skills_tags_html}</div>
  {bio_block}
</div>
""", unsafe_allow_html=True)

        c1, c2, c3, c4 = st.columns(4)
        for col, (val, lbl, delay) in zip([c1,c2,c3,c4], [
            (row["projects"], "Projects", "0.1s"),
            (f"{row['rating']}/5", "Rating", "0.18s"),
            (f"{row['completion_rate']}%", "Completion", "0.26s"),
            (f"${row.get('hourly_rate',30)}", "Hourly Rate", "0.34s"),
        ]):
            with col:
                st.markdown(f"""
<div class='m-card' style='animation-delay:{delay};text-align:center;'>
  <div class='m-lbl'>{lbl}</div>
  <div class='m-val' style='font-size:22px;'>{val}</div>
</div>
""", unsafe_allow_html=True)

    with col_r:
        apps_df = get_applications_for_talent(wallet)
        STATUS_COLORS = {"Pending":"ta","Shortlisted":"tb","Hired":"tg","Rejected":"tr"}

        if apps_df.empty:
            apps_inner = "<div style='text-align:center;padding:24px;color:#2a4a34;font-size:13px;'>No applications yet.<br>Browse the Marketplace!</div>"
        else:
            apps_inner = ""
            for _, app in apps_df.head(5).iterrows():
                sc_cls = score_class(app["match_score"])
                sc_col = STATUS_COLORS.get(app["status"], "ta")
                apps_inner += f"""
<div style='padding:10px 0;border-bottom:1px solid rgba(29,158,117,.09);'>
  <div style='display:flex;justify-content:space-between;align-items:center;'>
    <div>
      <div style='font-size:13px;font-weight:600;color:#fff;'>{str(app.get("title","Job"))[:30]}</div>
      <div style='font-size:11px;color:#4a6a84;margin-top:2px;'>{app.get("company","")}</div>
    </div>
    <div style='display:flex;gap:6px;align-items:center;'>
      <div class='sp {sc_cls}' style='font-size:11px;'>{app["match_score"]:.0f}%</div>
      <span class='tag {sc_col}' style='padding:2px 8px;font-size:10px;'>{app["status"]}</span>
    </div>
  </div>
</div>
"""

        st.markdown(f"""
<div class='g-card anim-up d2'>
  <div class='s-title' style='font-size:16px;margin-bottom:14px;'>
    My Applications
    <span style='font-size:12px;color:#4a6a84;font-weight:400;margin-left:8px;'>({len(apps_df)} total)</span>
  </div>
  {apps_inner}
</div>
""", unsafe_allow_html=True)

        bar1 = html_bar("Completion Rate", float(row["completion_rate"]),
                        "bar" if row["completion_rate"] >= 80 else "bar-a")
        bar2 = html_bar("Project Load", min(float(row["projects"])/25*100, 100), "bar-b")
        st.markdown(f"""
<div class='g-card anim-up d3' style='margin-top:14px;'>
  <div style='font-size:13px;font-weight:600;color:#fff;margin-bottom:10px;'>Risk Assessment</div>
  <div class='{risk_cls}' style='display:inline-flex;margin-bottom:10px;'>{risk_label}</div>
  {bar1}
  {bar2}
</div>
""", unsafe_allow_html=True)


# ════════════════════════════════════════════════
# TAB 2: AI INSIGHTS
# ════════════════════════════════════════════════
with tabs[1]:
    c1, c2 = st.columns(2)
    with c1:
        render_gauge("Overall Talent Score", float(talent_score), "auto")
    with c2:
        render_gauge("Skill Confidence", float(min(skill_s, 100)), "#378ADD")

    st.markdown("<br>", unsafe_allow_html=True)
    col_a, col_b = st.columns(2)
    with col_a:
        test_bar = html_bar("Skill Test Bonus", min(test_b * 10, 100), "bar-b") if test_b > 0 else ""
        st.markdown(f"""
<div class='g-card'>
  <div class='s-title' style='font-size:16px;margin-bottom:14px;'>Score Breakdown</div>
  {html_bar("Skill Depth", skill_s)}
  {html_bar("Experience", exp_s)}
  {html_bar("Peer Rating", rat_s)}
  {html_bar("Completion Rate", comp_s)}
  {test_bar}
  <div class='formula' style='margin-top:14px;'>
    <span class='hl'>Talent Score</span> = 0.28×Skill + 0.28×Exp + 0.24×Rating + 0.10×Completion + 0.10×TestBonus<br>
    = <span class='hl'>{talent_score:.0f}</span>
  </div>
</div>
""", unsafe_allow_html=True)

    with col_b:
        st.markdown("""
<div class='g-card'>
  <div class='s-title' style='font-size:16px;margin-bottom:14px;'>Performance Radar</div>
""", unsafe_allow_html=True)
        cats = ["Skill Depth","Experience","Delivery","Communication","Adaptability","Domain"]
        vals = [min(skill_s,100), min(exp_s,100), float(row["completion_rate"]),
                75, 70, min(exp_s*0.9,100)]
        render_radar(cats, [round(v) for v in vals], height=250)
        st.markdown("</div>", unsafe_allow_html=True)


# ════════════════════════════════════════════════
# TAB 3: NFT IDENTITY
# ════════════════════════════════════════════════
with tabs[2]:
    if row.get("nft_token_id"):
        col_nft, col_info = st.columns([1, 1.4], gap="large")
        with col_nft:
            st.markdown(nft_card_html(
                row["name"], row["role"],
                row["nft_token_id"], row["nft_tx_hash"], wallet
            ), unsafe_allow_html=True)
            explorer = f"https://amoy.polygonscan.com/token/0xConnectraNFT?a={row['nft_token_id']}"
            st.markdown(f"""
<div style='margin-top:12px;text-align:center;'>
  <a href='{explorer}' target='_blank'
     style='font-size:13px;color:#1D9E75;text-decoration:none;
            padding:8px 20px;border:1px solid rgba(29,158,117,.35);
            border-radius:50px;display:inline-block;'>View on Polygonscan →</a>
</div>
""", unsafe_allow_html=True)

        with col_info:
            st.markdown("""
<div class='g-card anim-up d2'>
  <div class='s-title' style='font-size:16px;margin-bottom:14px;'>What is a Soulbound NFT?</div>
  <div style='font-size:13px;color:#4a6a84;line-height:1.9;'>
    <div style='margin-bottom:12px;display:flex;gap:8px;'>
      <svg width='14' height='14' viewBox='0 0 24 24' fill='none' stroke='#1D9E75' stroke-width='2' style='margin-top:2px;flex-shrink:0;'><rect x='3' y='11' width='18' height='11' rx='2'/><path d='M7 11V7a5 5 0 0 1 10 0v4'/></svg>
      <span><strong style='color:#c8d8e8;'>Non-transferable</strong> — tied permanently to your wallet.</span>
    </div>
    <div style='margin-bottom:12px;display:flex;gap:8px;'>
      <svg width='14' height='14' viewBox='0 0 24 24' fill='none' stroke='#378ADD' stroke-width='2' style='margin-top:2px;flex-shrink:0;'><path d='M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z'/></svg>
      <span><strong style='color:#c8d8e8;'>IPFS Metadata</strong> — skills stored on decentralised storage.</span>
    </div>
    <div style='margin-bottom:12px;display:flex;gap:8px;'>
      <svg width='14' height='14' viewBox='0 0 24 24' fill='none' stroke='#4de8b4' stroke-width='2' style='margin-top:2px;flex-shrink:0;'><polyline points='9 11 12 14 22 4'/></svg>
      <span><strong style='color:#c8d8e8;'>Employer Verifiable</strong> — one-click check on Polygonscan.</span>
    </div>
    <div style='display:flex;gap:8px;'>
      <svg width='14' height='14' viewBox='0 0 24 24' fill='none' stroke='#7F77DD' stroke-width='2' style='margin-top:2px;flex-shrink:0;'><polyline points='17 1 21 5 17 9'/><path d='M3 11V9a4 4 0 0 1 4-4h14'/><polyline points='7 23 3 19 7 15'/><path d='M21 13v2a4 4 0 0 1-4 4H3'/></svg>
      <span><strong style='color:#c8d8e8;'>Portable Reputation</strong> — switch platforms without losing history.</span>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)
    else:
        st.markdown("""
<div style='text-align:center;padding:60px;'>
  <div style='font-size:48px;margin-bottom:14px;'>⬡</div>
  <div class='s-title' style='margin-bottom:8px;'>NFT Not Minted Yet</div>
  <div style='font-size:13px;color:#4a6a84;margin-bottom:20px;'>Go to Create Profile to mint your Soulbound identity.</div>
</div>
""", unsafe_allow_html=True)
        if st.button("Mint My NFT", key="mint_redirect"):
            st.switch_page("pages/2_Create_Profile.py")


# ════════════════════════════════════════════════
# TAB 4: APPLICATIONS + INTERVIEWS
# ════════════════════════════════════════════════
with tabs[3]:
    apps_df = get_applications_for_talent(wallet)
    interviews_df = get_interviews_for_talent(wallet)

    # Application summary
    if not apps_df.empty:
        c1, c2, c3, c4 = st.columns(4)
        for col, status, color in zip([c1,c2,c3,c4],
                                       ["Pending","Shortlisted","Hired","Rejected"],
                                       ["ta","tb","tg","tr"]):
            cnt = len(apps_df[apps_df["status"] == status])
            with col:
                st.markdown(f"""
<div class='m-card' style='text-align:center;'>
  <div class='m-lbl'>{status}</div>
  <div class='m-val' style='font-size:24px;'>{cnt}</div>
</div>
""", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

    # Scheduled Interviews section
    if not interviews_df.empty:
        st.markdown("""
<div style='font-size:14px;font-weight:600;color:#378ADD;margin-bottom:10px;display:flex;align-items:center;gap:6px;'>
  <svg width='14' height='14' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2'><rect x='3' y='4' width='18' height='18' rx='2' ry='2'/><line x1='16' y1='2' x2='16' y2='6'/><line x1='8' y1='2' x2='8' y2='6'/><line x1='3' y1='10' x2='21' y2='10'/></svg>
  Scheduled Interviews
</div>
""", unsafe_allow_html=True)
        for _, iv in interviews_df.iterrows():
            status_cls = "tb" if iv["status"] == "Scheduled" else "tg" if iv["status"] == "Completed" else "tr"
            st.markdown(f"""
<div class='g-card' style='padding:14px 18px;margin-bottom:8px;border-color:rgba(56,138,221,.25);'>
  <div style='display:flex;align-items:center;gap:12px;'>
    <div style='flex:1;'>
      <div style='font-size:14px;font-weight:600;color:#fff;'>{iv.get("title","Job")} — {iv.get("company","")}</div>
      <div style='font-size:12px;color:#4a6a84;margin-top:2px;'>
        {iv["scheduled_date"]} at {iv["scheduled_time"]}
      </div>
      {f'<div style="font-size:11px;color:#4a6a84;margin-top:3px;">{iv["notes"]}</div>' if iv.get("notes") else ""}
    </div>
    <span class='tag {status_cls}'>{iv["status"]}</span>
  </div>
</div>
""", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

    # All applications
    STATUS_COLORS = {"Pending":"ta","Shortlisted":"tb","Hired":"tg","Rejected":"tr"}
    if apps_df.empty:
        st.markdown("""
<div style='text-align:center;padding:60px;color:#2a4a34;'>
  <div style='font-size:32px;margin-bottom:12px;'>📋</div>
  <div>No applications yet. Head to the Marketplace!</div>
</div>
""", unsafe_allow_html=True)
    else:
        for _, app in apps_df.iterrows():
            sc_cls = score_class(app["match_score"])
            st.markdown(f"""
<div class='g-card' style='padding:16px 20px;margin-bottom:10px;'>
  <div style='display:flex;align-items:center;gap:14px;'>
    <div>
      <div style='font-size:14px;font-weight:600;color:#fff;'>{app.get("title","Job")}</div>
      <div style='font-size:12px;color:#4a6a84;margin-top:2px;'>
        {app.get("company","")} · ${app.get("budget_usdc",0):,} · Applied: {app.get("applied_date","—")}
      </div>
    </div>
    <div style='margin-left:auto;display:flex;gap:8px;align-items:center;'>
      <div class='sp {sc_cls}'>{app["match_score"]:.0f}% match</div>
      <span class='tag {STATUS_COLORS.get(app["status"],"ta")}'>{app["status"]}</span>
      {f'<span class="tag tg" style="font-size:10px;">Tx: {short_hash(app.get("tx_hash",""))}</span>' if app.get("tx_hash") else ""}
    </div>
  </div>
</div>
""", unsafe_allow_html=True)


# ════════════════════════════════════════════════
# TAB 5: SKILL TESTS
# ════════════════════════════════════════════════
with tabs[4]:
    results_df = get_skill_test_results(wallet)

    st.markdown("""
<div style='display:flex;align-items:center;justify-content:space-between;margin-bottom:16px;'>
  <div>
    <div class='s-title' style='font-size:18px;margin-bottom:2px;'>Your Skill Tests</div>
    <div class='s-sub' style='margin-bottom:0;'>Tests boost your Talent Score by up to 10 points</div>
  </div>
</div>
""", unsafe_allow_html=True)

    if results_df.empty:
        st.markdown("""
<div style='text-align:center;padding:40px;border:1px dashed rgba(29,158,117,.2);border-radius:14px;'>
  <div style='font-size:13px;color:#2a4a34;margin-bottom:12px;'>No tests taken yet</div>
  <div style='font-size:12px;color:#1a2a1a;'>Take skill tests to differentiate yourself and boost your Talent Score</div>
</div>
""", unsafe_allow_html=True)
    else:
        avg_pct = round(results_df["percentage"].mean(), 1)
        bonus = round(results_df["percentage"].mean() / 100 * 10, 1)

        c1, c2, c3 = st.columns(3)
        for col, (val, lbl) in zip([c1,c2,c3], [
            (f"{len(results_df)}", "Tests Completed"),
            (f"{avg_pct}%", "Average Score"),
            (f"+{bonus:.1f} pts", "Score Boost"),
        ]):
            with col:
                st.markdown(f"""
<div class='m-card' style='text-align:center;'>
  <div class='m-lbl'>{lbl}</div>
  <div class='m-val' style='font-size:22px;'>{val}</div>
</div>
""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        for _, res in results_df.iterrows():
            pct = float(res["percentage"])
            bar_col = "#1D9E75" if pct >= 70 else "#EF9F27" if pct >= 50 else "#E24B4A"
            grade = "Excellent" if pct >= 80 else "Good" if pct >= 60 else "Needs Practice"
            st.markdown(f"""
<div class='g-card' style='padding:14px 18px;margin-bottom:8px;'>
  <div style='display:flex;align-items:center;gap:12px;'>
    <div style='flex:1;'>
      <div style='font-size:14px;font-weight:600;color:#fff;margin-bottom:6px;'>{res["skill_name"]}</div>
      <div style='display:flex;justify-content:space-between;font-size:11px;color:#2a4a34;margin-bottom:4px;'>
        <span>{res["score"]}/{res["max_score"]} correct</span>
        <span style='color:{bar_col};font-weight:600;'>{pct:.0f}%</span>
      </div>
      <div class='bar-bg'><div class='bar' style='width:{pct}%;background:{bar_col};'></div></div>
    </div>
    <div style='text-align:right;'>
      <div style='font-size:11px;color:{bar_col};font-weight:600;'>{grade}</div>
      <div style='font-size:10px;color:#2a4a34;margin-top:2px;'>{str(res["taken_at"])[:10]}</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

    if st.button("Take / Retake Tests", use_container_width=False):
        st.switch_page("pages/8_Skill_Tests.py")


# ════════════════════════════════════════════════
# TAB 6: SKILL GAPS
# ════════════════════════════════════════════════
with tabs[5]:
    jobs_df = get_all_jobs()
    if jobs_df.empty:
        st.info("No jobs available for gap analysis.")
    else:
        st.markdown("""
<div class='s-title' style='font-size:18px;margin-bottom:6px;'>Skill Gap Analysis</div>
<div class='s-sub'>Skills that appear most in open jobs you don't yet have</div>
""", unsafe_allow_html=True)

        from collections import Counter
        import json as _json

        all_req = []
        for _, jrow in jobs_df.iterrows():
            try:
                all_req.extend(_json.loads(jrow["required_skills"]))
            except Exception:
                pass

        talent_set = set(s.lower() for s in skills_list)
        missing = [s for s in all_req if s.lower() not in talent_set]
        top_missing = Counter(missing).most_common(10)

        if top_missing:
            col_chart, col_list = st.columns([1.4, 1], gap="large")
            with col_chart:
                labels = [m[0] for m in top_missing]
                counts = [m[1] for m in top_missing]
                fig = go.Figure(go.Bar(
                    x=counts, y=labels, orientation="h",
                    marker=dict(
                        color=[f"rgba(239,159,39,{0.3 + 0.07*i})" for i in range(len(labels))],
                        line=dict(width=0)
                    ),
                    text=counts, textposition="inside",
                    textfont=dict(color="white", size=11),
                ))
                fig.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    xaxis=dict(tickfont=dict(color="#4a6a84",size=10),
                               gridcolor="rgba(255,255,255,.04)", zerolinecolor="rgba(0,0,0,0)"),
                    yaxis=dict(tickfont=dict(color="#c8d8e8",size=12)),
                    margin=dict(l=0,r=20,t=10,b=10), height=280, bargap=0.3,
                )
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

            with col_list:
                st.markdown("<div class='g-card'><div style='font-size:14px;font-weight:600;color:#fff;margin-bottom:12px;'>Top Skills to Learn</div>", unsafe_allow_html=True)
                for skill, count in top_missing[:6]:
                    st.markdown(f"""
<div style='display:flex;justify-content:space-between;padding:8px 0;border-bottom:1px solid rgba(29,158,117,.08);'>
  <span class='tag ta' style='margin:0;'>{skill}</span>
  <span style='font-size:11px;color:#4a6a84;'>in {count} jobs</span>
</div>
""", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
