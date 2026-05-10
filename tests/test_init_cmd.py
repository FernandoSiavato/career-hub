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
