"""Placeholder GUI for the Safety Management toolbox."""

from tkinter import Frame, Label

from analysis.safety_management import (
    SafetyManagementToolbox as CoreSafetyManagementToolbox,
    SafetyWorkProduct,
    LifecycleStage,
    SafetyWorkflow,
)


class SafetyManagementToolbox(Frame):
    """Minimal graphical wrapper around :class:`CoreSafetyManagementToolbox`."""

    def __init__(self, master):
        super().__init__(master)
        self.toolbox = CoreSafetyManagementToolbox()
        Label(self, text="Safety Management toolbox is under construction").pack(
            padx=10, pady=10
        )


__all__ = [
    "SafetyManagementToolbox",
    "SafetyWorkProduct",
    "LifecycleStage",
    "SafetyWorkflow",
]
