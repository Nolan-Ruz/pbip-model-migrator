import pytest

from pbip_model_migrator.core.mapping import MappingError, load_mapping

SPEC_EXAMPLE = """object_type,source_table,source_name,target_table,target_name
table,SalesSAP,,Sales,
column,SalesSAP,MATNR,Sales,ProductKey
column,SalesSAP,MENGE,Sales,Quantity
measure,SalesSAP,Total Qty,Sales,Total Quantity
"""


def _write(tmp_path, text, name="mapping.csv"):
    path = tmp_path / name
    path.write_text(text, encoding="utf-8")
    return path


def test_load_mapping_spec_example(tmp_path):
    mapping = load_mapping(_write(tmp_path, SPEC_EXAMPLE))

    assert mapping.resolve_table("SalesSAP") == "Sales"
    assert mapping.resolve_field("SalesSAP", "MATNR") == ("Sales", "ProductKey")
    assert mapping.resolve_field("SalesSAP", "MENGE") == ("Sales", "Quantity")
    assert mapping.resolve_field("SalesSAP", "Total Qty") == ("Sales", "Total Quantity")


def test_field_row_overrides_table_row(tmp_path):
    mapping = load_mapping(_write(tmp_path, SPEC_EXAMPLE))

    # A column not given its own row still moves table via the table row,
    # keeping its original name.
    assert mapping.resolve_field("SalesSAP", "WERKS") == ("Sales", "WERKS")


def test_unmapped_table_returns_none(tmp_path):
    mapping = load_mapping(_write(tmp_path, SPEC_EXAMPLE))

    assert mapping.resolve_table("Unrelated") is None
    assert mapping.resolve_field("Unrelated", "Foo") is None


def test_is_mapped_helpers(tmp_path):
    mapping = load_mapping(_write(tmp_path, SPEC_EXAMPLE))

    assert mapping.is_mapped_table("SalesSAP") is True
    assert mapping.is_mapped_field("SalesSAP", "MATNR") is True
    assert mapping.is_mapped_field("SalesSAP", "WERKS") is False


def test_names_are_case_sensitive(tmp_path):
    mapping = load_mapping(_write(tmp_path, SPEC_EXAMPLE))

    assert mapping.resolve_table("salessap") is None
    assert mapping.resolve_field("SalesSAP", "matnr") == ("Sales", "matnr")


def test_missing_required_column_raises(tmp_path):
    bad = "object_type,source_table,source_name,target_table\ntable,A,,B\n"
    with pytest.raises(MappingError, match="missing required column"):
        load_mapping(_write(tmp_path, bad))


def test_invalid_object_type_raises(tmp_path):
    bad = (
        "object_type,source_table,source_name,target_table,target_name\n"
        "hierarchy,A,H1,B,H1\n"
    )
    with pytest.raises(MappingError, match="object_type must be one of"):
        load_mapping(_write(tmp_path, bad))


def test_table_row_with_names_raises(tmp_path):
    bad = (
        "object_type,source_table,source_name,target_table,target_name\n"
        "table,A,Oops,B,\n"
    )
    with pytest.raises(MappingError, match="must leave source_name"):
        load_mapping(_write(tmp_path, bad))


def test_column_row_missing_names_raises(tmp_path):
    bad = (
        "object_type,source_table,source_name,target_table,target_name\n"
        "column,A,,B,\n"
    )
    with pytest.raises(MappingError, match="source_name is required"):
        load_mapping(_write(tmp_path, bad))


def test_duplicate_row_raises(tmp_path):
    bad = (
        "object_type,source_table,source_name,target_table,target_name\n"
        "column,A,X,B,Y\n"
        "column,A,X,B,Z\n"
    )
    with pytest.raises(MappingError, match="duplicate mapping row"):
        load_mapping(_write(tmp_path, bad))


def test_empty_mapping_file_raises(tmp_path):
    with pytest.raises(MappingError, match="no data rows"):
        load_mapping(_write(tmp_path, "object_type,source_table,source_name,target_table,target_name\n"))


def test_blank_lines_are_skipped(tmp_path):
    text = SPEC_EXAMPLE + "\n\n"
    mapping = load_mapping(_write(tmp_path, text))
    assert mapping.resolve_table("SalesSAP") == "Sales"
