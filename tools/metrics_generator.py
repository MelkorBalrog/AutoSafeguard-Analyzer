#!/usr/bin/env python3
"""Generate simple code metrics for ISO 26262 quality checks.

This script traverses a target directory and gathers basic metrics such as
source lines of code and a rudimentary cyclomatic complexity for each
function.  Results are written to a JSON file, ``metrics.json`` by default.

Example usage::

    python tools/metrics_generator.py --path analysis

The output path may be customised with ``--output``.
"""
from __future__ import annotations

import argparse
import ast
import json
from pathlib import Path
import sys
from typing import Dict, Iterable, List
from dataclasses import dataclass

# Ensure repository root is importable for local matplotlib stub
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


def _sloc(lines: Iterable[str]) -> int:
    """Return the number of source lines of code ignoring blanks and comments."""
    count = 0
    for line in lines:
        stripped = line.strip()
        if stripped and not stripped.startswith("#"):
            count += 1
    return count


class ComplexityVisitor(ast.NodeVisitor):
    """Very small cyclomatic complexity visitor."""

    def __init__(self) -> None:
        self.score = 1

    # Decision points increase complexity
    def visit_If(self, node: ast.If) -> None:  # noqa: N802 - required by ast
        self.score += 1
        self.generic_visit(node)

    visit_For = visit_If
    visit_AsyncFor = visit_If
    visit_While = visit_If

    def visit_With(self, node: ast.With) -> None:  # noqa: N802
        self.score += 1
        self.generic_visit(node)

    visit_AsyncWith = visit_With

    def visit_Try(self, node: ast.Try) -> None:  # noqa: N802
        self.score += len(node.handlers) + bool(node.orelse) + bool(node.finalbody)
        self.generic_visit(node)

    def visit_BoolOp(self, node: ast.BoolOp) -> None:  # noqa: N802
        self.score += len(node.values) - 1
        self.generic_visit(node)

    def visit_IfExp(self, node: ast.IfExp) -> None:  # noqa: N802
        self.score += 1
        self.generic_visit(node)

    def visit_comprehension(self, node: ast.comprehension) -> None:  # noqa: N802
        self.score += 1
        self.generic_visit(node)


@dataclass
class FunctionMetric:
    name: str
    lineno: int
    complexity: int


def analyze_file(path: Path) -> Dict[str, object]:
    """Analyse a single Python file and return metrics."""
    try:
        source = path.read_text(encoding="utf-8")
    except Exception:
        return {"file": str(path), "loc": 0, "functions": []}

    loc = _sloc(source.splitlines())
    tree = ast.parse(source, filename=str(path))
    functions: List[FunctionMetric] = []

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            visitor = ComplexityVisitor()
            visitor.visit(node)
            functions.append(FunctionMetric(node.name, node.lineno, visitor.score))

    return {"file": str(path), "loc": loc, "functions": [f.__dict__ for f in functions]}


def collect_metrics(root: Path) -> Dict[str, object]:
    """Collect metrics for all Python files under *root* directory."""
    files = [p for p in root.rglob("*.py")]
    results = [analyze_file(p) for p in files]

    total_loc = sum(r["loc"] for r in results)
    total_functions = sum(len(r["functions"]) for r in results)
    complexities = [f["complexity"] for r in results for f in r["functions"]]
    avg_complexity = (sum(complexities) / len(complexities)) if complexities else 0

    return {
        "total_files": len(files),
        "total_loc": total_loc,
        "total_functions": total_functions,
        "average_complexity": round(avg_complexity, 2),
        "files": results,
    }


def generate_plots(metrics: Dict[str, object], out_dir: Path) -> None:
    """Create simple visualisations of LOC and complexity metrics."""
    try:
        import matplotlib.pyplot as plt
    except Exception as exc:  # pragma: no cover - fallback if matplotlib missing
        print(f"Plotting skipped: {exc}")
        return

    files = metrics.get("files", [])
    if files:
        names = [Path(f["file"]).name for f in files]
        locs = [f["loc"] for f in files]
        plt.figure()
        plt.title("Lines of code per file")
        plt.bar(names, locs)
        plt.xticks(rotation=90)
        plt.tight_layout()
        plt.savefig(out_dir / "metrics_loc.png")
        plt.close()

    complexities = [f["complexity"] for r in files for f in r["functions"]]
    if complexities:
        plt.figure()
        plt.title("Function complexity distribution")
        plt.hist(complexities, bins=range(1, max(complexities) + 2))
        plt.xlabel("Complexity")
        plt.ylabel("Frequency")
        plt.tight_layout()
        plt.savefig(out_dir / "metrics_complexity.png")
        plt.close()

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--path", default=".", type=Path, help="Directory to analyse")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("metrics.json"),
        help="File to write JSON metrics (default: metrics.json)",
    )
    parser.add_argument(
        "--plots",
        action="store_true",
        help="Generate PNG plots for LOC and complexity",
    )
    args = parser.parse_args()

    metrics = collect_metrics(args.path)

    args.output.write_text(json.dumps(metrics, indent=2))
    print(f"Metrics written to {args.output}")
    if args.plots:
        generate_plots(metrics, args.output.parent)
        print("Plots written to metrics_loc.png and metrics_complexity.png")


if __name__ == "__main__":
    main()
