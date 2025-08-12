import types
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# Provide a minimal Pillow stub so importing AutoML does not fail.
pil = types.ModuleType("PIL")
pil.Image = types.ModuleType("Image")
pil.ImageTk = types.ModuleType("ImageTk")
pil.ImageDraw = types.ModuleType("ImageDraw")
pil.ImageFont = types.ModuleType("ImageFont")
sys.modules.setdefault("PIL", pil)
sys.modules.setdefault("PIL.Image", pil.Image)
sys.modules.setdefault("PIL.ImageTk", pil.ImageTk)
sys.modules.setdefault("PIL.ImageDraw", pil.ImageDraw)
sys.modules.setdefault("PIL.ImageFont", pil.ImageFont)

from analysis.models import HaraDoc, HaraEntry
from AutoML import FaultTreeApp


def test_update_hazard_list_uses_entry_severity():
    """Hazard severities from HARA entries should populate the hazard list."""
    entry = HaraEntry(
        malfunction="m",
        hazard="HZ",
        scenario="scen",
        severity=3,
        sev_rationale="",
        controllability=1,
        cont_rationale="",
        exposure=1,
        exp_rationale="",
        asil="",
        safety_goal="",
    )
    hara = HaraDoc("RA", [], [entry])
    app = types.SimpleNamespace(
        hara_docs=[hara],
        hazop_docs=[],
        hazard_severity={},
        hazards=[],
    )

    FaultTreeApp.update_hazard_list(app)

    assert app.hazard_severity["HZ"] == 3
    assert "HZ" in app.hazards
