def build_mapping(table_rows, column_rows):
    """Turn raw (old, new) table rows and (table, old, new) column rows into
    the mapping dict consumed by MigrationEngine. Blank fields are skipped
    and whitespace is stripped so the GUI can hand over rows as-typed.
    """
    tables = {}
    for old, new in table_rows:
        old = old.strip()
        new = new.strip()
        if not old or not new:
            continue
        tables[old] = new

    columns = []
    for table, old, new in column_rows:
        table = table.strip()
        old = old.strip()
        new = new.strip()
        if not table or not old or not new:
            continue
        columns.append({"table": table, "old": old, "new": new})

    return {"tables": tables, "columns": columns}
