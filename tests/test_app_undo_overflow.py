import os
import sys
import types

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

try:
    from AutoML import AutoMLApp
except ModuleNotFoundError:
    # Provide lightweight Pillow stubs so AutoML can be imported
    class _FakeImage:
        def __init__(self, size=(1, 1)):
            self.size = size

        def save(self, *_args, **_kwargs):
            pass

    def _image_new(_mode, size, _color):
        return _FakeImage(size)

    class _FakeDraw:
        def __init__(self, _img):
            pass

        def line(self, *_a, **_k):
            pass

        def polygon(self, *_a, **_k):
            pass

        def rectangle(self, *_a, **_k):
            pass

        def multiline_textbbox(self, *_a, **_k):
            return (0, 0, 10, 10)

        def multiline_text(self, *_a, **_k):
            pass

    class _FakeFontModule:
        @staticmethod
        def load_default():
            return object()

    PIL_stub = types.ModuleType("PIL")
    PIL_stub.Image = types.SimpleNamespace(new=_image_new)
    PIL_stub.ImageDraw = types.SimpleNamespace(Draw=lambda img: _FakeDraw(img))
    PIL_stub.ImageFont = _FakeFontModule
    PIL_stub.ImageTk = object
    sys.modules.setdefault("PIL", PIL_stub)
    sys.modules.setdefault("PIL.Image", PIL_stub.Image)
    sys.modules.setdefault("PIL.ImageDraw", PIL_stub.ImageDraw)
    sys.modules.setdefault("PIL.ImageFont", PIL_stub.ImageFont)
    sys.modules.setdefault("PIL.ImageTk", PIL_stub.ImageTk)
    from AutoML import AutoMLApp

from mainappsrc.models.sysml.sysml_repository import SysMLRepository


def test_undo_does_not_unload_project_when_stack_empty():
    SysMLRepository._instance = None
    repo = SysMLRepository.get_instance()
    # Create a block; repository maintains its own undo history
    blk = repo.create_element("Block", name="A")

    # Set up minimal app with empty undo stack
    app = AutoMLApp.__new__(AutoMLApp)
    app.export_model_data = lambda include_versions=False: {}
    app.apply_model_data = lambda data: None
    app.refresh_all = lambda: None
    app.diagram_tabs = {}
    app._undo_stack = []
    app._redo_stack = []
    app.undo = AutoMLApp.undo.__get__(app)

    # Undoing with an empty app stack should not remove repository elements
    app.undo()
    assert blk.elem_id in repo.elements
