import streamlit as st
from data.sqlite_db import init_db, seed_if_empty
import pandas as pd
import json

st.set_page_config(page_title="Connectra • Onchain Talent", page_icon="🔗", layout="wide")

# Initialize
init_db()
seed_if_empty()

# Session state
if "user_role" not in st.session_state:
    st.session_state.user_role = None
if "wallet" not in st.session_state:
    st.session_state.wallet = None

# Sidebar Demo Mode
with st.sidebar:
    st.title("🔗 Connectra")
    st.caption("Onchain Talent Marketplace")
    role = st.radio("Demo as:", ["Talent", "Employer"], horizontal=True)
    st.session_state.user_role = role.lower()
    
    if st.button("🔄 Reset Demo Data"):
        from data.seed_data import seed_database
        seed_database()
        st.rerun()
    
    st.divider()
    st.write("**Demo Wallet**")
    st.code("0x742d35Cc6634C0532925a3b844Bc454e4438f44e")

# Page navigation
page = st.navigation([
    st.Page("pages/1_Home.py", title="Home", icon="🏠"),
    st.Page("pages/2_Talent_Profile_Create.py", title="Create Profile", icon="👤"),
    st.Page("pages/3_Talent_Dashboard.py", title="Talent Dashboard", icon="📊"),
    st.Page("pages/4_Marketplace.py", title="Marketplace", icon="🔥"),
    st.Page("pages/5_Employer_Post_Job.py", title="Post Job", icon="📢"),
    st.Page("pages/6_Employer_Dashboard.py", title="Employer Dashboard", icon="🏢"),
])

page.run()