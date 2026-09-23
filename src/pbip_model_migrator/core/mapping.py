from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

VALID_OBJECT_TYPES = {"table", "column", "measure"}
REQUIRED_COLUMNS = [
    "object_type",
    "source_table",
    "source_name",
    "target_table",
    "target_name",
]


class MappingError(Exception):
    """Raised for a malformed mapping file (per FR7: this is an input error,
    exit code 2)."""


@dataclass(frozen=True)
class MappingRow:
    object_type: str  # "table" | "column" | "measure"
    source_table: str
    source_name: str  # "" for a table row
    target_table: str
    target_name: str  # "" for a table row


class Mapping:
    """A resolved source -> target mapping, built from the CSV rows.

    Field names are case-sensitive and matched exactly, per REQUIREMENTS.md.
    A `column`/`measure` row takes priority over a `table` row for the same
    source table: table rows only supply the table rename, field rows supply
    both the table and field rename for that specific field.
    """

    def __init__(self, rows: list[MappingRow]):
        self.rows = rows
        self._table_renames: dict[str, str] = {}
        self._field_renames: dict[tuple[str, str], tuple[str, str]] = {}

        for row in rows:
            if row.object_type == "table":
                self._table_renames[row.source_table] = row.target_table
            else:
                key = (row.source_table, row.source_name)
                self._field_renames[key] = (row.target_table, row.target_name)

    def resolve_table(self, source_table: str) -> Optional[str]:
        """The target table name for a bare table reference, or None if
        source_table has no mapping row at all."""
        return self._table_renames.get(source_table, None)

    def resolve_field(
        self, source_table: str, source_name: str
    ) -> Optional[tuple[str, str]]:
        """The (target_table, target_name) for a column/measure/hierarchy
        reference. Falls back to the table-level rename (field name
        unchanged) when there's no field-specific row. Returns None when
        source_table has no mapping at all."""
        key = (source_table, source_name)
        if key in self._field_renames:
            return self._field_renames[key]

        target_table = self._table_renames.get(source_table)
        if target_table is not None:
            return (target_table, source_name)

        return None

    def is_mapped_table(self, source_table: str) -> bool:
        return source_table in self._table_renames

    def is_mapped_field(self, source_table: str, source_name: str) -> bool:
        return (source_table, source_name) in self._field_renames


def load_mapping(path) -> Mapping:
    path = Path(path)
    try:
        text = path.read_text(encoding="utf-8-sig")
    except OSError as exc:
        raise MappingError(f"Could not read mapping file {path}: {exc}") from exc

    reader = csv.DictReader(text.splitlines())
    if reader.fieldnames is None:
        raise MappingError(f"Mapping file {path} is empty")

    missing = [c for c in REQUIRED_COLUMNS if c not in reader.fieldnames]
    if missing:
        raise MappingError(
            f"Mapping file {path} is missing required column(s): {', '.join(missing)}"
        )

    rows: list[MappingRow] = []
    seen_keys: set[tuple] = set()
    for line_no, raw in enumerate(reader, start=2):  # header is line 1
        object_type = (raw["object_type"] or "").strip()
        source_table = (raw["source_table"] or "").strip()
        source_name = (raw["source_name"] or "").strip()
        target_table = (raw["target_table"] or "").strip()
        target_name = (raw["target_name"] or "").strip()

        if not object_type and not source_table:
            continue  # blank line

        if object_type not in VALID_OBJECT_TYPES:
            raise MappingError(
                f"{path}:{line_no}: object_type must be one of "
                f"{sorted(VALID_OBJECT_TYPES)}, got {object_type!r}"
            )
        if not source_table:
            raise MappingError(f"{path}:{line_no}: source_table is required")
        if not target_table:
            raise MappingError(f"{path}:{line_no}: target_table is required")
        if object_type == "table":
            if source_name or target_name:
                raise MappingError(
                    f"{path}:{line_no}: table rows must leave source_name/"
                    "target_name blank"
                )
        else:
            if not source_name:
                raise MappingError(
                    f"{path}:{line_no}: source_name is required for a "
                    f"{object_type} row"
                )
            if not target_name:
                raise MappingError(
                    f"{path}:{line_no}: target_name is required for a "
                    f"{object_type} row"
                )

        key = (object_type, source_table, source_name)
        if key in seen_keys:
            raise MappingError(
                f"{path}:{line_no}: duplicate mapping row for {key}"
            )
        seen_keys.add(key)

        rows.append(
            MappingRow(
                object_type=object_type,
                source_table=source_table,
                source_name=source_name,
                target_table=target_table,
                target_name=target_name,
            )
        )

    if not rows:
        raise MappingError(f"Mapping file {path} has no data rows")

    return Mapping(rows)
