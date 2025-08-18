import sys
from pathlib import Path
import pytest

sys.path.append(str(Path(__file__).resolve().parents[1]))


def test_governance_elements_toolbox_excludes_select():
    arch_path = Path(__file__).resolve().parents[1] / "gui" / "architecture.py"
    text = arch_path.read_text()
    marker = "# Create toolbox for additional governance elements grouped by class"
    if marker not in text:
        pytest.skip("Governance elements toolbox markers not found")
    text = text.split(marker, 1)[1]
    text = text.split("# Repack toolbox to include selector", 1)[0]
    assert 'text="Select"' not in text

