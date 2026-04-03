import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import json, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from styles import GLOBAL_CSS
from data.sqlite_db import get_all_talents, get_all_jobs, get_platform_stats
from utils.matching import rank_talents_for_job
from utils.ui_components import render_score_distribution

st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

talents_df = get_all_talents()
jobs_df    = get_all_jobs()
stats      = get_platform_stats()

st.markdown("""
<div class='anim-up' style='margin-bottom:20px;'>
  <div class='s-title' style='font-size:26px;'>📈 Platform Analytics</div>
  <div class='s-sub'>Live insights across all verified talent and job activity</div>
</div>
""", unsafe_allow_html=True)

# ════════════════════════════════════════════════
# KPI ROW
# ════════════════════════════════════════════════
c1, c2, c3, c4, c5, c6 = st.columns(6)
kpis = [
    (stats["talents"],       "Total Talents",    "🧑‍💻", "0.05s"),
    (stats["jobs"],          "Open Jobs",         "💼", "0.1s"),
    (stats["nfts_minted"],   "NFTs Minted",       "⬡",  "0.15s"),
    (stats["applications"],  "Applications",      "📋", "0.2s"),
    (stats["hired"],         "Hired",             "✅", "0.25s"),
    (f"{stats['avg_match']}%","Avg Match",        "🤖", "0.3s"),
]
for col, (val, lbl, icon, delay) in zip([c1,c2,c3,c4,c5,c6], kpis):
    with col:
        st.markdown(f"""
        <div class='m-card' style='animation-delay:{delay};text-align:center;padding:16px;'>
          <div style='font-size:20px;margin-bottom:4px;'>{icon}</div>
          <div class='m-val' style='font-size:22px;'>{val}</div>
          <div class='m-lbl'>{lbl}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ════════════════════════════════════════════════
# ROW 2: SKILLS + ROLES
# ════════════════════════════════════════════════
col_skills, col_roles = st.columns(2, gap="large")

with col_skills:
    from collections import Counter
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
        marker=dict(
            color=[f"rgba(29,158,117,{0.35 + 0.05*(12-i)})" for i in range(len(labels))],
            line=dict(width=0)
        ),
        text=counts, textposition="inside",
        textfont=dict(color="white", size=11),
    ))
    fig.update_layout(
        title=dict(text="Top Skills on Platform", font=dict(color="#8ba8c4", size=14)),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(tickfont=dict(color="#4a6a84",size=10),
                   gridcolor="rgba(255,255,255,.04)", zerolinecolor="rgba(0,0,0,0)"),
        yaxis=dict(tickfont=dict(color="#c8d8e8",size=11)),
        margin=dict(l=0,r=10,t=40,b=10), height=340, bargap=0.3,
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

with col_roles:
    role_counts = talents_df["role"].value_counts().head(8)
    fig2 = go.Figure(go.Pie(
        labels=role_counts.index.tolist(),
        values=role_counts.values.tolist(),
        hole=0.55,
        marker=dict(colors=[
            "#1D9E75","#378ADD","#7F77DD","#EF9F27",
            "#4de8b4","#7ab8f5","#b3aeef","#f5c263"
        ], line=dict(color="rgba(4,13,26,.8)", width=2)),
        textfont=dict(color="white", size=11),
    ))
    fig2.update_layout(
        title=dict(text="Talent by Role", font=dict(color="#8ba8c4", size=14)),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        legend=dict(font=dict(color="#6b8aaa", size=10), bgcolor="rgba(0,0,0,0)"),
        margin=dict(l=0,r=0,t=40,b=0), height=340,
    )
    st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})

st.markdown("<br>", unsafe_allow_html=True)

# ════════════════════════════════════════════════
# ROW 3: MATCH DIST + EXP DIST + LOCATIONS
# ════════════════════════════════════════════════
col_md, col_loc = st.columns([1.4, 1], gap="large")

with col_md:
    import sqlite3
    conn = sqlite3.connect("data/talents.db")
    import pandas as pd
    apps_df = pd.read_sql("SELECT match_score FROM applications", conn)
    conn.close()

    st.markdown("""
    <div class='g-card anim-up' style='padding:20px;'>
      <div class='s-title' style='font-size:15px;margin-bottom:14px;'>Match Score Distribution</div>
    """, unsafe_allow_html=True)
    if not apps_df.empty:
        render_score_distribution(apps_df["match_score"].tolist(), height=200)
    else:
        st.info("No application data yet.")
    st.markdown("</div>", unsafe_allow_html=True)

with col_loc:
    loc_counts = talents_df["location"].value_counts()
    fig3 = go.Figure(go.Bar(
        x=loc_counts.values.tolist(),
        y=loc_counts.index.tolist(),
        orientation="h",
        marker=dict(
            color=["rgba(56,138,221,0.6)" if l=="Remote" else "rgba(29,158,117,0.5)" for l in loc_counts.index],
            line=dict(width=0)
        ),
        text=loc_counts.values.tolist(), textposition="inside",
        textfont=dict(color="white",size=11),
    ))
    fig3.update_layout(
        title=dict(text="Talent by Location", font=dict(color="#8ba8c4",size=14)),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(tickfont=dict(color="#4a6a84",size=10),
                   gridcolor="rgba(255,255,255,.04)", zerolinecolor="rgba(0,0,0,0)"),
        yaxis=dict(tickfont=dict(color="#c8d8e8",size=11)),
        margin=dict(l=0,r=10,t=40,b=10), height=260, bargap=0.3,
    )
    st.plotly_chart(fig3, use_container_width=True, config={"displayModeBar": False})

st.markdown("<br>", unsafe_allow_html=True)

# ════════════════════════════════════════════════
# ROW 4: SCATTER + BUDGET DIST
# ════════════════════════════════════════════════
col_sc, col_bud = st.columns(2, gap="large")

with col_sc:
    # Experience vs Rating scatter
    exp_vals  = talents_df["years_exp"].tolist()
    rat_vals  = talents_df["rating"].tolist()
    comp_vals = talents_df["completion_rate"].tolist()
    names     = talents_df["name"].tolist()

    fig4 = go.Figure(go.Scatter(
        x=exp_vals, y=rat_vals,
        mode="markers",
        marker=dict(
            size=[c/10 + 4 for c in comp_vals],
            color=comp_vals,
            colorscale="Teal",
            showscale=True,
            colorbar=dict(
                title=dict(text="Completion%", font=dict(color="#4a6a84", size=10)),
                tickfont=dict(color="#4a6a84", size=9),
            ),
            line=dict(color="rgba(4,13,26,.5)", width=0.5)
        ),
        text=names,
        hovertemplate="<b>%{text}</b><br>Exp: %{x}yr<br>Rating: %{y}<extra></extra>"
    ))
    fig4.update_layout(
        title=dict(text="Experience vs Rating (bubble = completion%)", font=dict(color="#8ba8c4",size=13)),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(title="Years Experience", titlefont=dict(color="#4a6a84",size=11),
                   tickfont=dict(color="#4a6a84",size=10),
                   gridcolor="rgba(255,255,255,.04)", zerolinecolor="rgba(0,0,0,0)"),
        yaxis=dict(title="Rating", titlefont=dict(color="#4a6a84",size=11),
                   tickfont=dict(color="#4a6a84",size=10),
                   gridcolor="rgba(255,255,255,.04)", zerolinecolor="rgba(0,0,0,0)"),
        margin=dict(l=0,r=60,t=40,b=20), height=280,
    )
    st.plotly_chart(fig4, use_container_width=True, config={"displayModeBar": False})

with col_bud:
    budgets = jobs_df["budget_usdc"].tolist() if not jobs_df.empty else []
    if budgets:
        import numpy as np
        bins   = [0,1500,3000,4500,6000,7500,10000]
        counts, _ = np.histogram(budgets, bins=bins)
        labels    = ["<$1.5k","$1.5-3k","$3-4.5k","$4.5-6k","$6-7.5k",">$7.5k"]
        fig5 = go.Figure(go.Bar(
            x=labels, y=counts,
            marker=dict(
                color=["rgba(239,159,39,0.5)","rgba(239,159,39,0.55)","rgba(29,158,117,0.5)",
                       "rgba(29,158,117,0.6)","rgba(29,158,117,0.65)","rgba(29,158,117,0.7)"],
                line=dict(width=0)
            ),
            text=counts, textposition="outside",
            textfont=dict(color="white",size=11),
        ))
        fig5.update_layout(
            title=dict(text="Job Budget Distribution", font=dict(color="#8ba8c4",size=13)),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(tickfont=dict(color="#c8d8e8",size=11), gridcolor="rgba(0,0,0,0)"),
            yaxis=dict(tickfont=dict(color="#4a6a84",size=10),
                       gridcolor="rgba(255,255,255,.04)", zerolinecolor="rgba(0,0,0,0)"),
            margin=dict(l=0,r=0,t=40,b=10), height=280, bargap=0.3,
        )
        st.plotly_chart(fig5, use_container_width=True, config={"displayModeBar": False})

st.markdown("<br>", unsafe_allow_html=True)

# ════════════════════════════════════════════════
# FOOTER: AI MODEL INFO
# ════════════════════════════════════════════════
st.markdown("""
<div class='g-card' style='text-align:center;padding:28px;'>
  <div class='s-title' style='font-size:16px;margin-bottom:10px;'>🤖 AI Model Transparency</div>
  <div style='font-size:13px;color:#4a6a84;line-height:1.9;max-width:600px;margin:0 auto;'>
    Match scores are computed using a <strong style='color:#c8d8e8;'>weighted linear model</strong>:<br>
    <code style='background:rgba(255,255,255,.05);padding:2px 8px;border-radius:4px;color:#4de8b4;'>
      Score = 0.45×Skill + 0.25×Experience + 0.20×Rating + 0.10×Completion
    </code>
    <br><br>
    Level-2 upgrade: LightGBM ranker trained on synthetic outcomes ·
    Level-3: LLM semantic skill matching via sentence-transformers
  </div>
</div>
""", unsafe_allow_html=True)
