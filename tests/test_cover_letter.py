"""Tests for ``jobsearch.cover_letter`` generation and humanizer rules."""

from __future__ import annotations

from dataclasses import dataclass, field

from jobsearch.cover_letter import HumanizerRules, generate_cover_letter


@dataclass
class _FakeFit:
    matched_skills: list[dict] = field(default_factory=list)
    gaps: list[dict] = field(default_factory=list)
    percentage: float = 80.0


def _fake_fit(
    matched: list[str] | None = None, gaps: list[str] | None = None, percentage: float = 80.0
) -> _FakeFit:
    return _FakeFit(
        matched_skills=[{"skill": s} for s in (matched or [])],
        gaps=[{"skill": s} for s in (gaps or [])],
        percentage=percentage,
    )


class TestHumanizerRules:
    def test_removes_em_dash(self):
        out = HumanizerRules.clean("first thing — second thing", lang="en")
        assert "—" not in out

    def test_collapses_double_commas(self):
        out = HumanizerRules.clean("hello, , world", lang="en")
        assert ", ," not in out


class TestGenerateCoverLetter:
    def test_pii_fallback_is_generic(self, sample_profile):
        # When the profile lacks a name, the fallback must NOT contain real names
        profile = {k: v for k, v in sample_profile.items() if k != "name"}
        letter = generate_cover_letter(
            profile, _fake_fit(matched=["Python"]), "JD", "Acme", lang="en"
        )
        assert "Luis" not in letter
        assert "Molina" not in letter
        # Generic fallback name should appear
        assert "Your Name" in letter

    def test_uses_profile_name_when_present(self, sample_profile):
        letter = generate_cover_letter(
            sample_profile, _fake_fit(matched=["Python"]), "JD", "Acme", lang="en"
        )
        assert "Test User" in letter
        assert "Your Name" not in letter

    def test_city_in_header_when_provided(self, sample_profile):
        letter = generate_cover_letter(
            sample_profile, _fake_fit(matched=["Python"]), "JD", "Acme", lang="es"
        )
        # Sample profile has city='Remote' -> must show in header
        first_line = letter.splitlines()[0]
        assert first_line.startswith("Remote, ")

    def test_no_city_omits_city_prefix(self, sample_profile):
        profile = {**sample_profile, "city": ""}
        letter = generate_cover_letter(
            profile, _fake_fit(matched=["Python"]), "JD", "Acme", lang="es"
        )
        # First line should be just the date (no leading "Caracas," etc.)
        first_line = letter.splitlines()[0]
        assert not first_line.startswith("Caracas")
        assert not first_line.startswith("Remote")

    def test_caracas_not_hardcoded_anywhere(self, sample_profile):
        """Regression test: Caracas should never appear unless city='Caracas'."""
        profile = {**sample_profile, "city": "Remote"}
        letter = generate_cover_letter(
            profile, _fake_fit(matched=["Python"]), "JD", "Acme", lang="es"
        )
        assert "Caracas" not in letter

    def test_mentions_company_and_role(self, sample_profile):
        letter = generate_cover_letter(
            sample_profile, _fake_fit(matched=["Python"]), "JD", "Acme", lang="en"
        )
        assert "Acme" in letter
        assert "Data Analyst" in letter
