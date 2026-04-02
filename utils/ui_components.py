import streamlit as st
import plotly.graph_objects as go

def render_gauge(label, value, color="#00ff88"):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        title={'text': label},
        gauge={'axis': {'range': [0, 100]},
               'bar': {'color': color},
               'steps': [{'range': [0, 100], 'color': 'rgba(255,255,255,0.1)'}]}))
    fig.update_layout(height=200, margin=dict(l=10, r=10, t=40, b=10))
    st.plotly_chart(fig, use_container_width=True)