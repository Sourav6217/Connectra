import sqlite3
import pandas as pd
import os
from datetime import date

DB_PATH = "data/talents.db"


def get_connection():
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def _query(sql: str, params=(), many=False):
    """Safe query helper — returns list of dicts."""
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(sql, params)
        if many:
            rows = cur.fetchall()
            if cur.description:
                cols = [d[0] for d in cur.description]
                return [dict(zip(cols, r)) for r in rows]
            return []
        row = cur.fetchone()
        if row and cur.description:
            return dict(zip([d[0] for d in cur.description], row))
        return None
    finally:
        conn.close()


def _to_df(rows: list) -> pd.DataFrame:
    return pd.DataFrame(rows) if rows else pd.DataFrame()


def _execute(sql: str, params=()):
    conn = get_connection()
    try:
        conn.execute(sql, params)
        conn.commit()
    finally:
        conn.close()


def init_db():
    conn = get_connection()
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS talents (
        wallet_address TEXT PRIMARY KEY,
        name TEXT, role TEXT, years_exp INTEGER,
        location TEXT, skills TEXT, projects INTEGER,
        rating REAL, completion_rate INTEGER,
        bio TEXT, github TEXT,
        nft_token_id TEXT, nft_tx_hash TEXT,
        availability TEXT DEFAULT 'Available',
        hourly_rate INTEGER DEFAULT 30,
        test_bonus REAL DEFAULT 0.0
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
        tx_hash TEXT, applied_date TEXT
    );
    CREATE TABLE IF NOT EXISTS skill_test_results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        wallet TEXT, skill TEXT, score REAL,
        taken_at TEXT, correct INTEGER, total INTEGER
    );
    CREATE TABLE IF NOT EXISTS interviews (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        employer_wallet TEXT, talent_wallet TEXT,
        job_id INTEGER, talent_name TEXT, job_title TEXT,
        preferred_date TEXT, note TEXT,
        status TEXT DEFAULT 'Requested',
        created_at TEXT
    );
    CREATE TABLE IF NOT EXISTS hire_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        employer_wallet TEXT, talent_wallet TEXT,
        job_id INTEGER, job_title TEXT, talent_name TEXT,
        talent_role TEXT, skills_used TEXT,
        start_date TEXT, end_date TEXT,
        amount_paid INTEGER, status TEXT DEFAULT 'Ongoing',
        employer_rating REAL, employer_notes TEXT
    );
    """)
    conn.commit()
    conn.close()


def seed_if_empty():
    try:
        rows = _query("SELECT COUNT(*) as c FROM talents", many=False)
        if not rows or rows.get("c", 0) == 0:
            from data.seed_data import seed_database
            seed_database()
    except Exception:
        from data.seed_data import seed_database
        seed_database()


# ── TALENT ──────────────────────────────────
def get_talent(wallet: str) -> pd.DataFrame:
    rows = _query("SELECT * FROM talents WHERE wallet_address=?", (wallet,), many=True)
    return _to_df(rows)


def get_all_talents() -> pd.DataFrame:
    rows = _query("SELECT * FROM talents", many=True)
    return _to_df(rows)


def upsert_talent(row: dict):
    conn = get_connection()
    conn.row_factory = None
    try:
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
    finally:
        conn.close()


def update_nft(wallet: str, token_id: str, tx_hash: str):
    _execute("UPDATE talents SET nft_token_id=?,nft_tx_hash=? WHERE wallet_address=?",
             (token_id, tx_hash, wallet))


def update_talent_test_bonus(wallet: str, bonus: float):
    _execute("UPDATE talents SET test_bonus=? WHERE wallet_address=?", (bonus, wallet))


# ── JOBS ─────────────────────────────────────
def get_all_jobs() -> pd.DataFrame:
    rows = _query("SELECT * FROM jobs WHERE status='Open'", many=True)
    return _to_df(rows)


def insert_job(row: dict) -> int:
    conn = get_connection()
    conn.row_factory = None
    try:
        cur = conn.execute("""
            INSERT INTO jobs (title,company,description,required_skills,budget_usdc,
               timeline_days,posted_by_wallet,posted_date,location_type,experience_required)
               VALUES (?,?,?,?,?,?,?,?,?,?)
        """, (row["title"], row["company"], row["description"], row["required_skills"],
              row["budget_usdc"], row["timeline_days"], row["posted_by_wallet"],
              str(date.today()), row.get("location_type","Remote"),
              row.get("experience_required", 2)))
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


# ── APPLICATIONS ─────────────────────────────
def get_applications_for_talent(wallet: str) -> pd.DataFrame:
    rows = _query("""
        SELECT a.id, a.talent_wallet, a.job_id, a.match_score, a.status,
               a.tx_hash, a.applied_date, j.title, j.company, j.budget_usdc
        FROM applications a
        LEFT JOIN jobs j ON a.job_id = j.job_id
        WHERE a.talent_wallet=?
        ORDER BY a.id DESC
    """, (wallet,), many=True)
    return _to_df(rows)


def get_applications_for_job(job_id: int) -> pd.DataFrame:
    rows = _query("""
        SELECT a.id, a.talent_wallet, a.job_id, a.match_score, a.status,
               a.tx_hash, a.applied_date,
               t.name, t.role, t.skills, t.rating, t.completion_rate,
               t.nft_token_id, t.years_exp
        FROM applications a
        LEFT JOIN talents t ON a.talent_wallet = t.wallet_address
        WHERE a.job_id=?
        ORDER BY a.match_score DESC
    """, (job_id,), many=True)
    return _to_df(rows)


def insert_application(talent_wallet: str, job_id: int, match_score: float, tx_hash: str = None) -> bool:
    existing = _query(
        "SELECT id FROM applications WHERE talent_wallet=? AND job_id=?",
        (talent_wallet, job_id), many=True
    )
    if existing:
        return False
    conn = get_connection()
    conn.row_factory = None
    try:
        conn.execute(
            "INSERT INTO applications (talent_wallet,job_id,match_score,status,tx_hash,applied_date) VALUES (?,?,?,?,?,?)",
            (talent_wallet, job_id, match_score, "Pending", tx_hash, str(date.today()))
        )
        conn.commit()
        return True
    finally:
        conn.close()


# ── SKILL TESTS ──────────────────────────────
def save_test_result(wallet: str, skill: str, score: float, correct: int, total: int):
    conn = get_connection()
    conn.row_factory = None
    try:
        conn.execute(
            "INSERT INTO skill_test_results (wallet,skill,score,taken_at,correct,total) VALUES (?,?,?,?,?,?)",
            (wallet, skill, score, str(date.today()), correct, total)
        )
        conn.commit()
    finally:
        conn.close()
    # Update talent test_bonus = avg of best scores across skills
    results = _query(
        "SELECT skill, MAX(score) as best FROM skill_test_results WHERE wallet=? GROUP BY skill",
        (wallet,), many=True
    )
    if results:
        avg_best = sum(r["best"] for r in results) / len(results)
        update_talent_test_bonus(wallet, round(avg_best, 1))


def get_test_results(wallet: str) -> pd.DataFrame:
    rows = _query(
        "SELECT skill, MAX(score) as best_score, COUNT(*) as attempts FROM skill_test_results WHERE wallet=? GROUP BY skill",
        (wallet,), many=True
    )
    return _to_df(rows)


def has_taken_test(wallet: str, skill: str) -> bool:
    row = _query(
        "SELECT id FROM skill_test_results WHERE wallet=? AND skill=? LIMIT 1",
        (wallet, skill), many=False
    )
    return row is not None


# ── INTERVIEWS ───────────────────────────────
def book_interview(employer_wallet: str, talent_wallet: str, job_id: int,
                   talent_name: str, job_title: str, preferred_date: str, note: str):
    conn = get_connection()
    conn.row_factory = None
    try:
        conn.execute("""
            INSERT INTO interviews (employer_wallet,talent_wallet,job_id,talent_name,
                job_title,preferred_date,note,status,created_at)
            VALUES (?,?,?,?,?,?,?,?,?)
        """, (employer_wallet, talent_wallet, job_id, talent_name, job_title,
              preferred_date, note, "Requested", str(date.today())))
        conn.commit()
    finally:
        conn.close()


def get_interviews_for_employer(employer_wallet: str) -> pd.DataFrame:
    rows = _query(
        "SELECT * FROM interviews WHERE employer_wallet=? ORDER BY id DESC",
        (employer_wallet,), many=True
    )
    return _to_df(rows)


def get_interviews_for_talent(talent_wallet: str) -> pd.DataFrame:
    rows = _query(
        "SELECT * FROM interviews WHERE talent_wallet=? ORDER BY id DESC",
        (talent_wallet,), many=True
    )
    return _to_df(rows)


# ── HIRE HISTORY ──────────────────────────────
def add_hire_history(row: dict):
    conn = get_connection()
    conn.row_factory = None
    try:
        conn.execute("""
            INSERT INTO hire_history
            (employer_wallet,talent_wallet,job_id,job_title,talent_name,talent_role,
             skills_used,start_date,end_date,amount_paid,status,employer_rating,employer_notes)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (
            row.get("employer_wallet",""), row.get("talent_wallet",""),
            row.get("job_id", 0), row.get("job_title",""),
            row.get("talent_name",""), row.get("talent_role",""),
            row.get("skills_used",""), row.get("start_date",""),
            row.get("end_date",""), row.get("amount_paid", 0),
            row.get("status","Ongoing"), row.get("employer_rating"),
            row.get("employer_notes","")
        ))
        conn.commit()
    finally:
        conn.close()


