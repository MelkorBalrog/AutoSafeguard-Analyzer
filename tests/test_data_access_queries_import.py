import ast
from pathlib import Path


def test_automl_core_imports_data_access_queries():
    code = Path("mainappsrc/core/automl_core.py").read_text()
    tree = ast.parse(code)
    assert any(
        isinstance(node, ast.ImportFrom)
        and node.module == "data_access_queries"
        and any(alias.name == "DataAccess_Queries" for alias in node.names)
        for node in ast.walk(tree)
    ), "DataAccess_Queries import missing in automl_core"
