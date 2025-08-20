from pathlib import Path


def compile_file(path: str) -> None:
    source = Path(path).read_text(encoding="utf-8")
    compile(source, path, "exec")


def test_gui_toolboxes_compiles() -> None:
    compile_file("gui/toolboxes.py")


def test_safety_management_toolbox_compiles() -> None:
    compile_file("gui/safety_management_toolbox.py")
