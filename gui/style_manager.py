import os
import sys
from pathlib import Path
import xml.etree.ElementTree as ET

# Allow overriding the default style (e.g. dark mode) via env var
_STYLE_NAME = os.environ.get("AUTOML_STYLE", "pastel")
_DEFAULT_STYLE = Path(__file__).resolve().parent.parent / 'styles' / f"{_STYLE_NAME}.xml"
if getattr(sys, 'frozen', False):
    # When packaged by PyInstaller resources live under sys._MEIPASS
    _DEFAULT_STYLE = Path(sys._MEIPASS) / 'styles' / f"{_STYLE_NAME}.xml"

class StyleManager:
    """Singleton manager for diagram styles loaded from XML files."""

    _instance = None

    def __init__(self):
        self.styles = {}
        self.background = '#FFFFFF'
        self.outline = '#000000'
        try:
            self.load_style(_DEFAULT_STYLE)
        except Exception:
            # fallback to hard coded white style
            self.styles = {}
            self.background = '#FFFFFF'
            self.outline = '#000000'

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
        bg = root.find('background')
        if bg is not None and bg.get('color'):
            self.background = bg.get('color')
        else:
            self.background = '#FFFFFF'
        ol = root.find('outline')
        if ol is not None and ol.get('color'):
            self.outline = ol.get('color')
        else:
            self.outline = '#000000'
        for obj in root.findall('object'):
            typ = obj.get('type')
            color = obj.get('color')
            if typ and color:
                self.styles[typ] = color

    def save_style(self, path: str) -> None:
        root = ET.Element('style')
        ET.SubElement(root, 'background', color=self.background)
        ET.SubElement(root, 'outline', color=self.outline)
        for typ, color in self.styles.items():
            ET.SubElement(root, 'object', type=typ, color=color)
        tree = ET.ElementTree(root)
        tree.write(path)

    def get_color(self, obj_type: str) -> str:
        return self.styles.get(obj_type, '#FFFFFF')

    def get_outline(self) -> str:
        """Return the default outline color for shapes."""
        return self.outline
