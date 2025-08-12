from analysis.models import DamageScenario, ThreatScenario, AttackPath, ThreatDoc


def test_threat_doc_creation_and_editing():
    doc = ThreatDoc("Doc1", [])
    ds = DamageScenario("Engine", "Start", "Confidentiality", "data leak")
    doc.damages.append(ds)
    ts = ThreatScenario("Spoofing", "fake command")
    ds.threats.append(ts)
    ap = AttackPath(["gain access"])
    ts.attack_paths.append(ap)

    # Edit values
    ds.category = "Integrity"
    ts.description = "alter command"
    ap.steps.append("impact system")

    assert doc.damages[0].category == "Integrity"
    assert doc.damages[0].threats[0].description == "alter command"
    assert doc.damages[0].threats[0].attack_paths[0].steps[-1] == "impact system"
