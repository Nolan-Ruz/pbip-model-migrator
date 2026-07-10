from pbip_model_migrator.gui.mapping_builder import build_mapping


def test_build_mapping_basic():
    tables = [("Sales_Old", "Sales_New")]
    columns = [("Sales_Old", "Amt", "Amount")]

    result = build_mapping(tables, columns)

    assert result == {
        "tables": {"Sales_Old": "Sales_New"},
        "columns": [{"table": "Sales_Old", "old": "Amt", "new": "Amount"}],
    }


def test_build_mapping_skips_blank_rows():
    tables = [("", "New"), ("Old", ""), ("A", "B")]
    columns = [("", "x", "y"), ("T", "", "y"), ("T", "x", "")]

    result = build_mapping(tables, columns)

    assert result == {"tables": {"A": "B"}, "columns": []}


def test_build_mapping_strips_whitespace():
    result = build_mapping([("  Old  ", "  New  ")], [])

    assert result == {"tables": {"Old": "New"}, "columns": []}


def test_build_mapping_last_duplicate_table_wins():
    result = build_mapping([("Old", "New1"), ("Old", "New2")], [])

    assert result["tables"]["Old"] == "New2"


def test_build_mapping_empty_input():
    assert build_mapping([], []) == {"tables": {}, "columns": []}
