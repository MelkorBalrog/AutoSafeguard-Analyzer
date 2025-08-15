import os
import sys
from pathlib import Path
import xml.etree.ElementTree as ET

_DEFAULT_STYLE = Path(__file__).resolve().parent.parent / 'styles' / 'pastel.xml'
if getattr(sys, 'frozen', False):
    # When packaged by PyInstaller resources live under sys._MEIPASS
    _DEFAULT_STYLE = Path(sys._MEIPASS) / 'styles' / 'pastel.xml'

class StyleManager:
    """Singleton manager for diagram styles loaded from XML files."""

    _instance = None

    def __init__(self):
        self.styles = {}
        self.canvas_bg = "#FFFFFF"
        # Default outline color follows canvas background.  For light
        # backgrounds we use black outlines, while a dark canvas uses
        # white outlines for visibility.
        self.outline_color = "black"
        try:
            self.load_style(_DEFAULT_STYLE)
        except Exception:
            # fallback to hard coded white style
            self.styles = {}
            self.canvas_bg = "#FFFFFF"
            self.outline_color = "black"

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = StyleManager()
        return cls._instance

    def load_style(self, path) -> None:
        """Load style definitions from *path* if it exists."""
        path = Path(path)
        if not path.is_file():
            return
        tree = ET.parse(path)
        root = tree.getroot()
        self.styles.clear()
        self.canvas_bg = "#FFFFFF"
        self.outline_color = "black"
        canvas = root.find('canvas')
        if canvas is not None:
            self.canvas_bg = canvas.get('color', "#FFFFFF")
        # Determine default outline color based on canvas brightness.
        self.outline_color = "#FFFFFF" if self._is_dark(self.canvas_bg) else "black"
        for obj in root.findall('object'):
            typ = obj.get('type')
            color = obj.get('color')
            if typ and color:
                self.styles[typ] = color

    def save_style(self, path: str) -> None:
        root = ET.Element('style')
        ET.SubElement(root, 'canvas', color=self.canvas_bg)
        for typ, color in self.styles.items():
            ET.SubElement(root, 'object', type=typ, color=color)
        tree = ET.ElementTree(root)
        tree.write(path)

    def get_color(self, obj_type: str) -> str:
        return self.styles.get(obj_type, '#FFFFFF')

    def get_canvas_color(self) -> str:
        return self.canvas_bg

    def get_outline_color(self) -> str:
        """Return the default outline color for shapes."""
        return self.outline_color

    @staticmethod
    def _is_dark(color: str) -> bool:
        """Return True if *color* is perceptually dark.

        The check converts the hex color to RGB and computes the luminance
        using the Rec. 601 luma formula.  Colors with luminance below 128 are
        treated as dark backgrounds.
        """
        if not isinstance(color, str) or not color.startswith("#") or len(color) != 7:
            return False
        try:
            r = int(color[1:3], 16)
            g = int(color[3:5], 16)
            b = int(color[5:7], 16)
        except ValueError:
            return False
        luminance = 0.299 * r + 0.587 * g + 0.114 * b
        return luminance < 128
