from pathlib import Path

from config import load_report_template


BASE_DIR = Path(__file__).resolve().parents[1]

def _load(name: str):
    path = BASE_DIR / "config" / name
    return load_report_template(path)


def test_item_definition_template_valid():
    data = _load("item_definition_template.json")
    assert "sections" in data and data["sections"]


def test_functional_safety_concept_template_valid():
    data = _load("functional_safety_concept_template.json")
    assert any(sec["title"] == "Safety Goals" for sec in data["sections"])


def test_technical_safety_concept_template_valid():
    data = _load("technical_safety_concept_template.json")
    assert any("Technical Safety Requirements" in sec["title"] for sec in data["sections"])


def test_pdf_report_template_includes_diagram_sections():
    data = _load("report_template.json")
    titles = [sec["title"] for sec in data["sections"]]
    assert {"Block Diagrams", "State Diagrams", "Fault Tree Analyses", "Hazard Analyses"} <= set(titles)
