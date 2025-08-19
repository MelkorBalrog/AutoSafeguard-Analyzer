import sys
import json
import types
from pathlib import Path

# Stub required third-party modules before importing application modules
PIL_stub = types.ModuleType("PIL")
PIL_stub.Image = types.SimpleNamespace(new=lambda *a, **k: None)
PIL_stub.ImageDraw = types.SimpleNamespace(Draw=lambda *a, **k: types.SimpleNamespace(rectangle=lambda *a, **k: None, text=lambda *a, **k: None))
PIL_stub.ImageTk = types.SimpleNamespace()
PIL_stub.ImageFont = types.SimpleNamespace()
sys.modules.setdefault("PIL", PIL_stub)
sys.modules.setdefault("PIL.Image", PIL_stub.Image)
sys.modules.setdefault("PIL.ImageDraw", PIL_stub.ImageDraw)
sys.modules.setdefault("PIL.ImageTk", PIL_stub.ImageTk)
sys.modules.setdefault("PIL.ImageFont", PIL_stub.ImageFont)

reportlab = types.ModuleType("reportlab")
reportlab.lib = types.SimpleNamespace()
reportlab.lib.pagesizes = types.SimpleNamespace(letter=(0, 0), landscape=lambda x: x)
reportlab.lib.units = types.SimpleNamespace(inch=1)
reportlab.lib.styles = types.SimpleNamespace(
    getSampleStyleSheet=lambda: {"Title": "", "Heading2": "", "Normal": ""},
    ParagraphStyle=lambda name, **k: None,
)
reportlab.lib.colors = types.SimpleNamespace(lightblue=0, lightgrey=0, grey=0)

class DummyDoc:
    def __init__(self, *a, **k):
        pass

    def build(self, story):
        pass

class DummyTable:
    def __init__(self, *a, **k):
        pass

    def setStyle(self, *a, **k):
        pass

class DummyTableStyle:
    def __init__(self, *a, **k):
        pass

reportlab.platypus = types.SimpleNamespace(
    Paragraph=lambda text, style=None: text,
    Spacer=lambda w, h: None,
    SimpleDocTemplate=DummyDoc,
    Image=lambda buf: None,
    Table=DummyTable,
    TableStyle=DummyTableStyle,
    PageBreak=lambda: None,
)
sys.modules.setdefault("reportlab", reportlab)
sys.modules.setdefault("reportlab.lib", reportlab.lib)
sys.modules.setdefault("reportlab.lib.pagesizes", reportlab.lib.pagesizes)
sys.modules.setdefault("reportlab.lib.units", reportlab.lib.units)
sys.modules.setdefault("reportlab.lib.styles", reportlab.lib.styles)
sys.modules.setdefault("reportlab.lib.colors", reportlab.lib.colors)
sys.modules.setdefault("reportlab.platypus", reportlab.platypus)

from AutoML import AutoMLApp, filedialog, messagebox


def test_generate_pdf_report_exports_template(tmp_path, monkeypatch):
    pdf_path = tmp_path / "out.pdf"
    template_path = tmp_path / "template.json"
    template_path.write_text(json.dumps({"elements": {}, "sections": []}))

    monkeypatch.setattr(filedialog, "asksaveasfilename", lambda **k: str(pdf_path))
    monkeypatch.setattr(filedialog, "askopenfilename", lambda **k: str(template_path))
    monkeypatch.setattr(messagebox, "showinfo", lambda *a, **k: None)
    monkeypatch.setattr(messagebox, "showerror", lambda *a, **k: None)

    app = type("A", (), {"project_properties": {}, "_generate_pdf_report": AutoMLApp._generate_pdf_report})()
    app._generate_pdf_report()

    assert pdf_path.with_suffix(".json").exists()
