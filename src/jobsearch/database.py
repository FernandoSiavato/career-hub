import sqlite3
from datetime import datetime
from pathlib import Path

from jobsearch import DB_PATH


def get_conn(db_path: Path | str | None = None) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path or DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def _migrate_scanned_jobs(conn: sqlite3.Connection):
    """Add new columns to scanned_jobs if missing (idempotent)."""
    existing = {row["name"] for row in conn.execute("PRAGMA table_info(scanned_jobs)").fetchall()}
    needed = {
        "description": "TEXT",
        "remote_type": "TEXT",
        "salary_text": "TEXT",
        "salary_usd_min": "REAL",
        "salary_usd_max": "REAL",
        "fit_analyzed_at": "TEXT",
    }
    for col, ctype in needed.items():
        if col not in existing:
            conn.execute(f"ALTER TABLE scanned_jobs ADD COLUMN {col} {ctype}")


def init_db(db_path: Path | str | None = None):
    """Create the SQLite schema if it does not exist.

    ``role`` and ``sector`` are no longer constrained at the schema level so
    users can declare arbitrary roles in their ``config.toml``.
    """
    conn = get_conn(db_path)
    with conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS applications (
            id                INTEGER PRIMARY KEY AUTOINCREMENT,
            company           TEXT NOT NULL,
            folder_path       TEXT,
            role              TEXT NOT NULL,
            sector            INTEGER,
            jd_text           TEXT,
            jd_file_path      TEXT,
            status            TEXT NOT NULL DEFAULT 'pending'
                              CHECK(status IN ('pending','applied','interview','technical_test',
                                               'offer','hired','rejected','withdrawn')),
            fit_score         REAL,
            fit_report_path   TEXT,
            cv_path           TEXT,
            cover_letter_path TEXT,
            language          TEXT DEFAULT 'es' CHECK(language IN ('es','en','both')),
            applied_date      TEXT,
            last_updated      TEXT DEFAULT (datetime('now')),
            notes             TEXT,
            created_at        TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS jd_skills (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            application_id  INTEGER NOT NULL REFERENCES applications(id) ON DELETE CASCADE,
            skill           TEXT NOT NULL,
            skill_category  TEXT,
            required        INTEGER DEFAULT 1,
            years_required  REAL,
            matched         INTEGER DEFAULT 0,
            proficiency_gap REAL
        );

        CREATE TABLE IF NOT EXISTS skill_patterns (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            skill           TEXT NOT NULL,
            profile         TEXT NOT NULL,
            frequency       INTEGER DEFAULT 0,
            matched_count   INTEGER DEFAULT 0,
            avg_fit_score   REAL,
            hired_count     INTEGER DEFAULT 0,
            rejected_count  INTEGER DEFAULT 0,
            last_seen       TEXT,
            UNIQUE(skill, profile)
        );

        CREATE TABLE IF NOT EXISTS status_history (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            application_id  INTEGER NOT NULL REFERENCES applications(id) ON DELETE CASCADE,
            old_status      TEXT,
            new_status      TEXT NOT NULL,
            changed_at      TEXT DEFAULT (datetime('now')),
            note            TEXT
        );

        CREATE TABLE IF NOT EXISTS scanned_jobs (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            url             TEXT NOT NULL UNIQUE,
            title           TEXT NOT NULL,
            company         TEXT NOT NULL,
            location        TEXT,
            source          TEXT,
            profile_tag     TEXT,
            first_seen      TEXT DEFAULT (datetime('now')),
            status          TEXT NOT NULL DEFAULT 'discovered'
                            CHECK(status IN ('discovered','evaluated','promoted','rejected','expired')),
            fit_score       REAL,
            application_id  INTEGER REFERENCES applications(id) ON DELETE SET NULL,
            notes           TEXT,
            description     TEXT,
            remote_type     TEXT,
            salary_text     TEXT,
            salary_usd_min  REAL,
            salary_usd_max  REAL,
            fit_analyzed_at TEXT
        );

        CREATE INDEX IF NOT EXISTS idx_app_company    ON applications(company);
        CREATE INDEX IF NOT EXISTS idx_app_role       ON applications(role);
        CREATE INDEX IF NOT EXISTS idx_app_status     ON applications(status);
        CREATE INDEX IF NOT EXISTS idx_jds_app_id     ON jd_skills(application_id);
        CREATE INDEX IF NOT EXISTS idx_jds_skill      ON jd_skills(skill);
        CREATE INDEX IF NOT EXISTS idx_scanned_status  ON scanned_jobs(status);
        CREATE INDEX IF NOT EXISTS idx_scanned_company ON scanned_jobs(company);
        CREATE INDEX IF NOT EXISTS idx_scanned_profile ON scanned_jobs(profile_tag);
        """)
        _migrate_scanned_jobs(conn)
    conn.close()


def insert_scanned_jobs(rows: list[dict]) -> int:
    """Upsert discovered jobs.

    - Insert nuevos por url UNIQUE.
    - Si ya existe: actualiza description / remote_type / salary_text SOLO
      si en BD estan NULL/vacio (back-fill no destructivo). No toca status,
      fit_score, application_id ni notes.

    Returns numero de filas NUEVAS insertadas (no contadas las enriquecidas).
    """
    if not rows:
        return 0
    conn = get_conn()
    inserted = 0
    with conn:
        for r in rows:
            existed = (
                conn.execute("SELECT 1 FROM scanned_jobs WHERE url=?", (r["url"],)).fetchone()
                is not None
            )
            payload = {
                "url": r["url"],
                "title": r["title"],
                "company": r["company"],
                "location": r.get("location"),
                "source": r.get("source"),
                "profile_tag": r.get("profile_tag"),
                "description": (r.get("description") or "")[:20000] or None,
                "remote_type": r.get("remote_type") or None,
                "salary_text": r.get("salary_text") or None,
            }
            conn.execute(
                """INSERT INTO scanned_jobs
                   (url, title, company, location, source, profile_tag,
                    description, remote_type, salary_text)
                   VALUES (:url, :title, :company, :location, :source, :profile_tag,
                           :description, :remote_type, :salary_text)
                   ON CONFLICT(url) DO UPDATE SET
                     description = COALESCE(NULLIF(scanned_jobs.description, ''), excluded.description),
                     remote_type = COALESCE(NULLIF(scanned_jobs.remote_type, ''), excluded.remote_type),
                     salary_text = COALESCE(NULLIF(scanned_jobs.salary_text, ''), excluded.salary_text)
                   """,
                payload,
            )
            if not existed:
                inserted += 1
    conn.close()
    return inserted


def update_scanned_fit(
    scanned_id: int,
    fit_score: float,
    salary_usd_min: float | None = None,
    salary_usd_max: float | None = None,
):
    """Update fit_score (and optional USD salary) on scanned_jobs row."""
    conn = get_conn()
    with conn:
        conn.execute(
            """UPDATE scanned_jobs
               SET fit_score=?, salary_usd_min=?, salary_usd_max=?,
                   fit_analyzed_at=datetime('now'), status='evaluated'
               WHERE id=?""",
            (fit_score, salary_usd_min, salary_usd_max, scanned_id),
        )
    conn.close()


def get_scanned_for_fit(
    profile: str | None = None, limit: int = 50, min_desc_len: int = 200
) -> list[sqlite3.Row]:
    """Devuelve scanned_jobs sin fit aun, con descripcion suficiente."""
    conn = get_conn()
    query = """SELECT * FROM scanned_jobs
               WHERE status IN ('discovered','evaluated')
                 AND fit_score IS NULL
                 AND description IS NOT NULL
                 AND length(description) >= ?"""
    params: list = [min_desc_len]
    if profile:
        query += " AND (profile_tag = ? OR profile_tag LIKE ? OR profile_tag LIKE ? OR profile_tag LIKE ?)"
        params.extend([profile, f"{profile},%", f"%,{profile}", f"%,{profile},%"])
    query += " ORDER BY first_seen DESC LIMIT ?"
    params.append(limit)
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return rows


def get_scanned_jobs(
    profile: str | None = None, status: str = "discovered", limit: int = 50
) -> list[sqlite3.Row]:
    conn = get_conn()
    query = "SELECT * FROM scanned_jobs WHERE status=?"
    params: list = [status]
    if profile:
        # profile_tag may be 'data,ai' (multi); match if profile appears in csv
        query += " AND (profile_tag = ? OR profile_tag LIKE ? OR profile_tag LIKE ? OR profile_tag LIKE ?)"
        params.extend([profile, f"{profile},%", f"%,{profile}", f"%,{profile},%"])
    query += " ORDER BY first_seen DESC LIMIT ?"
    params.append(limit)
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return rows


def get_seen_urls() -> set[str]:
    """Returns URLs already in scanned_jobs (any status) — used for dedup."""
    conn = get_conn()
    rows = conn.execute("SELECT url FROM scanned_jobs").fetchall()
    conn.close()
    return {r["url"] for r in rows if r["url"]}


def mark_scanned_status(
    scanned_id: int, status: str, application_id: int | None = None, note: str | None = None
):
    conn = get_conn()
    with conn:
        if application_id is not None:
            conn.execute(
                "UPDATE scanned_jobs SET status=?, application_id=?, notes=? WHERE id=?",
                (status, application_id, note, scanned_id),
            )
        else:
            conn.execute(
                "UPDATE scanned_jobs SET status=?, notes=? WHERE id=?",
                (status, note, scanned_id),
            )
    conn.close()


def insert_application(
    company: str,
    role: str,
    sector: int,
    folder_path: str = None,
    jd_text: str = None,
    jd_file_path: str = None,
    language: str = "es",
    notes: str = None,
) -> int:
    conn = get_conn()
    with conn:
        cur = conn.execute(
            """INSERT INTO applications
               (company, role, sector, folder_path, jd_text, jd_file_path, language, notes)
               VALUES (?,?,?,?,?,?,?,?)""",
            (company, role, sector, folder_path, jd_text, jd_file_path, language, notes),
        )
        app_id = cur.lastrowid
    conn.close()
    return app_id


def update_application(app_id: int, **kwargs):
    kwargs["last_updated"] = datetime.now().isoformat()
    fields = ", ".join(f"{k}=?" for k in kwargs)
    values = list(kwargs.values()) + [app_id]
    conn = get_conn()
    with conn:
        conn.execute(f"UPDATE applications SET {fields} WHERE id=?", values)
    conn.close()


def update_status(app_id: int, new_status: str, note: str = None):
    conn = get_conn()
    with conn:
        row = conn.execute("SELECT status FROM applications WHERE id=?", (app_id,)).fetchone()
        old_status = row["status"] if row else None
        conn.execute(
            "UPDATE applications SET status=?, last_updated=? WHERE id=?",
            (new_status, datetime.now().isoformat(), app_id),
        )
        conn.execute(
            "INSERT INTO status_history (application_id, old_status, new_status, note) VALUES (?,?,?,?)",
            (app_id, old_status, new_status, note),
        )
    conn.close()


def insert_jd_skills(app_id: int, skills: list[dict]):
    conn = get_conn()
    with conn:
        conn.executemany(
            """INSERT INTO jd_skills
               (application_id, skill, skill_category, required, years_required, matched, proficiency_gap)
               VALUES (:app_id, :skill, :category, :required, :years_required, :matched, :proficiency_gap)""",
            [{"app_id": app_id, **s} for s in skills],
        )
    conn.close()


def get_application_by_company(company: str) -> sqlite3.Row | None:
    conn = get_conn()
    row = conn.execute(
        "SELECT * FROM applications WHERE lower(company)=lower(?) ORDER BY id DESC LIMIT 1",
        (company,),
    ).fetchone()
    conn.close()
    return row


def get_all_applications() -> list[sqlite3.Row]:
    conn = get_conn()
    rows = conn.execute("SELECT * FROM applications ORDER BY created_at DESC").fetchall()
    conn.close()
    return rows


def rebuild_patterns():
    conn = get_conn()
    with conn:
        conn.execute("DELETE FROM skill_patterns")
        conn.execute("""
        INSERT INTO skill_patterns (skill, profile, frequency, matched_count, avg_fit_score,
                                    hired_count, rejected_count, last_seen)
        SELECT
            js.skill,
            a.role AS profile,
            COUNT(*) AS frequency,
            SUM(js.matched) AS matched_count,
            AVG(a.fit_score) AS avg_fit_score,
            SUM(CASE WHEN a.status='hired' THEN 1 ELSE 0 END) AS hired_count,
            SUM(CASE WHEN a.status='rejected' THEN 1 ELSE 0 END) AS rejected_count,
            MAX(a.created_at) AS last_seen
        FROM jd_skills js
        JOIN applications a ON a.id = js.application_id
        GROUP BY js.skill, a.role
        """)
    conn.close()
