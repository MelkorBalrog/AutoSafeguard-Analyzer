# Author: Miguel Marina <karel.capek.robotics@gmail.com>
import math
import tkinter.font as tkFont

class FTADrawingHelper:
    """
    A helper class that provides drawing functions for fault tree diagrams.
    These methods can be used to draw shapes (gates, events, connectors, etc.)
    onto a tkinter Canvas.
    """
    def __init__(self):
        pass

    def get_text_size(self, text, font_obj):
        """Return the (width, height) in pixels needed to render the text with the given font."""
        lines = text.split("\n")
        max_width = max(font_obj.measure(line) for line in lines)
        height = font_obj.metrics("linespace") * len(lines)
        return max_width, height

    def draw_page_clone_shape(self, canvas, x, y, scale=40.0,
                              top_text="Desc:\n\nRationale:", bottom_text="Node",
                              fill="lightgray", outline_color="dimgray",
                              line_width=1, font_obj=None):
        # First, draw the main triangle using the existing triangle routine.
        self.draw_triangle_shape(canvas, x, y, scale=scale,
                                 top_text=top_text, bottom_text=bottom_text,
                                 fill=fill, outline_color=outline_color,
                                 line_width=line_width, font_obj=font_obj)
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

    def draw_90_connection(self, canvas, parent_pt, child_pt, outline_color="dimgray", line_width=1, fixed_length=40):
        """Draw a 90° connection line from a parent point to a child point."""
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

    def draw_rotated_and_gate_shape(self, canvas, x, y, scale=40.0,
                                      top_text="Desc:\n\nRationale:",
                                      bottom_text="Event",
                                      fill="lightgray", outline_color="dimgray",
                                      line_width=1, font_obj=None):
        """Draw a rotated AND gate shape with top and bottom text labels."""
        if font_obj is None:
            font_obj = tkFont.Font(family="Arial", size=10)
        raw_verts = self.compute_rotated_and_gate_vertices(scale)
        flipped = [(vx, -vy) for (vx, vy) in raw_verts]
        xs = [v[0] for v in flipped]
        ys = [v[1] for v in flipped]
        cx, cy = (sum(xs) / len(xs), sum(ys) / len(ys))
        final_points = [(vx - cx + x, vy - cy + y) for (vx, vy) in flipped]
        canvas.create_polygon(final_points, fill=fill, outline=outline_color,
                                width=line_width, smooth=False)

        # Draw the top label box
        t_width, t_height = self.get_text_size(top_text, font_obj)
        padding = 6
        top_box_width = t_width + 2 * padding
        top_box_height = t_height + 2 * padding
        top_y = min(pt[1] for pt in final_points) - top_box_height - 5
        top_box_x = x - top_box_width / 2
        canvas.create_rectangle(top_box_x, top_y,
                                top_box_x + top_box_width,
                                top_y + top_box_height,
                                fill="lightblue", outline=outline_color,
                                width=line_width)
        canvas.create_text(top_box_x + top_box_width / 2,
                           top_y + top_box_height / 2,
                           text=top_text,
                           font=font_obj,
                           anchor="center",
                           width=top_box_width)

        # Draw the bottom label box
        b_width, b_height = self.get_text_size(bottom_text, font_obj)
        bottom_box_width = b_width + 2 * padding
        bottom_box_height = b_height + 2 * padding
        shape_lowest_y = max(pt[1] for pt in final_points)
        bottom_y = shape_lowest_y - (2 * bottom_box_height)
        bottom_box_x = x - bottom_box_width / 2
        canvas.create_rectangle(bottom_box_x, bottom_y,
                                bottom_box_x + bottom_box_width,
                                bottom_y + bottom_box_height,
                                fill="lightblue", outline=outline_color,
                                width=line_width)
        canvas.create_text(bottom_box_x + bottom_box_width / 2,
                           bottom_y + bottom_box_height / 2,
                           text=bottom_text,
                           font=font_obj,
                           anchor="center",
                           width=bottom_box_width)

    def draw_rotated_or_gate_shape(self, canvas, x, y, scale=40.0,
                                     top_text="Desc:\n\nRationale:",
                                     bottom_text="Event",
                                     fill="lightgray", outline_color="dimgray",
                                     line_width=1, font_obj=None):
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
        canvas.create_polygon(final_points, fill=fill, outline=outline_color,
                                width=line_width, smooth=True)

        # Draw the top label box
        padding = 6
        t_width, t_height = self.get_text_size(top_text, font_obj)
        top_box_width = t_width + 2 * padding
        top_box_height = t_height + 2 * padding
        top_y = min(pt[1] for pt in final_points) - top_box_height - 5
        top_box_x = x - top_box_width / 2
        canvas.create_rectangle(top_box_x, top_y,
                                top_box_x + top_box_width,
                                top_y + top_box_height,
                                fill="lightblue", outline=outline_color, width=line_width)
        canvas.create_text(top_box_x + top_box_width / 2,
                           top_y + top_box_height / 2,
                           text=top_text, font=font_obj, anchor="center",
                           width=top_box_width)

        # Draw the bottom label box
        b_width, b_height = self.get_text_size(bottom_text, font_obj)
        bottom_box_width = b_width + 2 * padding
        bottom_box_height = b_height + 2 * padding
        shape_lowest_y = max(pt[1] for pt in final_points)
        bottom_y = shape_lowest_y - (2 * bottom_box_height)
        bottom_box_x = x - bottom_box_width / 2
        canvas.create_rectangle(bottom_box_x, bottom_y,
                                bottom_box_x + bottom_box_width,
                                bottom_y + bottom_box_height,
                                fill="lightblue", outline=outline_color,
                                width=line_width)
        canvas.create_text(bottom_box_x + bottom_box_width / 2,
                           bottom_y + bottom_box_height / 2,
                           text=bottom_text, font=font_obj,
                           anchor="center", width=bottom_box_width)

    def draw_rotated_and_gate_clone_shape(self, canvas, x, y, scale=40.0,
                                            top_text="Desc:\n\nRationale:", bottom_text="Node",
                                            fill="lightgray", outline_color="dimgray",
                                            line_width=1, font_obj=None):
        """Draw a rotated AND gate shape with additional clone details."""
        self.draw_rotated_and_gate_shape(canvas, x, y, scale=scale,
                                         top_text=top_text, bottom_text=bottom_text,
                                         fill=fill, outline_color=outline_color,
                                         line_width=line_width, font_obj=font_obj)
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

    def draw_rotated_or_gate_clone_shape(self, canvas, x, y, scale=40.0,
                                           top_text="Desc:\n\nRationale:", bottom_text="Node",
                                           fill="lightgray", outline_color="dimgray",
                                           line_width=1, font_obj=None):
        """Draw a rotated OR gate shape with additional clone details."""
        self.draw_rotated_or_gate_shape(canvas, x, y, scale=scale,
                                        top_text=top_text, bottom_text=bottom_text,
                                        fill=fill, outline_color=outline_color,
                                        line_width=line_width, font_obj=font_obj)
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

    def draw_triangle_shape(self, canvas, x, y, scale=40.0,
                              top_text="Desc:\n\nRationale:",
                              bottom_text="Event",
                              fill="lightgray", outline_color="dimgray",
                              line_width=1, font_obj=None):
        if font_obj is None:
            font_obj = tkFont.Font(family="Arial", size=10)
        effective_scale = scale * 2  
        h = effective_scale * math.sqrt(3) / 2
        v1 = (0, -2 * h / 3)
        v2 = (-effective_scale / 2, h / 3)
        v3 = (effective_scale / 2, h / 3)
        vertices = [(x + v1[0], y + v1[1]),
                    (x + v2[0], y + v2[1]),
                    (x + v3[0], y + v3[1])]
        canvas.create_polygon(vertices, fill=fill, outline=outline_color, width=line_width)
        
        t_width, t_height = self.get_text_size(top_text, font_obj)
        padding = 6
        top_box_width = t_width + 2 * padding
        top_box_height = t_height + 2 * padding
        top_box_x = x - top_box_width / 2
        top_box_y = min(v[1] for v in vertices) - top_box_height
        canvas.create_rectangle(top_box_x, top_box_y,
                                top_box_x + top_box_width,
                                top_box_y + top_box_height,
                                fill="lightblue", outline=outline_color, width=line_width)
        canvas.create_text(top_box_x + top_box_width / 2,
                           top_box_y + top_box_height / 2,
                           text=top_text,
                           font=font_obj, anchor="center", width=top_box_width)
        
        b_width, b_height = self.get_text_size(bottom_text, font_obj)
        bottom_box_width = b_width + 2 * padding
        bottom_box_height = b_height + 2 * padding
        bottom_box_x = x - bottom_box_width / 2
        bottom_box_y = max(v[1] for v in vertices) + padding - 2 * bottom_box_height
        canvas.create_rectangle(bottom_box_x, bottom_box_y,
                                bottom_box_x + bottom_box_width,
                                bottom_box_y + bottom_box_height,
                                fill="lightblue", outline=outline_color, width=line_width)
        canvas.create_text(bottom_box_x + bottom_box_width / 2,
                           bottom_box_y + bottom_box_height / 2,
                           text=bottom_text,
                           font=font_obj, anchor="center", width=bottom_box_width)
                           
    def draw_circle_event_shape(self, canvas, x, y, radius,
                                top_text="",
                                bottom_text="",
                                fill="lightyellow",
                                outline_color="dimgray",
                                line_width=1,
                                font_obj=None,
                                base_event=False):
        """Draw a circular event shape with optional text labels."""
        if font_obj is None:
            font_obj = tkFont.Font(family="Arial", size=10)
        left = x - radius
        top = y - radius
        right = x + radius
        bottom = y + radius
        canvas.create_oval(left, top, right, bottom, fill=fill,
                           outline=outline_color, width=line_width)
        t_width, t_height = self.get_text_size(top_text, font_obj)
        padding = 6
        top_box_width = t_width + 2 * padding
        top_box_height = t_height + 2 * padding
        top_box_x = x - top_box_width / 2
        top_box_y = top - top_box_height
        canvas.create_rectangle(top_box_x, top_box_y,
                                top_box_x + top_box_width,
                                top_box_y + top_box_height,
                                fill="lightblue", outline=outline_color,
                                width=line_width)
        canvas.create_text(top_box_x + top_box_width / 2,
                           top_box_y + top_box_height / 2,
                           text=top_text,
                           font=font_obj, anchor="center",
                           width=top_box_width)
        b_width, b_height = self.get_text_size(bottom_text, font_obj)
        bottom_box_width = b_width + 2 * padding
        bottom_box_height = b_height + 2 * padding
        bottom_box_x = x - bottom_box_width / 2
        bottom_box_y = bottom - 2 * bottom_box_height
        canvas.create_rectangle(bottom_box_x, bottom_box_y,
                                bottom_box_x + bottom_box_width,
                                bottom_box_y + bottom_box_height,
                                fill="lightblue", outline=outline_color,
                                width=line_width)
        canvas.create_text(bottom_box_x + bottom_box_width / 2,
                           bottom_box_y + bottom_box_height / 2,
                           text=bottom_text,
                           font=font_obj, anchor="center",
                           width=bottom_box_width)
                           
    def draw_triangle_clone_shape(self, canvas, x, y, scale=40.0,
                                  top_text="Desc:\n\nRationale:", bottom_text="Node",
                                  fill="lightgray", outline_color="dimgray",
                                  line_width=1, font_obj=None):
        """
        Draws the same triangle as draw_triangle_shape but then adds two horizontal lines
        at the bottom and a small triangle on the right side as clone indicators.
        The small triangle is now positioned so that its top vertex aligns with the top of
        the big triangle.
        """
        if font_obj is None:
            font_obj = tkFont.Font(family="Arial", size=10)
        # Draw the base triangle.
        self.draw_triangle_shape(canvas, x, y, scale=scale,
                                 top_text=top_text, bottom_text=bottom_text,
                                 fill=fill, outline_color=outline_color,
                                 line_width=line_width, font_obj=font_obj)
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
