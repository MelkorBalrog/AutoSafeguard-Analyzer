from pathlib import Path


from config import load_diagram_rules


def test_governance_relations_grouped_without_duplicates():
    rules = load_diagram_rules(Path(__file__).resolve().parents[1] / "config/diagram_rules.json")
    rels = rules.get("governance_element_relations")
    assert isinstance(rels, dict)
    all_rels: list[str] = []
    for group in rels.values():
        all_rels.extend(group)
    # ensure relations are unique and no AI-specific duplicates like "Curation"
    assert len(all_rels) == len(set(all_rels))
    assert "Curation" not in all_rels

