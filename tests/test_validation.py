from pbip_model_migrator.core.mapping import load_mapping
from pbip_model_migrator.core.reference_discovery import FieldReference
from pbip_model_migrator.core.tmdl_reader import TargetModel, TargetTable
from pbip_model_migrator.core.validation import ReferenceStatus, classify_references


def _ref(table, field, kind="Column"):
    return FieldReference(file="v.json", path=(), kind=kind, table=table, field=field)


def _mapping(tmp_path, text):
    path = tmp_path / "mapping.csv"
    path.write_text(text, encoding="utf-8")
    return load_mapping(path)


def _target_with(tables: dict) -> TargetModel:
    return TargetModel(
        tables={
            name: TargetTable(name=name, columns=set(cols), measures=set(measures))
            for name, (cols, measures) in tables.items()
        }
    )


def test_resolved_when_mapped_field_exists_in_target(tmp_path):
    mapping = _mapping(
        tmp_path,
        "object_type,source_table,source_name,target_table,target_name\n"
        "column,SalesSAP,MENGE,Sales,Quantity\n",
    )
    target = _target_with({"Sales": ({"Quantity"}, set())})

    results = classify_references([_ref("SalesSAP", "MENGE")], mapping, target)

    assert results[0].status == ReferenceStatus.RESOLVED
    assert results[0].resolved_table == "Sales"
    assert results[0].resolved_field == "Quantity"


def test_mapped_but_missing_when_target_lacks_the_mapped_field(tmp_path):
    mapping = _mapping(
        tmp_path,
        "object_type,source_table,source_name,target_table,target_name\n"
        "column,SalesSAP,MENGE,Sales,Quantity\n",
    )
    target = _target_with({"Sales": ({"SomethingElse"}, set())})

    results = classify_references([_ref("SalesSAP", "MENGE")], mapping, target)

    assert results[0].status == ReferenceStatus.MAPPED_BUT_MISSING


def test_unmapped_when_no_mapping_row_and_not_in_target(tmp_path):
    mapping = _mapping(
        tmp_path,
        "object_type,source_table,source_name,target_table,target_name\n"
        "table,Other,,Other2,\n",
    )
    target = _target_with({"Other2": (set(), set())})

    results = classify_references([_ref("SalesSAP", "MENGE")], mapping, target)

    assert results[0].status == ReferenceStatus.UNMAPPED


def test_resolved_when_unmapped_field_already_exists_in_target_as_is(tmp_path):
    mapping = _mapping(
        tmp_path,
        "object_type,source_table,source_name,target_table,target_name\n"
        "table,Other,,Other2,\n",
    )
    target = _target_with({"Sales": ({"Amount"}, set())})

    results = classify_references([_ref("Sales", "Amount")], mapping, target)

    assert results[0].status == ReferenceStatus.RESOLVED
    assert results[0].resolved_table == "Sales"
    assert results[0].resolved_field == "Amount"


def test_table_level_mapping_applies_to_unlisted_fields(tmp_path):
    mapping = _mapping(
        tmp_path,
        "object_type,source_table,source_name,target_table,target_name\n"
        "table,SalesSAP,,Sales,\n",
    )
    target = _target_with({"Sales": ({"WERKS"}, set())})

    results = classify_references([_ref("SalesSAP", "WERKS")], mapping, target)

    assert results[0].status == ReferenceStatus.RESOLVED
    assert results[0].resolved_table == "Sales"
    assert results[0].resolved_field == "WERKS"
