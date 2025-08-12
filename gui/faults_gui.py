# faults_gui.py
# Autonomous Truck Fault Prioritization - Native Desktop GUI (PyQt6)
# Editable table with dropdowns/checkboxes, automatic Severity/Priority, CSV/XLSX export.
# Fixes: stable numeric outputs after edits, dtype coercion, formatted display.
# Added: comprehensive tooltips for thresholds & columns, per-row breakdown tooltips,
#        and Help menu with formulas & logic.

from __future__ import annotations

import sys
from typing import List, Dict, Any

import pandas as pd
from PyQt6.QtCore import (
    Qt, QModelIndex, QVariant, QAbstractTableModel
)
from PyQt6.QtGui import QAction, QPalette, QColor
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QFileDialog, QMessageBox, QTableView, QStyledItemDelegate, QComboBox,
    QToolBar, QStatusBar, QLabel, QDoubleSpinBox, QMenu, QListWidget,
    QListWidgetItem, QDialog, QVBoxLayout as QDialogVBox, QDialogButtonBox,
    QAbstractItemView,
)

# ----------------------------
# Categorical dictionaries
# ----------------------------
IMPACT_SCORES = {"None": 0, "Low": 1, "Medium": 2, "High": 3, "Critical": 4}
PROBABILITY_SCORES = {"Low": 1, "Medium": 2, "High": 3}
RECOVERY_SCORES = {
    "Auto-resolvable": 0,
    "Manual intervention": 1,
    "Restart required": 2,
    "Not recoverable": 3,
}
DETECTABILITY_SCORES = {"High": 0, "Medium": 1, "Low": 2}

STOP_MULTIPLIER_BY_IMPACT = {k: v / 4 for k, v in IMPACT_SCORES.items()}
STOP_MULTIPLIER_BY_RECOVERY = {
    "Auto-resolvable": 0.05,
    "Manual intervention": 0.25,
    "Restart required": 0.6,
    "Not recoverable": 1.0,
}

CBO_PROB = list(PROBABILITY_SCORES.keys())
CBO_IMPACT = list(IMPACT_SCORES.keys())
CBO_RECOV = list(RECOVERY_SCORES.keys())
CBO_DETECT = list(DETECTABILITY_SCORES.keys())

# ----------------------------
# Columns
# ----------------------------
INPUT_COLUMNS = [
    "Fault ID",
    "Description",
    "System",
    "Probability",
    "Mission Impact",
    "Recovery",
    "Detectability",
    "Safety Critical",
    "Time To Recover (s)",
    "Occurrences /100 missions",
    "Operational Requirement",
    "Technical Safety Requirement",
    "Functional Modification",
]

OUTPUT_COLUMNS = [
    "Severity (0-5)",
    "Expected Stops /100",
    "Implementation Priority",
]

ALL_COLUMNS = INPUT_COLUMNS + OUTPUT_COLUMNS

# Column tooltips (header)
COLUMN_TOOLTIPS: Dict[str, str] = {
    "Fault ID": "Unique identifier for the fault (e.g., F001).",
    "Description": "Short human\u2011readable description of the fault symptom or condition.",
    "System": "Subsystem affected (e.g., Perception, Control, Powertrain, Comms, Body/Cabin).",
    "Probability": (
        "Estimated frequency of occurrence.\n"
        "Allowed: Low=1, Medium=2, High=3 (numeric scores used in Severity)."
    ),
    "Mission Impact": (
        "How strongly this fault impacts mission continuity/safety.\n"
        "Allowed: None=0, Low=1, Medium=2, High=3, Critical=4 (numeric scores used in Severity, "
        "and an impact multiplier used in Expected Stops)."
    ),
    "Recovery": (
        "Difficulty to recover from the fault.\n"
        "Allowed: Auto-resolvable=0, Manual intervention=1, Restart required=2, Not recoverable=3 "
        "(numeric scores used in Severity, and a recovery multiplier used in Expected Stops)."
    ),
    "Detectability": (
        "How easy it is to detect/diagnose the fault.\n"
        "High=0 (good, reduces risk), Medium=1, Low=2 (hard to detect, increases risk)."
    ),
    "Safety Critical": (
        "If checked and Mission Impact is High or Critical, the row is prioritized as High "
        "regardless of thresholds."
    ),
    "Time To Recover (s)": (
        "Mean time (seconds) to fully recover/clear the fault. Increases Expected Stops via a penalty: "
        "TTR_penalty = 1 + min(2, TTR/300)."
    ),
    "Occurrences /100 missions": (
        "Historical or projected frequency of this fault per 100 missions. "
        "Used directly in Expected Stops /100."
    ),
    "Operational Requirement": "ID of an existing operational requirement to trace this fault to.",
    "Technical Safety Requirement": "ID of an existing technical safety requirement for this fault.",
    "Functional Modification": "ID of a functional modification requirement related to this fault.",
    "Severity (0-5)": (
        "Normalized severity risk score from Impact, Probability, Recovery, Detectability and Safety bonus "
        "scaled to 0–5. Higher is worse."
    ),
    "Expected Stops /100": (
        "Estimated mission stops contributed by this fault per 100 missions, factoring occurrence, impact, "
        "recovery, and time-to-recover penalty."
    ),
    "Implementation Priority": (
        "Resulting priority bucket (High/Medium/Low) determined by the rules using Safety flag, Severity, "
        "and Expected Stops thresholds."
    ),
}

