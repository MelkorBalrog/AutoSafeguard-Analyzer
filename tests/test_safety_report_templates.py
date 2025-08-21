from pathlib import Path

from config import load_report_template


BASE_DIR = Path(__file__).resolve().parents[1]

def _load(name: str):
    path = BASE_DIR / "config" / name
    return load_report_template(path)


def test_item_definition_template_valid():
    data = _load("item_definition_template.json")
    titles = {sec["title"] for sec in data["sections"]}
    assert {
        "Use Case Diagrams",
        "Activity Diagrams",
        "Block Diagrams",
        "Internal Block Diagrams",
        "Product Requirements",
        "Vehicle Requirements",
        "Activity Actions",
    } <= titles


def test_functional_safety_concept_template_valid():
    data = _load("functional_safety_concept_template.json")
    titles = {sec["title"] for sec in data["sections"]}
    assert {
        "Product Goals",
        "Functional Safety Concept",
        "Internal Block Diagrams",
        "Functional Safety Requirements",
        "Requirements Allocation Matrix",
        "Traceability Matrix",
    } <= titles


def test_technical_safety_concept_template_valid():
    data = _load("technical_safety_concept_template.json")
    titles = {sec["title"] for sec in data["sections"]}
    assert {
        "Internal Block Diagrams",
        "Technical Safety Requirements",
        "Requirements Allocation Matrix",
        "Traceability to Functional Safety Concept",
    } <= titles


def test_pdf_report_template_includes_diagram_sections():
    data = _load("report_template.json")
    titles = [sec["title"] for sec in data["sections"]]
    assert {
        "Block Diagrams",
        "State Diagrams",
        "Fault Tree Analyses (FTA)",
        "Hazard Analyses",
        "FMEA Analyses",
        "FMEDA Analyses",
    } <= set(titles)
