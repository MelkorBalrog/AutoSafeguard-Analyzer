from pathlib import Path

from config import load_report_template
from gsn import GSNDiagram, GSNNode
from analysis.safety_case import SafetyCase


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
        "Operational Requirements",
        "Activity Actions",
    } <= titles


def test_functional_cybersecurity_concept_template_valid():
    data = _load("functional_cybersecurity_concept_template.json")
    titles = {sec["title"] for sec in data["sections"]}
    assert {
        "Product Goals",
        "Functional & Cybersecurity Concept",
        "ODD Library",
        "Scenario Library",
        "Internal Block Diagrams",
        "Fault Tree Analyses (FTA)",
        "Threat Analysis",
        "Bayesian Network Analysis",
        "STPA Analyses",
        "FI2TC Mapping",
        "TC2FI Mapping",
        "Triggering Conditions",
        "Functional Insufficiencies",
        "Functional Safety Requirements",
        "Operational Safety Requirements",
        "Cybersecurity Requirements",
        "Requirements Allocation Matrix",
        "Traceability Matrix",
    } <= titles


def test_technical_cybersecurity_concept_template_valid():
    data = _load("technical_cybersecurity_concept_template.json")
    titles = {sec["title"] for sec in data["sections"]}
    assert {
        "Internal Block Diagrams",
        "Fault Tree Analyses (FTA)",
        "FMEA Analyses",
        "FMEDA Analyses",
        "Reliability Analysis",
        "Mission Profile",
        "Functional Modifications",
        "Cybersecurity Requirements",
        "AI Safety Requirements",
        "Technical Safety Requirements",
        "Requirements Allocation Matrix",
        "Traceability to Functional & Cybersecurity Concept",
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
        "Threat Analyses",
        "FMEA Analyses",
        "FMEDA Analyses",
        "Reliability Analysis",
        "Safety & Security Report",
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


def test_report_template_includes_operational_safety_and_decommissioning_sections():
    data = _load("report_template.json")
    titles = {sec["title"] for sec in data["sections"]}
    assert {"Operational Safety Requirements", "Decommissioning Requirements"} <= titles

    
def test_safety_security_report_template_valid():
    data = _load("safety_security_report_template.json")
    titles = {sec["title"] for sec in data["sections"]}
    assert {
        "GSR Argumentation",
        "Related Safety & Security Reports",
        "SPI Table",
        "Work Products and Evidence",
    } <= titles

def test_report_template_includes_trigger_and_insufficiency_sections():
    data = _load("report_template.json")
    titles = {sec["title"] for sec in data["sections"]}
    assert {
        "Triggering Conditions",
        "Functional Insufficiencies",
        "Functional Modifications",
    } <= titles


def test_production_service_decommissioning_template_valid():
    data = _load("production_service_decommissioning_template.json")
    titles = {sec["title"] for sec in data["sections"]}
    assert {
        "Production Requirements",
        "Service Requirements",
        "Decommissioning Requirements",
    } <= titles


def test_field_monitoring_template_valid():
    data = _load("field_monitoring_template.json")
    titles = {sec["title"] for sec in data["sections"]}
    assert {"Field Monitoring Requirements"} <= titles


def test_safety_security_management_template_valid():
    data = _load("safety_security_management_template.json")
    titles = {sec["title"] for sec in data["sections"]}
    assert {
        "Governance Diagrams",
        "GSN Diagrams",
        "Organizational Requirements",
        "Legal Requirements",
    } <= titles

def test_safety_case_dynamic_sections():
    root = GSNNode("G", "Goal")
    diag = GSNDiagram(root)
    s1 = GSNNode("S1", "Solution")
    s1.work_product = "FTA report"
    s2 = GSNNode("S2", "Solution")
    s2.work_product = "FMEA"
    diag.nodes.extend([s1, s2])
    case = SafetyCase("C", diag)
    case.collect_solutions()
    tpl = case.build_report_template()
    titles = {sec["title"] for sec in tpl["sections"]}
    assert "Fault Tree Analyses (FTA)" in titles
    assert "FMEA Analyses" in titles
    assert "FMEDA Analyses" not in titles
