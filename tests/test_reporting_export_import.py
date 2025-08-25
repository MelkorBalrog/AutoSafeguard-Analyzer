import ast
from pathlib import Path


def test_automl_core_imports_reporting_export():
    code = Path("mainappsrc/core/automl_core.py").read_text()
    tree = ast.parse(code)
    assert any(
        isinstance(node, ast.ImportFrom)
        and node.module == "reporting_export"
        and any(alias.name == "Reporting_Export" for alias in node.names)
        for node in ast.walk(tree)
    ), "Reporting_Export import missing in automl_core"
