"""Tests for ``jobsearch.fit_analyzer.extract_jd_signals``."""

from __future__ import annotations

from jobsearch.fit_analyzer import extract_jd_signals


class TestSalary:
    def test_usd_with_dollar_sign(self):
        sig = extract_jd_signals("We offer a salary of $80,000 USD annually.")
        assert sig["currency"] == "USD"
        assert sig["salary_min"] == 80000
        assert sig["salary_max"] == 80000

    def test_usd_with_k_suffix(self):
        sig = extract_jd_signals("Salary band: 70k-90k USD")
        assert sig["currency"] == "USD"
        assert sig["salary_min"] == 70000
        assert sig["salary_max"] == 90000

    def test_eur_with_thousands_dot(self):
        sig = extract_jd_signals("Compensación: EUR 60.000 anual")
        assert sig["currency"] == "EUR"
        assert sig["salary_min"] == 60000

    def test_no_salary_keyword_means_no_extraction(self):
        sig = extract_jd_signals("We use Python 3.10 and PostgreSQL.")
        assert "salary_min" not in sig
        assert "currency" not in sig


class TestModality:
    def test_fully_remote(self):
        sig = extract_jd_signals("This is a fully remote position.")
        assert sig["modality"] == "remote"

    def test_remote_spanish(self):
        sig = extract_jd_signals("Modalidad de trabajo remoto.")
        assert sig["modality"] == "remote"

    def test_hybrid_with_days(self):
        sig = extract_jd_signals("Hybrid model: 3 days per week in office.")
        assert sig["modality"] == "hybrid"
        assert sig["hybrid_days"] == 3

    def test_hybrid_spanish_with_days(self):
        sig = extract_jd_signals("Modelo hibrido, 2 dias a la semana presencial.")
        assert sig["modality"] == "hybrid"
        assert sig["hybrid_days"] == 2

    def test_onsite_in_office(self):
        sig = extract_jd_signals("Must work in-office at our HQ.")
        assert sig["modality"] == "onsite"

    def test_onsite_spanish(self):
        sig = extract_jd_signals("Trabajo presencial en la oficina.")
        assert sig["modality"] == "onsite"

    def test_no_remote_means_onsite_not_remote(self):
        """The phrase "no remote" must not be misread as the remote signal."""
        sig = extract_jd_signals("No remote work — onsite only.")
        assert sig["modality"] == "onsite"

    def test_silent_jd_returns_no_modality(self):
        sig = extract_jd_signals("We are hiring a backend engineer.")
        assert "modality" not in sig


class TestSectorTokens:
    def test_humanitarian(self):
        sig = extract_jd_signals("NGO seeking M&E officer for humanitarian programs.")
        assert "humanitarian" in sig["sector_tokens"]
        assert "ngo" in sig["sector_tokens"]

    def test_b2b_saas(self):
        sig = extract_jd_signals("B2B SaaS company, Series A startup.")
        assert "b2b" in sig["sector_tokens"]
        assert "saas" in sig["sector_tokens"]

    def test_multi_word_sector(self):
        sig = extract_jd_signals("Looking for an engineer with data platforms experience.")
        assert "data platforms" in sig["sector_tokens"]

    def test_unknown_sector_returns_empty(self):
        sig = extract_jd_signals("Generic developer role.")
        assert "sector_tokens" not in sig


class TestComposite:
    def test_full_jd_extracts_all_signals(self):
        jd = """
        Senior Data Engineer at AcmeNGO.

        We are an international NGO focused on humanitarian programs.
        Compensation: USD 90,000 - 110,000 annually.
        Hybrid model, 2 days per week in-office in Bogotá.
        """
        sig = extract_jd_signals(jd)
        assert sig["modality"] == "hybrid"
        assert sig["hybrid_days"] == 2
        assert sig["currency"] == "USD"
        assert sig["salary_min"] == 90000
        assert sig["salary_max"] == 110000
        assert "humanitarian" in sig["sector_tokens"]
