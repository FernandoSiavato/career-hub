"""Tests for ``jobsearch.init_cmd.run_init``."""

from __future__ import annotations

from pathlib import Path

from jobsearch.init_cmd import DATA_DIR_FOLDERS, TEMPLATE_FILES, run_init


class TestRunInit:
    def test_creates_all_folders(self, tmp_path: Path):
        run_init(tmp_path / "fresh")
        target = tmp_path / "fresh"
        for folder in DATA_DIR_FOLDERS:
            assert (target / folder).is_dir(), f"missing folder {folder}"

    def test_writes_all_template_files(self, tmp_path: Path):
        run_init(tmp_path / "fresh")
        target = tmp_path / "fresh"
        for _src, dest_rel in TEMPLATE_FILES:
            assert (target / dest_rel).is_file(), f"missing template {dest_rel}"

    def test_creates_sqlite_database(self, tmp_path: Path):
        run_init(tmp_path / "fresh")
        assert (tmp_path / "fresh" / "jobsearch.db").is_file()

    def test_per_folder_claude_md_present(self, tmp_path: Path):
        """All 8 per-folder CLAUDE.md guides must be copied."""
        run_init(tmp_path / "fresh")
        target = tmp_path / "fresh"
        for folder in (
            "profiles",
            "cvs",
            "roles",
            "work_experience",
            "documentation_hub",
            "certificates",
            "personal_brand",
            "applications",
        ):
            claude = target / folder / "CLAUDE.md"
            assert claude.is_file(), f"missing {claude}"
            assert claude.read_text(encoding="utf-8").strip(), f"{claude} is empty"

    def test_is_idempotent_by_default(self, tmp_path: Path):
        first = run_init(tmp_path / "fresh")
        second = run_init(tmp_path / "fresh")
        # First call writes everything, second call skips because files exist.
        assert first["files_written"]
        assert not second["files_written"]
        assert second["files_skipped"]

    def test_force_overwrites_files(self, tmp_path: Path):
        run_init(tmp_path / "fresh")
        custom = tmp_path / "fresh" / "CLAUDE.md"
        custom.write_text("custom content", encoding="utf-8")
        run_init(tmp_path / "fresh", force=True)
        # The template content should have replaced the custom one.
        assert custom.read_text(encoding="utf-8") != "custom content"

    def test_summary_structure(self, tmp_path: Path):
        summary = run_init(tmp_path / "fresh")
        assert set(summary.keys()) == {
            "data_dir",
            "folders_created",
            "files_written",
            "files_skipped",
        }


class TestBrainFolder:
    """The _brain/ folder holds persistent memory between AI sessions."""

    def test_brain_folder_present(self, tmp_path: Path):
        run_init(tmp_path / "fresh")
        brain = tmp_path / "fresh" / "_brain"
        assert brain.is_dir()
        for name in ("SESSION_START.md", "USER_CONTEXT.md", "INSIGHTS.md", "CLAUDE.md"):
            target = brain / name
            assert target.is_file(), f"missing {name}"
            assert target.read_text(encoding="utf-8").strip(), f"{name} is empty"

    def test_insights_not_overwritten_on_reinit(self, tmp_path: Path):
        """Re-init without --force must preserve INSIGHTS.md so the AI never
        loses learnings from past postulations."""
        target = tmp_path / "fresh"
        run_init(target)
        insights = target / "_brain" / "INSIGHTS.md"
        insights.write_text("CUSTOM MANUAL NOTE", encoding="utf-8")
        run_init(target)  # second init, no force
        assert insights.read_text(encoding="utf-8") == "CUSTOM MANUAL NOTE"

    def test_force_overwrites_brain_files(self, tmp_path: Path):
        """With force=True the brain folder is reset to the bundled template."""
        target = tmp_path / "fresh"
        run_init(target)
        insights = target / "_brain" / "INSIGHTS.md"
        insights.write_text("CUSTOM MANUAL NOTE", encoding="utf-8")
        run_init(target, force=True)
        assert insights.read_text(encoding="utf-8") != "CUSTOM MANUAL NOTE"


class TestPerFolderTemplates:
    """Every user-facing folder ships an interview template (question bank)
    in its ``_template/`` subdirectory."""

    EXPECTED_TEMPLATES = [
        "profiles/_template/profile-interview-template.md",
        "cvs/_template/cv-structure-template.md",
        "roles/_template/role-criteria-template.md",
        "work_experience/_template/star-interview-template.md",
        "documentation_hub/_template/case-study-template.md",
        "certificates/_template/certificate-template.md",
        "personal_brand/_template/brand-discovery-template.md",
        "personal_brand/_template/voice-and-tone-template.md",
        "personal_brand/_template/content-strategy-template.md",
        "applications/_template/post-mortem-template.md",
    ]

    def test_all_per_folder_templates_copied(self, tmp_path: Path):
        run_init(tmp_path / "fresh")
        target = tmp_path / "fresh"
        for rel in self.EXPECTED_TEMPLATES:
            f = target / rel
            assert f.is_file(), f"missing {rel}"
            assert f.read_text(encoding="utf-8").strip(), f"{rel} is empty"

    def test_templates_have_ai_preamble(self, tmp_path: Path):
        """Every interview template must open with a "For the AI:" block so
        any agent that opens it knows how to use it."""
        run_init(tmp_path / "fresh")
        target = tmp_path / "fresh"
        for rel in self.EXPECTED_TEMPLATES:
            content = (target / rel).read_text(encoding="utf-8")
            assert "**For the AI:**" in content, f"{rel} missing AI preamble"
