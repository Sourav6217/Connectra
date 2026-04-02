import streamlit as st
import json
from data.sqlite_db import get_connection

st.title("Post a New Job")

with st.form("job_form"):
    title = st.text_input("Job Title")
    desc = st.text_area("Description")
    req_skills = st.multiselect("Required Skills", ["Python","SQL","React","AWS","Docker","Machine Learning","Excel"])
    budget = st.slider("Budget (USDC)", 1000, 10000, 3500)
    timeline = st.slider("Timeline (days)", 15, 180, 60)
    
    if st.form_submit_button("Post Job onchain"):
        conn = get_connection()
        skills_json = json.dumps(req_skills)
        conn.execute("INSERT INTO jobs (title,description,required_skills,budget_usdc,timeline_days) VALUES (?,?,?,?,?)",
                     (title, desc, skills_json, budget, timeline))
        conn.commit()
        st.success("Job posted on Polygon testnet!")
        st.switch_page("pages/6_Employer_Dashboard.py")