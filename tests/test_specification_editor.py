from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))

from gui.specification_editor import SpecificationEditor, RequirementSection
from AutoML import FaultTreeApp


def test_editor_exports_and_review_methods():
    assert hasattr(SpecificationEditor, 'export_pdf')
    assert hasattr(SpecificationEditor, 'send_to_review')


def test_app_has_spec_editor():
    assert hasattr(FaultTreeApp, 'show_specification_editor')
