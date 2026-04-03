# ⬡ Connectra — Onchain Talent Marketplace

> **Verified Talent. Onchain Trust. Instant Matches.**

A premium Streamlit prototype combining Soulbound NFT identity, AI-powered matching,
and a full employer hiring flow on Polygon Amoy testnet.

---

## 🚀 Quick Start

```bash
pip install -r requirements.txt
streamlit run app.py
```

Open **http://localhost:8501**

---

## 📂 Structure

```
connectra/
├── app.py                          # Entry + sidebar + navigation
├── styles.py                       # Dark theme CSS + animations
├── requirements.txt
│
├── data/
│   ├── sqlite_db.py                # DB schema + queries
│   └── seed_data.py                # 80 talents, 30 jobs, 80 applications
│
├── utils/
│   ├── matching.py                 # AI matching engine (weighted model)
│   ├── blockchain.py               # NFT mint / job post / hire simulation
│   └── ui_components.py            # Gauges, radar, bars, cards
│
└── pages/
    ├── 1_🏠_Home.py                # Hero + platform stats + entry
    ├── 2_✨_Create_Profile.py      # 4-step wizard + NFT mint
    ├── 3_📊_Talent_Dashboard.py    # Profile, AI insights, NFT, applications, skill gaps
    ├── 4_🔥_Marketplace.py         # Filterable jobs + inline apply
    ├── 5_📢_Post_Job.py            # Employer job post + live preview
    ├── 6_🏢_Employer_Dashboard.py  # Candidates, leaderboard, hire flow
    └── 7_📈_Analytics.py           # Platform-wide data visualizations
```

---

## 🎨 Design Language

- **Font:** Syne (headings) + DM Sans (body) + DM Mono (addresses)
- **Theme:** Deep navy (`#040d1a`) + teal accent (`#1D9E75`, `#4de8b4`)
- **Animations:** fadeUp, fillBar, bounce, glow — pure CSS
- **Charts:** Plotly (dark, transparent bg, no axis clutter)

---

## 🤖 Matching Formula

```
Match Score = 0.45 × Skill Match
            + 0.25 × Experience Fit
            + 0.20 × Peer Rating
            + 0.10 × Completion Rate
```

---

## 🌐 Deploy to Streamlit Cloud

1. Push to GitHub
2. share.streamlit.io → connect repo → main file: `app.py`
3. Deploy → live in ~2 min ✅

---

## 🎤 Pitch One-liner

> *"We replace inflated CVs with tamper-proof on-chain reputation.
> Our AI predicts job success — not keyword matches.
> Hire smarter. Get hired faster."*
