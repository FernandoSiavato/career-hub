import re
from dataclasses import dataclass, field
from pathlib import Path

from jobsearch.config import FIT_THRESHOLD, SKILL_WEIGHTS
from jobsearch.profiles import (
    OPTIONAL_MARKERS,
    REQUIRED_MARKERS,
    SKILL_CANONICAL,
    SKILL_CONTEXT_WORDS,
    SKILL_DICTIONARY,
    match_skills_against_profile,
    normalize,
)

# ---------------------------------------------------------------------------
# JD Parsing
# ---------------------------------------------------------------------------


def read_jd(path_or_text: str) -> str:
    """Read JD text from .docx, .pdf, or raw string."""
    p = Path(path_or_text)
    if not p.exists():
        # Treat as raw text
        return path_or_text

    suffix = p.suffix.lower()
    if suffix == ".docx":
        try:
            import docx

            doc = docx.Document(str(p))
            parts = [para.text for para in doc.paragraphs if para.text.strip()]
            # Also read table cells
            for table in doc.tables:
                for row in table.rows:
                    for cell in row.cells:
                        if cell.text.strip():
                            parts.append(cell.text.strip())
            return "\n".join(parts)
        except Exception as e:
            raise RuntimeError(f"Cannot read .docx: {e}")

    if suffix == ".pdf":
        try:
            import pdfplumber

            with pdfplumber.open(str(p)) as pdf:
                return "\n".join(page.extract_text() or "" for page in pdf.pages)
        except Exception as e:
            raise RuntimeError(f"Cannot read .pdf: {e}")

    if suffix in (".txt", ".md"):
        return p.read_text(encoding="utf-8")

    raise ValueError(f"Unsupported file type: {suffix}")


def find_jd_in_folder(folder: Path) -> Path | None:
    """Auto-detect JD file in a company folder."""
    from jobsearch.config import JD_FILENAMES

    for name in JD_FILENAMES:
        candidate = folder / name
        if candidate.exists():
            return candidate
    # Fallback: any .docx not containing "CV" or "Carta"
    for f in folder.glob("*.docx"):
        if not any(w in f.stem.upper() for w in ("CV", "CARTA", "COVER", "RESUME")):
            return f
    for f in folder.glob("*.pdf"):
        if not any(w in f.stem.upper() for w in ("CV", "CARTA", "COVER", "RESUME")):
            return f
    return None


# ---------------------------------------------------------------------------
# Skill Extraction
# ---------------------------------------------------------------------------

YEARS_PATTERNS = [
    # Note: patterns run against ``normalize(text)`` which strips accents,
    # so ``años`` becomes ``anos``. Patterns must match the normalized form.
    r"(\d+)\+?\s*(?:anos?|years?)\s+(?:de\s+)?(?:experiencia|experience)",
    r"(?:al menos|minimum|minimo|min\.?)\s+(\d+)\s*(?:anos?|years?)",
    r"(\d+)\s*-\s*\d+\s*(?:anos?|years?)",  # range: take minimum
    r"experiencia\s+de\s+(\d+)\s*(?:anos?|years?)",
]


def extract_years_from_text(text: str) -> float:
    """Extract minimum years of experience required from JD text."""
    text_norm = normalize(text)
    years_found = []
    for pattern in YEARS_PATTERNS:
        matches = re.findall(pattern, text_norm)
        for m in matches:
            try:
                years_found.append(float(m))
            except ValueError:
                pass
    return min(years_found) if years_found else 0.0


def is_near_context(sentence: str) -> bool:
    """Check if a skill mention is near a context word (reduces false positives)."""
    s = normalize(sentence)
    return any(ctx in s for ctx in SKILL_CONTEXT_WORDS)


def classify_requirement(sentence: str) -> str:
    """Determine if a skill is required or optional based on surrounding text."""
    s = normalize(sentence)
    for marker in OPTIONAL_MARKERS:
        if marker in s:
            return "optional"
    for marker in REQUIRED_MARKERS:
        if marker in s:
            return "required"
    return "required"  # default: treat as required


def extract_skills(jd_text: str) -> list[dict]:
    """Extract skills from JD text with category, required flag, and years."""
    text_norm = normalize(jd_text)
    sentences = re.split(r"[.\n;]", jd_text)

    found: dict[str, dict] = {}  # normalized_skill → skill dict

    all_terms = []
    for category, terms in SKILL_DICTIONARY.items():
        for term in terms:
            all_terms.append((normalize(term), term, category))

    # Sort by length descending (match longer terms first, e.g., "power bi" before "bi")
    all_terms.sort(key=lambda x: len(x[0]), reverse=True)

    # Low-confidence single-word terms that need context to be valid
    low_confidence_terms = {
        "r",
        "word",
        "excel",
        "teams",
        "zoom",
        "slack",
        "desarrollo",
        "evaluacion",
        "informes",
        "colaboracion",
        "sem",
        "spanish",
        "espanol",
    }

    for norm_term, original_term, category in all_terms:
        if norm_term not in text_norm:
            continue
        if norm_term in found:
            continue  # already found a longer match covering this term

        # Find which sentence contains this term
        for sentence in sentences:
            if norm_term in normalize(sentence):
                if norm_term in low_confidence_terms and not is_near_context(sentence):
                    continue

                is_required = classify_requirement(sentence)
                years = extract_years_from_text(sentence) or 0.0

                found[norm_term] = {
                    "skill": SKILL_CANONICAL.get(norm_term, original_term),
                    "category": category,
                    "required": 1 if is_required == "required" else 0,
                    "years_required": years if years > 0 else None,
                    "matched": 0,
                    "proficiency_gap": None,
                }
                break

    return list(found.values())


