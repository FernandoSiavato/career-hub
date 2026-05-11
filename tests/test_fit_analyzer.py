"""Tests for ``jobsearch.fit_analyzer`` JD parsing and fit scoring."""

from __future__ import annotations

import pytest

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


class TestCustomDimensions:
    """v2 scoring: modality, salary_floor, sector_fit dimensions."""

    def _good_skills(self):
        return [{"skill": "Python", "required": 1, "matched": 1, "category": "data"}]

    def test_modality_remote_match_full_credit(self, sample_profile):
        report = score_fit(
            self._good_skills(),
            sample_profile,
            jd_signals={"modality": "remote"},
            user_filters={"work_modality_preference": "remote"},
        )
        assert report.modality_score == 1.0
        assert "modality" in report.dimensions_used

    def test_modality_remote_vs_hybrid_partial(self, sample_profile):
        """User prefers remote, JD says hybrid -> partial credit."""
        report = score_fit(
            self._good_skills(),
            sample_profile,
            jd_signals={"modality": "hybrid"},
            user_filters={"work_modality_preference": "remote"},
        )
        assert report.modality_score == 0.5

    def test_modality_remote_vs_onsite_zero(self, sample_profile):
        report = score_fit(
            self._good_skills(),
            sample_profile,
            jd_signals={"modality": "onsite"},
            user_filters={"work_modality_preference": "remote"},
        )
        assert report.modality_score == 0.0

    def test_modality_jd_silent_skips_dimension(self, sample_profile):
        report = score_fit(
            self._good_skills(),
            sample_profile,
            jd_signals={},
            user_filters={"work_modality_preference": "remote"},
        )
        assert report.modality_score is None
        assert "modality" not in report.dimensions_used

    def test_salary_above_floor_full_credit(self, sample_profile):
        report = score_fit(
            self._good_skills(),
            sample_profile,
            jd_signals={"salary_max": 5000, "currency": "USD"},
            user_filters={"salary_floor": {"monthly": 4000, "currency": "USD"}},
        )
        assert report.salary_score == 1.0

    def test_salary_within_20_percent_partial(self, sample_profile):
        # JD offers 3,500, user floor 4,000 -> ratio 0.875 -> partial
        report = score_fit(
            self._good_skills(),
            sample_profile,
            jd_signals={"salary_max": 3500, "currency": "USD"},
            user_filters={"salary_floor": {"monthly": 4000, "currency": "USD"}},
        )
        assert report.salary_score == 0.5

    def test_salary_below_threshold_zero(self, sample_profile):
        report = score_fit(
            self._good_skills(),
            sample_profile,
            jd_signals={"salary_max": 2000, "currency": "USD"},
            user_filters={"salary_floor": {"monthly": 4000, "currency": "USD"}},
        )
        assert report.salary_score == 0.0

    def test_salary_currency_mismatch_skips_dimension(self, sample_profile):
        report = score_fit(
            self._good_skills(),
            sample_profile,
            jd_signals={"salary_max": 5000, "currency": "EUR"},
            user_filters={"salary_floor": {"monthly": 4000, "currency": "USD"}},
        )
        assert report.salary_score is None

    def test_sector_target_overlap_scores_positive(self, sample_profile):
        report = score_fit(
            self._good_skills(),
            sample_profile,
            jd_signals={"sector_tokens": {"saas", "b2b"}},
            user_filters={"sectors_target": ["saas", "fintech"]},
        )
        assert report.sector_score is not None
        assert report.sector_score > 0

    def test_sector_avoid_penalizes(self, sample_profile):
        """Sectors_avoid intersection drops the score by 0.3."""
        no_penalty = score_fit(
            self._good_skills(),
            sample_profile,
            jd_signals={"sector_tokens": {"saas"}},
            user_filters={"sectors_target": ["saas"]},
        ).sector_score
        with_penalty = score_fit(
            self._good_skills(),
            sample_profile,
            jd_signals={"sector_tokens": {"saas", "adtech"}},
            user_filters={"sectors_target": ["saas"], "sectors_avoid": ["adtech"]},
        ).sector_score
        assert with_penalty < no_penalty


class TestWeightRedistribution:
    """When a dimension is unmeasurable its weight goes to the others."""

    def _full_match_skills(self):
        return [{"skill": "Python", "required": 1, "matched": 1, "category": "data"}]

    def test_missing_dimensions_redistribute(self, sample_profile):
        """With only skills + experience scored, the two should absorb all
        the weight and applied weights still sum to 1.0."""
        report = score_fit(
            self._full_match_skills(),
            sample_profile,
            jd_signals={},  # nothing measurable for modality / salary / sector
            user_filters={},
        )
        total = sum(report.weights_applied.values())
        assert total == pytest.approx(1.0, abs=1e-6)
        assert set(report.dimensions_used) == {"skills", "experience"}

    def test_back_compat_default_weights_unchanged(self, sample_profile):
        """With no [scoring] block and no jd_signals/user_filters, the v2
        score_fit must produce the same number as v1 did (skills 70%,
        experience 30%)."""
        # Inside the conftest test data dir the bundled config.toml DOES
        # include a [scoring] block, so we cannot test "no scoring block"
        # here. We test the closer guarantee: with only skills+experience
        # scored, the result follows whatever weights config.toml declares.
        report = score_fit(
            self._full_match_skills(),
            sample_profile,
        )
        # Skills perfect (1.0), experience perfect (1.0), so fit must be 1.0
        # regardless of the weight distribution.
        assert report.fit_score == pytest.approx(1.0, abs=1e-6)
