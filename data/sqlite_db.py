import sqlite3
import pandas as pd
import os

DB_PATH = "data/talents.db"


def get_connection():
    os.makedirs("data", exist_ok=True)
    return sqlite3.connect(DB_PATH)


def _ensure_column(conn, table: str, column: str, definition: str):
    cols = pd.read_sql(f"PRAGMA table_info({table})", conn)["name"].tolist()
    if column not in cols:
        conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")


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

    conn.execute("""
        CREATE TABLE IF NOT EXISTS skill_tests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            talent_wallet TEXT,
            skill TEXT,
            score REAL,
            duration_sec INTEGER,
            taken_date TEXT,
            FOREIGN KEY(talent_wallet) REFERENCES talents(wallet_address)
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS interviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_id INTEGER,
            talent_wallet TEXT,
            employer_wallet TEXT,
            scheduled_at TEXT,
            mode TEXT,
            status TEXT DEFAULT 'Scheduled',
            notes TEXT,
            created_date TEXT,
            UNIQUE(job_id, talent_wallet),
            FOREIGN KEY(talent_wallet) REFERENCES talents(wallet_address),
            FOREIGN KEY(job_id) REFERENCES jobs(job_id)
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS chat_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_id INTEGER,
            talent_wallet TEXT,
            employer_wallet TEXT,
            sender_role TEXT,
            message TEXT,
            sent_at TEXT,
            FOREIGN KEY(talent_wallet) REFERENCES talents(wallet_address),
            FOREIGN KEY(job_id) REFERENCES jobs(job_id)
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS hiring_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_id INTEGER,
            talent_wallet TEXT,
            employer_wallet TEXT,
            status TEXT DEFAULT 'Ongoing',
            start_date TEXT,
            end_date TEXT,
            fees_paid_usdc REAL DEFAULT 0,
            rating_by_employer REAL,
            skills_used TEXT,
            duration_days INTEGER,
            notes TEXT,
            UNIQUE(job_id, talent_wallet),
            FOREIGN KEY(talent_wallet) REFERENCES talents(wallet_address),
            FOREIGN KEY(job_id) REFERENCES jobs(job_id)
        )
    """)

    # Lightweight migrations for older seeded DBs.
    _ensure_column(conn, "talents", "skill_test_score", "REAL DEFAULT 0")
    _ensure_column(conn, "talents", "verified_skills_count", "INTEGER DEFAULT 0")
    _ensure_column(conn, "talents", "review_score", "REAL DEFAULT 0")
    _ensure_column(conn, "jobs", "status", "TEXT DEFAULT 'Open'")

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
         completion_rate,bio,github,nft_token_id,nft_tx_hash,availability,hourly_rate,
         skill_test_score,verified_skills_count,review_score)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, (
        row["wallet_address"], row["name"], row["role"], row["years_exp"],
        row["location"], row["skills"], row["projects"], row["rating"],
        row["completion_rate"], row.get("bio",""), row.get("github",""),
        row.get("nft_token_id"), row.get("nft_tx_hash"),
        row.get("availability","Available"), row.get("hourly_rate", 30),
        row.get("skill_test_score", 0), row.get("verified_skills_count", 0),
        row.get("review_score", 0)
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


def set_application_status(talent_wallet: str, job_id: int, status: str):
    conn = get_connection()
    conn.execute(
        "UPDATE applications SET status=? WHERE talent_wallet=? AND job_id=?",
        (status, talent_wallet, job_id)
    )
    conn.commit()
    conn.close()


def set_job_status(job_id: int, status: str):
    conn = get_connection()
    conn.execute("UPDATE jobs SET status=? WHERE job_id=?", (status, job_id))
    conn.commit()
    conn.close()


def upsert_interview(job_id: int, talent_wallet: str, employer_wallet: str,
                     scheduled_at: str, mode: str, notes: str = ""):
    from datetime import date
    conn = get_connection()
    conn.execute(
        """INSERT OR REPLACE INTO interviews
           (job_id,talent_wallet,employer_wallet,scheduled_at,mode,status,notes,created_date)
           VALUES (?,?,?,?,?,?,?,?)""",
        (job_id, talent_wallet, employer_wallet, scheduled_at, mode, "Scheduled", notes, str(date.today()))
    )
    conn.commit()
    conn.close()


def get_interview(job_id: int, talent_wallet: str) -> pd.DataFrame:
    conn = get_connection()
    df = pd.read_sql(
        "SELECT * FROM interviews WHERE job_id=? AND talent_wallet=?",
        conn, params=(job_id, talent_wallet)
    )
    conn.close()
    return df


def add_chat_message(job_id: int, talent_wallet: str, employer_wallet: str,
                     sender_role: str, message: str):
    from datetime import datetime
    conn = get_connection()
    conn.execute(
        """INSERT INTO chat_messages (job_id,talent_wallet,employer_wallet,sender_role,message,sent_at)
           VALUES (?,?,?,?,?,?)""",
        (job_id, talent_wallet, employer_wallet, sender_role, message, datetime.now().strftime("%Y-%m-%d %H:%M"))
    )
    conn.commit()
    conn.close()


def get_chat_messages(job_id: int, talent_wallet: str, employer_wallet: str) -> pd.DataFrame:
    conn = get_connection()
    df = pd.read_sql(
        """SELECT * FROM chat_messages
           WHERE job_id=? AND talent_wallet=? AND employer_wallet=?
           ORDER BY id ASC""",
        conn, params=(job_id, talent_wallet, employer_wallet)
    )
    conn.close()
    return df


def upsert_hiring_record(job_id: int, talent_wallet: str, employer_wallet: str,
                         status: str = "Ongoing", fees_paid_usdc: float = 0,
                         skills_used: str = "", duration_days: int = 0, notes: str = ""):
    from datetime import date
    conn = get_connection()
    existing = pd.read_sql(
        "SELECT id, start_date FROM hiring_history WHERE job_id=? AND talent_wallet=?",
        conn, params=(job_id, talent_wallet)
    )
    if existing.empty:
        conn.execute(
            """INSERT INTO hiring_history
               (job_id,talent_wallet,employer_wallet,status,start_date,fees_paid_usdc,skills_used,duration_days,notes)
               VALUES (?,?,?,?,?,?,?,?,?)""",
            (job_id, talent_wallet, employer_wallet, status, str(date.today()),
             fees_paid_usdc, skills_used, duration_days, notes)
        )
    else:
        conn.execute(
            """UPDATE hiring_history
               SET status=?, fees_paid_usdc=?, skills_used=?, duration_days=?, notes=?
               WHERE job_id=? AND talent_wallet=?""",
            (status, fees_paid_usdc, skills_used, duration_days, notes, job_id, talent_wallet)
        )
    conn.commit()
    conn.close()


def complete_hiring_and_rate(job_id: int, talent_wallet: str, employer_wallet: str,
                             fees_paid_usdc: float, duration_days: int,
                             rating_by_employer: float, skills_used: str, notes: str = ""):
    from datetime import date
    conn = get_connection()
    conn.execute(
        """UPDATE hiring_history
           SET status='Ended & Paid', end_date=?, fees_paid_usdc=?, duration_days=?,
               rating_by_employer=?, skills_used=?, notes=?
           WHERE job_id=? AND talent_wallet=?""",
        (str(date.today()), fees_paid_usdc, duration_days, rating_by_employer,
         skills_used, notes, job_id, talent_wallet)
    )

    # Employer feedback becomes part of long-term credibility.
    reviews = pd.read_sql(
        "SELECT AVG(rating_by_employer) AS r FROM hiring_history WHERE talent_wallet=? AND rating_by_employer IS NOT NULL",
        conn, params=(talent_wallet,)
    )
    avg_rating_5 = float(reviews["r"].iloc[0] or 0)
    conn.execute(
        "UPDATE talents SET review_score=? WHERE wallet_address=?",
        (round(avg_rating_5 / 5.0 * 100, 1), talent_wallet)
    )
    conn.commit()
    conn.close()


def get_hiring_history_for_employer(employer_wallet: str) -> pd.DataFrame:
    conn = get_connection()
    df = pd.read_sql(
        """SELECT h.*, t.name, t.role, t.skills, t.years_exp, t.rating,
                  j.title AS job_title, j.company
           FROM hiring_history h
           JOIN talents t ON h.talent_wallet=t.wallet_address
           JOIN jobs j ON h.job_id=j.job_id
           WHERE h.employer_wallet=?
           ORDER BY h.id DESC""",
        conn, params=(employer_wallet,)
    )
    conn.close()
    return df


def record_skill_test_attempt(talent_wallet: str, skill: str, score: float, duration_sec: int):
    from datetime import date
    conn = get_connection()
    conn.execute(
        "INSERT INTO skill_tests (talent_wallet,skill,score,duration_sec,taken_date) VALUES (?,?,?,?,?)",
        (talent_wallet, skill, score, duration_sec, str(date.today()))
    )

    stats = pd.read_sql(
        """SELECT AVG(score) AS avg_score,
                  COUNT(DISTINCT CASE WHEN score >= 60 THEN skill END) AS verified_count
           FROM skill_tests WHERE talent_wallet=?""",
        conn, params=(talent_wallet,)
    )
    avg_score = float(stats["avg_score"].iloc[0] or 0)
    verified = int(stats["verified_count"].iloc[0] or 0)
    conn.execute(
        "UPDATE talents SET skill_test_score=?, verified_skills_count=? WHERE wallet_address=?",
        (round(avg_score, 1), verified, talent_wallet)
    )
    conn.commit()
    conn.close()


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
