import pandas as pd
import random
import json
import sqlite3
import os
from pathlib import Path

try:
    from faker import Faker
    fake = Faker()
    Faker.seed(42)
    HAS_FAKER = True
except ImportError:
    HAS_FAKER = False

random.seed(42)

SKILLS_POOL = [
    "Python","SQL","JavaScript","React","AWS","Docker","Excel","Power BI",
    "Machine Learning","Data Analysis","Java","Node.js","MongoDB","Git",
    "TypeScript","Kubernetes","Tableau","Django","Flask","FastAPI",
    "Pandas","NumPy","Scikit-learn","TensorFlow","Blockchain","Solidity",
    "Web3.py","Risk Analytics","Financial Modeling","Streamlit"
]

ROLES = [
    "Software Engineer","Data Analyst","Full Stack Developer","Backend Developer",
    "Frontend Developer","Product Manager","Data Scientist","DevOps Engineer",
    "UI/UX Designer","QA Engineer","Risk Analyst","ML Engineer","Quant Analyst"
]

LOCATIONS = ["Mumbai","Bangalore","Delhi","Hyderabad","Pune","Chennai","Remote"]

COMPANIES = [
    "FinEdge Technologies","DataStart India","CapFirst NBFC","GrowthStack SaaS",
    "AlphaTrade Desk","TechCorp India","NexaAI","CloudBase Systems","RapidFlow",
    "QuantumLeap Labs","ZeroGravity Tech","PeakMetrics","InnovateBridge"
]

NAMES = [
    "Sourav Rana","Priya Kapoor","Arjun Mehta","Neha Sharma","Vikram Tiwari",
    "Ananya Bose","Rohit Chandra","Lakshmi Krishnan","Kartik Patel","Riya Gupta",
    "Aarav Singh","Divya Nair","Siddharth Rao","Pooja Verma","Manish Joshi",
    "Shreya Das","Abhishek Mishra","Tanvi Iyer","Kunal Agarwal","Meera Pillai",
    "Rahul Bansal","Sonali Desai","Nikhil Reddy","Kavya Shah","Amit Malhotra",
    "Preeti Sinha","Varun Kumar","Deepika Pandey","Gaurav Jain","Anjali Nambiar",
    "Harish Menon","Swati Dubey","Tarun Saxena","Roshni Paul","Akash Yadav",
    "Pallavi Misra","Karan Sethi","Shweta Bhatt","Rohan Tripathi","Smita Patil"
]


def _fake_name():
    if HAS_FAKER:
        return fake.name()
    return random.choice(NAMES)


def _fake_para():
    sentences = [
        "We are building next-generation financial infrastructure using cutting-edge technology.",
        "This role requires strong analytical skills and the ability to work in fast-paced environments.",
        "Join our high-growth startup and help shape the future of data-driven decision making.",
        "Looking for a passionate individual who can deliver results and collaborate cross-functionally.",
        "Strong problem-solving skills and attention to detail are essential for this position.",
        "You will work with senior engineers and product managers to build scalable solutions.",
        "Remote-friendly team with excellent benefits and a culture of continuous learning.",
        "Experience with modern tech stacks and agile methodologies is a plus.",
    ]
    return " ".join(random.sample(sentences, 2))


def generate_talents(n=80):
    data = []
    used_wallets = set()
    for i in range(n):
        skills = random.sample(SKILLS_POOL, k=random.randint(4, 9))
        wallet = f"0x{random.randint(10**15, 10**16-1):016x}"
        while wallet in used_wallets:
            wallet = f"0x{random.randint(10**15, 10**16-1):016x}"
        used_wallets.add(wallet)
        data.append({
            "wallet_address": wallet,
            "name": _fake_name(),
            "role": random.choice(ROLES),
            "years_exp": random.randint(1, 12),
            "location": random.choice(LOCATIONS),
            "skills": json.dumps(skills),
            "projects": random.randint(3, 25),
            "rating": round(random.uniform(3.5, 5.0), 1),
            "completion_rate": random.randint(62, 99),
            "bio": "Passionate professional with expertise in data-driven solutions and modern tech stacks.",
            "github": f"https://github.com/user{i+1000}",
            "nft_token_id": str(random.randint(10000, 99999)) if random.random() > 0.4 else None,
            "nft_tx_hash": f"0x{random.randint(10**20,10**30):064x}" if random.random() > 0.4 else None,
            "availability": random.choice(["Available","Part-time","Not Available"]),
            "hourly_rate": random.randint(15, 80),
            "test_score_bonus": round(random.uniform(0, 8), 1) if random.random() > 0.5 else 0,
        })
    return pd.DataFrame(data)


def generate_jobs(n=30):
    data = []
    for i in range(n):
        req_skills = random.sample(SKILLS_POOL, k=random.randint(3, 7))
        comp = random.choice(COMPANIES)
        role = random.choice(ROLES)
        data.append({
            "job_id": i + 1,
            "title": f"{role}",
            "company": comp,
            "description": _fake_para(),
            "required_skills": json.dumps(req_skills),
            "budget_usdc": random.randint(1200, 7500),
            "timeline_days": random.randint(25, 120),
            "posted_by_wallet": f"0x{random.randint(10**15,10**16-1):016x}",
            "posted_date": f"2025-0{random.randint(1,9)}-{random.randint(10,28):02d}",
            "location_type": random.choice(["Remote","Hybrid","On-site"]),
            "experience_required": random.randint(1, 8),
            "status": "Open",
        })
    return pd.DataFrame(data)


def seed_database(db_path=None):
    if db_path is None:
        _base = Path(__file__).resolve().parent.parent
        db_path = str(_base / "data" / "talents.db")

    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    talents_df = generate_talents(80)
    jobs_df = generate_jobs(30)

    talents_df.to_sql("talents", conn, if_exists="replace", index=False)
    jobs_df.to_sql("jobs", conn, if_exists="replace", index=False)

    apps = []
    wallets = talents_df["wallet_address"].tolist()
    for _ in range(80):
        wallet = random.choice(wallets)
        job_id = random.randint(1, 30)
        match_score = round(random.uniform(48, 95), 1)
        apps.append({
            "talent_wallet": wallet,
            "job_id": job_id,
            "match_score": match_score,
            "status": random.choice(["Pending","Shortlisted","Hired","Rejected"]),
            "tx_hash": f"0x{random.randint(10**20,10**30):064x}" if random.random() > 0.45 else None,
            "applied_date": f"2025-0{random.randint(1,9)}-{random.randint(10,28):02d}",
        })
    pd.DataFrame(apps).to_sql("applications", conn, if_exists="replace", index=False)
    conn.close()
    print("✅ Synthetic data seeded successfully!")


if __name__ == "__main__":
    seed_database()
