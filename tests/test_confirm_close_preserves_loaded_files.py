import os
import tempfile
from unittest.mock import MagicMock

from AutoML import AutoMLApp


class DummyRoot:
    def __init__(self):
        self.quit = MagicMock()
        self.destroy = MagicMock()


def test_confirm_close_preserves_loaded_files():
    fd, path = tempfile.mkstemp(suffix=".autml")
    os.close(fd)
    try:
        app = AutoMLApp.__new__(AutoMLApp)
        app.root = DummyRoot()
        app.has_unsaved_changes = lambda: False
        app._loaded_model_paths = [path]

        app.confirm_close()

        assert os.path.exists(path)
        app.root.quit.assert_called()
        app.root.destroy.assert_called()
    finally:
        if os.path.exists(path):
            os.remove(path)
