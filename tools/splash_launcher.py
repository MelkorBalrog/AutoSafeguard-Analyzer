from __future__ import annotations

"""Utility for displaying the splash screen while loading the main app."""

import importlib
import threading
import tkinter as tk
from typing import Optional

from config.automl_constants import AUTHOR, AUTHOR_EMAIL, AUTHOR_LINKEDIN
from gui.splash_screen import SplashScreen
from mainappsrc.version import VERSION


class SplashLauncher:
    """Show the splash screen until the application is ready."""

    def __init__(self, module_name: str = "AutoML") -> None:
        self.module_name = module_name
        self._module: Optional[object] = None

    def _load_module(self) -> None:
        """Import the target module in a background thread."""
        self._module = importlib.import_module(self.module_name)
        # Once loading is complete, close the splash screen on the main thread
        self._root.after(0, self._root.destroy)

    def launch(self) -> None:
        """Display the splash screen and run the application's main function."""
        self._root = tk.Tk()
        self._root.withdraw()
        SplashScreen(
            self._root,
            version=VERSION,
            author=AUTHOR,
            email=AUTHOR_EMAIL,
            linkedin=AUTHOR_LINKEDIN,
            duration=0,
        )
        threading.Thread(target=self._load_module, daemon=True).start()
        self._root.mainloop()
        if self._module:
            self._module.main()
