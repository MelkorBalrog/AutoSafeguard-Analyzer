import sys
from pathlib import Path
import pytest

sys.path.append(str(Path(__file__).resolve().parents[1]))


def test_safety_ai_toolbox_excludes_select():
    arch_path = Path(__file__).resolve().parents[1] / "gui" / "architecture.py"
    text = arch_path.read_text()
    marker = "# Create Safety & AI Lifecycle toolbox frame"
    if marker not in text:
        pytest.skip("Safety & AI toolbox markers not found")
    text = text.split(marker, 1)[1]
    text = text.split("# Create toolbox for additional governance elements", 1)[0]
    assert 'text="Select"' not in text
