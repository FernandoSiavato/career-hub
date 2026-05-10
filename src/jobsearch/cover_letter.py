"""
Cover letter generator with built-in Humanizer rules.
Based on Wikipedia's "Signs of AI writing" patterns.
"""

import re
from datetime import date
from pathlib import Path

# ---------------------------------------------------------------------------
# Humanizer Rules
# ---------------------------------------------------------------------------

AI_VOCAB = [
    "leveraging",
    "leverage",
    "delve",
    "delving",
    "innovative",
    "innovation",
    "cutting-edge",
    "cutting edge",
    "passionate",
    "passion",
    "thrilled",
    "excited to",
    "I am pleased to",
    "I am delighted to",
    "I am writing to express",
    "synergy",
    "synergies",
    "seamless",
    "robust",
    "transformative",
    "transformar de manera",
    "paradigm",
    "holistic",
    "holístico",
    "empower",
    "empoderar",
    "dynamic",
    "dinámico",
    "proactive",
    "proactivo",
    "thought leader",
    "game-changer",
    "disruptive",
    "impactful",
    "impactante",
]

# Spanish AI vocab
AI_VOCAB_ES = [
    "aprovechar",
    "apalancar",
    "apasionado por",
    "apasionada por",
    "es un placer",
    "me complace",
    "sinergias",
    "sinergia",
    "holístico",
    "holistica",
    "robusto",
    "robusta",
    "innovador",
    "innovadora",
    "transformador",
    "transformadora",
    "proactivo",
    "proactiva",
    "dinámico",
    "dinámica",
]

REPLACEMENTS_ES = {
    "aprovechar": "usar",
    "apalancar": "usar",
    "apasionado por": "interesado en",
    "apasionada por": "interesada en",
    "es un placer escribirle": "Le escribo",
    "me complace": "",
    "sinergias": "colaboración",
    "sinergia": "colaboración",
    "holístico": "integral",
    "holistica": "integral",
    "robusto": "sólido",
    "robusta": "sólida",
    "proactivo": "activo",
    "proactiva": "activa",
}

REPLACEMENTS_EN = {
    "leveraging": "using",
    "leverage": "use",
    "delve": "explore",
    "delving": "exploring",
    "cutting-edge": "advanced",
    "cutting edge": "advanced",
    "thought leader": "expert",
    "game-changer": "significant improvement",
    "I am pleased to inform": "I am writing to",
    "I am delighted to": "I am",
    "I am writing to express my interest": "I am applying",
    "thrilled": "interested",
    "passionate": "committed",
    "passion": "commitment",
    "robust": "solid",
    "seamless": "smooth",
    "holistic": "comprehensive",
    "transformative": "meaningful",
    "paradigm": "approach",
    "synergy": "collaboration",
    "synergies": "collaboration",
}


class HumanizerRules:
    @staticmethod
    def remove_em_dashes(text: str) -> str:
        """Replace em dashes (—) with commas or periods."""
        # em dash between clauses → comma
        text = re.sub(r"\s*—\s*", ", ", text)
        return text

    @staticmethod
    def break_rule_of_three(text: str) -> str:
        """
        Detect exact lists of 3 items joined by commas + 'y/and'.
        Converts 'A, B y C' → 'A y B, además de C'.
        """
        pattern = r"([A-Za-záéíóúÁÉÍÓÚñÑ][^,;.]{2,40}),\s+([A-Za-záéíóúÁÉÍÓÚñÑ][^,;.]{2,40})\s+y\s+([A-Za-záéíóúÁÉÍÓÚñÑ][^,;.]{2,40})"

        def replace_triple(m):
            a, b, c = m.group(1).strip(), m.group(2).strip(), m.group(3).strip()
            return f"{a} y {b}, además de {c}"

        return re.sub(pattern, replace_triple, text)

    @staticmethod
    def replace_ai_vocab(text: str, lang: str = "es") -> str:
        replacements = REPLACEMENTS_ES if lang == "es" else REPLACEMENTS_EN
        for ai_word, human_word in replacements.items():
            text = re.sub(re.escape(ai_word), human_word, text, flags=re.IGNORECASE)
        return text

    @staticmethod
    def remove_negative_parallelisms(text: str) -> str:
        """Remove 'not only X but also Y' patterns."""
        text = re.sub(
            r"no solo\s+(.+?)\s+sino también\s+(.+?)([.,])",
            lambda m: f"{m.group(1)} y {m.group(2)}{m.group(3)}",
            text,
            flags=re.IGNORECASE,
        )
        text = re.sub(
            r"not only\s+(.+?)\s+but also\s+(.+?)([.,])",
            lambda m: f"{m.group(1)} and {m.group(2)}{m.group(3)}",
            text,
            flags=re.IGNORECASE,
        )
        return text

    @staticmethod
    def fix_opening(text: str) -> str:
        """Replace generic AI openings with direct ones."""
        openings = [
            (r"^Me dirijo a usted con gran entusiasmo", "Le escribo"),
            (r"^Es un placer escribirles", "Les escribo"),
            (r"^I am writing to express my (interest|enthusiasm)", "I am applying"),
            (r"^I am excited to apply", "I am applying"),
            (r"^I am pleased to submit", "I am submitting"),
        ]
        for pattern, replacement in openings:
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE | re.MULTILINE)
        return text

    @classmethod
    def clean(cls, text: str, lang: str = "es") -> str:
        """Apply all humanizer rules."""
        text = cls.fix_opening(text)
        text = cls.remove_em_dashes(text)
        text = cls.replace_ai_vocab(text, lang)
        text = cls.remove_negative_parallelisms(text)
        text = cls.break_rule_of_three(text)
        # Clean up double spaces
        text = re.sub(r"  +", " ", text)
        # Clean up double commas
        text = re.sub(r",\s*,", ",", text)
        return text.strip()


