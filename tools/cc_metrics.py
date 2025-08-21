import ast
import json
import sys


class ComplexityVisitor(ast.NodeVisitor):
    def __init__(self):
        self.count = 1

    def generic_visit(self, node):
        if isinstance(
            node,
            (ast.If, ast.For, ast.While, ast.And, ast.Or, ast.ExceptHandler, ast.With, ast.Try, ast.BoolOp),
        ):
            self.count += 1
        super().generic_visit(node)


def function_complexity(node: ast.AST) -> int:
    visitor = ComplexityVisitor()
    visitor.visit(node)
    return visitor.count


def file_complexity(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read())
    result = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            result[node.name] = function_complexity(node)
    return result


def main(paths: list[str]) -> None:
    results = {path: file_complexity(path) for path in paths}
    print(json.dumps(results))


if __name__ == "__main__":
    main(sys.argv[1:])
