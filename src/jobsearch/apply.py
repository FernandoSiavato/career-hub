"""Logica de apply reusable desde CLI y web.

Toma un scanned_jobs.id, infiere el role del profile_tag, crea la carpeta
de la empresa, guarda la descripcion como JOB.txt, copia el CV, corre fit
analysis, genera la carta humanizada y mete la application en BD.
"""

from __future__ import annotations

from datetime import date

from jobsearch import ROOT
from jobsearch.config import ROLE_SECTOR, SECTOR_FOLDER
from jobsearch.database import (
    get_application_by_company,
    get_conn,
    insert_application,
    insert_jd_skills,
    mark_scanned_status,
    update_application,
)

# Profile_tag de scanned_jobs ('ai', 'data', 'meal', 'marketing') -> role
# valido para CV/cover letter (meal/data/marketing).
ROLE_MAPPING = {
    "ai": "data",
    "data": "data",
    "meal": "meal",
    "marketing": "marketing",
}


def _resolve_role(profile_tag: str | None, override: str | None = None) -> str:
    if override:
        return ROLE_MAPPING.get(override, override)
    tags = [t.strip() for t in (profile_tag or "").split(",") if t.strip()]
    for t in tags:
        if t in ROLE_MAPPING:
            return ROLE_MAPPING[t]
    return "data"


def apply_from_scanned(scanned_id: int, lang: str = "es", role_override: str | None = None) -> dict:
    """Ejecuta el flujo completo de apply para una scanned_job.

    Returns dict con: company, role, folder, cv_path, cover_letter_path,
    fit_score, application_id, jd_path.
    """
    from jobsearch.cover_letter import generate_cover_letter, save_cover_letter_docx
    from jobsearch.cv_builder import build_cv_copy
    from jobsearch.fit_analyzer import FitReport, analyze
    from jobsearch.profiles import load_profile

    conn = get_conn()
    row = conn.execute("SELECT * FROM scanned_jobs WHERE id=?", (scanned_id,)).fetchone()
    conn.close()
    if not row:
        raise ValueError(f"scanned_jobs.id={scanned_id} no existe")

    company = row["company"]
    description = row["description"] or ""
    role = _resolve_role(row["profile_tag"], role_override)
    sector = ROLE_SECTOR.get(role, 1)

    company_folder = ROOT / SECTOR_FOLDER[sector] / company
    company_folder.mkdir(parents=True, exist_ok=True)

    # 1. Save JD as JOB.txt
    jd_path = None
    if description and len(description) > 100:
        jd_path = company_folder / "JOB.txt"
        # Header con metadata
        header = (
            f"Source: {row['source'] or 'unknown'}\n"
            f"URL: {row['url']}\n"
            f"Location: {row['location'] or ''}\n"
            f"Remote: {row['remote_type'] or ''}\n"
            f"Salary: {row['salary_text'] or ''}\n"
            f"---\n\n"
        )
        jd_path.write_text(header + description, encoding="utf-8")

    # 2. Copy CV
    cv_path = None
    try:
        cv_path = build_cv_copy(role, company, company_folder, lang)
    except FileNotFoundError:
        pass

    # 3. Fit analysis (si hay descripcion)
    fit_report = None
    skills: list = []
    if description:
        try:
            fit_report, skills = analyze(
                description, role, company=company, save_to=company_folder / "fit_report.md"
            )
        except Exception:
            pass

    # 4. Cover letter
    carta_path = None
    try:
        profile = load_profile(role)
        if fit_report is None:
            fit_report = FitReport(
                company=company,
                role=role,
                fit_score=0.7,
                skills_score=0.7,
                experience_score=0.7,
                total_required=0,
                matched_required=0,
                total_optional=0,
                matched_optional=0,
            )
        text = generate_cover_letter(profile, fit_report, description, company, lang)
        today = date.today().strftime("%Y%m%d")
        carta_path = company_folder / f"Carta_de_Motivo_{company.replace(' ', '_')}_{today}.docx"
        save_cover_letter_docx(text, carta_path)
    except Exception:
        carta_path = None

    # 5. Save / update application in DB
    existing = get_application_by_company(company)
    if existing:
        update_application(
            existing["id"],
            cv_path=str(cv_path) if cv_path else None,
            cover_letter_path=str(carta_path) if carta_path else None,
            fit_score=fit_report.fit_score if fit_report else None,
        )
        app_id = existing["id"]
    else:
        app_id = insert_application(
            company=company,
            role=role,
            sector=sector,
            folder_path=str(company_folder.relative_to(ROOT)),
            jd_text=description[:5000] if description else None,
            jd_file_path=str(jd_path) if jd_path else None,
            language=lang,
        )
        update_application(
            app_id,
            cv_path=str(cv_path) if cv_path else None,
            cover_letter_path=str(carta_path) if carta_path else None,
            fit_score=fit_report.fit_score if fit_report else None,
        )
        if skills:
            insert_jd_skills(app_id, skills)

    # 6. Mark scanned_job as promoted, link application_id
    mark_scanned_status(scanned_id, "promoted", application_id=app_id)

    return {
        "company": company,
        "role": role,
        "folder": str(company_folder),
        "cv_path": str(cv_path) if cv_path else None,
        "cover_letter_path": str(carta_path) if carta_path else None,
        "jd_path": str(jd_path) if jd_path else None,
        "fit_score": fit_report.fit_score if fit_report else None,
        "fit_percentage": fit_report.percentage if fit_report else None,
        "application_id": app_id,
    }


def fit_scanned_jobs(profile: str | None = None, limit: int = 50) -> list[dict]:
    """Run fit analysis on scanned_jobs that have descriptions and no fit_score."""
    from jobsearch.database import get_scanned_for_fit, update_scanned_fit
    from jobsearch.fit_analyzer import analyze

    rows = get_scanned_for_fit(profile=profile, limit=limit)
    results = []
    for r in rows:
        role = _resolve_role(r["profile_tag"])
        try:
            report, _ = analyze(r["description"], role, company=r["company"])
            update_scanned_fit(r["id"], report.fit_score)
            results.append(
                {
                    "id": r["id"],
                    "company": r["company"],
                    "title": r["title"],
                    "fit_score": report.fit_score,
                    "percentage": report.percentage,
                    "ok": True,
                }
            )
        except Exception as e:
            results.append(
                {
                    "id": r["id"],
                    "company": r["company"],
                    "title": r["title"],
                    "ok": False,
                    "error": str(e),
                }
            )
    return results
