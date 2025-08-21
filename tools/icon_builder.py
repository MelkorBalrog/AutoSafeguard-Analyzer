#!/usr/bin/env python3
"""Utility to programmatically generate an AutoML icon.

This module contains four different strategies for drawing a very small
icon using pure Python byte manipulation so that it has no external
dependencies.  Strategy ``v4`` is used by default by the build scripts.
"""
from __future__ import annotations

import struct
from pathlib import Path
from typing import Callable, Dict, List, Tuple

Size = Tuple[int, int]
Color = Tuple[int, int, int, int]
SIZE: Size = (32, 32)


def _write_ico(path: Path, pixels: List[List[Color]], size: Size = SIZE) -> None:
    """Write *pixels* to *path* as a 32-bit ICO file."""
    width, height = size
    row_bytes = width * 4
    bmp_header_size = 40
    and_mask = b"\x00" * ((row_bytes // 4) * height)

    bmp_size = bmp_header_size + row_bytes * height + len(and_mask)
    ico_header = struct.pack("<3H", 0, 1, 1)
    entry = struct.pack(
        "<BBBBHHII", width, height, 0, 0, 1, 32, bmp_size, 6 + 16
    )
    bmp_header = struct.pack(
        "<IIIHHIIIIII",
        bmp_header_size,
        width,
        height * 2,
        1,
        32,
        0,
        row_bytes * height,
        0,
        0,
        0,
        0,
    )
    body = bytearray()
    for y in reversed(range(height)):
        for x in range(width):
            r, g, b, a = pixels[y][x]
            body.extend(struct.pack("<BBBB", b, g, r, a))
    data = ico_header + entry + bmp_header + body + and_mask
    Path(path).write_bytes(data)


def _solid(color: Color) -> List[List[Color]]:
    return [[color for _ in range(SIZE[0])] for _ in range(SIZE[1])]


def _diagonal(color1: Color, color2: Color) -> List[List[Color]]:
    pixels: List[List[Color]] = []
    for y in range(SIZE[1]):
        row = []
        for x in range(SIZE[0]):
            row.append(color1 if x < y else color2)
        pixels.append(row)
    return pixels


def _circle(inner: Color, outer: Color) -> List[List[Color]]:
    cx = cy = SIZE[0] // 2
    r = SIZE[0] // 2 - 2
    pixels: List[List[Color]] = []
    for y in range(SIZE[1]):
        row = []
        for x in range(SIZE[0]):
            if (x - cx) ** 2 + (y - cy) ** 2 <= r * r:
                row.append(inner)
            else:
                row.append(outer)
        pixels.append(row)
    return pixels


def _cross(color1: Color, color2: Color) -> List[List[Color]]:
    pixels: List[List[Color]] = []
    for y in range(SIZE[1]):
        row = []
        for x in range(SIZE[0]):
            if x == y or x == SIZE[0] - y - 1:
                row.append(color1)
            else:
                row.append(color2)
        pixels.append(row)
    return pixels


def build_icon_v1(path: Path) -> None:
    _write_ico(path, _solid((20, 20, 200, 255)))


def build_icon_v2(path: Path) -> None:
    _write_ico(path, _diagonal((200, 20, 20, 255), (20, 200, 20, 255)))


def build_icon_v3(path: Path) -> None:
    _write_ico(path, _circle((200, 200, 20, 255), (20, 20, 20, 255)))


def build_icon_v4(path: Path) -> None:
    _write_ico(path, _cross((240, 240, 240, 255), (30, 30, 30, 255)))

_BUILDERS: Dict[str, Callable[[Path], None]] = {
    "v1": build_icon_v1,
    "v2": build_icon_v2,
    "v3": build_icon_v3,
    "v4": build_icon_v4,
}


def build_icon(path: Path, strategy: str = "v4") -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    _BUILDERS[strategy](path)
    return path


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("bin/AutoML.ico"))
    parser.add_argument("--strategy", choices=sorted(_BUILDERS), default="v4")
    args = parser.parse_args()
    build_icon(args.output, args.strategy)
    print(f"Icon written to {args.output}")


if __name__ == "__main__":
    main()
