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


def _ensure_list_of_strings(val: Any, name: str) -> None:
    """Raise :class:`ValueError` if *val* is not a list of strings."""
    if not isinstance(val, list) or any(not isinstance(v, str) for v in val):
        raise ValueError(f"{name} must be a list of strings")


def validate_diagram_rules(data: Any) -> dict[str, Any]:
    """Validate diagram rule configuration structure.

    Parameters
    ----------
    data:
        Parsed JSON object representing the diagram rules configuration.

    Returns
    -------
    dict
        The validated configuration.

    Raises
    ------
    ValueError
        If the configuration does not follow the expected structure.
    """

    if not isinstance(data, dict):
        raise ValueError("Configuration root must be a JSON object")

    list_fields = [
        "ai_nodes",
        "ai_relations",
        "arch_diagram_types",
        "governance_node_types",
        "gate_node_types",
        "guard_nodes",
    ]
    for field in list_fields:
        if field in data:
            _ensure_list_of_strings(data[field], field)

    if "requirement_rules" in data or "relationship_rules" in data:
        rr = data.get("requirement_rules", data.get("relationship_rules", {}))
        if not isinstance(rr, dict):
            raise ValueError("requirement_rules must be an object")
        for label, info in rr.items():
            if not isinstance(info, dict):
                raise ValueError(f"requirement_rules[{label}] must be an object")
            action = info.get("action")
            if not isinstance(action, str):
                raise ValueError(
                    f"requirement_rules[{label}]['action'] must be a string"
                )
            if "subject" in info and not isinstance(info["subject"], str):
                raise ValueError(
                    f"requirement_rules[{label}]['subject'] must be a string"
                )
            if "constraint" in info and not isinstance(info["constraint"], bool):
                raise ValueError(
                    f"requirement_rules[{label}]['constraint'] must be a boolean"
                )

    if "node_roles" in data:
        nr = data["node_roles"]
        if not isinstance(nr, dict):
            raise ValueError("node_roles must be an object")
        allowed = {"subject", "action", "condition", "constraint", "object"}
        for node, role in nr.items():
            if role not in allowed:
                raise ValueError(
                    f"node_roles[{node}] has invalid role '{role}'"
                )

    if "safety_ai_relation_rules" in data:
        sar = data["safety_ai_relation_rules"]
        if not isinstance(sar, dict):
            raise ValueError("safety_ai_relation_rules must be an object")
        for rel, srcs in sar.items():
            if not isinstance(srcs, dict):
                raise ValueError(
                    f"safety_ai_relation_rules[{rel}] must be an object"
                )
            for src, dests in srcs.items():
                _ensure_list_of_strings(
                    dests, f"safety_ai_relation_rules[{rel}][{src}]"
                )

    if "connection_rules" in data:
        cr = data["connection_rules"]
        if not isinstance(cr, dict):
            raise ValueError("connection_rules must be an object")
        for diag, conns in cr.items():
            if not isinstance(conns, dict):
                raise ValueError(f"connection_rules[{diag}] must be an object")
            for conn, srcs in conns.items():
                if not isinstance(srcs, dict):
                    raise ValueError(
                        f"connection_rules[{diag}][{conn}] must be an object"
                    )
                for src, dests in srcs.items():
                    _ensure_list_of_strings(
                        dests, f"connection_rules[{diag}][{conn}][{src}]"
                    )

    if "node_connection_limits" in data:
        ncl = data["node_connection_limits"]
        if not isinstance(ncl, dict) or any(
            not isinstance(v, int) for v in ncl.values()
        ):
            raise ValueError(
                "node_connection_limits must map node types to integer limits"
            )

    return data


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


def load_diagram_rules(path: str | Path) -> dict[str, Any]:
    """Load and validate the diagram rules configuration file."""
    data = load_json_with_comments(path)
    return validate_diagram_rules(data)
