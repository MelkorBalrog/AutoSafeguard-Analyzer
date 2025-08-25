# Author: Miguel Marina <karel.capek.robotics@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later
#
# Copyright (C) 2025 Capek System Safety & Robotic Solutions
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from __future__ import annotations

"""Project persistence utilities for AutoMLApp."""

from tkinter import filedialog, simpledialog
from gui.dialogs.dialog_utils import askstring_fixed
from analysis.utils import (
    EXPOSURE_PROBABILITIES,
    CONTROLLABILITY_PROBABILITIES,
    SEVERITY_PROBABILITIES,
)
from mainappsrc.models.sysml.sysml_repository import SysMLRepository
from mainappsrc.core import config_utils


class ProjectManager:
    """Load and save AutoML projects."""

    def __init__(self, app: "AutoMLApp") -> None:
        self.app = app

    # ------------------------------------------------------------------
    def new_model(self) -> None:
        """Reset the application state and start a new model."""
        app = self.app
        mb = app.messagebox
        if app.has_unsaved_changes():
            result = mb.askyesnocancel(
                "Unsaved Changes", "Save changes before starting a new model?"
            )
            if result is None:
                return
            if result:
                self.save_model()
        if hasattr(app, "page_diagram") and app.page_diagram is not None:
            app.close_page_diagram()
        for tab_id in list(app.doc_nb.tabs()):
            app.doc_nb._closing_tab = tab_id
            app.doc_nb.event_generate("<<NotebookTabClosed>>")
            if tab_id in app.doc_nb.tabs():
                try:
                    app.doc_nb.forget(tab_id)
                except Exception:
                    pass
        app._reset_fta_state()
        import importlib
        from analysis.risk_assessment import AutoMLHelper as _AutoMLHelper

        automl_mod = importlib.import_module("AutoML")
        helper_cls = getattr(automl_mod, "AutoMLHelper", _AutoMLHelper)
        global AutoML_Helper, unique_node_id_counter
        AutoML_Helper = config_utils.AutoML_Helper = automl_mod.AutoML_Helper = helper_cls()
        unique_node_id_counter = (
            config_utils.unique_node_id_counter
        ) = automl_mod.unique_node_id_counter = 1
        SysMLRepository.reset_instance()
        app.zoom = 1.0
        app.diagram_font.config(size=int(8 * app.zoom))
        app.top_events = []
        app.cta_events = []
        app.paa_events = []
        app.root_node = None
        app.selected_node = None
        app.page_history = []
        app.project_properties = {
            "pdf_report_name": "AutoML-Analyzer PDF Report",
            "pdf_detailed_formulas": True,
            "exposure_probabilities": EXPOSURE_PROBABILITIES.copy(),
            "controllability_probabilities": CONTROLLABILITY_PROBABILITIES.copy(),
            "severity_probabilities": SEVERITY_PROBABILITIES.copy(),
        }
        app.probability_reliability.update_probability_tables(
            app.project_properties["exposure_probabilities"],
            app.project_properties["controllability_probabilities"],
            app.project_properties["severity_probabilities"],
        )
        app.apply_model_data({}, ensure_root=False)
        app._undo_stack.clear()
        app._redo_stack.clear()
        app.analysis_tree.delete(*app.analysis_tree.get_children())
        app.update_views()
        app.set_last_saved_state()
        if app.canvas:
            app.canvas.update()

    # ------------------------------------------------------------------
    def _reset_on_load(self) -> None:
        app = self.app
        if getattr(app, "page_diagram", None) is not None:
            app.close_page_diagram()
        for tab_id in list(getattr(app.doc_nb, "tabs", lambda: [])()):
            app.doc_nb._closing_tab = tab_id
            app.doc_nb.event_generate("<<NotebookTabClosed>>")
            if tab_id in getattr(app.doc_nb, "tabs", lambda: [])():
                try:
                    app.doc_nb.forget(tab_id)
                except Exception:
                    pass
        for win in (
            list(getattr(app, "use_case_windows", []))
            + list(getattr(app, "activity_windows", []))
            + list(getattr(app, "block_windows", []))
            + list(getattr(app, "ibd_windows", []))
        ):
            try:
                win.destroy()
            except Exception:
                pass
        app.use_case_windows = []
        app.activity_windows = []
        app.block_windows = []
        app.ibd_windows = []
        import importlib
        from analysis.risk_assessment import AutoMLHelper as _AutoMLHelper

        automl_mod = importlib.import_module("AutoML")
        helper_cls = getattr(automl_mod, "AutoMLHelper", _AutoMLHelper)
        global AutoML_Helper, unique_node_id_counter
        AutoML_Helper = config_utils.AutoML_Helper = automl_mod.AutoML_Helper = helper_cls()
        unique_node_id_counter = (
            config_utils.unique_node_id_counter
        ) = automl_mod.unique_node_id_counter = 1
        SysMLRepository.reset_instance()
        app.top_events = []
        app.cta_events = []
        app.paa_events = []
        app.root_node = None
        app.selected_node = None
        app.page_history = []
        app._undo_stack.clear()
        app._redo_stack.clear()
        if getattr(app, "analysis_tree", None):
            app.analysis_tree.delete(*app.analysis_tree.get_children())
        app._reset_fta_state()

    def _prompt_save_before_load(self):
        message = "You have unsaved changes. Save before loading a project?"
        return self.app.messagebox.askyesnocancel("Load Model", message)

    # ------------------------------------------------------------------
    def save_model(self) -> None:
        app = self.app
        mb = app.messagebox
        path = filedialog.asksaveasfilename(
            defaultextension=".autml",
            filetypes=[("AutoML Project", "*.autml"), ("JSON", "*.json")],
        )
        if not path:
            return
        try:
            from cryptography.fernet import Fernet  # type: ignore
        except Exception:
            import subprocess, sys
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", "cryptography"])
                from cryptography.fernet import Fernet  # type: ignore
            except Exception:
                mb.showerror(
                    "Save Model", "cryptography package is required for encrypted save."
                )
                return
        import base64, gzip, hashlib, json, os
        for fmea in app.fmeas:
            app.export_fmea_to_csv(fmea, fmea["file"])
        for fmeda in app.fmedas:
            app.export_fmeda_to_csv(fmeda, fmeda["file"])
        data = app.export_model_data()
        if path.endswith(".autml"):
            try:
                from cryptography.fernet import Fernet  # type: ignore
            except Exception:
                mb.showwarning(
                    "Save Model",
                    (
                        "cryptography package is required for encrypted save. "
                        "Saving unencrypted JSON instead."
                    ),
                )
                path = os.path.splitext(path)[0] + ".json"
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2)
            else:
                password = askstring_fixed(
                    simpledialog,
                    "Password",
                    "Enter encryption password:",
                    show="*",
                )
                if password is None:
                    return
                raw = json.dumps(data).encode("utf-8")
                compressed = gzip.compress(raw)
                key = base64.urlsafe_b64encode(hashlib.sha256(password.encode()).digest())
                token = Fernet(key).encrypt(compressed)
                with open(path, "wb") as f:
                    f.write(token)
        else:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        mb.showinfo(
            "Saved", "Model saved with all configuration and safety goal information."
        )
        app.set_last_saved_state()

    # ------------------------------------------------------------------
    def load_model(self) -> None:
        import json, re, base64, gzip, hashlib, importlib
        app = self.app
        mb = app.messagebox
        if getattr(app, "has_unsaved_changes", lambda: False)():
            resp = self._prompt_save_before_load()
            if resp is None:
                return
            if resp:
                self.save_model()
        path = filedialog.askopenfilename(
            defaultextension=".autml",
            filetypes=[("AutoML Project", "*.autml"), ("JSON", "*.json")],
        )
        if not path:
            return
        if path.endswith(".autml"):
            try:
                from cryptography.fernet import Fernet, InvalidToken  # type: ignore
            except Exception:
                import subprocess, sys
                try:
                    subprocess.check_call([sys.executable, "-m", "pip", "install", "cryptography"])
                    from cryptography.fernet import Fernet, InvalidToken  # type: ignore
                except Exception:
                    mb.showerror(
                        "Load Model", "cryptography package is required for encrypted files."
                    )
                    return
            password = askstring_fixed(
                simpledialog,
                "Password",
                "Enter decryption password:",
                show="*",
            )
            if password is None:
                return
            key = base64.urlsafe_b64encode(hashlib.sha256(password.encode()).digest())
            with open(path, "rb") as f:
                token = f.read()
            try:
                compressed = Fernet(key).decrypt(token)
            except InvalidToken:
                mb.showerror("Load Model", "Decryption failed. Check password.")
                return
            try:
                raw = gzip.decompress(compressed).decode("utf-8")
                data = json.loads(raw)
            except Exception as exc:
                mb.showerror("Load Model", f"Failed to parse model: {exc}")
                return
        else:
            with open(path, "r") as f:
                raw = f.read()
            try:
                data = json.loads(raw)
            except json.JSONDecodeError as exc:
                def clean(text: str) -> str:
                    text = re.sub(r"//.*", "", text)
                    text = re.sub(r"#.*", "", text)
                    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
                    text = re.sub(r",\s*(\]|\})", r"\1", text)
                    return text
                try:
                    data = json.loads(clean(raw))
                except json.JSONDecodeError:
                    mb.showerror("Load Model", f"Failed to parse JSON file:\n{exc}")
                    return
        self._reset_on_load()
        app.apply_model_data(data)
        app.set_last_saved_state()
        app._loaded_model_paths.append(path)
