import sqlite3
import pandas as pd
import os
from pathlib import Path

# ── Absolute path anchored to this file ──────────────────────────────────────
_BASE = Path(__file__).resolve().parent.parent
DB_PATH = str(_BASE / "data" / "talents.db")


def get_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def _safe_read_sql(query: str, conn, params=None) -> pd.DataFrame:
    """Run pd.read_sql safely — returns empty DataFrame if table doesn't exist yet."""
    try:
        if params:
            return pd.read_sql(query, conn, params=params)
        return pd.read_sql(query, conn)
    except Exception:
        return pd.DataFrame()


def init_db():
    conn = get_connection()
    c = conn.cursor()

    c.executescript("""
        CREATE TABLE IF NOT EXISTS talents (
            wallet_address TEXT PRIMARY KEY,
            name TEXT, role TEXT, years_exp INTEGER,
            location TEXT, skills TEXT, projects INTEGER,
            rating REAL, completion_rate INTEGER,
            bio TEXT, github TEXT,
            nft_token_id TEXT, nft_tx_hash TEXT,
            availability TEXT DEFAULT 'Available',
            hourly_rate INTEGER DEFAULT 30,
            test_score_bonus REAL DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS jobs (
            job_id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT, company TEXT, description TEXT,
            required_skills TEXT, budget_usdc INTEGER,
            timeline_days INTEGER, posted_by_wallet TEXT,
            posted_date TEXT, location_type TEXT DEFAULT 'Remote',
            experience_required INTEGER DEFAULT 2,
            status TEXT DEFAULT 'Open'
        );

        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            talent_wallet TEXT, job_id INTEGER,
            match_score REAL, status TEXT DEFAULT 'Pending',
            tx_hash TEXT, applied_date TEXT,
            FOREIGN KEY(talent_wallet) REFERENCES talents(wallet_address),
            FOREIGN KEY(job_id) REFERENCES jobs(job_id)
        );

        CREATE TABLE IF NOT EXISTS interviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            talent_wallet TEXT,
            job_id INTEGER,
            employer_wallet TEXT,
            scheduled_date TEXT,
            scheduled_time TEXT,
            status TEXT DEFAULT 'Scheduled',
            notes TEXT,
            created_at TEXT,
            FOREIGN KEY(talent_wallet) REFERENCES talents(wallet_address),
            FOREIGN KEY(job_id) REFERENCES jobs(job_id)
        );

        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            interview_id INTEGER,
            sender_wallet TEXT,
            sender_role TEXT,
            message TEXT,
            sent_at TEXT,
            FOREIGN KEY(interview_id) REFERENCES interviews(id)
        );

        CREATE TABLE IF NOT EXISTS hiring_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employer_wallet TEXT,
            talent_wallet TEXT,
            job_id INTEGER,
            job_title TEXT,
            company TEXT,
            amount_paid_usdc INTEGER,
            skills_used TEXT,
            start_date TEXT,
            end_date TEXT,
            status TEXT DEFAULT 'Ongoing',
            employer_rating REAL DEFAULT NULL,
            employer_feedback TEXT,
            tx_hash TEXT,
            FOREIGN KEY(talent_wallet) REFERENCES talents(wallet_address),
            FOREIGN KEY(job_id) REFERENCES jobs(job_id)
        );

        CREATE TABLE IF NOT EXISTS skill_test_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            talent_wallet TEXT,
            skill_name TEXT,
            score INTEGER,
            max_score INTEGER,
            percentage REAL,
            taken_at TEXT,
            UNIQUE(talent_wallet, skill_name),
            FOREIGN KEY(talent_wallet) REFERENCES talents(wallet_address)
        );
    """)

    # ── Migration: add new columns/tables to existing DBs ────────────────────
    migrations = [
        "ALTER TABLE talents ADD COLUMN test_score_bonus REAL DEFAULT 0",
        """CREATE TABLE IF NOT EXISTS interviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            talent_wallet TEXT, job_id INTEGER, employer_wallet TEXT,
            scheduled_date TEXT, scheduled_time TEXT,
            status TEXT DEFAULT 'Scheduled', notes TEXT, created_at TEXT,
            FOREIGN KEY(talent_wallet) REFERENCES talents(wallet_address),
            FOREIGN KEY(job_id) REFERENCES jobs(job_id)
        )""",
        """CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            interview_id INTEGER, sender_wallet TEXT, sender_role TEXT,
            message TEXT, sent_at TEXT,
            FOREIGN KEY(interview_id) REFERENCES interviews(id)
        )""",
        """CREATE TABLE IF NOT EXISTS hiring_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employer_wallet TEXT, talent_wallet TEXT, job_id INTEGER,
            job_title TEXT, company TEXT, amount_paid_usdc INTEGER,
            skills_used TEXT, start_date TEXT, end_date TEXT,
            status TEXT DEFAULT 'Ongoing', employer_rating REAL DEFAULT NULL,
            employer_feedback TEXT, tx_hash TEXT,
            FOREIGN KEY(talent_wallet) REFERENCES talents(wallet_address),
            FOREIGN KEY(job_id) REFERENCES jobs(job_id)
        )""",
        """CREATE TABLE IF NOT EXISTS skill_test_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            talent_wallet TEXT, skill_name TEXT, score INTEGER,
            max_score INTEGER, percentage REAL, taken_at TEXT,
            UNIQUE(talent_wallet, skill_name),
            FOREIGN KEY(talent_wallet) REFERENCES talents(wallet_address)
        )""",
    ]
    for sql in migrations:
        try:
            c.execute(sql)
        except Exception:
            pass  # column/table already exists

    conn.commit()
    conn.close()


