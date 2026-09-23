"""FR4 (partial): read just enough of a target model's TMDL to list its
tables, columns, measures and hierarchy levels for reference validation.

Per REQUIREMENTS.md, a full TMDL parser is not required in v1 - this is a
line-based, indentation-aware scanner. It handles quoted names
('Sales Order'), and relies on TMDL's strict indentation nesting to avoid
misreading multi-line DAX/M expression bodies (which sit several tabs
deeper than any real declaration) as object declarations.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

_BARE_NAME_RE = re.compile(r"[^\s=]+")


@dataclass
class TargetTable:
    name: str
    columns: set = field(default_factory=set)
    measures: set = field(default_factory=set)
    hierarchies: dict = field(default_factory=dict)  # hierarchy name -> set of level names

    def all_field_names(self) -> set:
        names = set(self.columns) | set(self.measures) | set(self.hierarchies.keys())
        for levels in self.hierarchies.values():
            names |= levels
        return names


@dataclass
class TargetModel:
    tables: dict  # table name -> TargetTable

    def has_table(self, table: str) -> bool:
        return table in self.tables

    def has_field(self, table: str, field_name: str) -> bool:
        target_table = self.tables.get(table)
        if target_table is None:
            return False
        return field_name in target_table.all_field_names()


def read_target_model(semantic_model_dir) -> TargetModel:
    semantic_model_dir = Path(semantic_model_dir)
    tables_dir = semantic_model_dir / "definition" / "tables"

    tables = {}
    if tables_dir.is_dir():
        for tmdl_file in sorted(tables_dir.glob("*.tmdl")):
            table = _parse_table_file(tmdl_file)
            if table is not None:
                tables[table.name] = table

    return TargetModel(tables=tables)


def _leading_tabs(line: str) -> int:
    count = 0
    for ch in line:
        if ch != "\t":
            break
        count += 1
    return count


def _parse_name(rest: str) -> str:
    rest = rest.strip()
    if rest.startswith("'"):
        idx = 1
        while idx < len(rest):
            if rest[idx] == "'":
                if idx + 1 < len(rest) and rest[idx + 1] == "'":
                    idx += 2
                    continue
                break
            idx += 1
        return rest[1:idx].replace("''", "'")

    match = _BARE_NAME_RE.match(rest)
    return match.group(0) if match else rest


def _parse_table_file(path: Path) -> Optional[TargetTable]:
    table: Optional[TargetTable] = None
    current_hierarchy: Optional[str] = None

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        if not raw_line.strip():
            continue

        depth = _leading_tabs(raw_line)
        content = raw_line[depth:]

        if depth == 0:
            current_hierarchy = None
            if content.startswith("table "):
                table = TargetTable(name=_parse_name(content[len("table "):]))
            continue

        if table is None:
            continue

        if depth == 1:
            current_hierarchy = None
            if content.startswith("column "):
                table.columns.add(_parse_name(content[len("column "):]))
            elif content.startswith("measure "):
                table.measures.add(_parse_name(content[len("measure "):]))
            elif content.startswith("hierarchy "):
                name = _parse_name(content[len("hierarchy "):])
                table.hierarchies.setdefault(name, set())
                current_hierarchy = name
            continue

        if depth == 2 and current_hierarchy is not None and content.startswith("level "):
            level_name = _parse_name(content[len("level "):])
            table.hierarchies[current_hierarchy].add(level_name)

    return table
