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

"""Replacement for :mod:`tkinter.messagebox` that also logs messages.

Informational messages are logged but do not display pop-up dialogs.  Only
message boxes that require user input (e.g. ``askyesno``) invoke the underlying
Tk widgets.  This keeps the GUI from interrupting the user with dialogs that
simply provide information while still allowing interactive prompts when a
decision is needed.
"""

from tkinter import TclError
import tkinter as tk
from tkinter import ttk

from gui.utils import logger, DIALOG_BG_COLOR


def _log_and_return(title: str | None, message: str | None, level: str) -> str:
    """Log a message and return ``"ok"`` without showing a dialog.

    Parameters
    ----------
    title:
        The dialog title that would have been shown.
    message:
        The dialog message that would have been shown.
    level:
        Log level to associate with the message.
    """

    logger.log_message(f"{title}: {message}", level)
    logger.show_temporarily()
    return "ok"


def showinfo(title=None, message=None, **options):
    return _log_and_return(title, message, "INFO")


def showwarning(title=None, message=None, **options):
    return _log_and_return(title, message, "WARNING")


def showerror(title=None, message=None, **options):
    return _log_and_return(title, message, "ERROR")


def _create_dialog(
    title: str | None,
    message: str | None,
    buttons: list[tuple[str, object]],
) -> object:
    """Create a simple ``ttk`` dialog returning the associated button value."""

    from .. import PurpleButton  # Local import to avoid circular dependency

    root = tk._default_root
    temp_root = False
    if root is None:
        root = tk.Tk()
        root.withdraw()
        temp_root = True

    dialog = tk.Toplevel(root)
    try:
        dialog.configure(bg=DIALOG_BG_COLOR)
    except Exception:
        pass
    dialog.title(title or "")
    dialog.resizable(False, False)
    dialog.transient(root)
    dialog.grab_set()

    # Ensure dialog appears above all other windows and is centered on screen
    dialog.attributes("-topmost", True)
    dialog.update_idletasks()
    width, height = 300, 150
    x = int(dialog.winfo_screenwidth() / 2 - width / 2)
    y = int(dialog.winfo_screenheight() / 2 - height / 2)
    dialog.geometry(f"{width}x{height}+{x}+{y}")
    dialog.lift()

    frame = ttk.Frame(dialog, padding=10)
    frame.pack(fill="both", expand=True)
    ttk.Label(frame, text=message or "").pack(pady=(0, 10))

    result: object = None

    def _set(value: object) -> None:
        nonlocal result
        result = value
        dialog.destroy()

    for text, value in buttons:
        PurpleButton(frame, text=text, command=lambda v=value: _set(v)).pack(
            side="left", padx=5
        )

    dialog.protocol("WM_DELETE_WINDOW", lambda: _set(None))
    dialog.wait_window()
    if temp_root:
        root.destroy()
    return result


def askyesno(title=None, message=None, **options):
    logger.log_message(f"{title}: {message}", "ASK")
    logger.show_temporarily()
    try:
        return bool(_create_dialog(title, message, [("Yes", True), ("No", False)]))
    except (TclError, RuntimeError):
        return False


def askyesnocancel(title=None, message=None, **options):
    logger.log_message(f"{title}: {message}", "ASK")
    logger.show_temporarily()
    try:
        return _create_dialog(
            title, message, [("Yes", True), ("No", False), ("Cancel", None)]
        )
    except (TclError, RuntimeError):
        return None


def askokcancel(title=None, message=None, **options):
    logger.log_message(f"{title}: {message}", "ASK")
    logger.show_temporarily()
    try:
        return bool(_create_dialog(title, message, [("OK", True), ("Cancel", False)]))
    except (TclError, RuntimeError):
        return False
