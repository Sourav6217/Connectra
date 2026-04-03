import streamlit as st
import json, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from styles import GLOBAL_CSS
from data.sqlite_db import get_talent, get_all_jobs, insert_application
from utils.matching import calculate_match, get_breakdown, get_success_prob, score_class
from utils.blockchain import mint_application_nft, short_hash

st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

wallet    = st.session_state.get("wallet","0x742d35Cc6634C0532925a3b844Bc454e4438f44e")
talent_df = get_talent(wallet)
jobs_df   = get_all_jobs()

st.markdown("""
<div class='ph aup'>
  <div class='ph-title'>Marketplace</div>
  <div class='ph-sub'>Select a gig · AI match score from your verified profile</div>
</div>
""", unsafe_allow_html=True)

has_profile = not talent_df.empty
talent_row  = talent_df.iloc[0] if has_profile else None

if not has_profile:
    st.markdown("<div class='gc' style='text-align:center;padding:32px;border-color:rgba(239,159,39,.3);'><div style='font-size:28px;margin-bottom:10px;'>⚠️</div><div style='font-size:14px;color:#f5c263;font-weight:600;margin-bottom:6px;'>Profile Required</div><div style='font-size:12px;color:#3a4a5c;'>Create your profile to see AI match scores.</div></div>", unsafe_allow_html=True)
    if st.button("Create Profile First"):
        st.switch_page("pages/2_Create_Profile.py")

if jobs_df.empty:
    st.info("No jobs posted yet."); st.stop()

# Compute all scores
job_scores = {}
for _, job in jobs_df.iterrows():
    job_scores[int(job["job_id"])] = calculate_match(talent_row, job) if has_profile else 0.0

# Filters
f1,f2,f3 = st.columns([1.5,1.2,1.2])
with f1: search = st.text_input("", placeholder="Search title or company...", label_visibility="collapsed")
with f2: loc_f  = st.selectbox("", ["All Locations","Remote","Hybrid","On-site"], label_visibility="collapsed")
with f3: sort_b = st.selectbox("", ["Best Match","Highest Pay","Newest"], label_visibility="collapsed")

rows = []
for _, job in jobs_df.iterrows():
    jid = int(job["job_id"]); sc = job_scores.get(jid, 0.0)
    if search:
        q = search.lower(); req = json.loads(job["required_skills"])
        if not (q in job["title"].lower() or q in job.get("company","").lower() or any(q in s.lower() for s in req)): continue
    if loc_f != "All Locations" and job.get("location_type","") != loc_f: continue
    rows.append((job, sc))

if sort_b == "Best Match":    rows.sort(key=lambda x:x[1], reverse=True)
elif sort_b == "Highest Pay": rows.sort(key=lambda x:x[0]["budget_usdc"], reverse=True)
elif sort_b == "Newest":      rows.sort(key=lambda x:str(x[0].get("posted_date","")), reverse=True)

if not rows:
    st.markdown("<div style='text-align:center;padding:60px;color:#2a3a4a;'>No gigs match your filters.</div>", unsafe_allow_html=True)
    st.stop()

def se(s): return "🟢" if s>=78 else "🟡" if s>=60 else "🔴"
LOC_I = {"Remote":"🌐","Hybrid":"🔀","On-site":"📍"}
AVPAIRS = [("#0c1e3a","#378ADD"),("#0a2d20","#1D9E75"),("#1a1430","#7F77DD"),
           ("#1a0e0a","#D85A30"),("#130a28","#9F7AEA"),("#0a1a0a","#48BB78")]

dd_labels = [f"{se(sc)}  {job['title']}  ·  {job.get('company','')}  ·  ${job['budget_usdc']:,}  ·  Match: {sc:.0f}%"
             for job,sc in rows]
sel_idx = st.selectbox(f"Choose from {len(rows)} gigs:", range(len(rows)), format_func=lambda i: dd_labels[i])

