import difflib
import unicodedata
from pathlib import Path

import yaml

from jobsearch import PROFILES_DIR, ROOT

# ---------------------------------------------------------------------------
# Normalization
# ---------------------------------------------------------------------------


def normalize(text: str) -> str:
    """Lowercase, strip accents, collapse whitespace."""
    nfkd = unicodedata.normalize("NFKD", text)
    ascii_text = nfkd.encode("ascii", "ignore").decode()
    return " ".join(ascii_text.lower().split())


# ---------------------------------------------------------------------------
# Skill Dictionary  (es + en, both normalized)
# ---------------------------------------------------------------------------

SKILL_DICTIONARY: dict[str, list[str]] = {
    "meal": [
        "kobo toolbox",
        "kobo",
        "kobo collect",
        "odk",
        "open data kit",
        "monitoreo y evaluacion",
        "monitoreo",
        "evaluacion",
        "monitoring and evaluation",
        "m&e",
        "meal",
        "seguimiento y evaluacion",
        "marco logico",
        "logical framework",
        "logframe",
        "teoria del cambio",
        "theory of change",
        "toc",
        "indicadores",
        "indicators",
        "kpi",
        "gestion de proyectos",
        "project management",
        "ciclo de proyecto",
        "rendicion de cuentas",
        "accountability",
        "psea",
        "siaf",
        "pmi",
        "gestion del ciclo de proyecto",
        "recoleccion de datos",
        "data collection",
        "encuestas",
        "focus groups",
        "entrevistas",
        "informes",
        "reporting",
        "sistematizacion",
        "base de datos",
        "database",
        "analisis cualitativo",
        "qualitative analysis",
        "analisis cuantitativo",
        "quantitative analysis",
        "proteccion",
        "protection",
        "genero",
        "gender",
        "vulnerabilidad",
        "vulnerability",
        "beneficiarios",
        "humanitarian",
        "humanitario",
        "desarrollo",
        "development",
        "cooperacion",
        "cooperation",
        "ong",
        "ngo",
    ],
    "data": [
        "python",
        "python3",
        "scripting",
        "sql",
        "postgresql",
        "mysql",
        "sqlite",
        "tsql",
        "consultas sql",
        "power bi",
        "powerbi",
        "dax",
        "power query",
        "tableau",
        "looker",
        "metabase",
        "pandas",
        "numpy",
        "dataframe",
        "etl",
        "pipeline",
        "data pipeline",
        "ingesta de datos",
        "data warehouse",
        "datawarehouse",
        "dwh",
        "excel",
        "microsoft excel",
        "tablas dinamicas",
        "pivot tables",
        "git",
        "github",
        "control de versiones",
        "version control",
        "machine learning",
        "ml",
        "modelos predictivos",
        "google analytics",
        "ga4",
        "google data studio",
        "bigquery",
        "spark",
        "hadoop",
        "airflow",
        "dbt",
        "rstudio",
        "r studio",
        "lenguaje r",
        "estadistica",
        "statistics",
        "visualizacion de datos",
        "data visualization",
        "dashboard",
        "analisis de datos",
        "data analysis",
        "data analytics",
        "automatizacion",
        "automation",
        "scripting",
        "apis",
        "rest api",
        "json",
        "xml",
        "jupyter",
        "notebooks",
    ],
    "marketing": [
        "automatizacion de marketing",
        "marketing automation",
        "email marketing",
        "email automation",
        "crm",
        "hubspot",
        "salesforce",
        "zoho",
        "google analytics",
        "ga4",
        "meta ads",
        "facebook ads",
        "google ads",
        "seo",
        "search engine optimization",
        "search engine marketing",
        "paid media",
        "funnels",
        "embudo de ventas",
        "conversion",
        "segmentacion",
        "segmentation",
        "audiencias",
        "copywriting",
        "contenido",
        "content",
        "redes sociales",
        "social media",
        "landing pages",
        "a/b testing",
    ],
    "soft": [
        "comunicacion",
        "communication",
        "trabajo en equipo",
        "teamwork",
        "colaboracion",
        "collaboration",
        "liderazgo",
        "leadership",
        "pensamiento critico",
        "critical thinking",
        "resolucion de problemas",
        "problem solving",
        "adaptabilidad",
        "adaptability",
        "gestion del tiempo",
        "time management",
        "orientacion a resultados",
        "results oriented",
    ],
    "tools": [
        "microsoft office",
        "word",
        "excel",
        "powerpoint",
        "teams",
        "slack",
        "zoom",
        "jira",
        "notion",
        "trello",
        "asana",
        "github",
        "gitlab",
    ],
    "language": [
        "ingles",
        "english",
        "bilingual",
        "bilingue",
        "espanol",
        "spanish",
        "frances",
        "french",
        "portugues",
        "portuguese",
    ],
}

# Canonical name for display (normalized key → pretty name)
SKILL_CANONICAL: dict[str, str] = {
    "kobo toolbox": "KoboToolbox",
    "kobo": "KoboToolbox",
    "odk": "ODK",
    "meal": "MEAL",
    "m&e": "M&E",
    "python": "Python",
    "python3": "Python",
    "sql": "SQL",
    "postgresql": "PostgreSQL",
    "mysql": "MySQL",
    "sqlite": "SQLite",
    "power bi": "Power BI",
    "powerbi": "Power BI",
    "dax": "DAX",
    "pandas": "pandas",
    "numpy": "NumPy",
    "etl": "ETL",
    "excel": "Excel",
    "git": "Git",
    "github": "GitHub",
    "machine learning": "Machine Learning",
    "google analytics": "Google Analytics",
    "ga4": "Google Analytics 4",
    "bigquery": "BigQuery",
    "tableau": "Tableau",
    "ingles": "Inglés",
    "english": "English",
    "espanol": "Español",
    "crm": "CRM",
    "hubspot": "HubSpot",
}

