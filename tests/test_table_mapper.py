from pbip_model_migrator.operations.table_mapper import TableMapper


def test_table_mapper_runs():
    mapper = TableMapper()
    mapper.apply({}, {})