sel_job, sel_sc = rows[sel_idx]
req_skills = json.loads(sel_job["required_skills"])
prob, emoji = get_success_prob(sel_sc)
sc_cls  = score_class(sel_sc)
bar_col = "#1D9E75" if sel_sc>=78 else "#EF9F27" if sel_sc>=60 else "#E24B4A"
loc_type = sel_job.get("location_type","Remote")
bg_c, fg_c = AVPAIRS[sel_idx % len(AVPAIRS)]
initials = "".join(w[0] for w in sel_job["title"].split()[:2]).upper()
skill_tags = " ".join(f"<span class='tag tg' style='font-size:10px;'>{s}</span>" for s in req_skills[:7])
if len(req_skills)>7: skill_tags += f"<span style='font-size:10px;color:#2a3a4a;'> +{len(req_skills)-7}</span>"

st.markdown("<br>", unsafe_allow_html=True)

col_d, col_a = st.columns([1.6, 1], gap="large")

with col_d:
    desc_txt = sel_job.get("description","")
    exp_req  = sel_job.get("experience_required",2)
    st.markdown(f"""
<div class='gc aup'>
  <div style='display:flex;align-items:flex-start;gap:14px;'>
    <div style='width:50px;height:50px;border-radius:12px;background:{bg_c};border:1px solid {fg_c}44;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:15px;color:{fg_c};flex-shrink:0;'>{initials}</div>
    <div style='flex:1;'>
      <div style='font-size:18px;font-weight:700;color:#fff;margin-bottom:3px;'>{sel_job["title"]}</div>
      <div style='font-size:12px;color:#3a4a5c;margin-bottom:8px;'>{sel_job.get("company","Company")} · {LOC_I.get(loc_type,"📍")} {loc_type} · {sel_job["timeline_days"]}d · {sel_job.get("posted_date","—")}</div>
      <div style='margin-bottom:12px;'>{skill_tags}</div>
      <div style='display:flex;align-items:center;gap:12px;'>
        <div style='flex:1;max-width:220px;'>
          <div style='display:flex;justify-content:space-between;font-size:10px;color:#2a3a4a;margin-bottom:3px;'><span>AI Match</span><span style='color:{bar_col};font-weight:700;'>{sel_sc:.0f}%</span></div>
          <div style='background:rgba(255,255,255,.05);border-radius:3px;height:4px;'><div style='height:4px;border-radius:3px;background:{bar_col};width:{sel_sc:.1f}%;'></div></div>
        </div>
        <div style='font-size:11px;color:#3a4a5c;'>{emoji} Success: <span style='color:#fff;font-weight:600;'>{prob:.0f}%</span></div>
        <div style='font-size:17px;font-weight:700;color:#fff;'>${sel_job["budget_usdc"]:,}</div>
      </div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

    st.markdown(f"""
<div class='gc aup d2' style='margin-top:12px;'>
  <div class='st2' style='margin-bottom:8px;'>Job Description</div>
  <div style='font-size:13px;color:#5a7088;line-height:1.75;margin-bottom:14px;'>{desc_txt}</div>
  <hr style='border:none;border-top:1px solid rgba(255,255,255,.05);margin:12px 0;'>
  <div style='display:grid;grid-template-columns:1fr 1fr;gap:8px;font-size:11px;color:#3a4a5c;'>
    <div>Budget: <span style='color:#fff;font-weight:600;'>${sel_job["budget_usdc"]:,}</span></div>
    <div>Timeline: <span style='color:#fff;'>{sel_job["timeline_days"]} days</span></div>
    <div>Type: <span style='color:#fff;'>{loc_type}</span></div>
    <div>Exp: <span style='color:#fff;'>{exp_req}+ yrs</span></div>
  </div>
</div>
""", unsafe_allow_html=True)

with col_a:
    if has_profile:
        breakdown = get_breakdown(talent_row, sel_job)
        bars_html = ""
        for factor, val in breakdown.items():
            col_c = "#1D9E75" if val>=78 else "#EF9F27" if val>=55 else "#E24B4A"
            bars_html += f"""
<div style='margin-bottom:9px;'>
  <div style='display:flex;justify-content:space-between;font-size:11px;color:#3a4a5c;margin-bottom:3px;'><span>{factor}</span><span style='color:#c8d8e8;font-weight:600;'>{val:.0f}%</span></div>
  <div style='background:rgba(255,255,255,.05);border-radius:3px;height:4px;'><div style='height:4px;border-radius:3px;background:{col_c};width:{val:.1f}%;'></div></div>
</div>"""
        st.markdown(f"""
<div class='gc aup d2'>
  <div class='st2' style='margin-bottom:12px;'>Match Breakdown</div>
  {bars_html}
  <div class='formula' style='margin-top:10px;font-size:10px;'>
    Match = 0.45xSkill + 0.25xExp + 0.20xRating + 0.10xCompletion = <span class='hl'>{sel_sc:.0f}%</span>
  </div>
</div>
""", unsafe_allow_html=True)
    else:
        st.markdown("<div class='gc' style='text-align:center;padding:20px;'><div style='color:#f5c263;font-size:12px;'>Create a profile to see your match breakdown</div></div>", unsafe_allow_html=True)

    grad_end = "#4de8b4" if sel_sc>=78 else "#f5c263"
    st.markdown(f"""
<div class='gc aup d3' style='margin-top:12px;border-color:rgba(29,158,117,.3);text-align:center;padding:20px;'>
  <div style='font-size:10px;color:#2a3a4a;margin-bottom:4px;'>YOUR MATCH</div>
  <div style='font-size:48px;font-weight:700;line-height:1;background:linear-gradient(90deg,{bar_col},{grad_end});-webkit-background-clip:text;-webkit-text-fill-color:transparent;'>{sel_sc:.0f}%</div>
  <div class='sp {sc_cls}' style='display:inline-block;margin-top:8px;font-size:11px;'>{emoji} {prob:.0f}% success probability</div>
  <hr style='border:none;border-top:1px solid rgba(255,255,255,.05);margin:12px 0;'>
  <div style='font-size:11px;color:#2a3a4a;'>Applying creates an onchain receipt NFT as proof.</div>
</div>
""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    if has_profile:
        if st.button("Apply Onchain", use_container_width=True, key=f"apply_btn_{sel_job['job_id']}"):
            import time
            with st.spinner("Recording on Polygon..."):
                time.sleep(0.8)
                nft_r = mint_application_nft(wallet, int(sel_job["job_id"]), sel_sc)
                success = insert_application(wallet, int(sel_job["job_id"]), sel_sc, nft_r["tx_hash"])
            if success:
                st.success(f"Applied! Match: {sel_sc:.0f}%")
                st.markdown(f"<div style='font-size:11px;margin-top:6px;'><span class='tag tg'>NFT #{nft_r['token_id']}</span><br><span style='font-family:DM Mono,monospace;color:#2a3a4a;font-size:9px;'>Tx: {short_hash(nft_r['tx_hash'])}</span></div>", unsafe_allow_html=True)
            else:
                st.warning("Already applied to this job.")
    else:
        if st.button("Create Profile to Apply", use_container_width=True):
            st.switch_page("pages/2_Create_Profile.py")

# Other recommended
st.markdown("<br>", unsafe_allow_html=True)
other = [r for r in rows if int(r[0]["job_id"]) != int(sel_job["job_id"])][:6]
if other:
    st.markdown("<div class='st2' style='margin-bottom:12px;'>Other Recommended Gigs</div>", unsafe_allow_html=True)
    cards = ""
    for job,sc in other:
        sc_c = score_class(sc); bc = "#1D9E75" if sc>=78 else "#EF9F27" if sc>=60 else "#E24B4A"
        try: req = json.loads(job["required_skills"])
        except: req = []
        st_h = " ".join(f"<span class='tag tg' style='font-size:9px;'>{s}</span>" for s in req[:3])
        cards += f"""
<div style='display:flex;align-items:center;gap:10px;padding:10px 14px;background:#0e1525;border:1px solid rgba(255,255,255,.07);border-radius:10px;margin-bottom:6px;'>
  <div style='flex:1;min-width:0;'>
    <div style='font-size:12px;font-weight:600;color:#fff;'>{job["title"]}</div>
    <div style='font-size:10px;color:#3a4a5c;margin:1px 0;'>{job.get("company","")} · ${job["budget_usdc"]:,} · {job.get("location_type","Remote")}</div>
    <div>{st_h}</div>
  </div>
  <div style='text-align:right;flex-shrink:0;'>
    <div class='sp {sc_c}' style='font-size:11px;'>{sc:.0f}%</div>
    <div style='font-size:9px;color:#2a3a4a;margin-top:3px;'>{job["timeline_days"]}d</div>
  </div>
</div>"""
    st.markdown(cards, unsafe_allow_html=True)
