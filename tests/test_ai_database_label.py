import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

def test_ai_database_and_cylinder_icons():
    arch_path = Path(__file__).resolve().parents[1] / "gui" / "architecture.py"
    content = arch_path.read_text()
    assert '"Data": self._create_icon("cylinder"' in content
    assert '"Field Data": self._create_icon("cylinder"' in content
    assert '"AI Database" if name == "Database" else name' in content