def seed_if_empty():
    try:
        conn = get_connection()
        df = pd.read_sql("SELECT COUNT(*) as cnt FROM talents", conn)
        conn.close()
        if df["cnt"].iloc[0] == 0:
            _run_seed()
    except Exception:
        _run_seed()


def _run_seed():
    import sys
    sys.path.insert(0, str(_BASE))
    try:
        from data.seed_data import seed_database
        seed_database(DB_PATH)
    except Exception as e:
        print(f"Seed failed: {e}")


# ── TALENT ────────────────────────────────────────────────────────────────────

def get_talent(wallet: str) -> pd.DataFrame:
    conn = get_connection()
    df = _safe_read_sql("SELECT * FROM talents WHERE wallet_address = ?", conn, params=(wallet,))
    conn.close()
    return df


def get_all_talents() -> pd.DataFrame:
    conn = get_connection()
    df = _safe_read_sql("SELECT * FROM talents", conn)
    conn.close()
    return df


def upsert_talent(row: dict):
    conn = get_connection()
    conn.execute("""
        INSERT OR REPLACE INTO talents
        (wallet_address,name,role,years_exp,location,skills,projects,rating,
         completion_rate,bio,github,nft_token_id,nft_tx_hash,availability,hourly_rate,test_score_bonus)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, (
        row["wallet_address"], row["name"], row["role"], row["years_exp"],
        row["location"], row["skills"], row["projects"], row["rating"],
        row["completion_rate"], row.get("bio", ""), row.get("github", ""),
        row.get("nft_token_id"), row.get("nft_tx_hash"),
        row.get("availability", "Available"), row.get("hourly_rate", 30),
        row.get("test_score_bonus", 0),
    ))
    conn.commit()
    conn.close()


def update_nft(wallet: str, token_id: str, tx_hash: str):
    conn = get_connection()
    conn.execute("UPDATE talents SET nft_token_id=?, nft_tx_hash=? WHERE wallet_address=?",
                 (token_id, tx_hash, wallet))
    conn.commit()
    conn.close()


def update_talent_test_bonus(wallet: str):
    """Recalculate and update test_score_bonus from all skill test results."""
    conn = get_connection()
    results = _safe_read_sql(
        "SELECT percentage FROM skill_test_results WHERE talent_wallet=?",
        conn, params=(wallet,)
    )
    if results.empty:
        bonus = 0.0
    else:
        bonus = round(results["percentage"].mean() * 0.10, 2)  # up to 10 points
    conn.execute("UPDATE talents SET test_score_bonus=? WHERE wallet_address=?", (bonus, wallet))
    conn.commit()
    conn.close()


# ── JOBS ──────────────────────────────────────────────────────────────────────

def get_all_jobs() -> pd.DataFrame:
    conn = get_connection()
    df = _safe_read_sql("SELECT * FROM jobs WHERE status='Open'", conn)
    conn.close()
    return df


def insert_job(row: dict) -> int:
    from datetime import date
    conn = get_connection()
    cur = conn.execute(
        """INSERT INTO jobs (title,company,description,required_skills,budget_usdc,
           timeline_days,posted_by_wallet,posted_date,location_type,experience_required)
           VALUES (?,?,?,?,?,?,?,?,?,?)""",
        (row["title"], row["company"], row["description"], row["required_skills"],
         row["budget_usdc"], row["timeline_days"], row["posted_by_wallet"],
         str(date.today()), row.get("location_type", "Remote"),
         row.get("experience_required", 2))
    )
    conn.commit()
    job_id = cur.lastrowid
    conn.close()
    return job_id


# ── APPLICATIONS ──────────────────────────────────────────────────────────────

def get_applications_for_talent(wallet: str) -> pd.DataFrame:
    conn = get_connection()
    df = _safe_read_sql(
        """SELECT a.*, j.title, j.company, j.budget_usdc
           FROM applications a JOIN jobs j ON a.job_id = j.job_id
           WHERE a.talent_wallet = ? ORDER BY a.id DESC""",
        conn, params=(wallet,)
    )
    conn.close()
    return df


def get_applications_for_job(job_id: int) -> pd.DataFrame:
    conn = get_connection()
    df = _safe_read_sql(
        """SELECT a.*, t.name, t.role, t.skills, t.rating, t.completion_rate,
                  t.nft_token_id, t.years_exp, t.test_score_bonus
           FROM applications a JOIN talents t ON a.talent_wallet = t.wallet_address
           WHERE a.job_id = ? ORDER BY a.match_score DESC""",
        conn, params=(job_id,)
    )
    conn.close()
    return df


def insert_application(talent_wallet: str, job_id: int, match_score: float, tx_hash: str = None):
    from datetime import date
    conn = get_connection()
    existing = _safe_read_sql(
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


def update_application_status(talent_wallet: str, job_id: int, status: str):
    conn = get_connection()
    conn.execute(
        "UPDATE applications SET status=? WHERE talent_wallet=? AND job_id=?",
        (status, talent_wallet, job_id)
    )
    conn.commit()
    conn.close()


# ── INTERVIEWS ────────────────────────────────────────────────────────────────

def insert_interview(talent_wallet: str, job_id: int, employer_wallet: str,
                     scheduled_date: str, scheduled_time: str, notes: str = "") -> int:
    from datetime import datetime
    conn = get_connection()
    cur = conn.execute(
        """INSERT INTO interviews (talent_wallet,job_id,employer_wallet,
           scheduled_date,scheduled_time,notes,created_at)
           VALUES (?,?,?,?,?,?,?)""",
        (talent_wallet, job_id, employer_wallet, scheduled_date, scheduled_time,
         notes, str(datetime.now().date()))
    )
    conn.commit()
    interview_id = cur.lastrowid
    conn.close()
    # Also update the application status to Shortlisted
    update_application_status(talent_wallet, job_id, "Shortlisted")
    return interview_id


def get_interviews_for_talent(wallet: str) -> pd.DataFrame:
    conn = get_connection()
    df = _safe_read_sql(
        """SELECT i.*, j.title, j.company
           FROM interviews i JOIN jobs j ON i.job_id = j.job_id
           WHERE i.talent_wallet = ? ORDER BY i.scheduled_date DESC""",
        conn, params=(wallet,)
    )
    conn.close()
    return df


def get_interviews_for_employer(employer_wallet: str) -> pd.DataFrame:
    conn = get_connection()
    df = _safe_read_sql(
        """SELECT i.*, j.title as job_title, j.company, t.name as talent_name, t.role as talent_role
           FROM interviews i
           JOIN jobs j ON i.job_id = j.job_id
           JOIN talents t ON i.talent_wallet = t.wallet_address
           WHERE i.employer_wallet = ? ORDER BY i.scheduled_date DESC""",
        conn, params=(employer_wallet,)
    )
    conn.close()
    return df


# ── MESSAGES ──────────────────────────────────────────────────────────────────

def insert_message(interview_id: int, sender_wallet: str, sender_role: str, message: str):
    from datetime import datetime
    conn = get_connection()
    conn.execute(
        "INSERT INTO messages (interview_id,sender_wallet,sender_role,message,sent_at) VALUES (?,?,?,?,?)",
        (interview_id, sender_wallet, sender_role, message, str(datetime.now()))
    )
    conn.commit()
    conn.close()


def get_messages(interview_id: int) -> pd.DataFrame:
    conn = get_connection()
    df = _safe_read_sql(
        "SELECT * FROM messages WHERE interview_id=? ORDER BY sent_at ASC",
        conn, params=(interview_id,)
    )
    conn.close()
    return df


# ── HIRING HISTORY ────────────────────────────────────────────────────────────

def insert_hiring_record(row: dict) -> int:
    from datetime import date
    conn = get_connection()
    cur = conn.execute(
        """INSERT INTO hiring_history
           (employer_wallet,talent_wallet,job_id,job_title,company,amount_paid_usdc,
            skills_used,start_date,status,tx_hash)
           VALUES (?,?,?,?,?,?,?,?,?,?)""",
        (row["employer_wallet"], row["talent_wallet"], row["job_id"],
         row["job_title"], row["company"], row["amount_paid_usdc"],
         row["skills_used"], str(date.today()), "Ongoing", row.get("tx_hash", ""))
    )
    conn.commit()
    hire_id = cur.lastrowid
    conn.close()
    return hire_id


def get_hiring_history(employer_wallet: str) -> pd.DataFrame:
    conn = get_connection()
    df = _safe_read_sql(
        """SELECT h.*, t.name as talent_name, t.role as talent_role, t.rating as talent_rating
           FROM hiring_history h
           JOIN talents t ON h.talent_wallet = t.wallet_address
           WHERE h.employer_wallet = ? ORDER BY h.id DESC""",
        conn, params=(employer_wallet,)
    )
    conn.close()
    return df


def rate_past_hire(hire_id: int, rating: float, feedback: str, talent_wallet: str):
    from datetime import date
    conn = get_connection()
    conn.execute(
        "UPDATE hiring_history SET employer_rating=?, employer_feedback=?, end_date=?, status='Completed' WHERE id=?",
        (rating, feedback, str(date.today()), hire_id)
    )
    # Update talent's overall rating (rolling average)
    existing = _safe_read_sql("SELECT rating FROM talents WHERE wallet_address=?", conn, params=(talent_wallet,))
    if not existing.empty:
        old_r = float(existing["rating"].iloc[0])
        new_r = round((old_r + rating) / 2, 1)
        conn.execute("UPDATE talents SET rating=? WHERE wallet_address=?", (new_r, talent_wallet))
    conn.commit()
    conn.close()


# ── SKILL TESTS ───────────────────────────────────────────────────────────────

def upsert_skill_test_result(talent_wallet: str, skill_name: str,
                              score: int, max_score: int):
    from datetime import datetime
    percentage = round(score / max_score * 100, 1)
    conn = get_connection()
    conn.execute(
        """INSERT OR REPLACE INTO skill_test_results
           (talent_wallet,skill_name,score,max_score,percentage,taken_at)
           VALUES (?,?,?,?,?,?)""",
        (talent_wallet, skill_name, score, max_score, percentage, str(datetime.now()))
    )
    conn.commit()
    conn.close()
    update_talent_test_bonus(talent_wallet)


def get_skill_test_results(talent_wallet: str) -> pd.DataFrame:
    conn = get_connection()
    df = _safe_read_sql(
        "SELECT * FROM skill_test_results WHERE talent_wallet=? ORDER BY taken_at DESC",
        conn, params=(talent_wallet,)
    )
    conn.close()
    return df


# ── STATS ──────────────────────────────────────────────────────────────────────

def get_platform_stats() -> dict:
    conn = get_connection()
    def _n(q):
        try:
            return int(_safe_read_sql(q, conn).iloc[0, 0])
        except Exception:
            return 0
    def _f(q):
        try:
            v = _safe_read_sql(q, conn).iloc[0, 0]
            return float(v or 0)
        except Exception:
            return 0.0
    stats = {
        "talents":      _n("SELECT COUNT(*) FROM talents"),
        "jobs":         _n("SELECT COUNT(*) FROM jobs"),
        "applications": _n("SELECT COUNT(*) FROM applications"),
        "hired":        _n("SELECT COUNT(*) FROM applications WHERE status='Hired'"),
        "nfts_minted":  _n("SELECT COUNT(*) FROM talents WHERE nft_token_id IS NOT NULL"),
        "avg_match":    round(_f("SELECT AVG(match_score) FROM applications"), 1),
    }
    conn.close()
    return stats
