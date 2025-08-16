import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from analysis.utils import truncate_to_height

def test_truncate_to_height_returns_shorter_table():
    base = [
        [1, 2, 3],
        [4, 5, 6],
        [7, 8, 9],
    ]
    result = truncate_to_height(base, 2)
    assert result == [[1, 2, 3], [4, 5, 6]]
    assert len(result) == 2
    assert len(result[0]) == len(base[0])

def test_truncate_to_height_handles_non_positive_height():
    base = [[1, 2, 3]]
    assert truncate_to_height(base, 0) == []
    assert truncate_to_height(base, -5) == []


def test_truncate_to_height_height_larger_than_source():
    base = [[1, 2], [3, 4]]
    result = truncate_to_height(base, 10)
    assert result == base
