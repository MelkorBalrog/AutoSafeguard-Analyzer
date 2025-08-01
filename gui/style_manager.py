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
        try:
            self.load_style(_DEFAULT_STYLE)
        except Exception:
            # fallback to hard coded white style
            self.styles = {}

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
        for obj in root.findall('object'):
            typ = obj.get('type')
            color = obj.get('color')
            if typ and color:
                self.styles[typ] = color

    def save_style(self, path: str) -> None:
        root = ET.Element('style')
        for typ, color in self.styles.items():
            ET.SubElement(root, 'object', type=typ, color=color)
        tree = ET.ElementTree(root)
        tree.write(path)

    def get_color(self, obj_type: str) -> str:
        return self.styles.get(obj_type, '#FFFFFF')
