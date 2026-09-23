# pbip-model-migrator: v1 TODO

Checklist of what's left to build for a working, tested v1. Check items off as
they land so progress is easy to see at a glance.

## Foundations

- [x] Locate/copy a PBIP project (`core/project_io.py`)
- [x] Detect current PBIR vs. legacy PBIR-Legacy, and current TMDL vs. legacy
      TMSL (`model.bim`); hard-stop with a clear message on legacy formats
- [x] CSV mapping file loader with `table`/`column`/`measure` rows and
      field-row-overrides-table-row precedence (`core/mapping.py`)
- [x] Synthetic fixture PBIP project for tests (2 tables, 1 relationship,
      cross-table measures, 1 RLS role, 1 report page, 2 visuals, 1 bookmark)
- [x] PySide6 GUI shell: report/target/mapping pickers wired to real
      validation, results panel, log panel
- [ ] Test fixtures: a **target** semantic model (renamed tables/columns) and
      a **golden** expected-migrated-report to diff the engine's output
      against

## Migration engine

- [ ] **Reference discovery**: walk every JSON file under the report's
      `definition/` folder and find every field reference *structurally*
      (any object with `SourceRef -> Entity` + `Property`) — visuals/query
      state, visual/page/report filters, sorts, conditional formatting,
      bookmarks, report-level measures, and the `queryRef`/`nativeQueryRef`
      display strings
- [ ] **Reference rewriting**: apply the mapping to every discovered
      reference, rewriting both the structured reference and any display
      string that encodes it, while keeping the rest of each file
      byte-for-byte identical (minimal git diff — no full JSON
      reparse/reserialize)
- [ ] **Rebind the report**: update `definition.pbir`'s `datasetReference`
      to point at the target semantic model
- [ ] **Target model validation**: parse just enough of the target model's
      TMDL to list its tables/columns/measures/hierarchies, then classify
      every reference as resolved / unmapped / mapped-but-missing
- [ ] Lightweight TMDL name parser that handles quoted names
      (`'Sales Order'`), indentation nesting, and multi-line expressions
      without misreading their contents as declarations
- [ ] Dry-run by default (prints a change/validation summary, writes
      nothing); `--apply` performs writes; writes to a copy (`--out`) unless
      `--in-place` is passed
- [ ] `migration_report.json` (machine-readable) and `migration_report.md`
      (human-readable) with per-change file/location/old-value/new-value,
      plus every unresolved reference

## CLI

- [ ] `pbip-migrate --report ... --target-model ... --mapping ...
      [--apply] [--out ...] [--in-place]` entry point
- [ ] Exit codes: `0` all resolved, `1` unresolved references remain,
      `2` input error (legacy format, bad mapping file, missing folder)

## GUI

- [ ] Wire "Run dry run" to the real engine (currently echoes inputs only)
- [ ] Wire "Apply migration" (currently a disabled placeholder)
- [ ] Show discovered reference counts / resolved-unmapped-missing results
      in the results panel instead of zeros
- [ ] Surface `migration_report.json`/`.md` as downloadable/openable output
- [ ] Basic progress/busy state while a run is in flight

## Testing & CI

- [x] Unit tests: mapping precedence, format validation, project I/O
- [ ] Unit tests: reference discovery, the TMDL name parser, diff
      minimality
- [ ] End-to-end test: run the engine on the fixture and compare output to
      the golden migrated report
- [ ] A run with one mapping row deliberately removed exits `1` and names
      the unresolved references
- [ ] GitHub Actions workflow running `pytest` on push/PR, on both
      `ubuntu-latest` and `windows-latest`

## Cleanup

- [ ] Remove the now-superseded `core/migration.py` /
      `operations/base.py` / `operations/table_mapper.py` scaffolding (the
      engine doesn't mutate the semantic model, so the old
      `MigrationEngine`/`BaseOperation` pipeline no longer fits) or repurpose
      them for the new engine shape

## Ship

- [ ] README: setup instructions, a worked example, before/after
      screenshots, a measured before/after time for a real-sized report
- [ ] Manual check: migrated fixture (and a real project) opens clean in
      Power BI Desktop, no broken visuals — screenshot in README
- [ ] Tag v0.1
