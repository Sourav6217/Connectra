import streamlit as st
from data.sqlite_db import get_connection
import pandas as pd
from utils.matching import get_risk_level
from utils.ui_components import render_gauge

st.title("👤 Talent Dashboard")

conn = get_connection()
df = pd.read_sql("SELECT * FROM talents WHERE wallet_address=?", conn, 
                 params=(st.session_state.get("wallet", "0xDemoWallet"),))

if not df.empty:
    row = df.iloc[0]
    st.subheader(f"Welcome, {row['name']}!")
    
    col1, col2, col3 = st.columns(3)
    with col1: st.metric("Role", row['role'])
    with col2: st.metric("Experience", f"{row['years_exp']} years")
    with col3: st.metric("Projects", row['projects'])
    
    render_gauge("Overall Talent Score", 87)
    render_gauge("Skill Confidence", 92, "#00ccff")
    
    if row['nft_token_id']:
        st.success(f"✅ NFT Minted # {row['nft_token_id']}")
    
    st.subheader("My Applications")
    apps = pd.read_sql("SELECT * FROM applications WHERE talent_wallet=?", conn, 
                       params=(st.session_state.get("wallet", "0xDemoWallet"),))
    st.dataframe(apps, use_container_width=True)
else:
    st.warning("No profile yet. Create one first!")
    st.switch_page("pages/2_Talent_Profile_Create.py")