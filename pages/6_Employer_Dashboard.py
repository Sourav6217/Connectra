import streamlit as st
import pandas as pd
from data.sqlite_db import get_connection
from utils.matching import calculate_match

st.title("🏢 Employer Dashboard")

conn = get_connection()
jobs = pd.read_sql("SELECT * FROM jobs", conn)
talents = pd.read_sql("SELECT * FROM talents", conn)

st.subheader("Best Candidates for your jobs")

for _, job in jobs.iterrows():
    st.write(f"**{job['title']}**")
    matches = []
    for _, talent in talents.iterrows():
        score = calculate_match(talent, job)
        matches.append({"name": talent['name'], "score": score})
    
    matches_df = pd.DataFrame(matches).sort_values("score", ascending=False).head(5)
    st.dataframe(matches_df, use_container_width=True)
    st.divider()