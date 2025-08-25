import ast
from pathlib import Path


def test_requirements_manager_defines_export_state():
    code = Path("mainappsrc/managers/requirements_manager.py").read_text()
    tree = ast.parse(code)
    class_node = next(
        node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == "RequirementsManagerSubApp"
    )
    assert any(
        isinstance(node, ast.FunctionDef) and node.name == "export_state" for node in class_node.body
    ), "RequirementsManagerSubApp.export_state missing"
