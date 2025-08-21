import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import tools.icon_builder as ib


def test_all_strategies(tmp_path):
    strategies = ["v1", "v2", "v3", "v4"]
    for strat in strategies:
        out = tmp_path / f"icon_{strat}.ico"
        ib.build_icon(out, strat)
        assert out.exists()
        assert out.stat().st_size > 0
        # basic validation: ensure file begins with ICO header bytes
        with out.open("rb") as f:
            header = f.read(4)
        assert header.startswith(b"\x00\x00")
