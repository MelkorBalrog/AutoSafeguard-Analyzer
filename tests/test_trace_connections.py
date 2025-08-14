import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from sysml.sysml_repository import SysMLRepository
from gui.architecture import link_trace_between_objects, DiagramConnection

def test_link_trace_between_objects_creates_connection():
    SysMLRepository.reset_instance()
    repo = SysMLRepository.get_instance()

    diag = repo.create_diagram("Activity Diagram", name="A")
    e1 = repo.create_element("Action", name="A1")
    e2 = repo.create_element("Action", name="A2")
    repo.add_element_to_diagram(diag.diag_id, e1.elem_id)
    repo.add_element_to_diagram(diag.diag_id, e2.elem_id)
    obj1 = {"obj_id": 1, "obj_type": "Action", "x": 0, "y": 0, "element_id": e1.elem_id}
    obj2 = {"obj_id": 2, "obj_type": "Action", "x": 100, "y": 0, "element_id": e2.elem_id}
    diag.objects = [obj1, obj2]

    conn = link_trace_between_objects(obj1, obj2, diag.diag_id)
    assert isinstance(conn, DiagramConnection)
    assert conn.conn_type == "Trace"
    assert any(
        c["conn_type"] == "Trace" and c["src"] == 1 and c["dst"] == 2
        for c in diag.connections
    )
    assert all(o["obj_type"] != "Trace" for o in diag.objects)
    rels = [r for r in repo.relationships if r.rel_type == "Trace"]
    assert any(r.source == e1.elem_id and r.target == e2.elem_id for r in rels)
    assert any(r.source == e2.elem_id and r.target == e1.elem_id for r in rels)
