import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

def test_safety_ai_toolbox_excludes_select():
    arch_path = Path(__file__).resolve().parents[1] / "gui" / "architecture.py"
    content = arch_path.read_text().split("# Create Safety & AI Lifecycle toolbox frame", 1)[1]
    section = content.split("# Create toolbox for additional governance elements", 1)[0]
    assert 'text="Select"' not in section
