import pandas as pd
import numpy as np
from faker import Faker
import random
import json
import sqlite3

fake = Faker()
Faker.seed(42)

SKILLS_POOL = ["Python", "SQL", "JavaScript", "React", "AWS", "Docker", "Excel", "Power BI",
               "Machine Learning", "Data Analysis", "Java", "Node.js", "MongoDB", "Git",
               "TypeScript", "Kubernetes", "Tableau", "Django", "Flask", "FastAPI"]

ROLES = ["Software Engineer", "Data Analyst", "Full Stack Developer", "Backend Developer",
         "Frontend Developer", "Product Manager", "Data Scientist", "DevOps Engineer",
         "UI/UX Designer", "QA Engineer"]

def generate_talents(n=80):
    data = []
    for i in range(n):
        skills = random.sample(SKILLS_POOL, k=random.randint(4, 8))
        data.append({
            "wallet_address": f"0x{random.randint(10**15, 10**16-1):016x}",
            "name": fake.name(),
            "role": random.choice(ROLES),
            "years_exp": random.randint(1, 12),
            "location": random.choice(["Mumbai", "Bangalore", "Delhi", "Hyderabad", "Pune", "Remote"]),
            "skills": json.dumps(skills),
            "projects": random.randint(3, 25),
            "rating": round(random.uniform(3.8, 5.0), 1),
            "completion_rate": random.randint(65, 98),
            "nft_token_id": None,
            "nft_tx_hash": None
        })
    return pd.DataFrame(data)

def generate_jobs(n=30):
    data = []
    for i in range(n):
        req_skills = random.sample(SKILLS_POOL, k=random.randint(3, 7))
        data.append({
            "job_id": i+1,
            "title": f"{random.choice(ROLES)} - {fake.company()}",
            "description": fake.paragraph(nb_sentences=3),
            "required_skills": json.dumps(req_skills),
            "budget_usdc": random.randint(1200, 6500),
            "timeline_days": random.randint(30, 120),
            "posted_by_wallet": f"0x{random.randint(10**15, 10**16-1):016x}",
            "posted_date": fake.date_this_year()
        })
    return pd.DataFrame(data)

def seed_database():
    conn = sqlite3.connect('data/talents.db')
    talents_df = generate_talents(80)
    jobs_df = generate_jobs(30)
    
    talents_df.to_sql('talents', conn, if_exists='replace', index=False)
    jobs_df.to_sql('jobs', conn, if_exists='replace', index=False)
    
    # Sample applications
    apps = []
    for _ in range(60):
        talent = random.choice(talents_df['wallet_address'].tolist())
        job_id = random.randint(1, 30)
        match_score = round(random.uniform(58, 94), 1)
        apps.append({
            "talent_wallet": talent,
            "job_id": job_id,
            "match_score": match_score,
            "status": random.choice(["Pending", "Shortlisted", "Hired"]),
            "tx_hash": f"0x{random.randint(10**20, 10**30):064x}" if random.random() > 0.5 else None
        })
    pd.DataFrame(apps).to_sql('applications', conn, if_exists='replace', index=False)
    conn.close()
    print("✅ Synthetic data seeded!")