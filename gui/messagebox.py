"""Replacement for :mod:`tkinter.messagebox` that also logs messages.

Informational messages are logged but do not display pop-up dialogs.  Only
message boxes that require user input (e.g. ``askyesno``) invoke the underlying
Tk widgets.  This keeps the GUI from interrupting the user with dialogs that
simply provide information while still allowing interactive prompts when a
decision is needed.
"""

from tkinter import TclError
import tkinter.messagebox as tk_messagebox

from . import logger


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


def askyesno(title=None, message=None, **options):
    logger.log_message(f"{title}: {message}", "ASK")
    logger.show_temporarily()
    try:
        return tk_messagebox.askyesno(title, message, **options)
    except (TclError, RuntimeError):
        return False


def askyesnocancel(title=None, message=None, **options):
    logger.log_message(f"{title}: {message}", "ASK")
    logger.show_temporarily()
    try:
        return tk_messagebox.askyesnocancel(title, message, **options)
    except (TclError, RuntimeError):
        return None


def askokcancel(title=None, message=None, **options):
    logger.log_message(f"{title}: {message}", "ASK")
    logger.show_temporarily()
    try:
        return tk_messagebox.askokcancel(title, message, **options)
    except (TclError, RuntimeError):
        return False