# Default thresholds
SEVERITY_HI_TH = 4.0
SEVERITY_MED_TH = 3.0
STOPS_HI = 2.0
STOPS_MED = 0.5

# Weights
W_IMPACT = 2.0
W_PROB = 1.5
W_RECOV = 1.75
W_DETECT = 1.0
W_SAFETY = 1.5


from analysis.models import global_requirements


def requirement_ids(req_type: str) -> List[str]:
    """Return sorted requirement IDs for the given type."""
    ids = [r["id"] for r in global_requirements.values() if r.get("req_type") == req_type]
    return sorted(ids)


class MultiSelectDialog(QDialog):
    """Simple dialog to choose multiple items from a list."""

    def __init__(self, options: List[str], selected: List[str] | None = None, title: str = "Select", parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        layout = QDialogVBox(self)
        self.list = QListWidget()
        self.list.setSelectionMode(QListWidget.MultiSelection)
        for opt in options:
            item = QListWidgetItem(opt)
            self.list.addItem(item)
            if selected and opt in selected:
                item.setSelected(True)
        layout.addWidget(self.list)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def selected_items(self) -> List[str]:
        return [i.text() for i in self.list.selectedItems()]


def compute_metrics(row: Dict[str, Any],
                    severity_hi: float,
                    severity_med: float,
                    stops_hi: float,
                    stops_med: float) -> Dict[str, Any]:
    impact_cat = str(row.get("Mission Impact", "Medium"))
    prob_cat = str(row.get("Probability", "Medium"))
    recov_cat = str(row.get("Recovery", "Manual intervention"))
    detect_cat = str(row.get("Detectability", "Medium"))
    safety = bool(row.get("Safety Critical", False))

    ttr = float(row.get("Time To Recover (s)", 0) or 0)
    occ_per_100 = float(row.get("Occurrences /100 missions", 0) or 0)

    impact_score = IMPACT_SCORES.get(impact_cat, 0)
    prob_score = PROBABILITY_SCORES.get(prob_cat, 1)
    recov_score = RECOVERY_SCORES.get(recov_cat, 0)
    detect_score = DETECTABILITY_SCORES.get(detect_cat, 1)

    raw = (
        W_IMPACT * impact_score
        + W_PROB * prob_score
        + W_RECOV * recov_score
        + W_DETECT * detect_score
    )
    if safety:
        raw += W_SAFETY

    max_raw = (
        W_IMPACT * max(IMPACT_SCORES.values())
        + W_PROB * max(PROBABILITY_SCORES.values())
        + W_RECOV * max(RECOVERY_SCORES.values())
        + W_DETECT * max(DETECTABILITY_SCORES.values())
        + W_SAFETY
    )
    severity = 0.0 if max_raw <= 0 else 5.0 * (raw / max_raw)
    severity = max(0.0, min(5.0, severity))
    severity_rounded = float(round(severity, 2))

    stop_mult = STOP_MULTIPLIER_BY_IMPACT.get(impact_cat, 0.5) * \
                STOP_MULTIPLIER_BY_RECOVERY.get(recov_cat, 0.5)
    ttr_penalty = 1.0 + min(2.0, (ttr / 300.0))
    expected_stops = max(0.0, occ_per_100 * stop_mult) * ttr_penalty
    expected_stops_rounded = float(round(expected_stops, 3))

    # Priority rules
    priority = "Low"
    if safety and impact_cat in ("High", "Critical"):
        priority = "High"
    elif severity >= severity_hi or expected_stops >= stops_hi:
        priority = "High"
    elif severity >= severity_med or expected_stops >= stops_med:
        priority = "Medium"

    return {
        "Severity (0-5)": severity_rounded,
        "Expected Stops /100": expected_stops_rounded,
        "Implementation Priority": priority,
        # Include internals for tooltips
        "_impact_score": impact_score,
        "_prob_score": prob_score,
        "_recov_score": recov_score,
        "_detect_score": detect_score,
        "_safety": safety,
        "_raw": raw,
        "_max_raw": max_raw,
        "_impact_mult": STOP_MULTIPLIER_BY_IMPACT.get(impact_cat, 0.5),
        "_recov_mult": STOP_MULTIPLIER_BY_RECOVERY.get(recov_cat, 0.5),
        "_ttr_penalty": ttr_penalty,
    }


class ComboDelegate(QStyledItemDelegate):
    """Delegate that shows a combo box with provided options."""
    def __init__(self, options: List[str], parent=None):
        super().__init__(parent)
        self.options = options

    def createEditor(self, parent, option, index):
        cb = QComboBox(parent)
        cb.addItems(self.options)
        cb.setEditable(False)
        return cb

    def setEditorData(self, editor: QComboBox, index):
        value = index.data(Qt.ItemDataRole.EditRole) or index.data(Qt.ItemDataRole.DisplayRole)
        if value is None:
            value = ""
        pos = editor.findText(str(value))
        if pos < 0:
            pos = 0
        editor.setCurrentIndex(pos)

    def setModelData(self, editor: QComboBox, model, index):
        model.setData(index, editor.currentText(), Qt.ItemDataRole.EditRole)


class PandasTableModel(QAbstractTableModel):
    """QAbstractTableModel backed by a pandas DataFrame, with recompute and tooltip callbacks."""
    def __init__(self, df: pd.DataFrame,
                 recompute_fn,
                 is_output_col_fn,
                 header_tooltip_map: Dict[str, str],
                 row_tooltip_fn):
        super().__init__()
        self.df = df
        self.recompute_fn = recompute_fn
        self.is_output_col_fn = is_output_col_fn
        self.header_tooltip_map = header_tooltip_map
        self.row_tooltip_fn = row_tooltip_fn  # callable(row_index) -> str

    # ---- Required overrides ----
    def rowCount(self, parent=QModelIndex()):
        return len(self.df)

    def columnCount(self, parent=QModelIndex()):
        return len(self.df.columns)

    def data(self, index: QModelIndex, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return QVariant()
        r, c = index.row(), index.column()
        col = self.df.columns[c]
        val = self.df.iloc[r, c]

        # Right-align numeric cells
        if role == Qt.ItemDataRole.TextAlignmentRole and col in (
            "Time To Recover (s)",
            "Occurrences /100 missions",
            "Severity (0-5)",
            "Expected Stops /100",
        ):
            return Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter

        # ---- ToolTip for each cell: per-row breakdown ----
        if role == Qt.ItemDataRole.ToolTipRole:
            try:
                return self.row_tooltip_fn(r)
            except Exception:
                return ""

        # ----- Editing values -----
        if role == Qt.ItemDataRole.EditRole:
            if col == "Safety Critical":
                return bool(val)
            if col == "Time To Recover (s)":
                try:
                    return float(0.0 if pd.isna(val) else val)
                except Exception:
                    return 0.0
            if col == "Occurrences /100 missions":
                try:
                    return float(0.0 if pd.isna(val) else val)
                except Exception:
                    return 0.0
            # Other columns
            return "" if pd.isna(val) else val

        # ----- Display values -----
        if role == Qt.ItemDataRole.DisplayRole:
            if col == "Safety Critical":
                return bool(val)

            # Output numerics with pretty formatting
            if col == "Severity (0-5)":
                try:
                    return f"{float(val):.2f}"
                except Exception:
                    return "0.00"
            if col == "Expected Stops /100":
                try:
                    return f"{float(val):.3f}"
                except Exception:
                    return "0.000"

            # Input numerics: format explicitly so we never show blanks
            if col == "Time To Recover (s)":
                try:
                    return f"{float(val):.0f}"
                except Exception:
                    return "0"
            if col == "Occurrences /100 missions":
                try:
                    return f"{float(val):.3f}"
                except Exception:
                    return "0.000"

            # Default
            return "" if pd.isna(val) else val

        # Color whole row by priority
        if role == Qt.ItemDataRole.BackgroundRole:
            try:
                pr_idx = self.df.columns.get_loc("Implementation Priority")
                pr = str(self.df.iloc[r, pr_idx])
                if pr == "High":
                    return QColor(255, 230, 230)
                if pr == "Medium":
                    return QColor(255, 245, 225)
                if pr == "Low":
                    return QColor(235, 245, 255)
            except Exception:
                pass

        if role == Qt.ItemDataRole.CheckStateRole and col == "Safety Critical":
            return Qt.CheckState.Checked if bool(val) else Qt.CheckState.Unchecked

        return QVariant()

    def setData(self, index: QModelIndex, value, role=Qt.ItemDataRole.EditRole):
        if not index.isValid():
            return False
        r, c = index.row(), index.column()
        col = self.df.columns[c]

        if col == "Safety Critical":
            if role == Qt.ItemDataRole.CheckStateRole:
                self.df.at[r, col] = (value == Qt.CheckState.Checked)
                self.recompute_fn(r)
                left = self.index(r, 0)
                right = self.index(r, self.columnCount() - 1)
                self.dataChanged.emit(left, right)
                return True

        if role in (Qt.ItemDataRole.EditRole, Qt.ItemDataRole.DisplayRole):
            try:
                if col in ("Time To Recover (s)", "Occurrences /100 missions"):
                    try:
                        numval = 0.0 if value in ("", None) else float(value)
                    except Exception:
                        numval = 0.0
                    self.df.at[r, col] = numval
                else:
                    self.df.at[r, col] = value
                # recompute
                self.recompute_fn(r)

                # Guarantee numeric outputs remain floats and priority is string
                self.df.at[r, "Severity (0-5)"] = float(self.df.at[r, "Severity (0-5)"])
                self.df.at[r, "Expected Stops /100"] = float(self.df.at[r, "Expected Stops /100"])
                self.df.at[r, "Implementation Priority"] = str(self.df.at[r, "Implementation Priority"])

                left = self.index(r, 0)
                right = self.index(r, self.columnCount() - 1)
                self.dataChanged.emit(left, right)
                return True
            except Exception:
                return False
        return False

    def flags(self, index: QModelIndex):
        if not index.isValid():
            return Qt.ItemFlag.NoItemFlags
        col = self.df.columns[index.column()]
        base = Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled
        if self.is_output_col_fn(col):
            return base  # read-only
        if col == "Safety Critical":
            return base | Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEditable
        return base | Qt.ItemFlag.ItemIsEditable

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if orientation == Qt.Orientation.Horizontal:
            colname = self.df.columns[section]
            if role == Qt.ItemDataRole.DisplayRole:
                return colname
            if role == Qt.ItemDataRole.ToolTipRole:
                return self.header_tooltip_map.get(colname, "")
            return QVariant()
        else:
            if role == Qt.ItemDataRole.DisplayRole:
                return section + 1
            return QVariant()

    # ---- Helpers ----
    def set_dataframe(self, df: pd.DataFrame):
        self.beginResetModel()
        self.df = df
        self.endResetModel()

    def column_index(self, name: str) -> int:
        return self.df.columns.get_loc(name)

    def sort(self, column: int, order: Qt.SortOrder = Qt.SortOrder.AscendingOrder):
        colname = self.df.columns[column]
        try:
            ascending = order == Qt.SortOrder.AscendingOrder
            self.layoutAboutToBeChanged.emit()
            self.df.sort_values(by=colname, ascending=ascending, inplace=True, kind="mergesort")
            self.df.reset_index(drop=True, inplace=True)
            self.layoutChanged.emit()
        except Exception:
            pass


class FaultsWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Autonomous Truck Fault Prioritization")
        self.resize(1400, 800)
        # Keep the window large enough for the table, toolbar and status bar
        # to remain fully visible when the user resizes it.
        self.setMinimumSize(1200, 700)

        # thresholds
        self.sev_hi = SEVERITY_HI_TH
        self.sev_med = SEVERITY_MED_TH
        self.stops_hi = STOPS_HI
        self.stops_med = STOPS_MED

        # DataFrame backing store
        self.df: pd.DataFrame = self.default_df()

        # Widgets
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        self.table = QTableView()
        self.table.setAlternatingRowColors(True)
        self.table.setSortingEnabled(True)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.doubleClicked.connect(self.on_table_double_clicked)
        layout.addWidget(self.table)

        # Buttons row
        btn_row = QHBoxLayout()
        layout.addLayout(btn_row)
        self.btn_add = QPushButton("Add Row")
        self.btn_del = QPushButton("Delete Selected")
        btn_row.addWidget(self.btn_add)
        btn_row.addWidget(self.btn_del)
        btn_row.addStretch(1)

        self.status = QStatusBar()
        self.setStatusBar(self.status)

        # Menus / toolbar
        self.build_menu_toolbar()
        self.build_help_menu()

        # Model hookup
        self.model_from_df()

        # Delegates for categorical columns
        self.install_delegates()

        # Signals
        self.btn_add.clicked.connect(self.add_row)
        self.btn_del.clicked.connect(self.delete_selected)

    # ---------- UI setup ----------

    def build_menu_toolbar(self):
        tb = QToolBar("Main")
        tb.setMovable(False)
        self.addToolBar(tb)

        act_new = QAction("New", self)
        act_new.triggered.connect(self.new_table)
        act_new.setToolTip("Create a fresh table with default sample rows.")
        tb.addAction(act_new)

        act_open = QAction("Open CSV…", self)
        act_open.triggered.connect(self.open_csv)
        act_open.setToolTip("Load a CSV file and recompute all outputs.")
        tb.addAction(act_open)

        act_save_csv = QAction("Save CSV…", self)
        act_save_csv.triggered.connect(self.save_csv)
        act_save_csv.setToolTip("Export the current table to CSV.")
        tb.addAction(act_save_csv)

        act_save_xlsx = QAction("Save Excel…", self)
        act_save_xlsx.triggered.connect(self.save_xlsx)
        act_save_xlsx.setToolTip("Export the current table to Excel (.xlsx).")
        tb.addAction(act_save_xlsx)

        tb.addSeparator()

        # Threshold controls (double spin boxes for decimals)
        lbl_sev_hi = QLabel("Severity High ≥")
        lbl_sev_hi.setToolTip(
            "If a row's Severity (0–5) is ≥ this value, it becomes High priority "
            "(unless safety rule already set it High)."
        )
        tb.addWidget(lbl_sev_hi)

        self.sb_sev_hi = QDoubleSpinBox()
        self.sb_sev_hi.setRange(0.0, 5.0)
        self.sb_sev_hi.setDecimals(2)
        self.sb_sev_hi.setSingleStep(0.1)
        self.sb_sev_hi.setValue(SEVERITY_HI_TH)
        self.sb_sev_hi.setToolTip(
            "High priority threshold for the Severity (0–5) risk score.\n"
            "Lower this to classify more rows as High based on risk."
        )
        self.sb_sev_hi.valueChanged.connect(self.on_thresholds_changed)
        tb.addWidget(self.sb_sev_hi)

        lbl_sev_med = QLabel("Severity Med ≥")
        lbl_sev_med.setToolTip(
            "If a row's Severity (0–5) is ≥ this value (but < High threshold), it becomes Medium priority."
        )
        tb.addWidget(lbl_sev_med)

        self.sb_sev_med = QDoubleSpinBox()
        self.sb_sev_med.setRange(0.0, 5.0)
        self.sb_sev_med.setDecimals(2)
        self.sb_sev_med.setSingleStep(0.1)
        self.sb_sev_med.setValue(SEVERITY_MED_TH)
        self.sb_sev_med.setToolTip(
            "Medium priority threshold for Severity (0–5).\n"
            "Lower this to widen the Medium bucket."
        )
        self.sb_sev_med.valueChanged.connect(self.on_thresholds_changed)
        tb.addWidget(self.sb_sev_med)

        lbl_stops_hi = QLabel("Stops High ≥")
        lbl_stops_hi.setToolTip(
            "If Expected Stops /100 is ≥ this value, the row becomes High priority.\n"
            "This directly targets the KPI (missions stopped)."
        )
        tb.addWidget(lbl_stops_hi)

        self.sb_stops_hi = QDoubleSpinBox()
        self.sb_stops_hi.setRange(0.0, 50.0)
        self.sb_stops_hi.setDecimals(2)
        self.sb_stops_hi.setSingleStep(0.1)
        self.sb_stops_hi.setValue(STOPS_HI)
        self.sb_stops_hi.setToolTip(
            "High priority threshold based on Expected Stops per 100 missions.\n"
            "Lower this to aggressively capture faults that most affect the KPI."
        )
        self.sb_stops_hi.valueChanged.connect(self.on_thresholds_changed)
        tb.addWidget(self.sb_stops_hi)

        lbl_stops_med = QLabel("Stops Med ≥")
        lbl_stops_med.setToolTip(
            "If Expected Stops /100 is ≥ this value (but < High threshold), the row becomes Medium priority."
        )
        tb.addWidget(lbl_stops_med)

        self.sb_stops_med = QDoubleSpinBox()
        self.sb_stops_med.setRange(0.0, 50.0)
        self.sb_stops_med.setDecimals(2)
        self.sb_stops_med.setSingleStep(0.1)
        self.sb_stops_med.setValue(STOPS_MED)
        self.sb_stops_med.setToolTip(
            "Medium priority threshold based on Expected Stops per 100 missions."
        )
        self.sb_stops_med.valueChanged.connect(self.on_thresholds_changed)
        tb.addWidget(self.sb_stops_med)

        tb.addSeparator()

        act_light = QAction("Light Theme", self)
        act_light.setToolTip("Switch to a light Fusion palette.")
        act_light.triggered.connect(lambda: apply_fusion_palette(light=True))
        tb.addAction(act_light)

        act_dark = QAction("Dark Theme", self)
        act_dark.setToolTip("Switch to a dark Fusion palette.")
        act_dark.triggered.connect(lambda: apply_fusion_palette(light=False))
        tb.addAction(act_dark)

    def build_help_menu(self):
        menubar = self.menuBar()
        help_menu: QMenu = menubar.addMenu("&Help")

        act_formulas = QAction("Formulas && Logic", self)
        act_formulas.setToolTip("Show formulas for Severity, Expected Stops, and Priority rules.")
        act_formulas.triggered.connect(self.show_formulas_dialog)
        help_menu.addAction(act_formulas)

    def install_delegates(self):
        def col_index(name: str) -> int:
            return self.model.column_index(name)

        self.table.setItemDelegateForColumn(col_index("Probability"), ComboDelegate(CBO_PROB, self))
        self.table.setItemDelegateForColumn(col_index("Mission Impact"), ComboDelegate(CBO_IMPACT, self))
        self.table.setItemDelegateForColumn(col_index("Recovery"), ComboDelegate(CBO_RECOV, self))
        self.table.setItemDelegateForColumn(col_index("Detectability"), ComboDelegate(CBO_DETECT, self))

    def on_table_double_clicked(self, index: QModelIndex):
        """Open an appropriate editor when the user double-clicks a table cell."""
        if not index.isValid():
            return

        col_name = self.df.columns[index.column()]
        row = index.row()

        # Ignore output columns which are read-only
        if self.is_output_column(col_name):
            return

        # Requirement columns open a multi-select dialog
        req_map = {
            "Operational Requirement": "operational requirement",
            "Technical Safety Requirement": "technical safety requirement",
            "Functional Modification": "functional modification",
        }
        if col_name in req_map:
            current_val = str(self.df.at[row, col_name])
            selected = [s for s in current_val.split(";") if s]
            options = requirement_ids(req_map[col_name])
            dlg = MultiSelectDialog(options, selected, title=col_name, parent=self)
            if dlg.exec() == QDialog.DialogCode.Accepted:
                new_val = ";".join(dlg.selected_items())
                self.model.setData(index, new_val, Qt.ItemDataRole.EditRole)
            return

        if col_name == "Safety Critical":
            current = self.model.data(index, Qt.ItemDataRole.CheckStateRole)
            new_state = (
                Qt.CheckState.Unchecked
                if current == Qt.CheckState.Checked
                else Qt.CheckState.Checked
            )
            self.model.setData(index, new_state, Qt.ItemDataRole.CheckStateRole)
            return

        # For all other editable cells, invoke the default editor
        self.table.edit(index)

    # ---------- Model <-> View ----------

    def model_from_df(self):
        self.model = PandasTableModel(
            self.df,
            self.recompute_row,
            self.is_output_column,
            header_tooltip_map=COLUMN_TOOLTIPS,
            row_tooltip_fn=self.row_tooltip_text,
        )
        self.table.setModel(self.model)
        self.table.resizeColumnsToContents()
        self.table.horizontalHeader().setStretchLastSection(True)

    def is_output_column(self, column_name: str) -> bool:
        return column_name in OUTPUT_COLUMNS

    def recompute_row(self, row_idx: int):
        if row_idx < 0 or row_idx >= len(self.df):
            return
        row = self.df.iloc[row_idx].to_dict()
        metrics = compute_metrics(
            row,
            float(self.sb_sev_hi.value()),
            float(self.sb_sev_med.value()),
            float(self.sb_stops_hi.value()),
            float(self.sb_stops_med.value()),
        )
        for k, v in metrics.items():
            # Only write known output/public columns; internal keys start with "_"
            if not str(k).startswith("_"):
                self.df.at[row_idx, k] = v

        # Ensure numeric outputs stay numeric
        self.df.at[row_idx, "Severity (0-5)"] = float(self.df.at[row_idx, "Severity (0-5)"])
        self.df.at[row_idx, "Expected Stops /100"] = float(self.df.at[row_idx, "Expected Stops /100"])
        self.df.at[row_idx, "Implementation Priority"] = str(self.df.at[row_idx, "Implementation Priority"])

    # ---------- Row tooltip content ----------

    def row_tooltip_text(self, r: int) -> str:
        """Return rich tooltip text explaining the row's calculations."""
        if r < 0 or r >= len(self.df):
            return ""
        row = self.df.iloc[r].to_dict()
        m = compute_metrics(
            row,
            float(self.sb_sev_hi.value()),
            float(self.sb_sev_med.value()),
            float(self.sb_stops_hi.value()),
            float(self.sb_stops_med.value()),
        )
        impact = row.get("Mission Impact", "Medium")
        prob = row.get("Probability", "Medium")
        recov = row.get("Recovery", "Manual intervention")
        detect = row.get("Detectability", "Medium")
        safety = bool(row.get("Safety Critical", False))
        ttr = float(row.get("Time To Recover (s)", 0) or 0)
        occ = float(row.get("Occurrences /100 missions", 0) or 0)

        # Build HTML tooltip
        html = f"""
        <b>Row breakdown</b><br>
        <b>Fault ID:</b> {row.get('Fault ID','')} &nbsp; <b>System:</b> {row.get('System','')}<br>
        <b>Probability:</b> {prob} (score {m['_prob_score']}) &nbsp; 
        <b>Impact:</b> {impact} (score {m['_impact_score']}) &nbsp;
        <b>Recovery:</b> {recov} (score {m['_recov_score']}) &nbsp; 
        <b>Detectability:</b> {detect} (score {m['_detect_score']})<br>
        <b>Safety Critical:</b> {safety}<br><br>

        <b>Severity calculation</b><br>
        Raw = {W_IMPACT}×{m['_impact_score']} + {W_PROB}×{m['_prob_score']} + {W_RECOV}×{m['_recov_score']} + {W_DETECT}×{m['_detect_score']}
        {" + " + str(W_SAFETY) + " (safety bonus)" if safety else ""}<br>
        Raw = <b>{m['_raw']:.3f}</b> &nbsp; / &nbsp; MaxRaw = <b>{m['_max_raw']:.3f}</b><br>
        Severity = 5 × Raw/MaxRaw = <b>{float(row.get('Severity (0-5)', m['Severity (0-5)'])):.2f}</b><br><br>

        <b>Expected Stops /100</b><br>
        Impact multiplier = {m['_impact_mult']:.3f} &nbsp; · &nbsp; Recovery multiplier = {m['_recov_mult']:.3f}<br>
        TTR penalty = 1 + min(2, TTR/300) = 1 + min(2, {ttr:.0f}/300) = <b>{m['_ttr_penalty']:.3f}</b><br>
        Expected Stops = Occurrences/100 × ImpactMult × RecoveryMult × TTR_penalty<br>
        = {occ:.3f} × {m['_impact_mult']:.3f} × {m['_recov_mult']:.3f} × {m['_ttr_penalty']:.3f} = 
        <b>{float(row.get('Expected Stops /100', m['Expected Stops /100'])):.3f}</b><br><br>

        <b>Priority rule</b><br>
        """
        # Determine which rule fired
        priority = str(row.get("Implementation Priority", m["Implementation Priority"]))
        sev = float(row.get("Severity (0-5)", m["Severity (0-5)"]))
        exp = float(row.get("Expected Stops /100", m["Expected Stops /100"]))
        sev_hi = float(self.sb_sev_hi.value())
        sev_med = float(self.sb_sev_med.value())
        st_hi = float(self.sb_stops_hi.value())
        st_med = float(self.sb_stops_med.value())

        rule_text = ""
        if safety and str(impact) in ("High", "Critical"):
            rule_text = "Safety-critical shortcut: Safety=True and Impact ∈ {High, Critical} ⇒ High."
        elif sev >= sev_hi or exp >= st_hi:
            rule_text = f"Severity ≥ {sev_hi:.2f} or Expected Stops ≥ {st_hi:.2f} ⇒ High."
        elif sev >= sev_med or exp >= st_med:
            rule_text = f"Severity ≥ {sev_med:.2f} or Expected Stops ≥ {st_med:.2f} ⇒ Medium."
        else:
            rule_text = "Else ⇒ Low."

        html += f"{rule_text}<br><b>Priority:</b> {priority}"
        return html

    # ---------- Actions ----------

    def new_table(self):
        if not self.confirm_discard():
            return
        self.df = self.default_df()
        self.model.set_dataframe(self.df)
        self.status.showMessage("New table created.", 4000)

    def open_csv(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open CSV", "", "CSV Files (*.csv)")
        if not path:
            return
        try:
            df = pd.read_csv(path)

            # Ensure all expected columns exist
            for col in ALL_COLUMNS:
                if col not in df.columns:
                    df[col] = "" if col != "Safety Critical" else False
            df = df[ALL_COLUMNS]

            # Coerce types to avoid NaNs rendering blank
            df["Time To Recover (s)"] = pd.to_numeric(df["Time To Recover (s)"], errors="coerce").fillna(0.0)
            df["Occurrences /100 missions"] = pd.to_numeric(df["Occurrences /100 missions"], errors="coerce").fillna(0.0)
            df["Severity (0-5)"] = pd.to_numeric(df.get("Severity (0-5)"), errors="coerce").fillna(0.0)
            df["Expected Stops /100"] = pd.to_numeric(df.get("Expected Stops /100"), errors="coerce").fillna(0.0)
            df["Implementation Priority"] = df.get("Implementation Priority").astype(str)

            # recompute
            for i in range(len(df)):
                row = df.iloc[i].to_dict()
                metrics = compute_metrics(
                    row,
                    float(self.sb_sev_hi.value()),
                    float(self.sb_sev_med.value()),
                    float(self.sb_stops_hi.value()),
                    float(self.sb_stops_med.value()),
                )
                for k, v in metrics.items():
                    if not str(k).startswith("_"):
                        df.at[i, k] = v

            # final dtype guarantees
            df["Severity (0-5)"] = pd.to_numeric(df["Severity (0-5)"], errors="coerce").fillna(0.0)
            df["Expected Stops /100"] = pd.to_numeric(df["Expected Stops /100"], errors="coerce").fillna(0.0)
            df["Implementation Priority"] = df["Implementation Priority"].astype(str)

            self.df = df
            self.model.set_dataframe(self.df)
            self.status.showMessage(f"Loaded {path}", 4000)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open CSV:\n{e}")

    def save_csv(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save CSV", "fault_priorities.csv", "CSV Files (*.csv)")
        if not path:
            return
        try:
            self.df.to_csv(path, index=False)
            self.status.showMessage(f"Saved to {path}", 4000)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save CSV:\n{e}")

    def save_xlsx(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Save Excel", "fault_priorities.xlsx",
            "Excel Files (*.xlsx)"
        )
        if not path:
            return
        try:
            with pd.ExcelWriter(path, engine="xlsxwriter") as writer:
                self.df.to_excel(writer, index=False, sheet_name="Fault Priorities")
            self.status.showMessage(f"Saved to {path}", 4000)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save Excel:\n{e}")

    def add_row(self):
        new_row = {
            "Fault ID": f"F{len(self.df)+1:03d}",
            "Description": "",
            "System": "",
            "Probability": "Medium",
            "Mission Impact": "Medium",
            "Recovery": "Manual intervention",
            "Detectability": "Medium",
            "Safety Critical": False,
            "Time To Recover (s)": 0.0,
            "Occurrences /100 missions": 0.0,
            "Operational Requirement": "",
            "Technical Safety Requirement": "",
            "Functional Modification": "",
            "Severity (0-5)": 0.0,
            "Expected Stops /100": 0.0,
            "Implementation Priority": "Low",
        }
        self.df.loc[len(self.df)] = new_row
        self.recompute_row(len(self.df) - 1)
        self.model.layoutChanged.emit()
        self.table.scrollToBottom()

    def delete_selected(self):
        sel = self.table.selectionModel().selectedRows()
        if not sel:
            return
        rows = sorted([idx.row() for idx in sel], reverse=True)
        for r in rows:
            self.df = self.df.drop(self.df.index[r]).reset_index(drop=True)
        self.model.set_dataframe(self.df)
        self.status.showMessage(f"Deleted {len(rows)} row(s).", 4000)

    def on_table_double_clicked(self, index: QModelIndex):
        """Open an editor for the clicked cell or show requirement selection."""
        if not index.isValid():
            return
        col_name = self.df.columns[index.column()]
        req_map = {
            "Operational Requirement": "operational",
            "Technical Safety Requirement": "technical safety",
            "Functional Modification": "functional modification",
        }
        if col_name in req_map:
            options = requirement_ids(req_map[col_name])
            current = [
                v for v in str(self.df.iat[index.row(), index.column()]).split(";") if v
            ]
            dlg = MultiSelectDialog(options, current, title=col_name, parent=self)
            if dlg.exec():
                new_val = ";".join(dlg.selected_items())
                self.model.setData(index, new_val, Qt.ItemDataRole.EditRole)
            return
        self.table.edit(index)

    def on_thresholds_changed(self, _value: float):
        for i in range(len(self.df)):
            self.recompute_row(i)
        self.model.layoutChanged.emit()
        self.status.showMessage("Recomputed with new thresholds.", 3000)

    # ---------- Helpers ----------

    def show_formulas_dialog(self):
        html = f"""
        <h3>Formulas & Logic</h3>
        <h4>Severity (0–5)</h4>
        <pre>
Raw = {W_IMPACT}·ImpactScore + {W_PROB}·ProbabilityScore + {W_RECOV}·RecoveryScore + {W_DETECT}·DetectabilityScore
      {"+ " + str(W_SAFETY) + " (if Safety Critical)" if W_SAFETY else ""}
MaxRaw = {W_IMPACT}·4 + {W_PROB}·3 + {W_RECOV}·3 + {W_DETECT}·2 + {W_SAFETY}
Severity = 5 · Raw / MaxRaw   (clipped to [0, 5])
        </pre>

        <h4>Expected Stops /100</h4>
        <pre>
ImpactMultiplier  = ImpactScore / 4    (None=0.00, Low=0.25, Medium=0.50, High=0.75, Critical=1.00)
RecoveryMultiplier = {{
    Auto-resolvable: 0.05,
    Manual intervention: 0.25,
    Restart required: 0.60,
    Not recoverable: 1.00
}}[Recovery]

TTR_penalty = 1 + min(2, TTR_seconds / 300)

ExpectedStopsPer100 = OccurrencesPer100 · ImpactMultiplier · RecoveryMultiplier · TTR_penalty
        </pre>

        <h4>Priority Rules (applied in order)</h4>
        <ol>
          <li><b>Safety shortcut:</b> If Safety Critical = True and Impact ∈ {High, Critical} → <b>High</b>.</li>
          <li>Else if Severity ≥ <b>Severity High</b> OR Expected Stops /100 ≥ <b>Stops High</b> → <b>High</b>.</li>
          <li>Else if Severity ≥ <b>Severity Med</b> OR Expected Stops /100 ≥ <b>Stops Med</b> → <b>Medium</b>.</li>
          <li>Else → <b>Low</b>.</li>
        </ol>

        <h4>Thresholds (top toolbar)</h4>
        <ul>
          <li><b>Severity High ≥</b> — sets High by severity risk.</li>
          <li><b>Severity Med ≥</b> — sets Medium by severity risk.</li>
          <li><b>Stops High ≥</b> — sets High by KPI impact (expected stops).</li>
          <li><b>Stops Med ≥</b> — sets Medium by KPI impact.</li>
        </ul>
        """
        msg = QMessageBox(self)
        msg.setWindowTitle("Formulas & Logic")
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setTextFormat(Qt.TextFormat.RichText)
        msg.setText(html)
        msg.exec()

    def confirm_discard(self) -> bool:
        resp = QMessageBox.question(
            self,
            "Discard current table?",
            "This will discard unsaved changes. Continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        return resp == QMessageBox.StandardButton.Yes

    @staticmethod
    def default_df() -> pd.DataFrame:
        df = pd.DataFrame([
            {
                "Fault ID": "F001",
                "Description": "LIDAR frame drop / data loss",
                "System": "Perception",
                "Probability": "Medium",
                "Mission Impact": "High",
                "Recovery": "Restart required",
                "Detectability": "High",
                "Safety Critical": True,
                "Time To Recover (s)": 90,
                "Occurrences /100 missions": 0.8,
                "Operational Requirement": "",
                "Technical Safety Requirement": "",
                "Functional Modification": "",
            },
            {
                "Fault ID": "F002",
                "Description": "CAN bus timeout",
                "System": "Control",
                "Probability": "Low",
                "Mission Impact": "Critical",
                "Recovery": "Not recoverable",
                "Detectability": "Medium",
                "Safety Critical": True,
                "Time To Recover (s)": 600,
                "Occurrences /100 missions": 0.2,
                "Operational Requirement": "",
                "Technical Safety Requirement": "",
                "Functional Modification": "",
            },
            {
                "Fault ID": "F003",
                "Description": "Low battery alert",
                "System": "Powertrain",
                "Probability": "High",
                "Mission Impact": "Medium",
                "Recovery": "Manual intervention",
                "Detectability": "High",
                "Safety Critical": False,
                "Time To Recover (s)": 300,
                "Occurrences /100 missions": 3.0,
                "Operational Requirement": "",
                "Technical Safety Requirement": "",
                "Functional Modification": "",
            },
            {
                "Fault ID": "F004",
                "Description": "Door sensor stuck",
                "System": "Body/Cabin",
                "Probability": "Medium",
                "Mission Impact": "Low",
                "Recovery": "Auto-resolvable",
                "Detectability": "High",
                "Safety Critical": False,
                "Time To Recover (s)": 5,
                "Occurrences /100 missions": 1.2,
                "Operational Requirement": "",
                "Technical Safety Requirement": "",
                "Functional Modification": "",
            },
        ], columns=INPUT_COLUMNS)

        # Enforce numeric dtypes
        df["Time To Recover (s)"] = pd.to_numeric(df["Time To Recover (s)"], errors="coerce").fillna(0.0)
        df["Occurrences /100 missions"] = pd.to_numeric(df["Occurrences /100 missions"], errors="coerce").fillna(0.0)

        # Initialize output columns
        for col in OUTPUT_COLUMNS:
            df[col] = pd.NA

        # Compute initial metrics
        for i in range(len(df)):
            row = df.iloc[i].to_dict()
            metrics = compute_metrics(row, SEVERITY_HI_TH, SEVERITY_MED_TH, STOPS_HI, STOPS_MED)
            for k, v in metrics.items():
                if not str(k).startswith("_"):
                    df.at[i, k] = v

        # Cast outputs to correct dtypes
        df["Severity (0-5)"] = pd.to_numeric(df["Severity (0-5)"], errors="coerce").fillna(0.0)
        df["Expected Stops /100"] = pd.to_numeric(df["Expected Stops /100"], errors="coerce").fillna(0.0)
        df["Implementation Priority"] = df["Implementation Priority"].astype(str)

        return df


def apply_fusion_palette(light=True):
    app = QApplication.instance()
    app.setStyle("Fusion")
    palette = QPalette()
    if light:
        palette.setColor(QPalette.ColorRole.Window, QColor(245, 245, 245))
        palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.black)
        palette.setColor(QPalette.ColorRole.Base, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(235, 235, 235))
        palette.setColor(QPalette.ColorRole.ToolTipBase, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.black)
        palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.black)
        palette.setColor(QPalette.ColorRole.Button, QColor(240, 240, 240))
        palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.black)
        palette.setColor(QPalette.ColorRole.Highlight, QColor(0, 120, 215))
        palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.white)
    else:
        palette.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
        palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.Base, QColor(35, 35, 35))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))
        palette.setColor(QPalette.ColorRole.ToolTipBase, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
        palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
        palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.black)
    app.setPalette(palette)


def main():
    app = QApplication(sys.argv)
    apply_fusion_palette(light=True)

    win = FaultsWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