def get_hire_history(employer_wallet: str) -> pd.DataFrame:
    rows = _query(
        "SELECT * FROM hire_history WHERE employer_wallet=? ORDER BY id DESC",
        (employer_wallet,), many=True
    )
    return _to_df(rows)


def rate_hire(hire_id: int, rating: float, notes: str, end_date: str):
    conn = get_connection()
    conn.row_factory = None
    try:
        conn.execute(
            "UPDATE hire_history SET employer_rating=?,employer_notes=?,end_date=?,status='Completed' WHERE id=?",
            (rating, notes, end_date, hire_id)
        )
        # Update talent rating based on new review
        row = _query("SELECT talent_wallet FROM hire_history WHERE id=?", (hire_id,))
        if row:
            wallet = row["talent_wallet"]
            all_ratings = _query(
                "SELECT AVG(employer_rating) as avg_r FROM hire_history WHERE talent_wallet=? AND employer_rating IS NOT NULL",
                (wallet,)
            )
            if all_ratings and all_ratings.get("avg_r"):
                new_rating = round(min(5.0, all_ratings["avg_r"]), 1)
                conn.execute("UPDATE talents SET rating=? WHERE wallet_address=?", (new_rating, wallet))
        conn.commit()
    finally:
        conn.close()


# ── PLATFORM STATS ────────────────────────────
def get_platform_stats() -> dict:
    def count(sql):
        r = _query(sql)
        return int(r.get("c", 0)) if r else 0
    return {
        "talents":      count("SELECT COUNT(*) as c FROM talents"),
        "jobs":         count("SELECT COUNT(*) as c FROM jobs"),
        "applications": count("SELECT COUNT(*) as c FROM applications"),
        "hired":        count("SELECT COUNT(*) as c FROM applications WHERE status='Hired'"),
        "nfts_minted":  count("SELECT COUNT(*) as c FROM talents WHERE nft_token_id IS NOT NULL"),
        "avg_match":    round(
            (_query("SELECT AVG(match_score) as s FROM applications") or {}).get("s") or 0, 1
        ),
        "tests_taken":  count("SELECT COUNT(DISTINCT wallet) as c FROM skill_test_results"),
        "interviews":   count("SELECT COUNT(*) as c FROM interviews"),
    }
