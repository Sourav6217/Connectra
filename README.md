# ⬡ Connectra - Onchain Talent Marketplace

Connectra is a Streamlit-based talent marketplace that connects skilled professionals with employers through transparent, data-driven matching and blockchain-inspired trust signals. The platform combines profile scoring, job posting, candidate discovery, skill testing, interview booking, messaging, and hiring history in one workflow.

## Live Application

https://connectra-on-chain-talent.streamlit.app/

## Project Overview

Connectra is designed around two user journeys:

1. Talent users create profiles, showcase skills, improve scores with skill tests, and apply to relevant jobs.
2. Employers post jobs, discover top candidates, schedule interviews, message candidates, and track hiring outcomes.

The application focuses on trust and quality using:

- Structured profile data
- Matching and ranking logic
- Talent score calculations
- Verifiable activity records (blockchain utility layer)

## Core Features

- Talent profile creation and management
- Employer job posting and dashboard workflows
- Smart candidate matching and ranking
- Marketplace discovery for open opportunities
- Skill tests with timed MCQs and score impact
- Interview booking for shortlisted candidates
- Built-in messaging before hiring decisions
- Hiring history and rating system
- Analytics views for platform insights

## Tech Stack

- Python
- Streamlit
- SQLite (local app database)
- Modular utility layer for matching, UI components, and blockchain-related logic

## Project Structure

```text
app.py
styles.py
requirements.txt
README.md

data/
	seed_data.py
	sqlite_db.py

pages/
	1_Home.py
	2_Create_Profile.py
	3_Talent_Dashboard.py
	4_Marketplace.py
	5_Post_Job.py
	6_Employer_Dashboard.py
	7_Analytics.py
	8_Skill_Tests.py

utils/
	blockchain.py
	matching.py
	ui_components.py
```

## Page Guide

- Home: landing overview and navigation entry point
- Create Profile: talent onboarding and profile setup
- Talent Dashboard: candidate insights, score, and opportunities
- Marketplace: browse and explore talent/jobs
- Post Job: employer job creation flow
- Employer Dashboard: candidate shortlist, interview booking, messaging, and hiring history
- Analytics: platform and engagement metrics
- Skill Tests: timed MCQ assessments per skill area

## Getting Started (Local)

### 1) Clone the repository

```bash
git clone <your-repo-url>
cd Connectra
```

### 2) Install dependencies

```bash
pip install -r requirements.txt
```

### 3) Run the app

```bash
streamlit run app.py
```

## Deployment (Streamlit Cloud)

1. Push this project to GitHub.
2. Open Streamlit Community Cloud and connect your repository.
3. Set the main file path to `app.py`.
4. Deploy.

The database path and app structure are set up to work in Streamlit Cloud environments.

## Notes

- If you are testing with sample data, check the files in `data/`.
- Matching and score behavior can be tuned in `utils/matching.py` and related page logic.
- UI styling and branding can be adjusted in `styles.py` and `utils/ui_components.py`.
