# Author: Miguel Marina <karel.capek.robotics@gmail.com>
import math
import tkinter as tk
import tkinter.font as tkFont

TEXT_BOX_COLOR = "#CFD8DC"

# Basic mapping of a few common color names to their hex equivalents. The
# gradient routines expect ``#RRGGBB`` colors; previously passing a named color
# such as ``"lightyellow"`` caused a ``ValueError`` when converting to integers.
# The small table below covers the named colors used by the drawing helpers and
# can be extended easily if additional names are required.
_NAMED_COLORS = {
    "lightgray": "#d3d3d3",
    "lightgrey": "#d3d3d3",
    "lightblue": "#add8e6",
    "lightyellow": "#ffffe0",
}

# Basic mapping of a few common color names to their hex equivalents. The
# gradient routines expect ``#RRGGBB`` colors; previously passing a named color
# such as ``"lightyellow"`` caused a ``ValueError`` when converting to integers.
# The small table below covers the named colors used by the drawing helpers and
# can be extended easily if additional names are required.
_NAMED_COLORS = {
    "lightgray": "#d3d3d3",
    "lightgrey": "#d3d3d3",
    "lightblue": "#add8e6",
    "lightyellow": "#ffffe0",
}

class FTADrawingHelper:
    """
    A helper class that provides drawing functions for fault tree diagrams.
    These methods can be used to draw shapes (gates, events, connectors, etc.)
    onto a tkinter Canvas.
    """
    def __init__(self):
        pass

    def clear_cache(self):
        """No-op for API compatibility."""
        pass

    def _interpolate_color(self, color: str, ratio: float) -> str:
        """Return *color* blended with white by *ratio* (0..1)."""
        # ``color`` may be provided as ``#RRGGBB`` or a Tk-style name such as
        # ``"lightgray"``.  Map known names to their hex representation so the
        # interpolation math can operate on integers.
        if not color.startswith("#"):
            color = _NAMED_COLORS.get(color.lower(), color)

        # Fallback to black if the color string is still not a valid ``#RRGGBB``
        # value to avoid raising ``ValueError`` during drawing.
        try:
            r = int(color[1:3], 16)
            g = int(color[3:5], 16)
            b = int(color[5:7], 16)
        except (ValueError, IndexError):  # pragma: no cover - defensive
            r = g = b = 0
        nr = int(255 * (1 - ratio) + r * ratio)
        ng = int(255 * (1 - ratio) + g * ratio)
        nb = int(255 * (1 - ratio) + b * ratio)
        return f"#{nr:02x}{ng:02x}{nb:02x}"

    def _fill_gradient_polygon(self, canvas, points, color: str) -> None:
        """Fill *points* polygon with a horizontal white → color gradient."""
        xs = [p[0] for p in points]
        left = math.floor(min(xs))
        right = math.ceil(max(xs))
        if right <= left:
            return
        x = left
        while x <= right:
            ratio = (x - left) / (right - left) if right > left else 1
            fill = self._interpolate_color(color, ratio)
            yvals = []
            for i in range(len(points)):
                x1, y1 = points[i]
                x2, y2 = points[(i + 1) % len(points)]
                if (x1 <= x <= x2) or (x2 <= x <= x1):
                    if abs(x1 - x2) < 1e-6:
                        if abs(x1 - x) < 0.25:
                            yvals.extend([y1, y2])
                        continue
                    t = (x - x1) / (x2 - x1)
                    yvals.append(y1 + t * (y2 - y1))
            yvals.sort()
            for j in range(0, len(yvals), 2):
                if j + 1 < len(yvals):
                    canvas.create_line(x, yvals[j], x, yvals[j + 1], fill=fill)
            x += 0.5

    def _fill_gradient_circle(self, canvas, cx: float, cy: float, radius: float, color: str) -> None:
        """Fill circle with gradient from white to *color*."""
        left = math.floor(cx - radius)
        right = math.ceil(cx + radius)
        if right <= left:
            return
        x = left
        while x <= right:
            ratio = (x - left) / (right - left) if right > left else 1
            fill = self._interpolate_color(color, ratio)
            dx = x - cx
            dy = math.sqrt(max(radius ** 2 - dx ** 2, 0))
            canvas.create_line(x, cy - dy, x, cy + dy, fill=fill)
            x += 0.5

    def _fill_gradient_rect(self, canvas, left: float, top: float, right: float, bottom: float, color: str) -> None:
        """Fill rectangle with gradient from white to *color*."""
        if right <= left:
            return
        x = left
        while x <= right:
            ratio = (x - left) / (right - left) if right > left else 1
            fill = self._interpolate_color(color, ratio)
            canvas.create_line(x, top, x, bottom, fill=fill)
            x += 0.5

    def get_text_size(self, text, font_obj):
        """Return the (width, height) in pixels needed to render the text with the given font."""
        lines = text.split("\n")
        max_width = max(font_obj.measure(line) for line in lines)
        height = font_obj.metrics("linespace") * len(lines)
        return max_width, height

    def draw_page_clone_shape(
        self,
        canvas,
        x,
        y,
        scale=40.0,
        top_text="Desc:\n\nRationale:",
        bottom_text="Node",
        fill="lightgray",
        outline_color="dimgray",
        line_width=1,
        font_obj=None,
        obj_id: str = "",
    ):
        # First, draw the main triangle using the existing triangle routine.
        self.draw_triangle_shape(
            canvas,
            x,
            y,
            scale=scale,
            top_text=top_text,
            bottom_text=bottom_text,
            fill=fill,
            outline_color=outline_color,
            line_width=line_width,
            font_obj=font_obj,
            obj_id=obj_id,
        )
        # Determine a baseline for the bottom of the triangle.
        # (You may need to adjust this value to match your triangle's dimensions.)
        bottom_y = y + scale * 0.75  
        # Draw two horizontal lines at the bottom
        line_offset1 = scale * 0.05
        line_offset2 = scale * 0.1
        canvas.create_line(x - scale/2, bottom_y - line_offset1,
                           x + scale/2, bottom_y - line_offset1,
                           fill=outline_color, width=line_width)
        canvas.create_line(x - scale/2, bottom_y - line_offset2,
                           x + scale/2, bottom_y - line_offset2,
                           fill=outline_color, width=line_width)
        # Draw a small triangle on the right side as a clone indicator.
        tri_side = scale * 0.5
        tri_height = (math.sqrt(3) / 2) * tri_side
        att_x = x + scale  # position to the right of the main triangle
        att_y = y - tri_height / 2 - tri_height# adjust vertical position as needed
        v1 = (att_x, att_y)
        v2 = (att_x + tri_side, att_y)
        v3 = (att_x + tri_side/2, att_y - tri_height)
        canvas.create_polygon(v1, v2, v3, fill="lightblue", outline=outline_color,
                              width=line_width)

    def draw_shared_marker(self, canvas, x, y, zoom):
        """Draw a small shared marker at the given canvas coordinates."""
        size = 10 * zoom
        v1 = (x, y)
        v2 = (x - size, y)
        v3 = (x, y - size)
        canvas.create_polygon([v1, v2, v3], fill="black", outline="black")

    def _segment_intersection(self, p1, p2, p3, p4):
        """Return intersection point (x, y, t) of segments *p1*-*p2* and *p3*-*p4* or None."""
        x1, y1 = p1
        x2, y2 = p2
        x3, y3 = p3
        x4, y4 = p4
        denom = (y4 - y3) * (x2 - x1) - (x4 - x3) * (y2 - y1)
        if denom == 0:
            return None
        t = ((x3 - x1) * (y4 - y3) - (y3 - y1) * (x4 - x3)) / denom
        u = ((x3 - x1) * (y2 - y1) - (y3 - y1) * (x2 - x1)) / denom
        if 0 <= t <= 1 and 0 <= u <= 1:
            ix = x1 + t * (x2 - x1)
            iy = y1 + t * (y2 - y1)
            return ix, iy, t
        return None

    def point_on_shape(self, shape, target_pt):
        """Return the intersection of the line to *target_pt* with *shape*."""
        typ = shape.get("type")
        if typ == "circle":
            cx, cy = shape.get("center", (0, 0))
            r = shape.get("radius", 0)
            dx = target_pt[0] - cx
            dy = target_pt[1] - cy
            dist = math.hypot(dx, dy) or 1
            return (cx + dx / dist * r, cy + dy / dist * r)
        elif typ == "rect":
            cx, cy = shape.get("center", (0, 0))
            w = shape.get("width", 0) / 2
            h = shape.get("height", 0) / 2
            dx = target_pt[0] - cx
            dy = target_pt[1] - cy
            if abs(dx) > abs(dy):
                if dx > 0:
                    cx += w
                    cy += dy * (w / abs(dx)) if dx != 0 else 0
                else:
                    cx -= w
                    cy += dy * (w / abs(dx)) if dx != 0 else 0
            else:
                if dy > 0:
                    cy += h
                    cx += dx * (h / abs(dy)) if dy != 0 else 0
                else:
                    cy -= h
                    cx += dx * (h / abs(dy)) if dy != 0 else 0
            return cx, cy
        elif typ == "polygon":
            cx, cy = shape.get("center", (0, 0))
            points = shape.get("points", [])
            if len(points) < 3:
                return target_pt
            best = None
            for i in range(len(points)):
                p3 = points[i]
                p4 = points[(i + 1) % len(points)]
                inter = self._segment_intersection((cx, cy), target_pt, p3, p4)
                if inter:
                    ix, iy, t = inter
                    if best is None or t < best[2]:
                        best = (ix, iy, t)
            if best:
                return best[0], best[1]
        return target_pt

    def draw_90_connection(self, canvas, parent_pt, child_pt, outline_color="dimgray", line_width=1,
                           fixed_length=40, parent_shape=None, child_shape=None):
        """Draw a 90° connection line from a parent point to a child point.

        If *parent_shape* or *child_shape* dictionaries are provided, the start
        and end points are adjusted so the connector touches the object's surface.
        """
        if parent_shape:
            parent_pt = self.point_on_shape(parent_shape, child_pt)
        if child_shape:
            child_pt = self.point_on_shape(child_shape, parent_pt)

        if parent_pt == child_pt:
            size = fixed_length
            x, y = parent_pt
            canvas.create_line(
                x,
                y,
                x,
                y - size,
                x + size,
                y - size,
                x + size,
                y,
                x,
                y,
                fill=outline_color,
                width=line_width,
            )
            return

        fixed_y = parent_pt[1] + fixed_length
        canvas.create_line(parent_pt[0], parent_pt[1], parent_pt[0], fixed_y,
                           fill=outline_color, width=line_width)
        canvas.create_line(parent_pt[0], fixed_y, child_pt[0], fixed_y,
                           fill=outline_color, width=line_width)
        canvas.create_line(child_pt[0], fixed_y, child_pt[0], child_pt[1],
                           fill=outline_color, width=line_width)

    def compute_rotated_and_gate_vertices(self, scale):
        """Compute vertices for a rotated AND gate shape scaled by 'scale'."""
        vertices = [(0, 0), (0, 2), (1, 2)]
        num_points = 50
        for i in range(num_points + 1):
            theta = math.pi / 2 - math.pi * i / num_points
            vertices.append((1 + math.cos(theta), 1 + math.sin(theta)))
        vertices.append((0, 0))
        def rotate_point(pt):
            x, y = pt
            return (2 - y, x)
        rotated = [rotate_point(pt) for pt in vertices]
        translated = [(vx + 2, vy + 1) for (vx, vy) in rotated]
        scaled = [(vx * scale, vy * scale) for (vx, vy) in translated]
        return scaled

    def draw_rotated_and_gate_shape(
        self,
        canvas,
        x,
        y,
        scale=40.0,
        top_text="Desc:\n\nRationale:",
        bottom_text="Event",
        fill="lightgray",
        outline_color="dimgray",
        line_width=1,
        font_obj=None,
        obj_id: str = "",
    ):
        """Draw a rotated AND gate shape with top and bottom text labels."""
        if font_obj is None:
            font_obj = tkFont.Font(family="Arial", size=10)
        raw_verts = self.compute_rotated_and_gate_vertices(scale)
        flipped = [(vx, -vy) for (vx, vy) in raw_verts]
        xs = [v[0] for v in flipped]
        ys = [v[1] for v in flipped]
        cx, cy = (sum(xs) / len(xs), sum(ys) / len(ys))
        final_points = [(vx - cx + x, vy - cy + y) for (vx, vy) in flipped]
        self._fill_gradient_polygon(canvas, final_points, fill)
        canvas.create_polygon(
            final_points,
            fill="",
            outline=outline_color,
            width=line_width,
            smooth=False,
        )

        # Draw the top label box
        t_width, t_height = self.get_text_size(top_text, font_obj)
        padding = 6
        top_box_width = t_width + 2 * padding
        top_box_height = t_height + 2 * padding
        top_y = min(pt[1] for pt in final_points) - top_box_height - 5
        top_box_x = x - top_box_width / 2
        self._fill_gradient_rect(
            canvas,
            top_box_x,
            top_y,
            top_box_x + top_box_width,
            top_y + top_box_height,
            "#CFD8DC",
        )
        canvas.create_rectangle(
            top_box_x,
            top_y,
            top_box_x + top_box_width,
            top_y + top_box_height,
            fill="",
            outline=outline_color,
            width=line_width,
            tags=(obj_id,),
        )
        canvas.create_text(top_box_x + top_box_width / 2,
                           top_y + top_box_height / 2,
                           text=top_text,
                           font=font_obj,
                           anchor="center",
                           width=top_box_width,
                           tags=(obj_id,))

        # Draw the bottom label box
        b_width, b_height = self.get_text_size(bottom_text, font_obj)
        bottom_box_width = b_width + 2 * padding
        bottom_box_height = b_height + 2 * padding
        shape_lowest_y = max(pt[1] for pt in final_points)
        bottom_y = shape_lowest_y - (2 * bottom_box_height)
        bottom_box_x = x - bottom_box_width / 2
        self._fill_gradient_rect(
            canvas,
            bottom_box_x,
            bottom_y,
            bottom_box_x + bottom_box_width,
            bottom_y + bottom_box_height,
            "#CFD8DC",
        )
        canvas.create_rectangle(
            bottom_box_x,
            bottom_y,
            bottom_box_x + bottom_box_width,
            bottom_y + bottom_box_height,
            fill="",
            outline=outline_color,
            width=line_width,
            tags=(obj_id,),
        )
        canvas.create_text(bottom_box_x + bottom_box_width / 2,
                           bottom_y + bottom_box_height / 2,
                           text=bottom_text,
                           font=font_obj,
                           anchor="center",
                           width=bottom_box_width,
                           tags=(obj_id,))

    def draw_rotated_or_gate_shape(
        self,
        canvas,
        x,
        y,
        scale=40.0,
        top_text="Desc:\n\nRationale:",
        bottom_text="Event",
        fill="lightgray",
        outline_color="dimgray",
        line_width=1,
        font_obj=None,
        obj_id: str = "",
    ):
        """Draw a rotated OR gate shape with text labels."""
        if font_obj is None:
            font_obj = tkFont.Font(family="Arial", size=10)
        def cubic_bezier(P0, P1, P2, P3, t):
            return ((1 - t) ** 3 * P0[0] + 3 * (1 - t) ** 2 * t * P1[0] +
                    3 * (1 - t) * t ** 2 * P2[0] + t ** 3 * P3[0],
                    (1 - t) ** 3 * P0[1] + 3 * (1 - t) ** 2 * t * P1[1] +
                    3 * (1 - t) * t ** 2 * P2[1] + t ** 3 * P3[1])
        num_points = 30
        t_values = [i / num_points for i in range(num_points + 1)]
        seg1 = [cubic_bezier((0, 0), (0.6, 0), (0.6, 2), (0, 2), t) for t in t_values]
        seg2 = [cubic_bezier((0, 2), (1, 2), (2, 1.6), (2, 1), t) for t in t_values]
        seg3 = [cubic_bezier((2, 1), (2, 0.4), (1, 0), (0, 0), t) for t in t_values]
        points = seg1[:-1] + seg2[:-1] + seg3
        rotated = [(2 - p[1], p[0]) for p in points]
        translated = [(pt[0] + 2, pt[1] + 1) for pt in rotated]
        scaled = [(sx * scale, sy * scale) for (sx, sy) in translated]
        flipped = [(vx, -vy) for (vx, vy) in scaled]
        xs = [p[0] for p in flipped]
        ys = [p[1] for p in flipped]
        cx, cy = (sum(xs) / len(xs), sum(ys) / len(ys))
        final_points = [(vx - cx + x, vy - cy + y) for (vx, vy) in flipped]
        self._fill_gradient_polygon(canvas, final_points, fill)
        canvas.create_polygon(
            final_points,
            fill="",
            outline=outline_color,
            width=line_width,
            smooth=True,
        )

        # Draw the top label box
        padding = 6
        t_width, t_height = self.get_text_size(top_text, font_obj)
        top_box_width = t_width + 2 * padding
        top_box_height = t_height + 2 * padding
        top_y = min(pt[1] for pt in final_points) - top_box_height - 5
        top_box_x = x - top_box_width / 2
        self._fill_gradient_rect(
            canvas,
            top_box_x,
            top_y,
            top_box_x + top_box_width,
            top_y + top_box_height,
            "#CFD8DC",
        )
        canvas.create_rectangle(
            top_box_x,
            top_y,
            top_box_x + top_box_width,
            top_y + top_box_height,
            fill="",
            outline=outline_color,
            width=line_width,
            tags=(obj_id,),
        )
        canvas.create_text(top_box_x + top_box_width / 2,
                           top_y + top_box_height / 2,
                           text=top_text, font=font_obj, anchor="center",
                           width=top_box_width,
                           tags=(obj_id,))

        # Draw the bottom label box
        b_width, b_height = self.get_text_size(bottom_text, font_obj)
        bottom_box_width = b_width + 2 * padding
        bottom_box_height = b_height + 2 * padding
        shape_lowest_y = max(pt[1] for pt in final_points)
        bottom_y = shape_lowest_y - (2 * bottom_box_height)
        bottom_box_x = x - bottom_box_width / 2
        self._fill_gradient_rect(
            canvas,
            bottom_box_x,
            bottom_y,
            bottom_box_x + bottom_box_width,
            bottom_y + bottom_box_height,
            "#CFD8DC",
        )
        canvas.create_rectangle(
            bottom_box_x,
            bottom_y,
            bottom_box_x + bottom_box_width,
            bottom_y + bottom_box_height,
            fill="",
            outline=outline_color,
            width=line_width,
            tags=(obj_id,),
        )
        canvas.create_text(bottom_box_x + bottom_box_width / 2,
                           bottom_y + bottom_box_height / 2,
                           text=bottom_text, font=font_obj,
                           anchor="center", width=bottom_box_width,
                           tags=(obj_id,))

    def draw_rotated_and_gate_clone_shape(
        self,
        canvas,
        x,
        y,
        scale=40.0,
        top_text="Desc:\n\nRationale:",
        bottom_text="Node",
        fill="lightgray",
        outline_color="dimgray",
        line_width=1,
        font_obj=None,
        obj_id: str = "",
    ):
        """Draw a rotated AND gate shape with additional clone details."""
        self.draw_rotated_and_gate_shape(
            canvas,
            x,
            y,
            scale=scale,
            top_text=top_text,
            bottom_text=bottom_text,
            fill=fill,
            outline_color=outline_color,
            line_width=line_width,
            font_obj=font_obj,
            obj_id=obj_id,
        )
        bottom_y = y + scale * 1.5
        line_offset1 = scale * 0.05
        line_offset2 = scale * 0.1
        canvas.create_line(x - scale/2, bottom_y - line_offset1,
                           x + scale/2, bottom_y - line_offset1,
                           fill=outline_color, width=line_width)
        canvas.create_line(x - scale/2, bottom_y - line_offset2,
                           x + scale/2, bottom_y - line_offset2,
                           fill=outline_color, width=line_width)
        tri_side = scale * 0.5
        tri_height = (math.sqrt(3) / 2) * tri_side
        att_x = x + scale
        att_y = y - tri_height / 2
        v1 = (att_x, att_y)
        v2 = (att_x + tri_side, att_y)
        v3 = (att_x + tri_side / 2, att_y - tri_height)
        canvas.create_polygon(v1, v2, v3, fill="lightblue", outline=outline_color,
                              width=line_width)
        final_line_offset = scale * 0.15
        canvas.create_line(x - scale/2, bottom_y + final_line_offset,
                           x + scale/2, bottom_y + final_line_offset,
                           fill=outline_color, width=line_width)

    def draw_rotated_or_gate_clone_shape(
        self,
        canvas,
        x,
        y,
        scale=40.0,
        top_text="Desc:\n\nRationale:",
        bottom_text="Node",
        fill="lightgray",
        outline_color="dimgray",
        line_width=1,
        font_obj=None,
        obj_id: str = "",
    ):
        """Draw a rotated OR gate shape with additional clone details."""
        self.draw_rotated_or_gate_shape(
            canvas,
            x,
            y,
            scale=scale,
            top_text=top_text,
            bottom_text=bottom_text,
            fill=fill,
            outline_color=outline_color,
            line_width=line_width,
            font_obj=font_obj,
            obj_id=obj_id,
        )
        bottom_y = y + scale * 1.5
        line_offset1 = scale * 0.05
        line_offset2 = scale * 0.1
        canvas.create_line(x - scale/2, bottom_y - line_offset1,
                           x + scale/2, bottom_y - line_offset1,
                           fill=outline_color, width=line_width)
        canvas.create_line(x - scale/2, bottom_y - line_offset2,
                           x + scale/2, bottom_y - line_offset2,
                           fill=outline_color, width=line_width)
        tri_side = scale * 0.5
        tri_height = (math.sqrt(3) / 2) * tri_side
        att_x = x + scale
        att_y = y - tri_height / 2
        v1 = (att_x, att_y)
        v2 = (att_x + tri_side, att_y)
        v3 = (att_x + tri_side / 2, att_y - tri_height)
        canvas.create_polygon(v1, v2, v3, fill="lightblue",
                              outline=outline_color, width=line_width)
        final_line_offset = scale * 0.15
        canvas.create_line(x - scale/2, bottom_y + final_line_offset,
                           x + scale/2, bottom_y + final_line_offset,
                           fill=outline_color, width=line_width)

    def draw_triangle_shape(
        self,
        canvas,
        x,
        y,
        scale=40.0,
        top_text="Desc:\n\nRationale:",
        bottom_text="Event",
        fill="lightgray",
        outline_color="dimgray",
        line_width=1,
        font_obj=None,
        obj_id: str = "",
    ):
        if font_obj is None:
            font_obj = tkFont.Font(family="Arial", size=10)
        effective_scale = scale * 2  
        h = effective_scale * math.sqrt(3) / 2
        v1 = (0, -2 * h / 3)
        v2 = (-effective_scale / 2, h / 3)
        v3 = (effective_scale / 2, h / 3)
        vertices = [
            (x + v1[0], y + v1[1]),
            (x + v2[0], y + v2[1]),
            (x + v3[0], y + v3[1]),
        ]
        self._fill_gradient_polygon(canvas, vertices, fill)
        canvas.create_polygon(vertices, fill="", outline=outline_color, width=line_width)
        
        t_width, t_height = self.get_text_size(top_text, font_obj)
        padding = 6
        top_box_width = t_width + 2 * padding
        top_box_height = t_height + 2 * padding
        top_box_x = x - top_box_width / 2
        top_box_y = min(v[1] for v in vertices) - top_box_height
        self._fill_gradient_rect(
            canvas,
            top_box_x,
            top_box_y,
            top_box_x + top_box_width,
            top_box_y + top_box_height,
            "#CFD8DC",
        )
        canvas.create_rectangle(
            top_box_x,
            top_box_y,
            top_box_x + top_box_width,
            top_box_y + top_box_height,
            fill="",
            outline=outline_color,
            width=line_width,
            tags=(obj_id,),
        )
        canvas.create_text(top_box_x + top_box_width / 2,
                           top_box_y + top_box_height / 2,
                           text=top_text,
                           font=font_obj, anchor="center", width=top_box_width,
                           tags=(obj_id,))
        
        b_width, b_height = self.get_text_size(bottom_text, font_obj)
        bottom_box_width = b_width + 2 * padding
        bottom_box_height = b_height + 2 * padding
        bottom_box_x = x - bottom_box_width / 2
        bottom_box_y = max(v[1] for v in vertices) + padding - 2 * bottom_box_height
        self._fill_gradient_rect(
            canvas,
            bottom_box_x,
            bottom_box_y,
            bottom_box_x + bottom_box_width,
            bottom_box_y + bottom_box_height,
            "#CFD8DC",
        )
        canvas.create_rectangle(
            bottom_box_x,
            bottom_box_y,
            bottom_box_x + bottom_box_width,
            bottom_box_y + bottom_box_height,
            fill="",
            outline=outline_color,
            width=line_width,
            tags=(obj_id,),
        )
        canvas.create_text(bottom_box_x + bottom_box_width / 2,
                           bottom_box_y + bottom_box_height / 2,
                           text=bottom_text,
                           font=font_obj, anchor="center", width=bottom_box_width,
                           tags=(obj_id,))
                           
    def draw_circle_event_shape(
        self,
        canvas,
        x,
        y,
        radius,
        top_text="",
        bottom_text="",
        fill="lightyellow",
        outline_color="dimgray",
        line_width=1,
        font_obj=None,
        base_event=False,
        obj_id: str = "",
    ):
        """Draw a circular event shape with optional text labels."""
        if font_obj is None:
            font_obj = self._scaled_font(radius * 2)
        left = x - radius
        top = y - radius
        right = x + radius
        bottom = y + radius
        self._fill_gradient_circle(canvas, x, y, radius, fill)
        canvas.create_oval(
            left,
            top,
            right,
            bottom,
            fill="",
            outline=outline_color,
            width=line_width,
            tags=(obj_id,),
        )
        t_width, t_height = self.get_text_size(top_text, font_obj)
        padding = 6
        top_box_width = t_width + 2 * padding
        top_box_height = t_height + 2 * padding
        top_box_x = x - top_box_width / 2
        top_box_y = top - top_box_height
        self._fill_gradient_rect(
            canvas,
            top_box_x,
            top_box_y,
            top_box_x + top_box_width,
            top_box_y + top_box_height,
            "#CFD8DC",
        )
        canvas.create_rectangle(
            top_box_x,
            top_box_y,
            top_box_x + top_box_width,
            top_box_y + top_box_height,
            fill="",
            outline=outline_color,
            width=line_width,
            tags=(obj_id,),
        )
        canvas.create_text(top_box_x + top_box_width / 2,
                           top_box_y + top_box_height / 2,
                           text=top_text,
                           font=font_obj, anchor="center",
                           width=top_box_width,
                           tags=(obj_id,))
        b_width, b_height = self.get_text_size(bottom_text, font_obj)
        bottom_box_width = b_width + 2 * padding
        bottom_box_height = b_height + 2 * padding
        bottom_box_x = x - bottom_box_width / 2
        bottom_box_y = bottom - 2 * bottom_box_height
        self._fill_gradient_rect(
            canvas,
            bottom_box_x,
            bottom_box_y,
            bottom_box_x + bottom_box_width,
            bottom_box_y + bottom_box_height,
            "#CFD8DC",
        )
        canvas.create_rectangle(
            bottom_box_x,
            bottom_box_y,
            bottom_box_x + bottom_box_width,
            bottom_box_y + bottom_box_height,
            fill="",
            outline=outline_color,
            width=line_width,
            tags=(obj_id,),
        )
        canvas.create_text(bottom_box_x + bottom_box_width / 2,
                           bottom_box_y + bottom_box_height / 2,
                           text=bottom_text,
                           font=font_obj, anchor="center",
                           width=bottom_box_width,
                           tags=(obj_id,))
                           
    def draw_triangle_clone_shape(
        self,
        canvas,
        x,
        y,
        scale=40.0,
        top_text="Desc:\n\nRationale:",
        bottom_text="Node",
        fill="lightgray",
        outline_color="dimgray",
        line_width=1,
        font_obj=None,
        obj_id: str = "",
    ):
        """
        Draws the same triangle as draw_triangle_shape but then adds two horizontal lines
        at the bottom and a small triangle on the right side as clone indicators.
        The small triangle is now positioned so that its top vertex aligns with the top of
        the big triangle.
        """
        if font_obj is None:
            font_obj = tkFont.Font(family="Arial", size=10)
        # Draw the base triangle.
        self.draw_triangle_shape(
            canvas,
            x,
            y,
            scale=scale,
            top_text=top_text,
            bottom_text=bottom_text,
            fill=fill,
            outline_color=outline_color,
            line_width=line_width,
            font_obj=font_obj,
            obj_id=obj_id,
        )
        # Compute the vertices of the big triangle.
        effective_scale = scale * 2  
        h = effective_scale * math.sqrt(3) / 2
        v1 = (0, -2 * h / 3)
        v2 = (-effective_scale / 2, h / 3)
        v3 = (effective_scale / 2, h / 3)
        vertices = [(x + v1[0], y + v1[1]),
                    (x + v2[0], y + v2[1]),
                    (x + v3[0], y + v3[1])]
        # Compute the bottom and top y-values of the big triangle.
        bottom_y = max(v[1] for v in vertices) + scale * 0.2
        top_y = min(v[1] for v in vertices)  # top edge of the big triangle
        half_width = effective_scale / 2  # equals 'scale'
        
        # Draw two horizontal lines at the bottom (unchanged).
        line_offset1 = scale * 0.05
        line_offset2 = scale * 0.1
        canvas.create_line(x - half_width, bottom_y - line_offset1,
                           x + half_width, bottom_y - line_offset1,
                           fill=outline_color, width=line_width)
        canvas.create_line(x - half_width, bottom_y - line_offset2,
                           x + half_width, bottom_y - line_offset2,
                           fill=outline_color, width=line_width)
        
        # Draw the small clone indicator triangle.
        tri_side = scale * 0.5
        tri_height = (math.sqrt(3) / 2) * tri_side
        att_x = x + half_width
        # Instead of basing its vertical position on bottom_y, we now align it with top_y.
        # We want the top vertex of the small triangle (which is at att_y - tri_height)
        # to equal top_y. Thus, set att_y - tri_height = top_y, so:
        att_y = top_y + tri_height
        v1_small = (att_x, att_y)
        v2_small = (att_x + tri_side, att_y)
        v3_small = (att_x + tri_side/2, att_y - tri_height)
        canvas.create_polygon(v1_small, v2_small, v3_small,
                              fill="lightblue", outline=outline_color,
                              width=line_width)
        
        # Draw the final horizontal line below the bottom.
        final_line_offset = scale * 0.15
        canvas.create_line(x - half_width, bottom_y + final_line_offset,
                           x + half_width, bottom_y + final_line_offset,
                           fill=outline_color, width=line_width)
                           
