import ast
from pathlib import Path


def test_ui_setup_mixin_defines_setup_style():
    tree = ast.parse(Path("mainappsrc/core/ui_setup.py").read_text())
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "UISetupMixin":
            if any(isinstance(n, ast.FunctionDef) and n.name == "setup_style" for n in node.body):
                return
            break
    raise AssertionError("UISetupMixin.setup_style is not defined")
