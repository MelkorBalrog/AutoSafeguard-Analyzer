from gui.architecture import SysMLDiagramWindow, SysMLObject


def test_sysml_find_object_strategies():
    win = object.__new__(SysMLDiagramWindow)
    obj = SysMLObject(
        obj_id=1,
        obj_type="Block",
        x=50,
        y=50,
        element_id=None,
        width=40,
        height=20,
        properties={},
        requirements=[],
        locked=False,
        hidden=False,
        collapsed={},
    )
    win.objects = [obj]
    win.zoom = 1.0

    assert win._find_object_strategy1(50, 50) is obj
    assert win._find_object_strategy2(50, 50) is obj
    assert win._find_object_strategy3(50, 50) is obj
    assert win._find_object_strategy4(50, 50) is obj
    assert win.find_object(50, 50) is obj

