"""FR4: classify every discovered reference against the target model.

- resolved: the (possibly mapped) table and field exist in the target model.
- unmapped: no mapping row covers the source reference, and it doesn't
  exist in the target model as-is either.
- mapped_but_missing: a mapping row points at a table/field that doesn't
  exist in the target model - a mapping-file error.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from pbip_model_migrator.core.mapping import Mapping
from pbip_model_migrator.core.reference_discovery import FieldReference
from pbip_model_migrator.core.tmdl_reader import TargetModel


class ReferenceStatus(str, Enum):
    RESOLVED = "resolved"
    UNMAPPED = "unmapped"
    MAPPED_BUT_MISSING = "mapped_but_missing"


@dataclass(frozen=True)
class ValidationResult:
    reference: FieldReference
    status: ReferenceStatus
    resolved_table: str
    resolved_field: str


def classify_references(
    references: list, mapping: Mapping, target_model: TargetModel
) -> list:
    results = []
    for ref in references:
        mapped = mapping.resolve_field(ref.table, ref.field)

        if mapped is not None:
            target_table, target_field = mapped
            status = (
                ReferenceStatus.RESOLVED
                if target_model.has_field(target_table, target_field)
                else ReferenceStatus.MAPPED_BUT_MISSING
            )
        else:
            target_table, target_field = ref.table, ref.field
            status = (
                ReferenceStatus.RESOLVED
                if target_model.has_field(target_table, target_field)
                else ReferenceStatus.UNMAPPED
            )

        results.append(ValidationResult(ref, status, target_table, target_field))

    return results