# Context words that validate a skill mention (reduces false positives)
SKILL_CONTEXT_WORDS = [
    "conocimiento",
    "manejo",
    "experiencia",
    "dominio",
    "uso",
    "conocimientos en",
    "manejo de",
    "experiencia en",
    "uso de",
    "proficiency",
    "experience with",
    "knowledge of",
    "working with",
    "expertise",
    "skilled in",
    "familiar with",
    "requerido",
    "required",
    "deseable",
    "preferible",
    "indispensable",
    "must have",
    "plus",
]

OPTIONAL_MARKERS = [
    "deseable",
    "preferible",
    "plus",
    "nice to have",
    "valuable",
    "idealmente",
    "ideally",
    "sera un plus",
    "will be a plus",
    "se valora",
    "ventaja",
]

REQUIRED_MARKERS = [
    "requerido",
    "required",
    "indispensable",
    "must have",
    "essential",
    "obligatorio",
    "se requiere",
    "necesario",
    "mandatory",
]


# ---------------------------------------------------------------------------
# Profile Loader
# ---------------------------------------------------------------------------


def load_profile(role: str) -> dict:
    """Load a profile from profiles/PROFILE_{ROLE}.md frontmatter."""
    profile_file = PROFILES_DIR / f"PROFILE_{role.upper()}.md"
    if not profile_file.exists():
        raise FileNotFoundError(f"Profile not found: {profile_file}")

    content = profile_file.read_text(encoding="utf-8")

    # Extract YAML frontmatter between --- markers
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            frontmatter = yaml.safe_load(parts[1])
            frontmatter["_narrative"] = parts[2].strip()
            return frontmatter

    raise ValueError(f"No valid YAML frontmatter found in {profile_file}")


# ---------------------------------------------------------------------------
# Skill Matching
# ---------------------------------------------------------------------------


def get_skill_category(skill_norm: str) -> str:
    for category, terms in SKILL_DICTIONARY.items():
        if skill_norm in [normalize(t) for t in terms]:
            return category
    return "other"


def fuzzy_match_skill(
    skill_norm: str, profile_skills: list[dict], threshold: float = 0.82
) -> dict | None:
    """Find best matching skill in profile using normalization + fuzzy matching."""
    for ps in profile_skills:
        ps_norm = normalize(ps["name"])
        # Direct match
        if skill_norm == ps_norm:
            return ps
        # Alias match
        for alias in ps.get("aliases", []):
            if skill_norm == normalize(alias):
                return ps
        # Fuzzy match
        ratio = difflib.SequenceMatcher(None, skill_norm, ps_norm).ratio()
        if ratio >= threshold:
            return ps
    return None


def match_skills_against_profile(jd_skills: list[dict], profile: dict) -> list[dict]:
    """Mark each JD skill as matched/unmatched against the profile."""
    profile_skills = profile.get("skills", [])
    result = []
    for skill in jd_skills:
        skill_norm = normalize(skill["skill"])
        matched_ps = fuzzy_match_skill(skill_norm, profile_skills)
        if matched_ps:
            skill["matched"] = 1
            profile_level = matched_ps.get("level", 3)
            years_req = skill.get("years_required") or 0
            # Heuristic: normalize years to 1-5 scale
            years_norm = min(5, max(1, years_req / 2)) if years_req else profile_level
            skill["proficiency_gap"] = profile_level - years_norm
        else:
            skill["matched"] = 0
            skill["proficiency_gap"] = None
        result.append(skill)
    return result


# ---------------------------------------------------------------------------
# Role filters (v2 scoring dimensions)
# ---------------------------------------------------------------------------


def _read_frontmatter(path: Path) -> dict:
    """Return the YAML frontmatter of a markdown file or ``{}`` if absent."""
    if not path.exists():
        return {}
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return {}
    if not text.startswith("---"):
        return {}
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}
    try:
        data = yaml.safe_load(parts[1]) or {}
    except yaml.YAMLError:
        return {}
    return data if isinstance(data, dict) else {}


_ROLE_FILTER_KEYS = (
    "work_modality_preference",
    "hybrid_days_max",
    "salary_floor",
    "sectors_target",
    "sectors_avoid",
    "hard_constraints",
)


def load_role_filters(role: str | None = None) -> dict:
    """Load the user's filters that feed the v2 scoring dimensions.

    Resolution order, with later sources overriding earlier ones:

    1. ``_brain/USER_CONTEXT.md`` — global defaults for the user.
    2. ``roles/<role>.md`` — role-specific overrides (only the keys that
       differ from USER_CONTEXT are written there).

    Returns a dict with any subset of the keys in ``_ROLE_FILTER_KEYS`` that
    were found. ``salary_floor`` is normalized into a single dict
    ``{"currency": ..., "monthly": ...}`` even when the source uses a list
    (the first entry wins; callers can extend to multi-currency later).
    """
    filters: dict = {}

    # 1. USER_CONTEXT — global defaults.
    user_context = _read_frontmatter(ROOT / "_brain" / "USER_CONTEXT.md")
    for key in _ROLE_FILTER_KEYS:
        if key in user_context:
            filters[key] = user_context[key]

    # 2. Role-specific overrides.
    if role:
        role_path = ROOT / "roles" / f"{role}.md"
        role_data = _read_frontmatter(role_path)
        for key in _ROLE_FILTER_KEYS:
            if key in role_data:
                filters[key] = role_data[key]

    # Normalize ``salary_floor``: accept either a dict or a list of dicts.
    floor = filters.get("salary_floor")
    if isinstance(floor, list):
        filters["salary_floor"] = floor[0] if floor else {}

    return filters
