from __future__ import annotations

from pathlib import Path


class ProjectLoadError(Exception):
    """Raised when a report or semantic model folder can't be located or has
    an unsupported layout."""


class UnsupportedFormatError(ProjectLoadError):
    """Raised when a folder is a legacy PBIR-Legacy report or TMSL (model.bim)
    semantic model. Per REQUIREMENTS.md these are out of scope for v1: the
    tool must hard-stop with a clear message and never attempt a partial
    migration.
    """


def validate_report_dir(path) -> Path:
    """Confirm `path` is a *.Report folder in current PBIR format.

    Raises UnsupportedFormatError for a legacy PBIR-Legacy report (a single
    report.json at the report root, no definition/ folder), and
    ProjectLoadError if it's not a report folder at all.
    """
    path = Path(path)
    if not path.is_dir():
        raise ProjectLoadError(f"{path} is not a folder")

    definition_dir = path / "definition"
    if definition_dir.is_dir() and (definition_dir / "report.json").is_file():
        return path

    if (path / "report.json").is_file():
        raise UnsupportedFormatError(
            f"{path} is a legacy PBIR-Legacy report (report.json at the report "
            "root, not under definition/). Open it in current Power BI Desktop "
            "and save to upgrade it to PBIR before migrating."
        )

    raise ProjectLoadError(f"{path} does not look like a *.Report (PBIR) folder")


def validate_semantic_model_dir(path) -> Path:
    """Confirm `path` is a *.SemanticModel folder in current TMDL format.

    Raises UnsupportedFormatError for a legacy TMSL semantic model
    (model.bim), and ProjectLoadError if it's not a semantic model folder
    at all.
    """
    path = Path(path)
    if not path.is_dir():
        raise ProjectLoadError(f"{path} is not a folder")

    tables_dir = path / "definition" / "tables"
    if tables_dir.is_dir():
        return path

    if (path / "model.bim").is_file():
        raise UnsupportedFormatError(
            f"{path} is a legacy TMSL semantic model (model.bim). Open it in "
            "current Power BI Desktop and save to upgrade it to TMDL before "
            "migrating."
        )

    raise ProjectLoadError(
        f"{path} does not look like a *.SemanticModel (TMDL) folder"
    )
