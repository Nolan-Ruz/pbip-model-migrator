"""FR1: discover every field reference in a PBIR report, structurally.

Per REQUIREMENTS.md, this must not hard-code assumed JSON paths. Instead it
walks every JSON file under the report's definition/ folder and treats any
object shaped like:

    {"Expression": {"SourceRef": {"Entity": <table>}}, "Property": <field>}

as a field reference, wherever it appears - visual projections/query state,
visual/page/report filters, sorts, conditional formatting, bookmarks, and
report-level measures all use this same shape, just at different nesting
depths, so one structural walk finds them all.

Where a reference sits inside a query projection (the common
`{"field": {...}, "queryRef": "...", "nativeQueryRef": "..."}` shape used by
visual.json), the sibling queryRef/nativeQueryRef display strings are linked
onto the same FieldReference so a later rewrite pass can update them too.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Union

PathKey = Union[str, int]
JsonPath = tuple[PathKey, ...]


@dataclass(frozen=True)
class FieldReference:
    """A single field/table reference discovered inside a report JSON file.

    `path` locates the reference's structural node (the dict holding
    Expression/Property) from the parsed file's root, as a tuple of dict
    keys (str) and list indices (int) - enough for a rewrite pass to find
    the exact node again without re-walking the tree.
    """

    file: Path  # relative to the report folder, e.g. definition/pages/.../visual.json
    path: JsonPath
    kind: str  # the wrapping key: "Column", "Measure", "HierarchyLevel", ...
    table: str
    field: str
    query_ref_path: Optional[JsonPath] = None
    native_query_ref_path: Optional[JsonPath] = None


def discover_references_in_report(report_dir) -> list[FieldReference]:
    report_dir = Path(report_dir)
    definition_dir = report_dir / "definition"

    references: list[FieldReference] = []
    for json_file in sorted(definition_dir.rglob("*.json")):
        references.extend(_discover_in_file(json_file, report_dir))
    return references


def _discover_in_file(json_file: Path, report_dir: Path) -> list[FieldReference]:
    try:
        data = json.loads(json_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []

    relative = json_file.relative_to(report_dir)
    return list(_walk(data, relative, (), ()))


def _walk(node, file: Path, path: JsonPath, ancestors: tuple):
    if isinstance(node, dict):
        ref = _as_field_reference(node, file, path, ancestors)
        if ref is not None:
            yield ref
        for key, value in node.items():
            yield from _walk(value, file, path + (key,), ancestors + (node,))
    elif isinstance(node, list):
        for index, item in enumerate(node):
            yield from _walk(item, file, path + (index,), ancestors + (node,))


def _as_field_reference(
    node: dict, file: Path, path: JsonPath, ancestors: tuple
) -> Optional[FieldReference]:
    field_name = node.get("Property")
    if not isinstance(field_name, str):
        return None

    expression = node.get("Expression")
    if not isinstance(expression, dict):
        return None

    source_ref = expression.get("SourceRef")
    if not isinstance(source_ref, dict):
        return None

    table = source_ref.get("Entity")
    if not isinstance(table, str):
        return None

    kind = path[-1] if path and isinstance(path[-1], str) else "Field"

    query_ref_path, native_query_ref_path = _find_display_ref_paths(path, ancestors)

    return FieldReference(
        file=file,
        path=path,
        kind=kind,
        table=table,
        field=field_name,
        query_ref_path=query_ref_path,
        native_query_ref_path=native_query_ref_path,
    )


def _find_display_ref_paths(
    path: JsonPath, ancestors: tuple
) -> tuple[Optional[JsonPath], Optional[JsonPath]]:
    """The `{"field": {...}, "queryRef": "...", "nativeQueryRef": "..."}`
    projection shape puts the display strings two levels above the
    Expression/Property node (its grandparent). Any other shape (filters,
    bookmarks, sorts, ...) simply has no display strings to link."""
    if len(ancestors) < 2:
        return None, None

    container = ancestors[-2]
    if not isinstance(container, dict):
        return None, None

    base = path[:-2]
    query_ref_path = base + ("queryRef",) if isinstance(container.get("queryRef"), str) else None
    native_query_ref_path = (
        base + ("nativeQueryRef",) if isinstance(container.get("nativeQueryRef"), str) else None
    )
    return query_ref_path, native_query_ref_path