# ---------------------------------------------------------------------------
# Fit Scoring
# ---------------------------------------------------------------------------


@dataclass
class FitReport:
    company: str
    role: str
    fit_score: float
    skills_score: float
    experience_score: float
    total_required: int
    matched_required: int
    total_optional: int
    matched_optional: int
    gaps: list[dict] = field(default_factory=list)
    matched_skills: list[dict] = field(default_factory=list)
    years_required: float = 0.0
    years_profile: float = 0.0
    recommendation: str = ""
    threshold: float = FIT_THRESHOLD

    def __post_init__(self):
        self.recommendation = "APPLY ✓" if self.fit_score >= self.threshold else "REVIEW GAPS FIRST"

    @property
    def percentage(self) -> float:
        return round(self.fit_score * 100, 1)

    @property
    def skills_pct(self) -> float:
        return round(self.skills_score * 100, 1)

    @property
    def exp_pct(self) -> float:
        return round(self.experience_score * 100, 1)


def score_fit(
    jd_skills: list[dict], profile: dict, company: str = "", role: str = "", jd_text: str = ""
) -> FitReport:
    """Calculate fit score from matched skills and experience."""

    required = [s for s in jd_skills if s.get("required", 1)]
    optional = [s for s in jd_skills if not s.get("required", 1)]

    matched_req = [s for s in required if s.get("matched")]
    matched_opt = [s for s in optional if s.get("matched")]
    gaps = [s for s in required if not s.get("matched")]

    # Skills score
    if len(required) == 0:
        skills_score = 0.5
    else:
        base = len(matched_req) / len(required)
        opt_bonus = (len(matched_opt) / max(len(optional), 1)) * 0.1
        skills_score = min(1.0, base + opt_bonus)

    # Experience score
    years_required = extract_years_from_text(jd_text) if jd_text else 0.0
    years_profile = float(profile.get("total_years_experience", 0))

    if years_required == 0:
        exp_score = 1.0
    else:
        shortfall = years_required - years_profile
        if shortfall <= 0:
            exp_score = 1.0
        elif shortfall <= 2:
            exp_score = 0.75
        elif shortfall <= 4:
            exp_score = 0.4
        else:
            exp_score = 0.1

    w = SKILL_WEIGHTS
    fit_score = (skills_score * w["skills"]) + (exp_score * w["experience"])

    return FitReport(
        company=company,
        role=role,
        fit_score=round(fit_score, 4),
        skills_score=round(skills_score, 4),
        experience_score=round(exp_score, 4),
        total_required=len(required),
        matched_required=len(matched_req),
        total_optional=len(optional),
        matched_optional=len(matched_opt),
        gaps=gaps,
        matched_skills=matched_req,
        years_required=years_required,
        years_profile=years_profile,
    )


# ---------------------------------------------------------------------------
# Report Generator
# ---------------------------------------------------------------------------


def generate_fit_report_md(report: FitReport, jd_source: str = "") -> str:
    from datetime import date

    lines = [
        f"# Fit Report — {report.company}",
        f"**Rol:** {report.role}  |  **Fecha:** {date.today().isoformat()}",
        f"**JD:** {jd_source}" if jd_source else "",
        "",
        "---",
        "",
        f"## Score: {report.percentage}% — {report.recommendation}",
        "",
        "| Componente | Score |",
        "|------------|-------|",
        f"| Skills match | {report.matched_required}/{report.total_required} ({report.skills_pct}%) |",
        f"| Experiencia | {report.years_profile} años vs {report.years_required} requeridos ({report.exp_pct}%) |",
        f"| **TOTAL** | **{report.percentage}%** |",
        "",
        "---",
        "",
        "## Skills Encontradas en tu Perfil",
    ]

    if report.matched_skills:
        for s in report.matched_skills:
            lines.append(f"- ✅ {s['skill']} ({s.get('category', '')})")
    else:
        lines.append("_Ninguna skill requerida detectada en tu perfil._")

    lines += [
        "",
        "## Gaps (Skills que piden y no tienes en el perfil)",
    ]

    if report.gaps:
        for g in report.gaps:
            yr = f" — {g['years_required']} años requeridos" if g.get("years_required") else ""
            lines.append(f"- ❌ {g['skill']} ({g.get('category', '')}){yr}")
    else:
        lines.append("_Sin gaps detectados._")

    if report.total_optional > 0:
        lines += [
            "",
            f"## Skills Opcionales ({report.matched_optional}/{report.total_optional} tienes)",
        ]

    lines += [
        "",
        "---",
        f"_Umbral para postular: {int(FIT_THRESHOLD * 100)}%_",
    ]

    return "\n".join(l for l in lines)


def analyze(jd_path_or_text: str, role: str, company: str = "", save_to: Path = None) -> FitReport:
    """Full pipeline: read JD → extract skills → match → score → report."""
    from jobsearch.profiles import load_profile

    jd_text = read_jd(jd_path_or_text)
    profile = load_profile(role)
    skills = extract_skills(jd_text)
    skills = match_skills_against_profile(skills, profile)
    report = score_fit(skills, profile, company=company, role=role, jd_text=jd_text)

    if save_to:
        md = generate_fit_report_md(report, jd_source=str(jd_path_or_text))
        save_to.write_text(md, encoding="utf-8")

    return report, skills
