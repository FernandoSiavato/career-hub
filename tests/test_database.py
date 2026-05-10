"""Tests for ``jobsearch.database`` schema and CRUD helpers."""

from __future__ import annotations

import sqlite3

from jobsearch.database import (
    get_conn,
    init_db,
    insert_application,
    insert_jd_skills,
    insert_scanned_jobs,
    update_status,
)


class TestInitDb:
    def test_creates_expected_tables(self, fresh_db):
        conn = sqlite3.connect(fresh_db)
        tables = {
            row[0]
            for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
        }
        conn.close()
        for required in {
            "applications",
            "jd_skills",
            "skill_patterns",
            "status_history",
            "scanned_jobs",
        }:
            assert required in tables

    def test_is_idempotent(self, fresh_db):
        # Calling init_db again on the same path must not raise nor wipe data.
        init_db(db_path=fresh_db)


class TestInsertApplication:
    def test_inserts_and_returns_id(self, fresh_db, monkeypatch):
        # The helpers use the package-global DB_PATH; redirect it to the fresh
        # per-test database for isolation.
        monkeypatch.setattr("jobsearch.database.DB_PATH", fresh_db)
        app_id = insert_application(
            company="Acme",
            role="data",
            sector=1,
            folder_path="applications/data/Acme",
            jd_text="JD text",
            language="es",
        )
        assert isinstance(app_id, int)
        assert app_id > 0

    def test_inserted_row_has_default_status_pending(self, fresh_db, monkeypatch):
        monkeypatch.setattr("jobsearch.database.DB_PATH", fresh_db)
        app_id = insert_application(company="Acme", role="data", sector=1)
        conn = get_conn(fresh_db)
        row = conn.execute("SELECT status FROM applications WHERE id=?", (app_id,)).fetchone()
        conn.close()
        assert row["status"] == "pending"


class TestStatusTransitions:
    def test_update_status_records_history(self, fresh_db, monkeypatch):
        monkeypatch.setattr("jobsearch.database.DB_PATH", fresh_db)
        app_id = insert_application(company="Acme", role="data", sector=1)
        update_status(app_id, "applied", note="enviada vía portal")
        conn = get_conn(fresh_db)
        app = conn.execute("SELECT status FROM applications WHERE id=?", (app_id,)).fetchone()
        history = conn.execute(
            "SELECT old_status, new_status, note FROM status_history WHERE application_id=?",
            (app_id,),
        ).fetchall()
        conn.close()
        assert app["status"] == "applied"
        assert len(history) == 1
        assert history[0]["old_status"] == "pending"
        assert history[0]["new_status"] == "applied"


class TestJdSkills:
    def test_insert_jd_skills_persists_each_row(self, fresh_db, monkeypatch):
        monkeypatch.setattr("jobsearch.database.DB_PATH", fresh_db)
        app_id = insert_application(company="Acme", role="data", sector=1)
        skills = [
            {
                "skill": "Python",
                "category": "data",
                "required": 1,
                "years_required": 3,
                "matched": 1,
                "proficiency_gap": 0.5,
            },
            {
                "skill": "SQL",
                "category": "data",
                "required": 1,
                "years_required": None,
                "matched": 1,
                "proficiency_gap": 0,
            },
        ]
        insert_jd_skills(app_id, skills)
        conn = get_conn(fresh_db)
        count = conn.execute(
            "SELECT COUNT(*) AS c FROM jd_skills WHERE application_id=?", (app_id,)
        ).fetchone()["c"]
        conn.close()
        assert count == 2


class TestScannedJobs:
    def test_insert_scanned_jobs_dedupes_by_url(self, fresh_db, monkeypatch):
        monkeypatch.setattr("jobsearch.database.DB_PATH", fresh_db)
        rows = [
            {
                "url": "https://example.com/jobs/1",
                "title": "Data Analyst",
                "company": "Acme",
                "location": "Remote",
                "source": "greenhouse",
                "profile_tag": "data",
                "description": "x" * 250,
            },
            # duplicate URL — should not count as new
            {
                "url": "https://example.com/jobs/1",
                "title": "Data Analyst",
                "company": "Acme",
            },
        ]
        new_count = insert_scanned_jobs(rows)
        assert new_count == 1

    def test_insert_scanned_jobs_empty_list(self, fresh_db, monkeypatch):
        monkeypatch.setattr("jobsearch.database.DB_PATH", fresh_db)
        assert insert_scanned_jobs([]) == 0
