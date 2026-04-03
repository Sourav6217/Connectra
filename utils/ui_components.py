import streamlit as st
import plotly.graph_objects as go
import json


# ══════════════════════════════════════════
# GAUGE CHART
# ══════════════════════════════════════════
def render_gauge(label: str, value: float, color: str = "#1D9E75", height: int = 220):
    bar_color = color
    if color == "auto":
        bar_color = "#1D9E75" if value >= 78 else "#EF9F27" if value >= 60 else "#E24B4A"

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        domain={"x": [0, 1], "y": [0, 1]},
        title={"text": label, "font": {"color": "#6b8aaa", "size": 13, "family": "DM Sans"}},
        number={"font": {"color": "#ffffff", "size": 42, "family": "Syne"},
                "suffix": "%"},
        gauge={
            "axis": {
                "range": [0, 100],
                "tickcolor": "#2a3a4a", "tickfont": {"color": "#2a3a4a", "size": 10}
            },
            "bar":  {"color": bar_color, "thickness": 0.22},
            "bgcolor": "rgba(0,0,0,0)",
            "bordercolor": "rgba(0,0,0,0)",
            "steps": [
                {"range": [0, 60],   "color": "rgba(226,75,74,.08)"},
                {"range": [60, 80],  "color": "rgba(239,159,39,.08)"},
                {"range": [80, 100], "color": "rgba(29,158,117,.08)"},
            ],
            "threshold": {
                "line": {"color": "#4de8b4", "width": 2},
                "thickness": 0.75, "value": value
            }
        }
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        height=height, margin=dict(l=20, r=20, t=50, b=10),
        font=dict(color="#8ba8c4")
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


# ══════════════════════════════════════════
# RADAR CHART
# ══════════════════════════════════════════
def render_radar(categories: list, talent_vals: list, req_vals: list = None, height: int = 290):
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=talent_vals + [talent_vals[0]],
        theta=categories + [categories[0]],
        fill="toself",
        fillcolor="rgba(29,158,117,.18)",
        line=dict(color="#1D9E75", width=2.5),
        marker=dict(color="#4de8b4", size=6),
        name="Your Profile"
    ))
    if req_vals:
        fig.add_trace(go.Scatterpolar(
            r=req_vals + [req_vals[0]],
            theta=categories + [categories[0]],
            fill="toself",
            fillcolor="rgba(56,138,221,.09)",
            line=dict(color="#378ADD", width=1.5, dash="dash"),
            marker=dict(color="#7ab8f5", size=4),
            name="Job Requirement"
        ))
    fig.update_layout(
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(visible=True, range=[0, 100],
                            tickfont=dict(color="#2a3a4a", size=9),
                            gridcolor="rgba(29,158,117,.1)",
                            linecolor="rgba(29,158,117,.12)"),
            angularaxis=dict(tickfont=dict(color="#8ba8c4", size=11),
                             gridcolor="rgba(29,158,117,.1)")
        ),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        showlegend=bool(req_vals),
        legend=dict(font=dict(color="#6b8aaa", size=11), bgcolor="rgba(0,0,0,0)",
                    orientation="h", yanchor="bottom", y=-0.18, xanchor="center", x=0.5),
        margin=dict(l=30, r=30, t=20, b=40),
        height=height,
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


# ══════════════════════════════════════════
# SKILLS TAGS
# ══════════════════════════════════════════
TAG_COLORS = ["tg", "tb", "ta", "tp", "tc", "tg", "tb"]

def render_skills(skills: list | str, limit: int = 12):
    if isinstance(skills, str):
        try:
            skills = json.loads(skills)
        except Exception:
            skills = []
    skills = skills[:limit]
    tags = " ".join(
        f"<span class='tag {TAG_COLORS[i % len(TAG_COLORS)]}'>{s}</span>"
        for i, s in enumerate(skills)
    )
    st.markdown(tags, unsafe_allow_html=True)


# ══════════════════════════════════════════
# STAT BADGE (inline)
# ══════════════════════════════════════════
def stat_badge(icon: str, text: str) -> str:
    return f"<span class='stat-b'>{icon} {text}</span>"


# ══════════════════════════════════════════
# PROGRESS BAR (HTML)
# ══════════════════════════════════════════
def html_bar(label: str, value: float, color_cls: str = "bar", show_val: bool = True) -> str:
    val_disp = f"{value:.0f}%" if show_val else ""
    text_col  = "#4de8b4" if color_cls == "bar" else "#f5c263" if "a" in color_cls else "#7ab8f5"
    return f"""
    <div style='margin-bottom:12px;'>
      <div style='display:flex;justify-content:space-between;margin-bottom:4px;'>
        <div style='font-size:12px;color:#8ba8c4;'>{label}</div>
        <div style='font-size:12px;color:{text_col};font-weight:600;'>{val_disp}</div>
      </div>
      <div class='bar-bg'><div class='{color_cls}' style='width:{value}%;'></div></div>
    </div>"""


