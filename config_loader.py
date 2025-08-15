import json
import re
from pathlib import Path
from typing import Any

def load_json_with_comments(path: str | Path) -> Any:
    """Load a JSON file allowing // and /* */ comments."""
    p = Path(path)
    text = p.read_text()
    # Remove // comments
    text = re.sub(r"//.*", "", text)
    # Remove /* */ comments
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.DOTALL)
    return json.loads(text)
