from pathlib import Path

from pbip_model_migrator.core.tmdl_reader import read_target_model

FIXTURE_MODEL = Path(__file__).parent / "fixtures" / "SampleProject" / "SampleProject.SemanticModel"


def test_reads_tables_columns_and_measures_from_the_fixture():
    model = read_target_model(FIXTURE_MODEL)

    assert set(model.tables.keys()) == {"Sales", "Customer"}

    sales = model.tables["Sales"]
    assert sales.columns == {"OrderDate", "CustomerID", "Amount"}
    assert sales.measures == {"Total Sales", "Total Sales x2", "West Region Sales"}

    customer = model.tables["Customer"]
    assert customer.columns == {"CustomerID", "CustomerName", "Region"}
    assert customer.measures == set()


def test_has_field_and_has_table():
    model = read_target_model(FIXTURE_MODEL)

    assert model.has_table("Sales") is True
    assert model.has_table("Nonexistent") is False
    assert model.has_field("Sales", "Amount") is True
    assert model.has_field("Sales", "West Region Sales") is True
    assert model.has_field("Sales", "Nope") is False
    assert model.has_field("Nonexistent", "Anything") is False


def test_multiline_partition_body_is_not_mistaken_for_declarations():
    # The M partition code in the fixture is indented well past any real
    # column/measure/hierarchy declaration - confirm nothing from it leaked
    # into the parsed field names (e.g. "let", "Source", "in", "ChangedType").
    model = read_target_model(FIXTURE_MODEL)

    sales_names = model.tables["Sales"].all_field_names()
    for leaked in ("let", "Source", "in", "ChangedType", "Table.FromRows"):
        assert leaked not in sales_names


def test_quoted_names_with_spaces_and_hierarchy_levels(tmp_path):
    tables_dir = tmp_path / "definition" / "tables"
    tables_dir.mkdir(parents=True)
    (tables_dir / "Date.tmdl").write_text(
        "table 'Date'\n"
        "\tlineageTag: x\n"
        "\n"
        "\tcolumn 'Calendar Year'\n"
        "\t\tdataType: int64\n"
        "\n"
        "\thierarchy 'Fiscal Calendar'\n"
        "\t\tlevel Year\n"
        "\t\t\tordinal: 0\n"
        "\t\tlevel 'Fiscal Quarter'\n"
        "\t\t\tordinal: 1\n"
        "\n"
        "\tannotation PBI_ResultType = Table\n",
        encoding="utf-8",
    )

    model = read_target_model(tmp_path)

    assert "Date" in model.tables
    date_table = model.tables["Date"]
    assert date_table.columns == {"Calendar Year"}
    assert date_table.hierarchies == {"Fiscal Calendar": {"Year", "Fiscal Quarter"}}
    assert model.has_field("Date", "Fiscal Quarter") is True
