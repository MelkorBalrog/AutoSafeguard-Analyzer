import ast
from pathlib import Path


def test_sysml_repository_defines_export_state():
    code = Path("mainappsrc/models/sysml/sysml_repository.py").read_text()
    tree = ast.parse(code)
    class_node = next(
        node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == "SysMLRepository"
    )
    assert any(
        isinstance(node, ast.FunctionDef) and node.name == "export_state" for node in class_node.body
    ), "SysMLRepository.export_state missing"
