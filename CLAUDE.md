# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

pbip-model-migrator is a Python tool that automates refactoring of Power BI PBIP files by remapping tables and columns between a source and target semantic model (e.g. after an ERP system change or schema update). It works directly on the PBIP JSON structure.

The project is in early scaffolding stages — most modules are stubs (`pass`-equivalent placeholders) establishing the intended architecture rather than working functionality.

## Commands

- Install (editable, from `src/` layout): `pip install -e .`
- Run tests: `pytest`
- Run a single test: `pytest tests/test_table_mapper.py::test_table_mapper_runs`

There is no configured lint/format/build tooling yet (no ruff/black/mypy config present).

## Architecture

The package lives at `src/pbip_model_migrator/` (src-layout; `pyproject.toml` sets `pythonpath = ["src"]` for pytest).

- **`core/migration.py`** — `MigrationEngine` is the orchestrator. It's constructed with a list of `operations` and its `run(project, mapping)` method calls `operation.apply(project, mapping)` on each one in sequence. This is the central pipeline: add a new migration step by implementing an operation and including it in the engine's operation list.
- **`operations/base.py`** — `BaseOperation` defines the operation interface: a single `apply(self, project, mapping)` method that subclasses must override.
- **`operations/table_mapper.py`** — `TableMapper(BaseOperation)` is the first concrete operation, intended to handle table-level remapping. Currently a stub.
- **`mappings/`** — intended home for source-to-target table/column mapping definitions (currently empty).
- **`gui/`** — intended home for a GUI front-end (currently empty; note the `__init__.py` file is misspelled as `__intit__.py`).

The `project` and `mapping` parameters threaded through `MigrationEngine.run` and every operation's `apply` are the two core data structures of this domain: `project` represents the PBIP project being migrated, `mapping` represents the source→target table/column mapping. New operations should follow this same `apply(project, mapping)` signature so they can be added to the engine's operation list interchangeably.

## Key features (per README, not all yet implemented)

- Table-level remapping
- Column-level mapping
- Bulk refactoring across semantic model files
- Works directly with PBIP structure
