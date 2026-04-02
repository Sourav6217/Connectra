import streamlit as st
from data.sqlite_db import get_connection
from utils.blockchain import mint_nft
import json

st.title("Create Your Onchain Profile")

with st.form("profile_form"):
    name = st.text_input("Full Name")
    role = st.selectbox("Role", ["Software Engineer", "Data Analyst", "Full Stack Developer", ...])  # you can expand
    years = st.slider("Years of Experience", 0, 15, 3)
    location = st.selectbox("Location", ["Mumbai", "Bangalore", "Remote", ...])
    skills = st.multiselect("Skills", ["Python","SQL","React","AWS","Docker","Machine Learning","Excel","Power BI","Node.js","Java"])
    projects = st.number_input("Number of Projects", 0, 50, 5)
    rating = st.slider("Self Rating (1-5)", 1.0, 5.0, 4.5, 0.1)
    completion = st.slider("Project Completion Rate %", 0, 100, 85)
    
    submitted = st.form_submit_button("Create Profile & Mint NFT")
    
    if submitted and name and skills:
        conn = get_connection()
        skills_json = json.dumps(skills)
        conn.execute("""
            INSERT OR REPLACE INTO talents VALUES (?,?,?,?,?,?,?,?,?,?,?)
        """, (st.session_state.get("wallet", "0xDemoWallet"), name, role, years, location,
              skills_json, projects, rating, completion, None, None))
        conn.commit()
        
        # Mint NFT
        token_id, tx, link, _ = mint_nft(st.session_state.get("wallet", "0xDemoWallet"), name, role, skills, 87)
        conn.execute("UPDATE talents SET nft_token_id=?, nft_tx_hash=? WHERE wallet_address=?", 
                     (token_id, tx, st.session_state.get("wallet", "0xDemoWallet")))
        conn.commit()
        conn.close()
        
        st.success(f"✅ Profile created! NFT minted → Token #{token_id}")
        st.markdown(f"[View on Polygon Amoy]({link})")
        st.switch_page("pages/3_Talent_Dashboard.py")