"""Visual design tokens and the QSS stylesheet for the PySide6 app.

Kept as a single source of truth so palette changes don't require hunting
through widget code.
"""

BG = "#F5F6FA"
SURFACE = "#FFFFFF"
BORDER = "#E2E4EA"
TEXT_PRIMARY = "#1F2430"
TEXT_SECONDARY = "#6B7280"
ACCENT = "#4F46E5"
ACCENT_HOVER = "#4338CA"
ACCENT_PRESSED = "#3730A3"
ACCENT_SOFT = "#EEF0FF"
SUCCESS = "#16A34A"
SUCCESS_SOFT = "#E9F9EF"
WARNING = "#D97706"
WARNING_SOFT = "#FEF3E2"
DANGER = "#DC2626"
DANGER_SOFT = "#FDECEC"
NEUTRAL_SOFT = "#EEF0F4"

STYLE_SHEET = f"""
QWidget {{
    background: {BG};
    color: {TEXT_PRIMARY};
    font-family: "Segoe UI";
    font-size: 13px;
}}

QScrollArea {{
    border: none;
}}

#pageTitle {{
    font-size: 22px;
    font-weight: 600;
    color: {TEXT_PRIMARY};
}}

#pageSubtitle {{
    font-size: 13px;
    color: {TEXT_SECONDARY};
}}

#stepCard {{
    background: {SURFACE};
    border: 1px solid {BORDER};
    border-radius: 10px;
}}

#stepBadge {{
    background: {ACCENT_SOFT};
    color: {ACCENT};
    border-radius: 14px;
    font-weight: 600;
}}

#stepTitle {{
    font-size: 14px;
    font-weight: 600;
    color: {TEXT_PRIMARY};
}}

#stepSubtitle {{
    font-size: 12px;
    color: {TEXT_SECONDARY};
}}

QLabel#pathLabel {{
    background: {NEUTRAL_SOFT};
    border: 1px solid {BORDER};
    border-radius: 6px;
    padding: 7px 10px;
    color: {TEXT_PRIMARY};
}}

QLabel#pathLabel[empty="true"] {{
    color: {TEXT_SECONDARY};
    font-style: italic;
}}

QLabel#statusPill {{
    border-radius: 10px;
    padding: 3px 10px;
    font-size: 11px;
    font-weight: 600;
}}

QLabel#statusPill[kind="neutral"] {{
    background: {NEUTRAL_SOFT};
    color: {TEXT_SECONDARY};
}}

QLabel#statusPill[kind="success"] {{
    background: {SUCCESS_SOFT};
    color: {SUCCESS};
}}

QLabel#statusPill[kind="warning"] {{
    background: {WARNING_SOFT};
    color: {WARNING};
}}

QLabel#statusPill[kind="danger"] {{
    background: {DANGER_SOFT};
    color: {DANGER};
}}

QPushButton {{
    border-radius: 7px;
    padding: 8px 16px;
    font-weight: 600;
}}

QPushButton#primaryButton {{
    background: {ACCENT};
    color: white;
    border: none;
}}

QPushButton#primaryButton:hover {{
    background: {ACCENT_HOVER};
}}

QPushButton#primaryButton:pressed {{
    background: {ACCENT_PRESSED};
}}

QPushButton#primaryButton:disabled {{
    background: {NEUTRAL_SOFT};
    color: {TEXT_SECONDARY};
}}

QPushButton#secondaryButton {{
    background: {SURFACE};
    color: {TEXT_PRIMARY};
    border: 1px solid {BORDER};
}}

QPushButton#secondaryButton:hover {{
    background: {NEUTRAL_SOFT};
}}

QPushButton#secondaryButton:disabled {{
    color: {TEXT_SECONDARY};
    background: {NEUTRAL_SOFT};
}}

#statCard {{
    background: {SURFACE};
    border: 1px solid {BORDER};
    border-radius: 10px;
}}

#statValue {{
    font-size: 24px;
    font-weight: 700;
}}

#statLabel {{
    font-size: 12px;
    color: {TEXT_SECONDARY};
}}

QTableWidget {{
    background: {SURFACE};
    border: 1px solid {BORDER};
    border-radius: 8px;
    gridline-color: {BORDER};
    selection-background-color: {ACCENT_SOFT};
    selection-color: {TEXT_PRIMARY};
}}

QHeaderView::section {{
    background: {NEUTRAL_SOFT};
    color: {TEXT_SECONDARY};
    border: none;
    border-bottom: 1px solid {BORDER};
    padding: 6px 8px;
    font-weight: 600;
}}

QScrollBar:vertical {{
    background: transparent;
    width: 10px;
}}

QScrollBar::handle:vertical {{
    background: {BORDER};
    border-radius: 5px;
    min-height: 24px;
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}

#logPanel {{
    background: #14162B;
    color: #C9CCE3;
    border-radius: 8px;
    font-family: Consolas, monospace;
    font-size: 12px;
}}
"""
