"""Small reusable widgets shared across the main window."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class StepCard(QFrame):
    """A numbered section: badge + title/subtitle header, a status pill, and
    a content area subclasses/callers fill in via `.content`."""

    def __init__(self, number: int, title: str, subtitle: str = "", parent=None):
        super().__init__(parent)
        self.setObjectName("stepCard")

        outer = QVBoxLayout(self)
        outer.setContentsMargins(20, 18, 20, 18)
        outer.setSpacing(10)

        header = QHBoxLayout()
        header.setSpacing(12)

        badge = QLabel(str(number))
        badge.setObjectName("stepBadge")
        badge.setAlignment(Qt.AlignCenter)
        badge.setFixedSize(28, 28)
        header.addWidget(badge)

        title_box = QVBoxLayout()
        title_box.setSpacing(0)
        title_label = QLabel(title)
        title_label.setObjectName("stepTitle")
        title_box.addWidget(title_label)
        if subtitle:
            subtitle_label = QLabel(subtitle)
            subtitle_label.setObjectName("stepSubtitle")
            title_box.addWidget(subtitle_label)
        header.addLayout(title_box)
        header.addStretch(1)

        self.status_label = QLabel("")
        self.status_label.setObjectName("statusPill")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.hide()
        header.addWidget(self.status_label)

        outer.addLayout(header)

        self.content = QVBoxLayout()
        self.content.setSpacing(8)
        outer.addLayout(self.content)

    def set_status(self, text: str, kind: str = "neutral"):
        self.status_label.setText(text)
        self.status_label.setProperty("kind", kind)
        self._repolish(self.status_label)
        self.status_label.show()

    def clear_status(self):
        self.status_label.hide()

    @staticmethod
    def _repolish(widget: QWidget):
        widget.style().unpolish(widget)
        widget.style().polish(widget)


class PathPickerRow(QWidget):
    """A read-only path display plus a Browse button, for either a folder or
    a single file. Emits `changed(Path)` when a selection is made."""

    changed = Signal(object)

    def __init__(
        self,
        placeholder: str,
        mode: str = "dir",
        file_filter: str = "All files (*.*)",
        parent=None,
    ):
        super().__init__(parent)
        self.mode = mode
        self.file_filter = file_filter
        self._path: Optional[Path] = None

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        self.path_label = QLabel(placeholder)
        self.path_label.setObjectName("pathLabel")
        self.path_label.setProperty("empty", True)
        layout.addWidget(self.path_label, 1)

        self.browse_button = QPushButton("Browse...")
        self.browse_button.setObjectName("secondaryButton")
        self.browse_button.setCursor(Qt.PointingHandCursor)
        self.browse_button.clicked.connect(self._browse)
        layout.addWidget(self.browse_button)

    def _browse(self):
        if self.mode == "dir":
            selected = QFileDialog.getExistingDirectory(self, "Select folder")
        else:
            selected, _ = QFileDialog.getOpenFileName(
                self, "Select file", "", self.file_filter
            )
        if selected:
            self.set_path(Path(selected))

    def set_path(self, path: Path):
        self._path = path
        self.path_label.setText(str(path))
        self.path_label.setProperty("empty", False)
        StepCard._repolish(self.path_label)
        self.changed.emit(path)

    @property
    def path(self) -> Optional[Path]:
        return self._path


class StatCard(QFrame):
    """A small metric tile: a big number and a caption, used in the results
    panel for resolved/unmapped/mapped-but-missing counts."""

    def __init__(self, label: str, parent=None):
        super().__init__(parent)
        self.setObjectName("statCard")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(2)

        self.value_label = QLabel("0")
        self.value_label.setObjectName("statValue")
        layout.addWidget(self.value_label)

        caption = QLabel(label)
        caption.setObjectName("statLabel")
        layout.addWidget(caption)

    def set_value(self, value: int, kind: str = "neutral"):
        colors = {
            "neutral": "#1F2430",
            "success": "#16A34A",
            "warning": "#D97706",
            "danger": "#DC2626",
        }
        self.value_label.setText(str(value))
        self.value_label.setStyleSheet(f"color: {colors.get(kind, colors['neutral'])};")
