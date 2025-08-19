import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from gui import architecture


def test_toolbox_relations_have_no_duplicates():
    defs = architecture._toolbox_defs()
    for group, data in defs.items():
        rels = data.get("relations", [])
        assert rels == sorted(set(rels))
        for ext in data.get("externals", {}).values():
            ext_rels = ext.get("relations", [])
            assert ext_rels == sorted(set(ext_rels))
