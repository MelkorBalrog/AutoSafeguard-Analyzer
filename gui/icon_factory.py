import tkinter as tk
from typing import Optional


def create_icon(
    shape: str, color: str = "black", bg: Optional[str] = None
) -> tk.PhotoImage:
    """Return a small 16x16 PhotoImage for *shape* using *color*.

    Icons now have filled interiors and simple outlines so they look like
    miniature versions of the objects they represent. By default the returned
    image has a transparent background so the icons blend with any widget.
    The implementation is deliberately lightweight and only uses
    ``tk.PhotoImage`` drawing primitives so it works in the same environments
    as the previous icon helpers.
    """
    size = 16
    img = tk.PhotoImage(width=size, height=size)
    if bg:
        img.put(bg, to=(0, 0, size - 1, size - 1))
    c = color
    outline = "black"
    if shape == "circle":
        r = size // 2 - 3
        cx = cy = size // 2
        for y in range(size):
            for x in range(size):
                dist = (x - cx) ** 2 + (y - cy) ** 2
                if dist <= r * r:
                    img.put(c, (x, y))
                if r * r <= dist <= (r + 1) * (r + 1):
                    img.put(outline, (x, y))
    elif shape == "ellipse":
        rx = size // 2 - 2
        ry = size // 2 - 4
        cx = cy = size // 2
        for y in range(size):
            for x in range(size):
                norm = ((x - cx) ** 2) / (rx * rx) + ((y - cy) ** 2) / (ry * ry)
                if norm <= 1:
                    img.put(c, (x, y))
                if 1 <= norm <= 1.2:
                    img.put(outline, (x, y))
    elif shape == "human":
        cx = size // 2
        head_r = 3
        head_cy = 4
        for y in range(head_cy - head_r, head_cy + head_r + 1):
            for x in range(cx - head_r, cx + head_r + 1):
                dist = (x - cx) ** 2 + (y - head_cy) ** 2
                if dist <= head_r * head_r:
                    img.put(c, (x, y))
                if head_r * head_r <= dist <= (head_r + 1) * (head_r + 1):
                    img.put(outline, (x, y))
        for y in range(head_cy + head_r, size - 3):
            img.put(c, (cx, y))
        arm_y = head_cy + head_r + 2
        for x in range(cx - 4, cx + 5):
            img.put(c, (x, arm_y))
        leg_start = size - 4
        for i in range(4):
            img.put(c, (cx - i, leg_start + i))
            img.put(c, (cx + i, leg_start + i))
    elif shape == "diamond":
        mid = size // 2
        for y in range(2, size - 2):
            span = mid - abs(mid - y)
            img.put(c, to=(mid - span, y, mid + span + 1, y + 1))
            img.put(outline, (mid - span, y))
            img.put(outline, (mid + span, y))
    elif shape == "rect":
        img.put(c, to=(3, 3, size - 3, size - 3))
        for x in range(3, size - 3):
            img.put(outline, (x, 3))
            img.put(outline, (x, size - 4))
        for y in range(3, size - 3):
            img.put(outline, (3, y))
            img.put(outline, (size - 4, y))
    elif shape == "folder":
        img.put(c, to=(1, 5, size - 2, size - 2))
        img.put(c, to=(1, 3, size // 2, 5))
        for x in range(1, size - 1):
            img.put(outline, (x, 5))
            img.put(outline, (x, size - 2))
        for y in range(5, size - 1):
            img.put(outline, (1, y))
            img.put(outline, (size - 2, y))
        for x in range(1, size // 2):
            img.put(outline, (x, 3))
        for y in range(3, 5):
            img.put(outline, (1, y))
    elif shape == "arrow":
        mid = size // 2
        # Draw a thin horizontal shaft
        for x in range(2, size - 5):
            img.put(c, (x, mid))
            img.put(outline, (x, mid))
        # Add a triangular arrow head
        head = size - 5
        for i in range(5):
            img.put(outline, (mid + i, mid - 3 - i))
            img.put(outline, (mid + i, mid + 3 + i))
    elif shape == "relation":
        mid = size // 2
        for x in range(2, size - 4):
            img.put(c, (x, mid))
        for i in range(4):
            img.put(c, (size - 4 + i, mid - i))
            img.put(c, (size - 4 + i, mid + i))
    elif shape == "triangle":
        mid = size // 2
        height = size - 4
        for y in range(height):
            span = (y * mid) // height
            img.put(c, to=(mid - span, 2 + y, mid + span + 1, 3 + y))
            img.put(outline, (mid - span, 2 + y))
            img.put(outline, (mid + span, 2 + y))
        for x in range(2, size - 2):
            img.put(outline, (x, height + 2))
    elif shape == "cylinder":
        img.put(c, to=(2, 4, size - 2, size - 4))
        for x in range(2, size - 2):
            img.put(outline, (x, 4))
            img.put(outline, (x, size - 4))
        for x in range(3, size - 3):
            img.put(outline, (x, 3))
            img.put(outline, (x, size - 3))
    elif shape == "document":
        img.put(c, to=(2, 2, size - 2, size - 2))
        fold = bg or "white"
        for i in range(4):
            img.put(fold, to=(size - 6 + i, 2, size - 2, 6 - i))
        for x in range(2, size - 2):
            img.put(outline, (x, 2))
            img.put(outline, (x, size - 2))
        for y in range(2, size - 2):
            img.put(outline, (2, y))
            img.put(outline, (size - 2, y))
    elif shape == "bar":
        top = size // 2 - 2
        img.put(c, to=(2, top, size - 2, top + 4))
        for x in range(2, size - 2):
            img.put(outline, (x, top))
            img.put(outline, (x, top + 3))
    elif shape == "nested":
        for x in range(1, size - 1):
            img.put(outline, (x, 1))
            img.put(outline, (x, size - 2))
        for y in range(1, size - 1):
            img.put(outline, (1, y))
            img.put(outline, (size - 2, y))
        for x in range(4, size - 4):
            img.put(outline, (x, 4))
            img.put(outline, (x, size - 5))
        for y in range(4, size - 4):
            img.put(outline, (4, y))
            img.put(outline, (size - 5, y))
    elif shape == "plus":
        mid = size // 2
        for x in range(3, size - 3):
            img.put(c, (x, mid))
        for y in range(3, size - 3):
            img.put(c, (mid, y))
        for x in range(3, size - 3):
            img.put(outline, (x, mid - 1))
            img.put(outline, (x, mid + 1))
        for y in range(3, size - 3):
            img.put(outline, (mid - 1, y))
            img.put(outline, (mid + 1, y))
    elif shape == "cross":
        for i in range(3, size - 3):
            img.put(c, (i, i))
            img.put(c, (i, size - i - 1))
            img.put(outline, (i, i))
            img.put(outline, (i, size - i - 1))
    elif shape == "gear":
        mid = size // 2
        r = size // 2 - 4
        for y in range(size):
            for x in range(size):
                dist = (x - mid) ** 2 + (y - mid) ** 2
                if dist <= r * r:
                    img.put(c, (x, y))
                if r * r <= dist <= (r + 1) * (r + 1):
                    img.put(outline, (x, y))
        for t in (-r, r):
            for x in range(mid - 1, mid + 2):
                img.put(c, (x, mid + t))
                img.put(outline, (x, mid + t))
            for y in range(mid - 1, mid + 2):
                img.put(c, (mid + t, y))
                img.put(outline, (mid + t, y))
    elif shape == "sigma":
        for x in range(3, size - 3):
            img.put(c, (x, 3))
            img.put(c, (x, size - 4))
            img.put(outline, (x, 3))
            img.put(outline, (x, size - 4))
        for i in range(6):
            img.put(c, (3 + i, 3 + i))
            img.put(c, (size - 4 - i, 3 + i))
            img.put(outline, (3 + i, 3 + i))
            img.put(outline, (size - 4 - i, 3 + i))
    elif shape == "disk":
        img.put(c, to=(2, 2, size - 2, size - 2))
        if bg:
            img.put(bg, to=(size - 6, 2, size - 2, 6))
            img.put(bg, to=(3, 3, size - 3, 6))
        for x in range(2, size - 2):
            img.put(outline, (x, 2))
            img.put(outline, (x, size - 2))
        for y in range(2, size - 2):
            img.put(outline, (2, y))
            img.put(outline, (size - 2, y))
    elif shape == "neural":
        nodes_left = [(4, 4), (4, 12)]
        nodes_mid = [(8, 4), (8, 12)]
        node_out = (12, 8)

        def draw_node(x: int, y: int) -> None:
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    if dx * dx + dy * dy <= 1:
                        img.put(outline, (x + dx, y + dy))

        def draw_line(p1, p2) -> None:
            x1, y1 = p1
            x2, y2 = p2
            steps = max(abs(x2 - x1), abs(y2 - y1))
            for i in range(steps + 1):
                x = int(round(x1 + (x2 - x1) * i / steps))
                y = int(round(y1 + (y2 - y1) * i / steps))
                img.put(outline, (x, y))

        for s in nodes_left:
            for h in nodes_mid:
                draw_line(s, h)
        for h in nodes_mid:
            draw_line(h, node_out)
        for p in nodes_left + nodes_mid + [node_out]:
            draw_node(*p)
    else:
        img.put(c, to=(2, 2, size - 2, size - 2))
        for x in range(2, size - 2):
            img.put(outline, (x, 2))
            img.put(outline, (x, size - 2))
        for y in range(2, size - 2):
            img.put(outline, (2, y))
            img.put(outline, (size - 2, y))
    return img
