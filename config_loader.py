"""Utilities for reading JSON configuration files with comments.

The project relies on a central ``diagram_rules.json`` file that users edit by
hand.  Allowing JavaScript‐style comments makes the file approachable but the
standard :func:`json.loads` routine is very strict and rejects them.  This
module exposes :func:`load_json_with_comments` which performs lightweight
parsing to strip comments and optional trailing commas before handing the
resulting string to the JSON loader.

The implementation purposely avoids removing text inside string literals and
therefore works with URLs such as ``"http://example"``.
"""

from pathlib import Path
from typing import Any
import json
import re


def _strip_comments(text: str) -> str:
    """Return *text* with // and /* ... */ comments removed.

    The function walks the string character by character so that comment tokens
    inside quoted strings remain untouched.
    """

    result: list[str] = []
    in_str = False
    escape = False
    i = 0
    while i < len(text):
        ch = text[i]
        if escape:
            result.append(ch)
            escape = False
            i += 1
            continue
        if ch == "\\":
            result.append(ch)
            escape = True
            i += 1
            continue
        if ch == '"':
            in_str = not in_str
            result.append(ch)
            i += 1
            continue
        if not in_str and text.startswith("//", i):
            # Skip to end of line
            j = text.find("\n", i)
            if j == -1:
                break
            i = j + 1
            continue
        if not in_str and text.startswith("/*", i):
            j = text.find("*/", i + 2)
            if j == -1:
                break
            i = j + 2
            continue
        result.append(ch)
        i += 1
    return "".join(result)


def load_json_with_comments(path: str | Path) -> Any:
    """Load a JSON file allowing // and /* */ comments and trailing commas."""
    p = Path(path)
    text = _strip_comments(p.read_text())
    # Remove trailing commas left after comment stripping
    text = re.sub(r",\s*(?=[}\]])", "", text)
    return json.loads(text)
