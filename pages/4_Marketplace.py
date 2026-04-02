import streamlit as st
import pandas as pd
from data.sqlite_db import get_connection
from utils.matching import calculate_match, get_success_prob

st.title("🔥 Job Marketplace")

conn = get_connection()
jobs = pd.read_sql("SELECT * FROM jobs", conn)
talent = pd.read_sql("SELECT * FROM talents WHERE wallet_address=?", conn, 
                     params=(st.session_state.get("wallet", "0xDemoWallet"),))

if not talent.empty:
    for _, job in jobs.iterrows():
        match = calculate_match(talent.iloc[0], job)
        prob, emoji = get_success_prob(match)
        
        with st.container():
            col1, col2, col3 = st.columns([3,1,1])
            with col1:
                st.write(f"**{job['title']}**")
                st.caption(job['description'][:120] + "...")
            with col2:
                st.metric("Match", f"{match}%")
            with col3:
                if st.button("Apply", key=f"apply_{job['job_id']}"):
                    conn.execute("INSERT INTO applications VALUES (?,?,?,?,?)",
                                 (talent.iloc[0]['wallet_address'], job['job_id'], match, "Pending", None))
                    conn.commit()
                    st.success("Applied onchain! ✅")
            st.divider()
else:
    st.warning("Create profile first")