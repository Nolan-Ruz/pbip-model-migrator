from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMainWindow,
    QPlainTextEdit,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from pbip_model_migrator.core.mapping import MappingError, load_mapping
from pbip_model_migrator.core.project_io import (
    ProjectLoadError,
    UnsupportedFormatError,
    validate_report_dir,
    validate_semantic_model_dir,
)
from pbip_model_migrator.gui.theme import STYLE_SHEET
from pbip_model_migrator.gui.widgets import PathPickerRow, StatCard, StepCard

MAPPING_COLUMNS = ["object_type", "source_table", "source_name", "target_table", "target_name"]


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PBIP Model Migrator")
        self.resize(980, 840)
        self.setMinimumWidth(760)

        self.mapping = None

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        self.setCentralWidget(scroll)

        page = QWidget()
        scroll.setWidget(page)

        root = QVBoxLayout(page)
        root.setContentsMargins(32, 28, 32, 28)
        root.setSpacing(18)

        root.addLayout(self._build_header())
        self.report_card = self._build_report_card()
        root.addWidget(self.report_card)
        self.target_card = self._build_target_card()
        root.addWidget(self.target_card)
        self.mapping_card = self._build_mapping_card()
        root.addWidget(self.mapping_card)
        root.addLayout(self._build_action_row())
        root.addWidget(self._build_results_panel())
        root.addWidget(self._build_log_panel())
        root.addStretch(1)

        self.report_dir: Path | None = None
        self.target_model_dir: Path | None = None

    # -- header -------------------------------------------------------------

    def _build_header(self):
        layout = QVBoxLayout()
        layout.setSpacing(2)
        title = QLabel("PBIP Model Migrator")
        title.setObjectName("pageTitle")
        subtitle = QLabel(
            "Remap tables and columns from a report onto a new semantic model, "
            "and check every field resolves before you touch Power BI Desktop."
        )
        subtitle.setObjectName("pageSubtitle")
        subtitle.setWordWrap(True)
        layout.addWidget(title)
        layout.addWidget(subtitle)
        return layout

    # -- step 1: report -------------------------------------------------------

    def _build_report_card(self):
        card = StepCard(1, "Source report", "The *.Report folder (PBIR) to migrate")
        self.report_picker = PathPickerRow("No report folder selected", mode="dir")
        self.report_picker.changed.connect(self._on_report_changed)
        card.content.addWidget(self.report_picker)
        return card

    def _on_report_changed(self, path: Path):
        try:
            validate_report_dir(path)
        except UnsupportedFormatError as exc:
            self.report_dir = None
            self.report_card.set_status("Unsupported format", "danger")
            self._log(str(exc))
        except ProjectLoadError as exc:
            self.report_dir = None
            self.report_card.set_status("Not a report folder", "danger")
            self._log(str(exc))
        else:
            self.report_dir = path
            self.report_card.set_status("PBIR detected", "success")
            self._log(f"Report folder set: {path}")
        self._refresh_actions()

    # -- step 2: target model -------------------------------------------------

    def _build_target_card(self):
        card = StepCard(
            2, "Target semantic model", "The *.SemanticModel folder (TMDL) to migrate onto"
        )
        self.target_picker = PathPickerRow("No target model selected", mode="dir")
        self.target_picker.changed.connect(self._on_target_changed)
        card.content.addWidget(self.target_picker)
        return card

    def _on_target_changed(self, path: Path):
        try:
            validate_semantic_model_dir(path)
        except UnsupportedFormatError as exc:
            self.target_model_dir = None
            self.target_card.set_status("Unsupported format", "danger")
            self._log(str(exc))
        except ProjectLoadError as exc:
            self.target_model_dir = None
            self.target_card.set_status("Not a semantic model folder", "danger")
            self._log(str(exc))
        else:
            self.target_model_dir = path
            self.target_card.set_status("TMDL detected", "success")
            self._log(f"Target model set: {path}")
        self._refresh_actions()

    # -- step 3: mapping ------------------------------------------------------

    def _build_mapping_card(self):
        card = StepCard(
            3, "Mapping file", "CSV: object_type, source_table, source_name, target_table, target_name"
        )
        self.mapping_picker = PathPickerRow(
            "No mapping file selected", mode="file", file_filter="CSV files (*.csv)"
        )
        self.mapping_picker.changed.connect(self._on_mapping_changed)
        card.content.addWidget(self.mapping_picker)

        self.mapping_table = QTableWidget(0, len(MAPPING_COLUMNS))
        self.mapping_table.setHorizontalHeaderLabels(MAPPING_COLUMNS)
        self.mapping_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.mapping_table.verticalHeader().setVisible(False)
        self.mapping_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.mapping_table.setSelectionMode(QTableWidget.NoSelection)
        self.mapping_table.setMinimumHeight(160)
        self.mapping_table.setMaximumHeight(220)
        card.content.addWidget(self.mapping_table)
        return card

    def _on_mapping_changed(self, path: Path):
        try:
            self.mapping = load_mapping(path)
        except MappingError as exc:
            self.mapping = None
            self.mapping_card.set_status("Invalid mapping file", "danger")
            self._log(str(exc))
            self.mapping_table.setRowCount(0)
        else:
            self.mapping_card.set_status(f"{len(self.mapping.rows)} rows loaded", "success")
            self._log(f"Mapping file loaded: {path} ({len(self.mapping.rows)} rows)")
            self._populate_mapping_table()
        self._refresh_actions()

    def _populate_mapping_table(self):
        rows = self.mapping.rows if self.mapping else []
        self.mapping_table.setRowCount(len(rows))
        for row_idx, row in enumerate(rows):
            values = [row.object_type, row.source_table, row.source_name, row.target_table, row.target_name]
            for col_idx, value in enumerate(values):
                item = QTableWidgetItem(value)
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                self.mapping_table.setItem(row_idx, col_idx, item)

    # -- actions ----------------------------------------------------------------

    def _build_action_row(self):
        layout = QHBoxLayout()
        layout.setSpacing(10)

        self.in_place_checkbox = QCheckBox("Write in place (overwrite the report folder)")

        self.dry_run_button = QPushButton("Run dry run")
        self.dry_run_button.setObjectName("primaryButton")
        self.dry_run_button.setCursor(Qt.PointingHandCursor)
        self.dry_run_button.clicked.connect(self._run_dry_run)
        self.dry_run_button.setEnabled(False)

        self.apply_button = QPushButton("Apply migration")
        self.apply_button.setObjectName("secondaryButton")
        self.apply_button.setCursor(Qt.PointingHandCursor)
        self.apply_button.setEnabled(False)

        layout.addWidget(self.in_place_checkbox)
        layout.addStretch(1)
        layout.addWidget(self.dry_run_button)
        layout.addWidget(self.apply_button)
        return layout

    def _refresh_actions(self):
        ready = self.report_dir is not None and self.target_model_dir is not None and self.mapping is not None
        self.dry_run_button.setEnabled(ready)

    def _run_dry_run(self):
        self._log("--- Dry run ---")
        self._log(f"Report: {self.report_dir}")
        self._log(f"Target model: {self.target_model_dir}")
        self._log(f"Mapping rows: {len(self.mapping.rows)}")
        self._log(
            "Reference discovery/validation engine is not implemented yet - "
            "this is a UI preview of the dry-run flow."
        )
        self.resolved_stat.set_value(0, "neutral")
        self.unmapped_stat.set_value(0, "neutral")
        self.missing_stat.set_value(0, "neutral")

    # -- results panel ------------------------------------------------------

    def _build_results_panel(self):
        card = StepCard(4, "Results", "Populated after a dry run")
        stats_row = QHBoxLayout()
        stats_row.setSpacing(10)

        self.resolved_stat = StatCard("Resolved")
        self.unmapped_stat = StatCard("Unmapped")
        self.missing_stat = StatCard("Mapped but missing")

        stats_row.addWidget(self.resolved_stat)
        stats_row.addWidget(self.unmapped_stat)
        stats_row.addWidget(self.missing_stat)
        card.content.addLayout(stats_row)
        return card

    # -- log panel ------------------------------------------------------------

    def _build_log_panel(self):
        frame = QFrame()
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(0, 0, 0, 0)

        self.log_view = QPlainTextEdit()
        self.log_view.setObjectName("logPanel")
        self.log_view.setReadOnly(True)
        self.log_view.setFixedHeight(160)
        self.log_view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        layout.addWidget(self.log_view)
        return frame

    def _log(self, message: str):
        self.log_view.appendPlainText(message)


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setStyleSheet(STYLE_SHEET)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
