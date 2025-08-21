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
        "Item Description",
        "Assumptions",
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
        "ODD Library",
        "Scenario Library",
        "Internal Block Diagrams",
        "Fault Tree Analyses (FTA)",
        "Functional Safety Requirements",
        "Requirements Allocation Matrix",
        "Traceability Matrix",
    } <= titles


def test_technical_safety_concept_template_valid():
    data = _load("technical_safety_concept_template.json")
    titles = {sec["title"] for sec in data["sections"]}
    assert {
        "Internal Block Diagrams",
        "Fault Tree Analyses (FTA)",
        "FMEA Analyses",
        "FMEDA Analyses",
        "Reliability Analysis",
        "Mission Profile",
        "Technical Safety Requirements",
        "Requirements Allocation Matrix",
        "Traceability to Functional Safety Concept",
        "PMHF Results",
        "SPFM Results",
        "LPFM Results",
        "Diagnostic Coverage Results",
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
        "Reliability Analysis",
        "Safety Case",
    } <= set(titles)


def test_report_template_includes_item_definition_section():
    data = _load("report_template.json")
    assert {"item_description", "assumptions"} <= set(data["elements"].keys())
    section = next(sec for sec in data["sections"] if sec["title"] == "Item Definition")
    assert "<item_description>" in section["content"]
    assert "<assumptions>" in section["content"]


def test_report_template_includes_odd_and_scenario_sections():
    data = _load("report_template.json")
    titles = {sec["title"] for sec in data["sections"]}
    assert {"ODD Library", "Scenario Library"} <= titles


def test_safety_case_template_valid():
    data = _load("safety_case_template.json")
    titles = {sec["title"] for sec in data["sections"]}
    assert {
        "GSR Argumentation",
        "Related Safety Cases",
        "Fault Tree Analyses (FTA)",
        "FMEA Analyses",
        "FMEDA Analyses",
        "Reliability Analyses",
        "Work Products and Evidence",
    } <= titles
