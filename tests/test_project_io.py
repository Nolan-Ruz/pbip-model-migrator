from pathlib import Path

import pytest

from pbip_model_migrator.core.project_io import (
    ProjectLoadError,
    copy_project_to,
    load_project,
)

FIXTURE_ROOT = Path(__file__).parent / "fixtures" / "SampleProject"
FIXTURE_PBIP = FIXTURE_ROOT / "SampleProject.pbip"


def test_load_project_from_pbip_file():
    project = load_project(FIXTURE_PBIP)

    assert project.name == "SampleProject"
    assert project.root == FIXTURE_ROOT
    assert project.report_dir == FIXTURE_ROOT / "SampleProject.Report"
    assert project.semantic_model_dir == FIXTURE_ROOT / "SampleProject.SemanticModel"


def test_load_project_from_directory():
    project = load_project(FIXTURE_ROOT)

    assert project.pbip_path == FIXTURE_PBIP


def test_tables_dir_lists_fixture_tables():
    project = load_project(FIXTURE_PBIP)

    table_names = sorted(p.stem for p in project.tables_dir.glob("*.tmdl"))
    assert table_names == ["Customer", "Sales"]


def test_load_project_missing_pbip_raises(tmp_path):
    with pytest.raises(ProjectLoadError, match="No .pbip file found"):
        load_project(tmp_path)


def test_load_project_missing_semantic_model_raises(tmp_path):
    pbip = tmp_path / "Orphan.pbip"
    pbip.write_text('{"version": "1.0", "artifacts": []}', encoding="utf-8")

    with pytest.raises(ProjectLoadError, match="SemanticModel"):
        load_project(pbip)


def test_copy_project_to_creates_independent_copy(tmp_path):
    project = load_project(FIXTURE_PBIP)
    output_root = tmp_path / "copy"

    copy = copy_project_to(project, output_root)

    assert copy.root == output_root
    assert copy.pbip_path.is_file()
    assert (copy.tables_dir / "Sales.tmdl").is_file()
    assert (copy.tables_dir / "Customer.tmdl").is_file()
    assert (copy.report_dir / "definition.pbir").is_file()

    # Mutating the copy must never touch the original fixture on disk.
    (copy.tables_dir / "Sales.tmdl").write_text("mutated", encoding="utf-8")
    original_contents = (project.tables_dir / "Sales.tmdl").read_text(encoding="utf-8")
    assert "mutated" not in original_contents


def test_copy_project_to_refuses_nonempty_output(tmp_path):
    project = load_project(FIXTURE_PBIP)
    output_root = tmp_path / "copy"
    output_root.mkdir()
    (output_root / "existing.txt").write_text("x", encoding="utf-8")

    with pytest.raises(ProjectLoadError, match="not empty"):
        copy_project_to(project, output_root)
