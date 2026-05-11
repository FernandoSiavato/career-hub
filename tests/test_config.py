"""Tests for ``jobsearch.config`` scoring helpers."""

from __future__ import annotations

import importlib

import pytest


def _reload_config(data_dir, toml_text: str | None):
    """Helper: rewrite the active config.toml and reload jobsearch.config."""
    config_path = data_dir / "config.toml"
    if toml_text is None:
        if config_path.exists():
            config_path.unlink()
    else:
        config_path.write_text(toml_text, encoding="utf-8")
    import jobsearch.config as cfg

    return importlib.reload(cfg)


@pytest.fixture(autouse=True)
def _restore_config_after_test(data_dir):
    """Snapshot ``config.toml`` before each test and restore afterwards so
    rewrites here do not leak into tests in other modules."""
    config_path = data_dir / "config.toml"
    original = config_path.read_text(encoding="utf-8") if config_path.exists() else None
    yield
    if original is None:
        if config_path.exists():
            config_path.unlink()
    else:
        config_path.write_text(original, encoding="utf-8")
    import jobsearch.config as cfg

    importlib.reload(cfg)


class TestScoringWeights:
    def test_default_weights_normalize_to_one(self, data_dir):
        cfg = _reload_config(
            data_dir,
            """
default_role = "data"
[roles.data]
sector = 1
profile = "PROFILE_DATA"
folder = "applications/data"

[scoring]
threshold = 0.70

[scoring.weights]
skills       = 0.40
experience   = 0.20
modality     = 0.15
salary_floor = 0.10
sector_fit   = 0.15
""",
        )
        weights = cfg.scoring_weights()
        assert sum(weights.values()) == pytest.approx(1.0, abs=1e-9)
        # 0.40/1.00 -> 0.40 because the raw weights already sum to 1.0
        assert weights["skills"] == pytest.approx(0.40)
        assert set(weights.keys()) == {
            "skills",
            "experience",
            "modality",
            "salary_floor",
            "sector_fit",
        }

    def test_partial_weights_normalize(self, data_dir):
        """Weights that do not sum to 1.0 are normalized proportionally."""
        cfg = _reload_config(
            data_dir,
            """
default_role = "data"
[roles.data]
sector = 1
profile = "PROFILE_DATA"
folder = "applications/data"

[scoring]
[scoring.weights]
skills     = 2
experience = 1
modality   = 1
""",
        )
        weights = cfg.scoring_weights()
        assert sum(weights.values()) == pytest.approx(1.0, abs=1e-9)
        assert weights["skills"] == pytest.approx(0.5)
        assert weights["experience"] == pytest.approx(0.25)
        assert weights["modality"] == pytest.approx(0.25)
        assert "salary_floor" not in weights
        assert "sector_fit" not in weights

    def test_back_compat_no_scoring_block(self, data_dir):
        """With no ``[scoring]`` block the loader falls back to v1 weights."""
        cfg = _reload_config(
            data_dir,
            """
default_role = "data"
[roles.data]
sector = 1
profile = "PROFILE_DATA"
folder = "applications/data"
""",
        )
        weights = cfg.scoring_weights()
        assert weights == pytest.approx({"skills": 0.70, "experience": 0.30})
        assert cfg.scoring_threshold() == pytest.approx(0.70)

    def test_back_compat_skill_weights_alias(self, data_dir):
        """The legacy ``SKILL_WEIGHTS`` constant stays usable for old callers."""
        cfg = _reload_config(
            data_dir,
            """
default_role = "data"
[roles.data]
sector = 1
profile = "PROFILE_DATA"
folder = "applications/data"

[scoring]
threshold = 0.65

[scoring.weights]
skills     = 1
experience = 1
""",
        )
        # SKILL_WEIGHTS is module-level — derived from scoring_weights() at
        # import. Since we reloaded the module, it must reflect the new file.
        assert cfg.SKILL_WEIGHTS == pytest.approx({"skills": 0.5, "experience": 0.5})
        assert cfg.FIT_THRESHOLD == pytest.approx(0.65)


class TestScoringThreshold:
    def test_threshold_override(self, data_dir):
        cfg = _reload_config(
            data_dir,
            """
default_role = "data"
[roles.data]
sector = 1
profile = "PROFILE_DATA"
folder = "applications/data"

[scoring]
threshold = 0.55
""",
        )
        assert cfg.scoring_threshold() == pytest.approx(0.55)

    def test_threshold_default_when_block_absent(self, data_dir):
        cfg = _reload_config(
            data_dir,
            """
default_role = "data"
[roles.data]
sector = 1
profile = "PROFILE_DATA"
folder = "applications/data"
""",
        )
        assert cfg.scoring_threshold() == pytest.approx(0.70)


class TestScoringDimensions:
    def test_unknown_dimensions_are_ignored(self, data_dir):
        """Unknown keys in [scoring.weights] are dropped, not exploded into
        a runtime error. Keeps the config forward-compatible."""
        cfg = _reload_config(
            data_dir,
            """
default_role = "data"
[roles.data]
sector = 1
profile = "PROFILE_DATA"
folder = "applications/data"

[scoring]
[scoring.weights]
skills        = 1
experience    = 1
made_up_thing = 99
""",
        )
        weights = cfg.scoring_weights()
        assert "made_up_thing" not in weights
        assert weights["skills"] == pytest.approx(0.5)

    def test_zero_or_negative_weights_dropped(self, data_dir):
        cfg = _reload_config(
            data_dir,
            """
default_role = "data"
[roles.data]
sector = 1
profile = "PROFILE_DATA"
folder = "applications/data"

[scoring]
[scoring.weights]
skills     = 1
experience = 0
modality   = -0.2
""",
        )
        weights = cfg.scoring_weights()
        assert weights == pytest.approx({"skills": 1.0})
