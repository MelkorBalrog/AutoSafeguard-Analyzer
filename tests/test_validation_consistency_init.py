import ast
from pathlib import Path


def test_automl_core_initialises_validation_consistency():
    code = Path("mainappsrc/core/automl_core.py").read_text()
    tree = ast.parse(code)
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            if any(isinstance(t, ast.Attribute) and t.attr == "validation_consistency" and isinstance(t.value, ast.Name) and t.value.id == "self" for t in node.targets):
                if isinstance(node.value, ast.Call) and getattr(node.value.func, "id", None) == "Validation_Consistency":
                    break
    else:
        raise AssertionError("AutoMLApp.__init__ does not assign Validation_Consistency to self.validation_consistency")
