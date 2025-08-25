import ast
from pathlib import Path


def test_automl_core_initialises_structure_tree_operations():
    code = Path("mainappsrc/core/automl_core.py").read_text()
    tree = ast.parse(code)
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            if any(
                isinstance(t, ast.Attribute)
                and t.attr == "structure_tree_operations"
                and isinstance(t.value, ast.Name)
                and t.value.id == "self"
                for t in node.targets
            ):
                if (
                    isinstance(node.value, ast.Call)
                    and getattr(node.value.func, "id", None) == "Structure_Tree_Operations"
                ):
                    break
    else:
        raise AssertionError(
            "AutoMLApp.__init__ does not assign Structure_Tree_Operations to self.structure_tree_operations"
        )