# ══════════════════════════════════════════
# NFT CARD HTML
# ══════════════════════════════════════════
def nft_card_html(name: str, role: str, token_id: str, tx_hash: str, wallet: str) -> str:
    from utils.blockchain import short_hash, format_wallet
    return f"""
    <div class='nft-card'>
      <div style='font-size:10px;letter-spacing:.14em;color:#2a4a34;
                  text-transform:uppercase;margin-bottom:12px;'>
        Soulbound Identity · Polygon Amoy
      </div>
      <div style='display:flex;align-items:center;gap:14px;margin-bottom:14px;'>
        <div style='width:50px;height:50px;border-radius:14px;
                    background:rgba(29,158,117,.15);border:1px solid #1D9E75;
                    display:flex;align-items:center;justify-content:center;font-size:26px;'>
          ⬡
        </div>
        <div>
          <div style='font-family:Syne,sans-serif;font-size:16px;font-weight:700;color:#fff;'>
            Talent #{token_id}
          </div>
          <div style='font-size:12px;color:#6b8aaa;margin-top:2px;'>{name} · {role}</div>
        </div>
      </div>
      <hr class='div'>
      <div style='display:grid;grid-template-columns:1fr 1fr;gap:10px;font-size:11px;'>
        <div>
          <div style='color:#2a4a34;margin-bottom:3px;'>Wallet</div>
          <div class='nft-hex'>{format_wallet(wallet)}</div>
        </div>
        <div>
          <div style='color:#2a4a34;margin-bottom:3px;'>Tx Hash</div>
          <div class='nft-hex'>{short_hash(tx_hash)}</div>
        </div>
        <div>
          <div style='color:#2a4a34;margin-bottom:3px;'>Network</div>
          <div style='color:#c8d8e8;'>Polygon Amoy</div>
        </div>
        <div>
          <div style='color:#2a4a34;margin-bottom:3px;'>Type</div>
          <div style='color:#4de8b4;font-weight:600;'>Soulbound</div>
        </div>
      </div>
    </div>"""


# ══════════════════════════════════════════
# HORIZONTAL BAR CHART (Plotly)
# ══════════════════════════════════════════
def render_hbar(names: list, scores: list, highlight_name: str = "", height: int = 240):
    colors = ["#1D9E75" if highlight_name and highlight_name.split()[0] in n else "#1e4a70"
              for n in names]
    fig = go.Figure(go.Bar(
        x=scores, y=names, orientation="h",
        marker=dict(color=colors, line=dict(width=0)),
        text=[f"{s:.0f}%" for s in scores],
        textposition="inside",
        textfont=dict(color="white", size=12, family="Syne"),
        hovertemplate="%{y}: %{x:.1f}%<extra></extra>"
    ))
    fig.add_vline(x=75, line_dash="dot", line_color="#2a3a4a", line_width=1,
                  annotation_text="Threshold", annotation_font_color="#3d5a7a",
                  annotation_font_size=10)
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(range=[0, 100], tickfont=dict(color="#2a3a4a", size=10),
                   gridcolor="rgba(255,255,255,.04)", zerolinecolor="rgba(0,0,0,0)"),
        yaxis=dict(tickfont=dict(color="#c8d8e8", size=12)),
        margin=dict(l=0, r=20, t=10, b=20), height=height, bargap=0.3,
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


# ══════════════════════════════════════════
# PLATFORM ANALYTICS BAR CHART
# ══════════════════════════════════════════
def render_score_distribution(scores: list, height: int = 200):
    import numpy as np
    bins  = list(range(0, 101, 10))
    counts, _ = np.histogram(scores, bins=bins)
    labels = [f"{b}-{b+10}" for b in bins[:-1]]
    colors = ["#E24B4A" if b < 60 else "#EF9F27" if b < 80 else "#1D9E75" for b in bins[:-1]]

    fig = go.Figure(go.Bar(
        x=labels, y=counts,
        marker=dict(color=colors, line=dict(width=0)),
        hovertemplate="%{x}: %{y} applicants<extra></extra>"
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(tickfont=dict(color="#4a6a84", size=10), gridcolor="rgba(0,0,0,0)"),
        yaxis=dict(tickfont=dict(color="#4a6a84", size=10),
                   gridcolor="rgba(255,255,255,.04)", zerolinecolor="rgba(0,0,0,0)"),
        margin=dict(l=0, r=0, t=10, b=10), height=height, bargap=0.25,
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