# ---------------------------------------------------------------------------
# Cover Letter Generator
# ---------------------------------------------------------------------------


def generate_cover_letter(
    profile: dict, fit_report, jd_text: str, company: str, lang: str = "es"
) -> str:
    """
    Generate a cover letter based on the profile and fit analysis.
    Uses humanizer rules to avoid AI patterns.
    """
    name = profile.get("name", "Your Name")
    city = profile.get("city", "")
    role_title = profile.get("role_title", "")
    positioning = profile.get("positioning", "")
    achievements = profile.get("achievements", [])
    # Deduplicate skills preserving order
    seen = set()
    matched_skills = []
    for s in fit_report.matched_skills:
        if s["skill"] not in seen:
            seen.add(s["skill"])
            matched_skills.append(s["skill"])
    matched_skills = matched_skills[:4]
    gaps = [s["skill"] for s in fit_report.gaps[:2]]

    if lang == "es":
        text = _generate_es(
            name=name,
            city=city,
            role_title=role_title,
            company=company,
            positioning=positioning,
            achievements=achievements,
            matched_skills=matched_skills,
            gaps=gaps,
            fit_pct=fit_report.percentage,
        )
    else:
        text = _generate_en(
            name=name,
            city=city,
            role_title=role_title,
            company=company,
            positioning=positioning,
            achievements=achievements,
            matched_skills=matched_skills,
            fit_pct=fit_report.percentage,
        )

    return HumanizerRules.clean(text, lang=lang)


MESES_ES = {
    1: "enero",
    2: "febrero",
    3: "marzo",
    4: "abril",
    5: "mayo",
    6: "junio",
    7: "julio",
    8: "agosto",
    9: "septiembre",
    10: "octubre",
    11: "noviembre",
    12: "diciembre",
}


def _generate_es(
    name, city, role_title, company, positioning, achievements, matched_skills, gaps, fit_pct
) -> str:
    d = date.today()
    today = f"{d.day} de {MESES_ES[d.month]} de {d.year}"
    skills_str = ", ".join(matched_skills) if matched_skills else "las herramientas requeridas"

    ach_line = ""
    if achievements:
        ach_line = achievements[0]

    header = f"{city}, {today}" if city else today
    letter = f"""{header}

Estimado equipo de {company},

Les escribo para postular a la posición de {role_title}. {positioning.strip()}

A lo largo de mi trayectoria, he trabajado con {skills_str}, lo que me permite aportar desde el primer día al equipo. {ach_line}

Considero que mi experiencia y formación se alinean con los objetivos de {company}. Quedo disponible para una entrevista y ampliar cualquier punto de mi perfil.

Atentamente,
{name}
"""
    return letter


def _generate_en(
    name, city, role_title, company, positioning, achievements, matched_skills, fit_pct
) -> str:
    today = date.today().strftime("%B %d, %Y")
    skills_str = ", ".join(matched_skills) if matched_skills else "the required tools"

    ach_line = ""
    if achievements:
        ach_line = achievements[0]

    header = f"{city}, {today}" if city else today
    letter = f"""{header}

Dear {company} team,

I am applying for the {role_title} position. {positioning.strip()}

Throughout my career, I have worked with {skills_str}, allowing me to contribute from day one. {ach_line}

I believe my background aligns with {company}'s goals. I am available for an interview at your convenience.

Sincerely,
{name}
"""
    return letter


# ---------------------------------------------------------------------------
# Save as .docx
# ---------------------------------------------------------------------------


def save_cover_letter_docx(text: str, output_path: Path):
    """Save cover letter text as a formatted .docx file."""
    try:
        import docx
        from docx.enum.text import WD_ALIGN_PARAGRAPH
        from docx.shared import Inches, Pt

        doc = docx.Document()

        # Page margins
        for section in doc.sections:
            section.top_margin = Inches(1)
            section.bottom_margin = Inches(1)
            section.left_margin = Inches(1.2)
            section.right_margin = Inches(1.2)

        # Set default font
        style = doc.styles["Normal"]
        style.font.name = "Calibri"
        style.font.size = Pt(11)

        for line in text.split("\n"):
            para = doc.add_paragraph(line)
            para.paragraph_format.space_after = Pt(0)

        output_path.parent.mkdir(parents=True, exist_ok=True)
        doc.save(str(output_path))
    except ImportError:
        # Fallback: save as .txt
        txt_path = output_path.with_suffix(".txt")
        txt_path.write_text(text, encoding="utf-8")
        return txt_path
    return output_path
