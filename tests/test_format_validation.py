from pathlib import Path

import pytest

from pbip_model_migrator.core.project_io import (
    ProjectLoadError,
    UnsupportedFormatError,
    validate_report_dir,
    validate_semantic_model_dir,
)

FIXTURE_ROOT = Path(__file__).parent / "fixtures" / "SampleProject"


def test_validate_report_dir_accepts_pbir():
    result = validate_report_dir(FIXTURE_ROOT / "SampleProject.Report")
    assert result.is_dir()


def test_validate_report_dir_rejects_legacy_pbir(tmp_path):
    legacy = tmp_path / "Old.Report"
    legacy.mkdir()
    (legacy / "report.json").write_text("{}", encoding="utf-8")

    with pytest.raises(UnsupportedFormatError, match="legacy PBIR-Legacy"):
        validate_report_dir(legacy)


def test_validate_report_dir_rejects_non_report_folder(tmp_path):
    with pytest.raises(ProjectLoadError, match="does not look like"):
        validate_report_dir(tmp_path)


def test_validate_semantic_model_dir_accepts_tmdl():
    result = validate_semantic_model_dir(
        FIXTURE_ROOT / "SampleProject.SemanticModel"
    )
    assert result.is_dir()


def test_validate_semantic_model_dir_rejects_legacy_tmsl(tmp_path):
    legacy = tmp_path / "Old.SemanticModel"
    legacy.mkdir()
    (legacy / "model.bim").write_text("{}", encoding="utf-8")

    with pytest.raises(UnsupportedFormatError, match="legacy TMSL"):
        validate_semantic_model_dir(legacy)


def test_validate_semantic_model_dir_rejects_non_model_folder(tmp_path):
    with pytest.raises(ProjectLoadError, match="does not look like"):
        validate_semantic_model_dir(tmp_path)
