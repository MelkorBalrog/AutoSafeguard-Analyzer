import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from sysml.sysml_repository import SysMLRepository


def setup_repo():
    SysMLRepository._instance = None
    return SysMLRepository.get_instance()


def test_activity_diagram_requirements():
    repo = setup_repo()
    ad = repo.create_diagram("Activity Diagram", name="Main")
    a1 = repo.create_element("Action", name="Start")
    a2 = repo.create_element("Action", name="End")
    ad.objects = [
        {"obj_id": 1, "obj_type": "Action", "element_id": a1.elem_id, "properties": {"name": "Start"}},
        {"obj_id": 2, "obj_type": "Action", "element_id": a2.elem_id, "properties": {"name": "End"}},
    ]
    ad.connections = [{"src": 1, "dst": 2, "conn_type": "Control Flow"}]
    reqs = repo.generate_requirements(ad.diag_id)
    texts = [r[0] for r in reqs]
    assert "Start shall precede End." in texts
    assert {r[1] for r in reqs} == {"vehicle"}


def test_call_behavior_action_dependencies():
    repo = setup_repo()
    sub = repo.create_diagram("Activity Diagram", name="Sub")
    s1 = repo.create_element("Action", name="S1")
    s2 = repo.create_element("Action", name="S2")
    sub.objects = [
        {"obj_id": 1, "obj_type": "Action", "element_id": s1.elem_id, "properties": {"name": "S1"}},
        {"obj_id": 2, "obj_type": "Action", "element_id": s2.elem_id, "properties": {"name": "S2"}},
    ]
    sub.connections = [{"src": 1, "dst": 2, "conn_type": "Control Flow"}]

    main = repo.create_diagram("Activity Diagram", name="Main")
    start = repo.create_element("Action", name="Start")
    call_elem = repo.create_element("CallBehaviorAction", name="CallSub")
    end = repo.create_element("Action", name="End")
    main.objects = [
        {"obj_id": 1, "obj_type": "Action", "element_id": start.elem_id, "properties": {"name": "Start"}},
        {
            "obj_id": 2,
            "obj_type": "CallBehaviorAction",
            "element_id": call_elem.elem_id,
            "properties": {"name": "CallSub", "behavior": sub.diag_id},
        },
        {"obj_id": 3, "obj_type": "Action", "element_id": end.elem_id, "properties": {"name": "End"}},
    ]
    main.connections = [
        {"src": 1, "dst": 2, "conn_type": "Control Flow"},
        {"src": 2, "dst": 3, "conn_type": "Control Flow"},
    ]
    reqs = repo.generate_requirements(main.diag_id)
    texts = [r[0] for r in reqs]
    assert "Start shall precede CallSub." in texts
    assert "CallSub shall precede End." in texts
    assert "S1 shall precede S2." in texts
    assert {r[1] for r in reqs} == {"vehicle"}


def test_non_activity_diagram_requirement_type():
    repo = setup_repo()
    bdd = repo.create_diagram("Block Definition Diagram", name="Struct")
    b1 = repo.create_element("Block", name="A")
    b2 = repo.create_element("Block", name="B")
    bdd.objects = [
        {"obj_id": 1, "obj_type": "Block", "element_id": b1.elem_id, "properties": {"name": "A"}},
        {"obj_id": 2, "obj_type": "Block", "element_id": b2.elem_id, "properties": {"name": "B"}},
    ]
    bdd.connections = [{"src": 1, "dst": 2, "conn_type": "Association"}]
    reqs = repo.generate_requirements(bdd.diag_id)
    assert reqs == [("A shall be connected to B.", "functional")]
