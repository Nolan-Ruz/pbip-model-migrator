from pathlib import Path

from pbip_model_migrator.core.reference_discovery import discover_references_in_report

FIXTURE_REPORT = Path(__file__).parent / "fixtures" / "SampleProject" / "SampleProject.Report"


def _find(refs, table, field, file_contains=None):
    matches = [r for r in refs if r.table == table and r.field == field]
    if file_contains is not None:
        matches = [r for r in matches if file_contains in r.file.as_posix()]
    return matches


def test_discovers_every_reference_in_the_fixture():
    refs = discover_references_in_report(FIXTURE_REPORT)

    # 2 in VisualSalesByDate, 3 in VisualSalesByRegion (2 projections + 1
    # filter), 1 in the bookmark.
    assert len(refs) == 6


def test_discovers_column_projection_with_display_refs():
    refs = discover_references_in_report(FIXTURE_REPORT)

    matches = _find(refs, "Sales", "OrderDate", "VisualSalesByDate")
    assert len(matches) == 1
    ref = matches[0]
    assert ref.kind == "Column"
    assert ref.query_ref_path is not None
    assert ref.native_query_ref_path is not None


def test_discovers_measure_projection():
    refs = discover_references_in_report(FIXTURE_REPORT)

    matches = _find(refs, "Sales", "Total Sales", "VisualSalesByDate")
    assert len(matches) == 1
    assert matches[0].kind == "Measure"


def test_discovers_cross_table_measure_in_second_visual():
    refs = discover_references_in_report(FIXTURE_REPORT)

    matches = _find(refs, "Sales", "West Region Sales", "VisualSalesByRegion")
    assert len(matches) == 1
    assert matches[0].kind == "Measure"


def test_discovers_visual_filter_without_display_refs():
    refs = discover_references_in_report(FIXTURE_REPORT)

    # Category.projections (has queryRef/nativeQueryRef) plus
    # filterConfig.filters (no display strings) both reference Customer.Region.
    matches = _find(refs, "Customer", "Region", "VisualSalesByRegion")
    assert len(matches) == 2

    with_display = [r for r in matches if r.query_ref_path is not None]
    without_display = [r for r in matches if r.query_ref_path is None]
    assert len(with_display) == 1
    assert len(without_display) == 1
    assert without_display[0].native_query_ref_path is None


def test_discovers_bookmark_reference():
    refs = discover_references_in_report(FIXTURE_REPORT)

    matches = _find(refs, "Customer", "Region", "bookmark")
    assert len(matches) == 1
    assert matches[0].query_ref_path is None


def test_reference_paths_resolve_back_to_the_source_node():
    import json

    refs = discover_references_in_report(FIXTURE_REPORT)
    ref = _find(refs, "Sales", "OrderDate", "VisualSalesByDate")[0]

    data = json.loads((FIXTURE_REPORT / ref.file).read_text(encoding="utf-8"))
    node = data
    for key in ref.path:
        node = node[key]

    assert node["Property"] == "OrderDate"
    assert node["Expression"]["SourceRef"]["Entity"] == "Sales"

    query_node = data
    for key in ref.query_ref_path:
        query_node = query_node[key]
    assert query_node == "Sales.OrderDate"
