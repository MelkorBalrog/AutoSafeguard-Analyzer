"""Replacement for tkinter.messagebox that logs messages to the GUI log window."""
import tkinter.messagebox as tk_messagebox
from . import logger


def showinfo(title=None, message=None, **options):
    logger.log_message(f"{title}: {message}", "INFO")
    return "ok"


def showwarning(title=None, message=None, **options):
    logger.log_message(f"{title}: {message}", "WARNING")
    return "ok"


def showerror(title=None, message=None, **options):
    logger.log_message(f"{title}: {message}", "ERROR")
    return "ok"


def askyesno(title=None, message=None, **options):
    logger.log_message(f"{title}: {message}", "ASK")
    return tk_messagebox.askyesno(title, message, **options)


def askyesnocancel(title=None, message=None, **options):
    logger.log_message(f"{title}: {message}", "ASK")
    return tk_messagebox.askyesnocancel(title, message, **options)


def askokcancel(title=None, message=None, **options):
    logger.log_message(f"{title}: {message}", "ASK")
    return tk_messagebox.askokcancel(title, message, **options)
