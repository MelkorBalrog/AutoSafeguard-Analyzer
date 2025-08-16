import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))


def test_governance_elements_toolbox_excludes_select():
    arch_path = Path(__file__).resolve().parents[1] / "gui" / "architecture.py"
    text = arch_path.read_text().split(
        "# Create toolbox for additional governance elements grouped by class", 1
    )[1]
    section = text.split("# Repack toolbox to include selector", 1)[0]
    assert 'text="Select"' not in section

