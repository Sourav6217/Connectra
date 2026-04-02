import streamlit as st

st.title("Welcome to Connectra")
st.markdown("**Verified Talent. Onchain Trust. Instant Matches.**")

col1, col2 = st.columns(2)
with col1:
    st.image("https://picsum.photos/id/1015/600/400", use_column_width=True)
    if st.button("👤 I am Talent", use_container_width=True, type="primary"):
        st.session_state.user_role = "talent"
        st.switch_page("pages/3_Talent_Dashboard.py")

with col2:
    st.image("https://picsum.photos/id/201/600/400", use_column_width=True)
    if st.button("🏢 I am Employer", use_container_width=True):
        st.session_state.user_role = "employer"
        st.switch_page("pages/6_Employer_Dashboard.py")

st.info("💡 This is a fully functional prototype. Try every button!")