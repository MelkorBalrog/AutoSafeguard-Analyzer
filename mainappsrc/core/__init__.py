#!/usr/bin/env python3
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

"""Core package initialisation and application entry point."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
import tkinter as tk

from gui.controls.button_utils import enable_listbox_hover_highlight
from gui.dialogs.user_select_dialog import UserSelectDialog
from gui.dialogs.user_info_dialog import UserInfoDialog
from analysis.user_config import (
    load_all_users,
    load_user_config,
    save_user_config,
    set_last_user,
    set_current_user,
)
from analysis.risk_assessment import AutoMLHelper

from . import automl_core, config_utils
from .automl_core import AutoMLApp

__all__ = ["AutoMLApp", "load_user_data", "main"]


def load_user_data() -> tuple[dict, tuple[str, str]]:
    """Load cached users and last user config concurrently."""
    with ThreadPoolExecutor() as executor:
        users_future = executor.submit(load_all_users)
        config_future = executor.submit(load_user_config)
        return users_future.result(), config_future.result()


def main() -> None:
    """Launch the main AutoML application window."""
    root = tk.Tk()
    root.minsize(1200, 700)
    enable_listbox_hover_highlight(root)
    root.withdraw()
    users, (last_name, last_email) = load_user_data()
    if users:
        dlg = UserSelectDialog(root, users, last_name)
        if dlg.result:
            name, email = dlg.result
            if name == "New User...":
                info = UserInfoDialog(root, "", "").result
                if info:
                    name, email = info
                    save_user_config(name, email)
            else:
                email = users.get(name, email)
                set_last_user(name)
    else:
        dlg = UserInfoDialog(root, last_name, last_email)
        if dlg.result:
            name, email = dlg.result
            save_user_config(name, email)
    set_current_user(name, email)

    automl_core.AutoML_Helper = config_utils.AutoML_Helper = AutoMLHelper()

    root.deiconify()
    try:
        root.state("zoomed")
    except tk.TclError:
        try:
            root.attributes("-zoomed", True)
        except tk.TclError:
            pass

    AutoMLApp(root)
    root.mainloop()


if __name__ == "__main__":  # pragma: no cover
    main()
