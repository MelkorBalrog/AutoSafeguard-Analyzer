"""Replacement for :mod:`tkinter.messagebox` that also logs messages.

The original implementation only logged messages to the GUI log window and
returned ``"ok"`` without displaying the actual message boxes.  As a result,
users would not see the pop-up dialogs they expected.  This module now invokes
the real Tk message box functions while still logging the messages.  If the
environment does not support a Tk display (e.g. during automated tests), the
underlying Tk calls are safely skipped to avoid errors.
"""

from tkinter import TclError
import tkinter.messagebox as tk_messagebox

from . import logger


def showinfo(title=None, message=None, **options):
    logger.log_message(f"{title}: {message}", "INFO")
    logger.show_temporarily()
    try:
        return tk_messagebox.showinfo(title, message, **options)
    except (TclError, RuntimeError):
        return "ok"


def showwarning(title=None, message=None, **options):
    logger.log_message(f"{title}: {message}", "WARNING")
    logger.show_temporarily()
    try:
        return tk_messagebox.showwarning(title, message, **options)
    except (TclError, RuntimeError):
        return "ok"


def showerror(title=None, message=None, **options):
    logger.log_message(f"{title}: {message}", "ERROR")
    logger.show_temporarily()
    try:
        return tk_messagebox.showerror(title, message, **options)
    except (TclError, RuntimeError):
        return "ok"


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
