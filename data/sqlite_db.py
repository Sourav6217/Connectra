import sqlite3
import pandas as pd
import os

DB_PATH = "data/talents.db"

def get_connection():
    return sqlite3.connect(DB_PATH)

def init_db():
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS talents (
            wallet_address TEXT PRIMARY KEY,
            name TEXT,
            role TEXT,
            years_exp INTEGER,
            location TEXT,
            skills TEXT,
            projects INTEGER,
            rating REAL,
            completion_rate INTEGER,
            nft_token_id TEXT,
            nft_tx_hash TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            job_id INTEGER PRIMARY KEY,
            title TEXT,
            description TEXT,
            required_skills TEXT,
            budget_usdc INTEGER,
            timeline_days INTEGER,
            posted_by_wallet TEXT,
            posted_date TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS applications (
            talent_wallet TEXT,
            job_id INTEGER,
            match_score REAL,
            status TEXT,
            tx_hash TEXT,
            FOREIGN KEY(talent_wallet) REFERENCES talents(wallet_address),
            FOREIGN KEY(job_id) REFERENCES jobs(job_id)
        )
    """)
    conn.commit()
    conn.close()

def seed_if_empty():
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM talents", conn)
    if df.empty:
        from data.seed_data import seed_database
        seed_database()
    conn.close()