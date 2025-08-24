import types
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

# Provide dummy PIL modules so AutoML can be imported without Pillow
sys.modules.setdefault("PIL", types.ModuleType("PIL"))
sys.modules.setdefault("PIL.Image", types.ModuleType("Image"))
sys.modules.setdefault("PIL.ImageTk", types.ModuleType("ImageTk"))
sys.modules.setdefault("PIL.ImageDraw", types.ModuleType("ImageDraw"))
sys.modules.setdefault("PIL.ImageFont", types.ModuleType("ImageFont"))

from AutoML import EditNodeDialog
from analysis.models import global_requirements


def test_add_new_requirement_records_phase():
    dlg = EditNodeDialog.__new__(EditNodeDialog)
    dlg.app = types.SimpleNamespace(
        safety_mgmt_toolbox=types.SimpleNamespace(active_module="Phase1")
    )
    global_requirements.clear()

    req = dlg.add_new_requirement("R1", "vehicle", "Req1")
    assert req["phase"] == "Phase1"
    assert global_requirements["R1"]["phase"] == "Phase1"

    dlg.app.safety_mgmt_toolbox.active_module = None
    req2 = dlg.add_new_requirement("R2", "vehicle", "Req2")
    assert req2["phase"] is None
    assert global_requirements["R2"]["phase"] is None