# Create a single FTADrawingHelper object that can be used by other classes
fta_drawing_helper = FTADrawingHelper()

class GSNDrawingHelper(FTADrawingHelper):
    """Drawing helper providing shapes for GSN argumentation diagrams."""

    def _scaled_font(self, scale: float) -> tkFont.Font:
        """Return a font scaled proportionally to *scale*."""
        size = max(1, int(scale / 4))
        return tkFont.Font(family="Arial", size=size)

    def draw_goal_shape(
        self,
        canvas,
        x,
        y,
        scale=60.0,
        text="Goal",
        fill="lightyellow",
        outline_color="dimgray",
        line_width=1,
        font_obj=None,
        obj_id: str = "",
    ):
        if font_obj is None:
            font_obj = self._scaled_font(scale)
        padding = 4
        t_width, t_height = self.get_text_size(text, font_obj)
        w = max(scale, t_width + 2 * padding)
        h = max(scale * 0.6, t_height + 2 * padding)
        left = x - w / 2
        top = y - h / 2
        right = x + w / 2
        bottom = y + h / 2
        self._fill_gradient_rect(canvas, left, top, right, bottom, fill)
        canvas.create_rectangle(
            left,
            top,
            right,
            bottom,
            fill="",
            outline=outline_color,
            width=line_width,
            tags=(obj_id,),
        )
        canvas.create_text(
            x,
            y,
            text=text,
            font=font_obj,
            anchor="center",
            width=w - 2 * padding,
            tags=(obj_id,),
        )

    def draw_solved_by_connection(
        self,
        canvas,
        parent_pt,
        child_pt,
        outline_color="dimgray",
        line_width=1,
    ):
        """Draw a curved connector indicating a 'solved by' relationship."""
        px, py = parent_pt
        cx, cy = child_pt
        if parent_pt == child_pt:
            size = 20
            canvas.create_line(
                px,
                py,
                px,
                py - size,
                px + size,
                py - size,
                px + size,
                py,
                px,
                py,
                fill=outline_color,
                width=line_width,
                arrow=tk.LAST,
            )
            return
        offset = (cy - py) / 2
        canvas.create_line(
            px,
            py,
            px,
            py + offset,
            cx,
            cy - offset,
            cx,
            cy,
            smooth=True,
            fill=outline_color,
            width=line_width,
            arrow=tk.LAST,
        )

    def draw_in_context_connection(
        self,
        canvas,
        parent_pt,
        child_pt,
        outline_color="dimgray",
        line_width=1,
    ):
        """Draw a dashed curved connector for an 'in context of' relationship."""
        px, py = parent_pt
        cx, cy = child_pt
        offset = (cy - py) / 2
        dash = (4, 2)
        if parent_pt == child_pt:
            size = 20
            canvas.create_line(
                px,
                py,
                px,
                py - size,
                px + size,
                py - size,
                px + size,
                py,
                px,
                py,
                fill=outline_color,
                width=line_width,
                dash=dash,
            )
            return
        canvas.create_line(
            px,
            py,
            px,
            py + offset,
            cx,
            cy - offset,
            cx,
            cy,
            smooth=True,
            fill=outline_color,
            width=line_width,
            dash=dash,
        )

    def draw_strategy_shape(
        self,
        canvas,
        x,
        y,
        scale=60.0,
        text="Strategy",
        fill="lightyellow",
        outline_color="dimgray",
        line_width=1,
        font_obj=None,
        obj_id: str = "",
    ):
        if font_obj is None:
            font_obj = self._scaled_font(scale)
        padding = 4
        t_width, t_height = self.get_text_size(text, font_obj)
        w = max(scale, t_width + 2 * padding)
        h = max(scale * 0.5, t_height + 2 * padding)
        offset = w * 0.2
        points = [
            (x - w / 2 + offset, y - h / 2),
            (x + w / 2, y - h / 2),
            (x + w / 2 - offset, y + h / 2),
            (x - w / 2, y + h / 2),
        ]
        self._fill_gradient_polygon(canvas, points, fill)
        canvas.create_polygon(points, outline=outline_color, width=line_width, fill="", tags=(obj_id,))
        canvas.create_text(
            x,
            y,
            text=text,
            font=font_obj,
            anchor="center",
            width=w - 2 * padding,
            tags=(obj_id,),
        )

    def draw_solution_shape(
        self,
        canvas,
        x,
        y,
        scale=40.0,
        text="Solution",
        fill="lightyellow",
        outline_color="dimgray",
        line_width=1,
        font_obj=None,
        obj_id: str = "",
    ):
        radius = scale / 2
        if font_obj is None:
            font_obj = self._scaled_font(scale)
        left = x - radius
        top = y - radius
        right = x + radius
        bottom = y + radius
        self._fill_gradient_circle(canvas, x, y, radius, fill)
        canvas.create_oval(
            left,
            top,
            right,
            bottom,
            fill="",
            outline=outline_color,
            width=line_width,
            tags=(obj_id,),
        )
        canvas.create_text(
            x,
            y,
            text=text,
            font=font_obj,
            anchor="center",
            width=scale - 8,
            tags=(obj_id,),
        )

    def draw_assumption_shape(
        self,
        canvas,
        x,
        y,
        scale=60.0,
        text="Assumption",
        fill="lightyellow",
        outline_color="dimgray",
        line_width=1,
        font_obj=None,
        obj_id: str = "",
    ):
        if font_obj is None:
            font_obj = self._scaled_font(scale)
        padding = 4
        t_width, t_height = self.get_text_size(text, font_obj)
        w = max(scale, t_width + 2 * padding)
        h = max(scale * 0.5, t_height + 2 * padding)
        left = x - w / 2
        top = y - h / 2
        right = x + w / 2
        bottom = y + h / 2
        self._fill_gradient_rect(canvas, left, top, right, bottom, fill)
        canvas.create_rectangle(
            left,
            top,
            right,
            bottom,
            fill="",
            outline=outline_color,
            dash=(4, 2),
            width=line_width,
            tags=(obj_id,),
        )
        canvas.create_text(
            x,
            y,
            text=text,
            font=font_obj,
            anchor="center",
            width=w - 2 * padding,
            tags=(obj_id,),
        )

    def draw_justification_shape(
        self,
        canvas,
        x,
        y,
        scale=60.0,
        text="Justification",
        fill="lightyellow",
        outline_color="dimgray",
        line_width=1,
        font_obj=None,
        obj_id: str = "",
    ):
        if font_obj is None:
            font_obj = self._scaled_font(scale)
        padding = 4
        t_width, t_height = self.get_text_size(text, font_obj)
        w = max(scale, t_width + 2 * padding)
        h = max(scale * 0.5, t_height + 2 * padding)
        left = x - w / 2
        top = y - h / 2
        right = x + w / 2
        bottom = y + h / 2
        self._fill_gradient_rect(canvas, left, top, right, bottom, fill)
        canvas.create_rectangle(
            left,
            top,
            right,
            bottom,
            fill="",
            outline=outline_color,
            width=line_width,
            tags=(obj_id,),
        )
        inset = 4
        canvas.create_rectangle(
            left + inset,
            top + inset,
            right - inset,
            bottom - inset,
            outline=outline_color,
            width=line_width,
        )
        canvas.create_text(
            x,
            y,
            text=text,
            font=font_obj,
            anchor="center",
            width=w - 2 * padding,
            tags=(obj_id,),
        )

    def draw_context_shape(
        self,
        canvas,
        x,
        y,
        scale=60.0,
        text="Context",
        fill="lightyellow",
        outline_color="dimgray",
        line_width=1,
        font_obj=None,
        obj_id: str = "",
    ):
        if font_obj is None:
            font_obj = self._scaled_font(scale)
        padding = 4
        t_width, t_height = self.get_text_size(text, font_obj)
        w = max(scale, t_width + 2 * padding)
        h = max(scale * 0.5, t_height + 2 * padding)
        left = x - w / 2
        top = y - h / 2
        right = x + w / 2
        bottom = y + h / 2
        self._fill_gradient_rect(canvas, left, top, right, bottom, fill)
        canvas.create_rectangle(
            left,
            top,
            right,
            bottom,
            fill="",
            outline=outline_color,
            width=line_width,
            tags=(obj_id,),
        )
        canvas.create_text(
            x,
            y,
            text=text,
            font=font_obj,
            anchor="center",
            width=w - 2 * padding,
            tags=(obj_id,),
        )

    def draw_away_solution_shape(self, canvas, x, y, scale=40.0, **kwargs):
        self.draw_solution_shape(canvas, x, y, scale=scale, **kwargs)
        radius = scale / 2
        self.draw_shared_marker(canvas, x + radius, y - radius, 1)

    def draw_away_goal_shape(self, canvas, x, y, scale=60.0, **kwargs):
        self.draw_goal_shape(canvas, x, y, scale=scale, **kwargs)
        self.draw_shared_marker(canvas, x + scale / 2, y - scale * 0.3, 1)

    def draw_away_module_shape(self, canvas, x, y, scale=60.0, **kwargs):
        self.draw_goal_shape(canvas, x, y, scale=scale, **kwargs)
        self.draw_shared_marker(canvas, x + scale / 2, y - scale * 0.3, 1)


# Create a single GSNDrawingHelper object for convenience

gsn_drawing_helper = GSNDrawingHelper()
