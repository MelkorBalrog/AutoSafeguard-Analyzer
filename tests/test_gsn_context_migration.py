from gsn import GSNNode


def test_legacy_context_entries_load_as_context():
    """Older models stored context nodes in both ``children`` and ``context``.
    Ensure they are treated purely as context relationships when loading."""

    # Simulate legacy serialised data where the context node ID appears in both
    # the ``children`` and ``context`` fields of the parent.
    root_data = {
        "unique_id": "1",
        "user_name": "G",
        "node_type": "Goal",
        "children": ["2"],
        "context": ["2"],
    }
    ctx_data = {
        "unique_id": "2",
        "user_name": "C",
        "node_type": "Context",
    }
    nodes = {}
    root = GSNNode.from_dict(root_data, nodes)
    ctx = GSNNode.from_dict(ctx_data, nodes)

    # Should not raise even though the ID is listed twice.
    GSNNode.resolve_references(nodes)

    assert ctx in root.children
    assert ctx in root.context_children
    assert root in ctx.parents
    # The context node should only appear once in the children list.
    assert root.children.count(ctx) == 1

