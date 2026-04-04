# ⬡ Connectra — Onchain Talent Marketplace

## Quick Start

```bash
pip install -r requirements.txt
streamlit run app.py
```

## New in this version

- **Fixed**: DB path anchored to project root — works on Streamlit Cloud
- **Fixed**: Sidebar always visible with sticky branding
- **Fixed**: Outline SVG icons replace emoji throughout
- **New**: Skill Tests (8_Skill_Tests.py) — timed MCQ per skill, boosts Talent Score
- **New**: Interview Booking — employers schedule from Top Candidates tab
- **New**: Messaging — quick chat before hire
- **New**: Hiring History — past/ongoing hires with rating system
- **Updated**: Talent score formula includes skill test bonus (10% weight)

## Deploy to Streamlit Cloud

1. Push to GitHub
2. share.streamlit.io → connect repo → main file: `app.py`
3. Deploy → live in ~2 min ✅
