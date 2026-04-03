import sqlite3
import pandas as pd
import os

DB_PATH = "data/talents.db"


def get_connection():
    os.makedirs("data", exist_ok=True)
    return sqlite3.connect(DB_PATH)


def init_db():
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS talents (
            wallet_address TEXT PRIMARY KEY,
            name TEXT, role TEXT, years_exp INTEGER,
            location TEXT, skills TEXT, projects INTEGER,
            rating REAL, completion_rate INTEGER,
            bio TEXT, github TEXT,
            nft_token_id TEXT, nft_tx_hash TEXT,
            availability TEXT DEFAULT 'Available',
            hourly_rate INTEGER DEFAULT 30
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            job_id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT, company TEXT, description TEXT,
            required_skills TEXT, budget_usdc INTEGER,
            timeline_days INTEGER, posted_by_wallet TEXT,
            posted_date TEXT, location_type TEXT DEFAULT 'Remote',
            experience_required INTEGER DEFAULT 2,
            status TEXT DEFAULT 'Open'
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            talent_wallet TEXT, job_id INTEGER,
            match_score REAL, status TEXT DEFAULT 'Pending',
            tx_hash TEXT, applied_date TEXT,
            FOREIGN KEY(talent_wallet) REFERENCES talents(wallet_address),
            FOREIGN KEY(job_id) REFERENCES jobs(job_id)
        )
    """)
    conn.commit()
    conn.close()


def seed_if_empty():
    try:
        conn = get_connection()
        df = pd.read_sql("SELECT COUNT(*) as cnt FROM talents", conn)
        conn.close()
        if df["cnt"].iloc[0] == 0:
            from data.seed_data import seed_database
            seed_database()
    except Exception:
        from data.seed_data import seed_database
        seed_database()


def get_talent(wallet: str) -> pd.DataFrame:
    conn = get_connection()
    df = pd.read_sql(
        "SELECT * FROM talents WHERE wallet_address = ?", conn, params=(wallet,)
    )
    conn.close()
    return df


def get_all_talents() -> pd.DataFrame:
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM talents", conn)
    conn.close()
    return df


def get_all_jobs() -> pd.DataFrame:
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM jobs WHERE status='Open'", conn)
    conn.close()
    return df


def get_applications_for_talent(wallet: str) -> pd.DataFrame:
    conn = get_connection()
    df = pd.read_sql(
        """SELECT a.*, j.title, j.company, j.budget_usdc
           FROM applications a
           JOIN jobs j ON a.job_id = j.job_id
           WHERE a.talent_wallet = ?
           ORDER BY a.id DESC""",
        conn, params=(wallet,)
    )
    conn.close()
    return df


def get_applications_for_job(job_id: int) -> pd.DataFrame:
    conn = get_connection()
    df = pd.read_sql(
        """SELECT a.*, t.name, t.role, t.skills, t.rating, t.completion_rate,
                  t.nft_token_id, t.years_exp
           FROM applications a
           JOIN talents t ON a.talent_wallet = t.wallet_address
           WHERE a.job_id = ?
           ORDER BY a.match_score DESC""",
        conn, params=(job_id,)
    )
    conn.close()
    return df


def upsert_talent(row: dict):
    conn = get_connection()
    conn.execute("""
        INSERT OR REPLACE INTO talents
        (wallet_address,name,role,years_exp,location,skills,projects,rating,
         completion_rate,bio,github,nft_token_id,nft_tx_hash,availability,hourly_rate)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, (
        row["wallet_address"], row["name"], row["role"], row["years_exp"],
        row["location"], row["skills"], row["projects"], row["rating"],
        row["completion_rate"], row.get("bio",""), row.get("github",""),
        row.get("nft_token_id"), row.get("nft_tx_hash"),
        row.get("availability","Available"), row.get("hourly_rate", 30)
    ))
    conn.commit()
    conn.close()


def update_nft(wallet: str, token_id: str, tx_hash: str):
    conn = get_connection()
    conn.execute(
        "UPDATE talents SET nft_token_id=?, nft_tx_hash=? WHERE wallet_address=?",
        (token_id, tx_hash, wallet)
    )
    conn.commit()
    conn.close()


def insert_application(talent_wallet: str, job_id: int, match_score: float, tx_hash: str = None):
    from datetime import date
    conn = get_connection()
    # prevent duplicate applications
    existing = pd.read_sql(
        "SELECT id FROM applications WHERE talent_wallet=? AND job_id=?",
        conn, params=(talent_wallet, job_id)
    )
    if existing.empty:
        conn.execute(
            "INSERT INTO applications (talent_wallet,job_id,match_score,status,tx_hash,applied_date) VALUES (?,?,?,?,?,?)",
            (talent_wallet, job_id, match_score, "Pending", tx_hash, str(date.today()))
        )
        conn.commit()
        conn.close()
        return True
    conn.close()
    return False


def insert_job(row: dict) -> int:
    from datetime import date
    conn = get_connection()
    cur = conn.execute(
        """INSERT INTO jobs (title,company,description,required_skills,budget_usdc,
           timeline_days,posted_by_wallet,posted_date,location_type,experience_required)
           VALUES (?,?,?,?,?,?,?,?,?,?)""",
        (row["title"], row["company"], row["description"], row["required_skills"],
         row["budget_usdc"], row["timeline_days"], row["posted_by_wallet"],
         str(date.today()), row.get("location_type","Remote"),
         row.get("experience_required", 2))
    )
    conn.commit()
    job_id = cur.lastrowid
    conn.close()
    return job_id


def get_platform_stats() -> dict:
    conn = get_connection()
    talents_count = pd.read_sql("SELECT COUNT(*) as c FROM talents", conn)["c"].iloc[0]
    jobs_count    = pd.read_sql("SELECT COUNT(*) as c FROM jobs", conn)["c"].iloc[0]
    apps_count    = pd.read_sql("SELECT COUNT(*) as c FROM applications", conn)["c"].iloc[0]
    hired_count   = pd.read_sql("SELECT COUNT(*) as c FROM applications WHERE status='Hired'", conn)["c"].iloc[0]
    nft_count     = pd.read_sql("SELECT COUNT(*) as c FROM talents WHERE nft_token_id IS NOT NULL", conn)["c"].iloc[0]
    avg_score     = pd.read_sql("SELECT AVG(match_score) as s FROM applications", conn)["s"].iloc[0]
    conn.close()
    return {
        "talents": int(talents_count), "jobs": int(jobs_count),
        "applications": int(apps_count), "hired": int(hired_count),
        "nfts_minted": int(nft_count),
        "avg_match": round(float(avg_score or 0), 1),
    }
