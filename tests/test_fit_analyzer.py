"""Tests for ``jobsearch.fit_analyzer`` JD parsing and fit scoring."""

from __future__ import annotations

from jobsearch.fit_analyzer import (
    FitReport,
    classify_requirement,
    extract_skills,
    extract_years_from_text,
    score_fit,
)
from jobsearch.profiles import match_skills_against_profile


class TestExtractYearsFromText:
    def test_finds_years_es(self):
        assert extract_years_from_text("se requieren 3 años de experiencia") == 3.0

    def test_finds_years_en(self):
        assert extract_years_from_text("minimum 5 years experience") == 5.0

    def test_range_takes_minimum(self):
        assert extract_years_from_text("entre 2-4 años de experiencia") == 2.0

    def test_no_years_returns_zero(self):
        assert extract_years_from_text("Solid problem-solving skills.") == 0.0


class TestClassifyRequirement:
    def test_optional_marker_detected(self):
        assert classify_requirement("Tableau deseable") == "optional"

    def test_required_marker_detected(self):
        assert classify_requirement("Python requerido") == "required"

    def test_defaults_to_required(self):
        assert classify_requirement("Manejo de SQL") == "required"


class TestExtractSkills:
    def test_finds_core_skills(self, sample_jd_text):
        skills = extract_skills(sample_jd_text)
        names = {s["skill"] for s in skills}
        assert "Python" in names
        assert "SQL" in names
        assert "Power BI" in names

    def test_marks_required_vs_optional(self, sample_jd_text):
        skills = extract_skills(sample_jd_text)
        by_name = {s["skill"]: s for s in skills}
        assert by_name["Python"]["required"] == 1
        # 'Tableau' appears next to 'deseable'
        assert by_name["Tableau"]["required"] == 0

    def test_excludes_unrelated_skills(self, sample_jd_text):
        skills = extract_skills(sample_jd_text)
        names = {s["skill"] for s in skills}
        assert "KoboToolbox" not in names
        assert "HubSpot" not in names


class TestScoreFit:
    def test_full_match_high_score(self, sample_profile):
        jd_skills = [
            {"skill": "Python", "required": 1, "matched": 1, "category": "data"},
            {"skill": "SQL", "required": 1, "matched": 1, "category": "data"},
        ]
        report = score_fit(jd_skills, sample_profile, company="Acme", role="data", jd_text="")
        assert isinstance(report, FitReport)
        assert report.fit_score == 1.0
        assert report.recommendation.startswith("APPLY")

    def test_no_matches_low_score(self, sample_profile):
        jd_skills = [
            {"skill": "Kubernetes", "required": 1, "matched": 0, "category": "data"},
            {"skill": "Rust", "required": 1, "matched": 0, "category": "data"},
        ]
        report = score_fit(jd_skills, sample_profile, company="Acme", role="data")
        assert report.fit_score < 0.5
        assert "REVIEW" in report.recommendation

    def test_experience_shortfall_penalty(self, sample_profile):
        jd_skills = [
            {"skill": "Python", "required": 1, "matched": 1, "category": "data"},
        ]
        # JD demands 8 years; profile has 3 -> shortfall 5 years
        jd_text = "se requieren 8 años de experiencia"
        report = score_fit(jd_skills, sample_profile, company="Acme", role="data", jd_text=jd_text)
        assert report.years_required == 8.0
        assert report.years_profile == 3.0
        # exp_score for shortfall > 4 is 0.1 -> total fit ~ 0.73
        assert report.experience_score == 0.1

    def test_end_to_end_pipeline(self, sample_jd_text, sample_profile):
        skills = extract_skills(sample_jd_text)
        skills = match_skills_against_profile(skills, sample_profile)
        report = score_fit(
            skills, sample_profile, company="Acme", role="data", jd_text=sample_jd_text
        )
        # Profile has Python, SQL, Power BI, Excel — 4 of the required skills.
        # Expect a high fit score.
        assert report.fit_score >= 0.7
        assert report.matched_required >= 3


class TestFitReportProperties:
    def test_percentage_helpers(self, sample_profile):
        jd_skills = [
            {"skill": "Python", "required": 1, "matched": 1, "category": "data"},
        ]
        report = score_fit(jd_skills, sample_profile, company="Acme", role="data")
        assert report.percentage == round(report.fit_score * 100, 1)
        assert report.skills_pct == round(report.skills_score * 100, 1)
        assert report.exp_pct == round(report.experience_score * 100, 1)
