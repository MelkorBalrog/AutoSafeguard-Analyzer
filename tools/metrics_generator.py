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
from typing import Dict, Iterable, List, Sequence
from dataclasses import dataclass

# Ensure repository root is importable for local matplotlib stub
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


def _sloc(lines: Iterable[str]) -> int:
    """Return the number of source lines of code ignoring blanks and comments."""
    return sum(
        1
        for line in lines
        if (stripped := line.strip()) and not stripped.startswith("#")
    )


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


def _function_metrics(tree: ast.AST) -> List[FunctionMetric]:
    """Return complexity metrics for all functions within *tree*."""
    functions: List[FunctionMetric] = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            visitor = ComplexityVisitor()
            visitor.visit(node)
            functions.append(FunctionMetric(node.name, node.lineno, visitor.score))
    return functions


def analyze_file(path: Path) -> Dict[str, object]:
    """Analyse a single Python file and return metrics."""
    try:
        source = path.read_text(encoding="utf-8")
    except Exception:
        return {"file": str(path), "loc": 0, "functions": []}

    loc = _sloc(source.splitlines())
    tree = ast.parse(source, filename=str(path))
    functions = _function_metrics(tree)

    return {"file": str(path), "loc": loc, "functions": [f.__dict__ for f in functions]}


def _python_files(root: Path) -> List[Path]:
    """Return all Python files under *root*."""
    return list(root.rglob("*.py"))


def _total_loc(results: Sequence[Dict[str, object]]) -> int:
    return sum(r["loc"] for r in results)


def _total_functions(results: Sequence[Dict[str, object]]) -> int:
    return sum(len(r["functions"]) for r in results)


def _average_complexity(results: Sequence[Dict[str, object]]) -> float:
    complexities = [f["complexity"] for r in results for f in r["functions"]]
    if not complexities:
        return 0.0
    return round(sum(complexities) / len(complexities), 2)


def collect_metrics(root: Path) -> Dict[str, object]:
    """Collect metrics for all Python files under *root* directory."""
    files = _python_files(root)
    results = [analyze_file(p) for p in files]
    return {
        "total_files": len(files),
        "total_loc": _total_loc(results),
        "total_functions": _total_functions(results),
        "average_complexity": _average_complexity(results),
        "files": results,
    }


def _plot_loc(files: Sequence[Dict[str, object]], out_dir: Path, plt) -> None:
    names = [Path(f["file"]).name for f in files]
    locs = [f["loc"] for f in files]
    plt.figure()
    plt.title("Lines of code per file")
    plt.bar(names, locs)
    plt.xticks(rotation=90)
    plt.tight_layout()
    plt.savefig(out_dir / "metrics_loc.png")
    plt.close()


def _plot_complexity(files: Sequence[Dict[str, object]], out_dir: Path, plt) -> None:
    complexities = [f["complexity"] for r in files for f in r["functions"]]
    if not complexities:
        return
    plt.figure()
    plt.title("Function complexity distribution")
    plt.hist(complexities, bins=range(1, max(complexities) + 2))
    plt.xlabel("Complexity")
    plt.ylabel("Frequency")
    plt.tight_layout()
    plt.savefig(out_dir / "metrics_complexity.png")
    plt.close()


def generate_plots(metrics: Dict[str, object], out_dir: Path) -> None:
    """Create simple visualisations of LOC and complexity metrics."""
    try:
        import matplotlib.pyplot as plt
    except Exception as exc:  # pragma: no cover - fallback if matplotlib missing
        print(f"Plotting skipped: {exc}")
        return

    files = metrics.get("files", [])
    if not files:
        return
    _plot_loc(files, out_dir, plt)
    _plot_complexity(files, out_dir, plt)

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
