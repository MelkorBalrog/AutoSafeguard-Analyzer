import os
import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
PyQt6 = pytest.importorskip("PyQt6")
from PyQt6.QtWidgets import QApplication
from gui.faults_gui import FaultsWindow


@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])


def test_status_bar_transparency(app):
    win = FaultsWindow()
    alpha = win.status.palette().color(win.status.backgroundRole()).alpha()
    assert alpha < 255
    win.close()
