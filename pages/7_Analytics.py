import streamlit as st
import plotly.graph_objects as go
import json, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from styles import GLOBAL_CSS
from data.sqlite_db import get_all_talents, get_all_jobs, get_platform_stats, _query

st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

talents_df = get_all_talents()
jobs_df    = get_all_jobs()
stats      = get_platform_stats()

DARK = dict(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
AXIS = dict(tickfont=dict(color="#4a6a84",size=10), gridcolor="rgba(255,255,255,.04)",
            zerolinecolor="rgba(0,0,0,0)", linecolor="rgba(0,0,0,0)")

st.markdown("""
<div class='ph aup'>
  <div class='ph-title'>📈 Platform Analytics</div>
  <div class='ph-sub'>Live insights across all talent, jobs, and applications</div>
</div>
""", unsafe_allow_html=True)

# ── KPIs ──
kpis = [
    (stats["talents"],      "Total Talents",   "▲ Live"),
    (stats["jobs"],         "Open Jobs",        "▲ Open now"),
    (stats["nfts_minted"],  "NFTs Minted",      "On-chain"),
    (stats["applications"], "Applications",     "All time"),
    (stats["tests_taken"],  "Skill Tests Taken","Verified"),
    (f"{stats['avg_match']}%","Avg Match Score","AI-computed"),
]
cols = st.columns(6)
for col, (val, lbl, delta) in zip(cols, kpis):
    with col:
        st.markdown(f"""
<div class='kpi' style='text-align:center;'>
  <div class='kpi-val'>{val}</div>
  <div class='kpi-lbl'>{lbl}</div>
  <div class='kpi-delta'>{delta}</div>
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Skills + Roles ──
col_s, col_r = st.columns(2, gap="large")
from collections import Counter

with col_s:
    all_skills = []
    for _, t in talents_df.iterrows():
        try:
            all_skills.extend(json.loads(t["skills"]))
        except Exception:
            pass
    top_skills = Counter(all_skills).most_common(12)
    labels = [s[0] for s in top_skills]
    counts = [s[1] for s in top_skills]
    fig = go.Figure(go.Bar(
        x=counts, y=labels, orientation="h",
        marker=dict(color=[f"rgba(29,158,117,{.3+.05*(12-i)})" for i in range(len(labels))],
                    line=dict(width=0)),
        text=counts, textposition="inside",
        textfont=dict(color="white", size=10),
    ))
    fig.update_layout(**DARK, title=dict(text="Top Skills on Platform",
                       font=dict(color="#8ba8c4",size=13)),
        xaxis=dict(**AXIS), yaxis=dict(**AXIS, tickfont=dict(color="#c8d8e8",size=11)),
        margin=dict(l=0,r=10,t=40,b=10), height=330, bargap=0.3)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

with col_r:
    role_counts = talents_df["role"].value_counts().head(8) if not talents_df.empty else None
    if role_counts is not None:
        fig2 = go.Figure(go.Pie(
            labels=role_counts.index.tolist(), values=role_counts.values.tolist(),
            hole=0.55, textfont=dict(color="white", size=10),
            marker=dict(colors=["#1D9E75","#378ADD","#7F77DD","#EF9F27",
                                 "#4de8b4","#7ab8f5","#b3aeef","#f5c263"],
                        line=dict(color="rgba(8,12,23,.8)",width=2)),
        ))
        fig2.update_layout(**DARK, title=dict(text="Talent by Role",
                            font=dict(color="#8ba8c4",size=13)),
            legend=dict(font=dict(color="#6b8aaa",size=10),bgcolor="rgba(0,0,0,0)"),
            margin=dict(l=0,r=0,t=40,b=0), height=330)
        st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})

st.markdown("<br>", unsafe_allow_html=True)

# ── Match dist + Locations ──
col_md, col_loc = st.columns([1.4, 1], gap="large")

with col_md:
    apps_rows = _query("SELECT match_score FROM applications", many=True)
    apps_scores = [r["match_score"] for r in apps_rows] if apps_rows else []
    st.markdown("<div class='gc aup'><div class='st2'>Match Score Distribution</div><div class='st3'>Across all applications</div>", unsafe_allow_html=True)
    if apps_scores:
        import numpy as np
        bins = list(range(0,101,10))
        counts2, _ = np.histogram(apps_scores, bins=bins)
        labels2 = [f"{b}-{b+10}" for b in bins[:-1]]
        colors2 = ["#E24B4A" if b<60 else "#EF9F27" if b<80 else "#1D9E75" for b in bins[:-1]]
        fig3 = go.Figure(go.Bar(
            x=labels2, y=counts2,
            marker=dict(color=colors2, line=dict(width=0)),
            hovertemplate="%{x}: %{y} applicants<extra></extra>"
        ))
        fig3.update_layout(**DARK, xaxis=dict(**AXIS), yaxis=dict(**AXIS),
            margin=dict(l=0,r=0,t=10,b=10), height=190, bargap=0.25)
        st.plotly_chart(fig3, use_container_width=True, config={"displayModeBar": False})
    else:
        st.info("No application data yet.")
    st.markdown("</div>", unsafe_allow_html=True)

with col_loc:
    if not talents_df.empty:
        loc_counts = talents_df["location"].value_counts()
        fig4 = go.Figure(go.Bar(
            x=loc_counts.values.tolist(), y=loc_counts.index.tolist(), orientation="h",
            marker=dict(color=["rgba(56,138,221,.6)" if l=="Remote"
                               else "rgba(29,158,117,.5)" for l in loc_counts.index],
                        line=dict(width=0)),
            text=loc_counts.values.tolist(), textposition="inside",
            textfont=dict(color="white",size=10),
        ))
        fig4.update_layout(**DARK, title=dict(text="Talent by Location",
                            font=dict(color="#8ba8c4",size=13)),
            xaxis=dict(**AXIS), yaxis=dict(**AXIS, tickfont=dict(color="#c8d8e8",size=11)),
            margin=dict(l=0,r=10,t=40,b=10), height=270, bargap=0.3)
        st.plotly_chart(fig4, use_container_width=True, config={"displayModeBar": False})

st.markdown("<br>", unsafe_allow_html=True)

# ── Scatter + Budget ──
col_sc, col_bud = st.columns(2, gap="large")

with col_sc:
    if not talents_df.empty:
        exp_vals  = [int(v) for v in talents_df["years_exp"].tolist()]
        rat_vals  = [float(v) for v in talents_df["rating"].tolist()]
        comp_vals = [float(v) for v in talents_df["completion_rate"].tolist()]
        names_v   = talents_df["name"].tolist()

        fig5 = go.Figure(go.Scatter(
            x=exp_vals, y=rat_vals, mode="markers",
            marker=dict(
                size=[c/10+4 for c in comp_vals],
                color=comp_vals, colorscale="Teal", showscale=True,
                colorbar=dict(
                    title=dict(text="Completion%", font=dict(color="#4a6a84",size=10)),
                    tickfont=dict(color="#4a6a84",size=9),
                    outlinecolor="rgba(0,0,0,0)",
                ),
                line=dict(color="rgba(8,12,23,.5)",width=0.5),
            ),
            text=names_v,
            hovertemplate="<b>%{text}</b><br>Exp: %{x}yr<br>Rating: %{y:.1f}<extra></extra>"
        ))
        fig5.update_layout(**DARK,
            title=dict(text="Experience vs Rating (bubble = completion%)", font=dict(color="#8ba8c4",size=12)),
            xaxis=dict(**AXIS, title=dict(text="Years Exp", font=dict(color="#4a6a84",size=11))),
            yaxis=dict(**AXIS, title=dict(text="Rating",    font=dict(color="#4a6a84",size=11))),
            margin=dict(l=0,r=60,t=40,b=20), height=270)
        st.plotly_chart(fig5, use_container_width=True, config={"displayModeBar": False})

with col_bud:
    if not jobs_df.empty:
        budgets = [int(v) for v in jobs_df["budget_usdc"].tolist()]
        import numpy as np
        bins_b = [0,1500,3000,4500,6000,7500,10001]
        counts_b, _ = np.histogram(budgets, bins=bins_b)
        labels_b = ["<$1.5k","$1.5-3k","$3-4.5k","$4.5-6k","$6-7.5k",">$7.5k"]
        colors_b = ["rgba(239,159,39,.5)","rgba(239,159,39,.55)","rgba(29,158,117,.5)",
                    "rgba(29,158,117,.6)","rgba(29,158,117,.65)","rgba(29,158,117,.7)"]
        fig6 = go.Figure(go.Bar(
            x=labels_b, y=counts_b,
            marker=dict(color=colors_b, line=dict(width=0)),
            text=counts_b, textposition="outside",
            textfont=dict(color="white",size=10),
        ))
        fig6.update_layout(**DARK,
            title=dict(text="Job Budget Distribution", font=dict(color="#8ba8c4",size=13)),
            xaxis=dict(**AXIS, tickfont=dict(color="#c8d8e8",size=11)),
            yaxis=dict(**AXIS),
            margin=dict(l=0,r=0,t=40,b=10), height=270, bargap=0.3)
        st.plotly_chart(fig6, use_container_width=True, config={"displayModeBar": False})

# ── Skill Test Leaderboard ──
st.markdown("<br>", unsafe_allow_html=True)
test_rows = _query("""
    SELECT t.name, t.role, COUNT(DISTINCT s.skill) as skills_tested,
           AVG(s.score) as avg_score, t.nft_token_id
    FROM skill_test_results s
    JOIN talents t ON s.wallet = t.wallet_address
    GROUP BY s.wallet ORDER BY avg_score DESC LIMIT 8
""", many=True)

if test_rows:
    st.markdown("<div class='gc aup'><div class='st2'>🧪 Skill Test Leaderboard</div><div class='st3'>Talents who have verified their skills through tests</div>", unsafe_allow_html=True)
    MEDALS = ["🥇","🥈","🥉"]
    AV = ["av-g","av-b","av-a","av-p"]
    rows_html = ""
    for i, r in enumerate(test_rows, 1):
        nm = r.get("name","—")
        init = nm[0] + (nm.split()[-1][0] if " " in nm else "")
        medal = MEDALS[i-1] if i<=3 else f"#{i}"
        nft = "<span class='tag tp' style='font-size:9px;'>NFT</span>" if r.get("nft_token_id") else ""
        sc = round(float(r.get("avg_score",0)),1)
        sc_col = "#4de8b4" if sc>=75 else "#f5c263" if sc>=55 else "#f08080"
        rows_html += f"""
<div class='cand-row'>
  <div style='font-size:16px;width:24px;'>{medal}</div>
  <div class='av {AV[i%len(AV)]}' style='width:34px;height:34px;font-size:12px;'>{init.upper()}</div>
  <div style='flex:1;'>
    <div style='font-size:13px;font-weight:600;color:#fff;display:flex;gap:6px;align-items:center;'>{nm} {nft}</div>
    <div style='font-size:11px;color:#3a4a5c;'>{r.get("role","")} · {r.get("skills_tested",0)} skills tested</div>
  </div>
  <div style='font-family:DM Mono,monospace;font-size:16px;font-weight:700;color:{sc_col};'>{sc}%</div>
</div>
"""
    st.markdown(rows_html, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ── AI Model note ──
st.markdown("""
<div class='gc aup d4' style='text-align:center;padding:24px;margin-top:16px;'>
  <div class='st2' style='margin-bottom:8px;'>AI Model Transparency</div>
  <div style='font-size:12px;color:#3a4a5c;line-height:1.9;'>
    Match Score = <span style='color:#4de8b4;font-family:DM Mono,monospace;'>0.45×Skill + 0.25×Exp + 0.20×Rating + 0.10×Completion</span><br>
    Talent Score = base score + <span style='color:#7ab8f5;font-family:DM Mono,monospace;'>0.15×Skill Test Bonus</span> — upgradeable to LightGBM / LLM semantic matching
  </div>
</div>
""", unsafe_allow_html=True)
