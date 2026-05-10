"""Tests for ``jobsearch.profiles`` skill normalization and matching."""

from __future__ import annotations

from jobsearch.profiles import (
    fuzzy_match_skill,
    get_skill_category,
    match_skills_against_profile,
    normalize,
)


class TestNormalize:
    def test_lowercases(self):
        assert normalize("Python") == "python"

    def test_strips_accents(self):
        assert normalize("Análisis Cuantitativo") == "analisis cuantitativo"

    def test_collapses_whitespace(self):
        assert normalize("  power\t\n bi   ") == "power bi"

    def test_preserves_known_acronyms(self):
        assert normalize("M&E") == "m&e"

    def test_empty_string(self):
        assert normalize("") == ""


class TestGetSkillCategory:
    def test_data_skill(self):
        assert get_skill_category("python") == "data"

    def test_meal_skill(self):
        assert get_skill_category("kobo toolbox") == "meal"

    def test_marketing_skill(self):
        assert get_skill_category("hubspot") == "marketing"

    def test_unknown_skill_returns_other(self):
        assert get_skill_category("totally-fake-skill") == "other"


class TestFuzzyMatchSkill:
    def test_direct_match(self, sample_profile):
        match = fuzzy_match_skill("python", sample_profile["skills"])
        assert match is not None
        assert match["name"] == "Python"

    def test_alias_match(self, sample_profile):
        # 'mysql' is registered as an alias of SQL in the sample profile
        match = fuzzy_match_skill("mysql", sample_profile["skills"])
        assert match is not None
        assert match["name"] == "SQL"

    def test_fuzzy_close_match(self, sample_profile):
        # 'powerbi' close to 'power bi'; ratio above 0.82
        match = fuzzy_match_skill("powerbi", sample_profile["skills"])
        assert match is not None
        assert match["name"] == "Power BI"

    def test_no_match_returns_none(self, sample_profile):
        assert fuzzy_match_skill("kubernetes", sample_profile["skills"]) is None

    def test_threshold_strictness(self, sample_profile):
        # With a higher threshold, only direct/alias matches should survive
        match = fuzzy_match_skill("pythn", sample_profile["skills"], threshold=0.99)
        assert match is None


class TestMatchSkillsAgainstProfile:
    def test_marks_matched_skills(self, sample_profile):
        jd_skills = [
            {"skill": "Python", "category": "data", "required": 1, "years_required": 2},
            {"skill": "Kubernetes", "category": "data", "required": 1, "years_required": None},
        ]
        result = match_skills_against_profile(jd_skills, sample_profile)
        assert result[0]["matched"] == 1
        assert result[1]["matched"] == 0
        # Unmatched skills get no proficiency gap
        assert result[1]["proficiency_gap"] is None

    def test_proficiency_gap_uses_years_when_provided(self, sample_profile):
        jd_skills = [
            {"skill": "Python", "category": "data", "required": 1, "years_required": 6},
        ]
        result = match_skills_against_profile(jd_skills, sample_profile)
        # JD asks for 6 years (years_norm = 3.0), profile level = 4 -> gap = 1.0
        assert result[0]["matched"] == 1
        assert result[0]["proficiency_gap"] == 1.0

    def test_proficiency_gap_uses_profile_level_when_no_years(self, sample_profile):
        jd_skills = [
            {"skill": "SQL", "category": "data", "required": 1, "years_required": None},
        ]
        result = match_skills_against_profile(jd_skills, sample_profile)
        # No years_required -> gap should be 0 (profile_level - profile_level)
        assert result[0]["matched"] == 1
        assert result[0]["proficiency_gap"] == 0
