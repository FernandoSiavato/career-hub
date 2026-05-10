import shutil
from datetime import date
from pathlib import Path

from jobsearch.config import CV_TEMPLATES


def get_template(role: str, lang: str = "es") -> Path:
    """Get the CV template path for a given role and language."""
    templates = CV_TEMPLATES.get(role, {})
    template = templates.get(lang) or templates.get("es")
    if not template or not template.exists():
        raise FileNotFoundError(
            f"CV template not found for role='{role}' lang='{lang}'. Expected at: {template}"
        )
    return template


def build_cv_copy(role: str, company: str, company_folder: Path, lang: str = "es") -> Path:
    """
    Copy the appropriate CV template to the company folder.
    Returns the path of the copied CV.
    Uses shutil.copy2 to preserve all formatting (python-docx re-save would strip styles).
    """
    template = get_template(role, lang)
    today = date.today().strftime("%Y%m%d")
    safe_company = company.replace(" ", "_")
    dest_name = f"CV_{role}_{safe_company}_{today}.docx"
    dest_path = company_folder / dest_name

    company_folder.mkdir(parents=True, exist_ok=True)
    shutil.copy2(template, dest_path)
    return dest_path
