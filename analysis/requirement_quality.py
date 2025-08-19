"""Requirement quality checker.

This module provides simple heuristics to verify that requirement
statements are grammatically sensible.  It focuses on two aspects:

* the verb that follows ``shall`` uses the base form (no ``-s``/``-ed``)
* subordinate clauses after commas begin with a connecting word such as
  ``ensuring`` or ``that`` so the sentence flows naturally

The goal is to catch obviously incorrect requirement templates such as::

    Safety engineer shall assess the <obj1> using the <obj0>,
    mitigates the <obj2>, develops the <obj3>, verify the <obj4>, and
    produces the <obj5>.

The checker detects the missing connecting words after commas and the
incorrect ``shall assesses`` verb form.

The implementation intentionally avoids external dependencies to keep the
checker lightweight and easy to run in constrained environments.
"""

from __future__ import annotations

import re
from typing import List, Tuple

# Words that can legitimately begin a clause following a comma.  These
# connectors ensure the sentence reads naturally.
CONNECTING_WORDS = {
    "and",
    "or",
    "but",
    "so",
    "then",
    "ensuring",
    "that",
    "which",
    "who",
    "while",
    "with",
    "by",
    "to",
}

# Words that may start a leading conditional clause.  If the requirement
# begins with one of these, the next clause is treated as the main one and
# is exempt from the connector rule.
LEADING_CONDITIONS = (
    "when",
    "if",
    "after",
    "before",
    "once",
)


def check_requirement_quality(text: str) -> Tuple[bool, List[str]]:
    """Return ``(passed, issues)`` for *text*.

    ``passed`` is ``True`` when no issues were detected.  ``issues`` lists
    the human-readable error descriptions when the requirement is not
    well-formed.
    """

    issues: List[str] = []
    if not text or not text.strip():
        return False, ["requirement text is empty"]

    text = text.strip()

    # ------------------------------------------------------------------
    # Check the verb form following "shall"
    # ------------------------------------------------------------------
    m = re.search(r"\bshall\s+(\w+)", text, flags=re.IGNORECASE)
    if not m:
        issues.append("missing 'shall' modal verb")
    else:
        verb = m.group(1)
        lower = verb.lower()
        # Flag obvious third-person forms such as "assesses" or "mitigates".
        if (lower.endswith("ed") or (lower.endswith("s") and not lower.endswith("ss"))):
            issues.append("verb following 'shall' must be base form")

    # ------------------------------------------------------------------
    # Split into comma-separated clauses and ensure each subsequent clause
    # starts with a connecting word so the sentence flows naturally.
    # ------------------------------------------------------------------
    clauses = [c.strip() for c in text.split(",")]
    start_index = 1
    if clauses and clauses[0].lower().startswith(LEADING_CONDITIONS):
        # Skip the clause with the condition and the main clause that
        # follows it.
        start_index = 2
    for clause in clauses[start_index:]:
        if not clause:
            continue
        first = clause.split(" ", 1)[0].lower()
        if first not in CONNECTING_WORDS:
            issues.append(
                f"clause '{clause}' lacks a connecting word for natural flow"
            )

    return not issues, issues


__all__ = ["check_requirement_quality"]
