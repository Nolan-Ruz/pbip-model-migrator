from __future__ import annotations

import json
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


class ProjectLoadError(Exception):
    """Raised when a .pbip project can't be located or has an unsupported layout."""


class UnsupportedFormatError(ProjectLoadError):
    """Raised when a folder is a legacy PBIR-Legacy report or TMSL (model.bim)
    semantic model. Per REQUIREMENTS.md these are out of scope for v1: the
    tool must hard-stop with a clear message and never attempt a partial
    migration.
    """


@dataclass
class PbipProject:
    """A located PBIP project: the pointer file plus its report and semantic
    model folders. This is the real `project` object threaded through
    MigrationEngine.run() and every operation's apply(), replacing the
    placeholder {"path": ...} dict used before file I/O existed.
    """

    pbip_path: Path
    root: Path
    name: str
    report_dir: Optional[Path]
    semantic_model_dir: Path

    @property
    def tables_dir(self) -> Path:
        return self.semantic_model_dir / "definition" / "tables"

    @property
    def relationships_path(self) -> Path:
        return self.semantic_model_dir / "definition" / "relationships.tmdl"

    @property
    def roles_dir(self) -> Path:
        return self.semantic_model_dir / "definition" / "roles"


def load_project(pbip_path) -> PbipProject:
    """Locate a PBIP project from a .pbip file path or a directory containing
    exactly one, and resolve its *.Report and *.SemanticModel folders.

    Raises ProjectLoadError for anything that isn't a TMDL-format PBIP project
    (ambiguous or missing .pbip, missing semantic model, or a legacy
    single-file model.bim semantic model, which isn't supported yet).
    """
    pbip_path = Path(pbip_path)
    if pbip_path.is_dir():
        candidates = sorted(pbip_path.glob("*.pbip"))
        if not candidates:
            raise ProjectLoadError(f"No .pbip file found in {pbip_path}")
        if len(candidates) > 1:
            raise ProjectLoadError(
                f"Multiple .pbip files found in {pbip_path}; specify one explicitly"
            )
        pbip_path = candidates[0]

    if not pbip_path.is_file() or pbip_path.suffix != ".pbip":
        raise ProjectLoadError(f"{pbip_path} is not a .pbip file")

    root = pbip_path.parent
    name = pbip_path.stem

    try:
        manifest = json.loads(pbip_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ProjectLoadError(f"{pbip_path} is not valid JSON") from exc

    report_dir = _find_report_dir(root, name, manifest)
    semantic_model_dir = _find_semantic_model_dir(root, name, report_dir)

    if semantic_model_dir is None:
        raise ProjectLoadError(
            f"Could not locate a *.SemanticModel folder for {pbip_path.name}"
        )

    validate_semantic_model_dir(semantic_model_dir)

    return PbipProject(
        pbip_path=pbip_path,
        root=root,
        name=name,
        report_dir=report_dir,
        semantic_model_dir=semantic_model_dir,
    )


def _find_report_dir(root: Path, name: str, manifest: dict) -> Optional[Path]:
    for artifact in manifest.get("artifacts", []):
        report_ref = artifact.get("report")
        if report_ref and "path" in report_ref:
            candidate = (root / report_ref["path"]).resolve()
            return candidate if candidate.is_dir() else None

    candidate = root / f"{name}.Report"
    return candidate if candidate.is_dir() else None


def _find_semantic_model_dir(
    root: Path, name: str, report_dir: Optional[Path]
) -> Optional[Path]:
    candidate = root / f"{name}.SemanticModel"
    if candidate.is_dir():
        return candidate

    if report_dir is not None:
        pbir_path = report_dir / "definition.pbir"
        if pbir_path.is_file():
            try:
                pbir = json.loads(pbir_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                pbir = {}
            by_path = (pbir.get("datasetReference") or {}).get("byPath")
            if by_path and "path" in by_path:
                resolved = (report_dir / by_path["path"]).resolve()
                if resolved.is_dir():
                    return resolved

    matches = [p for p in root.glob("*.SemanticModel") if p.is_dir()]
    if len(matches) == 1:
        return matches[0]
    return None


def copy_project_to(project: PbipProject, output_root) -> PbipProject:
    """Copy the .pbip file plus the report and semantic model folders to
    output_root, and return a PbipProject pointing at the copy.

    The source project is never modified: every migration operation runs
    against the copy this returns, not against `project` itself.
    """
    output_root = Path(output_root)
    if output_root.exists() and any(output_root.iterdir()):
        raise ProjectLoadError(
            f"Output directory {output_root} already exists and is not empty"
        )
    output_root.mkdir(parents=True, exist_ok=True)

    shutil.copy2(project.pbip_path, output_root / project.pbip_path.name)
    if project.report_dir is not None:
        shutil.copytree(project.report_dir, output_root / project.report_dir.name)
    shutil.copytree(
        project.semantic_model_dir, output_root / project.semantic_model_dir.name
    )

    return load_project(output_root / project.pbip_path.name)


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
