import os
import xml.etree.ElementTree as ET

_DEFAULT_STYLE = os.path.join(os.path.dirname(__file__), '..', 'styles', 'modern.xml')

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

    def load_style(self, path: str) -> None:
        if not os.path.isfile(path):
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
