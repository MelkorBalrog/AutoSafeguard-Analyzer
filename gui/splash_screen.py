import tkinter as tk
import math


class SplashScreen(tk.Toplevel):
    """Simple splash screen with rotating cube and gear."""

    def __init__(
        self,
        master,
        version: str = "Unknown",
        author: str = "Your Name",
        email: str = "email@example.com",
        linkedin: str = "https://www.linkedin.com/in/yourprofile",
        duration: int = 3000,
        auto_start: bool = True,
    ):
        super().__init__(master)
        self.duration = duration
        self.overrideredirect(True)

        # Track whether transparency is supported
        try:
            self.attributes("-alpha", 0.0)
            self._alpha_supported = True
        except tk.TclError:
            self._alpha_supported = False

        # Shadow window to create simple 3D effect
        self.shadow = tk.Toplevel(master)
        self.shadow.overrideredirect(True)
        self.shadow.configure(bg="black")
        self._shadow_alpha_target = 0.3
        try:
            # Start fully transparent for fade in
            self.shadow.attributes("-alpha", 0.0)
        except tk.TclError:
            self._shadow_alpha_target = None

        self.canvas_size = 300
        # Black background so colors pop
        self.canvas = tk.Canvas(
            self,
            width=self.canvas_size,
            height=self.canvas_size,
            highlightthickness=0,
            bg="black",
        )
        self.canvas.pack()
        self._draw_gradient()
        self._center()
        # Initialize cube geometry
        self.angle = 0.0
        self.vertices = [
            (-1, -1, -1),
            (1, -1, -1),
            (1, 1, -1),
            (-1, 1, -1),
            (-1, -1, 1),
            (1, -1, 1),
            (1, 1, 1),
            (-1, 1, 1),
        ]
        self.edges = [
            (0, 1), (1, 2), (2, 3), (3, 0),
            (4, 5), (5, 6), (6, 7), (7, 4),
            (0, 4), (1, 5), (2, 6), (3, 7),
        ]
        # Text at bottom center
        self.canvas.create_text(
            self.canvas_size / 2,
            self.canvas_size - 40,
            text="Automotive Modeling Language\nby\nKarel Capek Robotics",
            justify="center",
            font=("Helvetica", 12),
            fill="white",
        )

        # Version and author info at top right
        info_text = f"v{version}\n{author}\n{email}\n{linkedin}"
        self.canvas.create_text(
            self.canvas_size - 10,
            10,
            text=info_text,
            anchor="ne",
            justify="right",
            font=("Helvetica", 9),
            fill="white",
        )
        # Start animation and fade-in effect
        if auto_start:
            self.after(10, self._animate)
            self.after(10, self._fade_in)

    def _fade_in(self):
        if not getattr(self, "_alpha_supported", False):
            self.after(self.duration, self._close)
            return
        alpha = min(self.attributes("-alpha") + 0.05, 1.0)
        self.attributes("-alpha", alpha)
        if self._shadow_alpha_target is not None:
            try:
                self.shadow.attributes("-alpha", alpha * self._shadow_alpha_target)
            except tk.TclError:
                pass
        if alpha < 1.0:
            self.after(50, self._fade_in)
        else:
            self.after(self.duration, self._fade_out)

    def _fade_out(self):
        if not getattr(self, "_alpha_supported", False):
            self._close()
            return
        alpha = max(self.attributes("-alpha") - 0.05, 0.0)
        self.attributes("-alpha", alpha)
        if self._shadow_alpha_target is not None:
            try:
                self.shadow.attributes("-alpha", alpha * self._shadow_alpha_target)
            except tk.TclError:
                pass
        if alpha > 0.0:
            self.after(50, self._fade_out)
        else:
            self._close()

    def _center(self):
        self.update_idletasks()
        w = self.canvas_size
        h = self.canvas_size
        x = (self.winfo_screenwidth() // 2) - (w // 2)
        y = (self.winfo_screenheight() // 2) - (h // 2)
        # Position shadow slightly offset from the splash window
        self.shadow.geometry(f"{w}x{h}+{x + 5}+{y + 5}")
        self.geometry(f"{w}x{h}+{x}+{y}")
        self.shadow.lower(self)

    def _draw_gradient(self):
        """Draw a gradient with a horizon to give depth."""
        def lerp(a: int, b: int, t: float) -> int:
            return int(a + (b - a) * t)

        steps = self.canvas_size
        horizon = int(steps * 0.6)
        for i in range(steps):
            if i < horizon:
                t = i / horizon
                r = lerp(10, 135, t)
                g = lerp(10, 206, t)
                b = lerp(30, 235, t)
            else:
                t = (i - horizon) / (steps - horizon)
                r = lerp(222, 0, t)
                g = lerp(184, 0, t)
                b = lerp(135, 0, t)
            color = f"#{r:02x}{g:02x}{b:02x}"
            self.canvas.create_line(0, i, self.canvas_size, i, fill=color)
        self.canvas.create_line(
            0,
            horizon,
            self.canvas_size,
            horizon,
            fill="white",
            width=2,
            tags="horizon",
        )

    def _project(self, x, y, z):
        """Project 3D point onto 2D canvas."""
        distance = 5
        factor = self.canvas_size / (2 * (z + distance))
        x = x * factor + self.canvas_size / 2
        y = y * factor + self.canvas_size / 2
        return x, y

    def _draw_cube(self):
        self.canvas.delete("cube")
        self.canvas.delete("shadow")
        self.canvas.delete("cube_face")
        # Simple oval shadow to give cube a floating appearance
        shadow_w = 80
        shadow_h = 20
        cx = self.canvas_size / 2
        cy = self.canvas_size / 2 + 60
        self.canvas.create_oval(
            cx - shadow_w / 2,
            cy - shadow_h / 2,
            cx + shadow_w / 2,
            cy + shadow_h / 2,
            fill="black",
            outline="",
            tags="shadow",
            stipple="gray50",
        )
        angle = math.radians(self.angle)
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        points = []
        for x, y, z in self.vertices:
            x1 = x * cos_a - z * sin_a
            z1 = x * sin_a + z * cos_a
            y1 = y * cos_a - z1 * sin_a
            z2 = y * sin_a + z1 * cos_a
            points.append(self._project(x1, y1, z2))

        faces = [
            (0, 1, 2, 3),
            (4, 5, 6, 7),
            (0, 1, 5, 4),
            (2, 3, 7, 6),
            (1, 2, 6, 5),
            (0, 3, 7, 4),
        ]
        for face in faces:
            coords = []
            for idx in face:
                coords.extend(points[idx])
            self.canvas.create_polygon(
                *coords,
                fill="cyan",
                outline="",
                stipple="gray25",
                tags=("cube_face", "cube"),
            )
        fx1, fy1 = points[4]
        fx2, fy2 = points[6]
        self.canvas.create_line(
            fx1,
            fy1,
            fx2,
            fy2,
            fill="white",
            width=2,
            tags=("cube_shine", "cube"),
            stipple="gray25",
        )
        for i, j in self.edges:
            x1, y1 = points[i]
            x2, y2 = points[j]
            self.canvas.create_line(
                x1,
                y1,
                x2,
                y2,
                fill="cyan",
                width=2,
                tags="cube",
            )

    def _draw_gear(self):
        self.canvas.delete("gear")
        self.canvas.delete("gear_glow")
        teeth = 8
        inner = 20
        outer = 30
        pts = []
        angle = math.radians(self.angle * 2)
        for i in range(teeth * 2):
            r = outer if i % 2 == 0 else inner
            theta = angle + i * math.pi / teeth
            x = self.canvas_size / 2 + r * math.cos(theta)
            y = self.canvas_size / 2 + r * math.sin(theta)
            pts.append((x, y))
        self.canvas.create_polygon(
            pts,
            outline="#00ffff",
            fill="",
            width=6,
            tags="gear_glow",
        )
        self.canvas.create_polygon(
            pts,
            outline="lightgray",
            fill="",
            width=2,
            tags="gear",
        )

    def _animate(self):
        self.angle = (self.angle + 2) % 360
        self._draw_cube()
        self._draw_gear()
        self.after(50, self._animate)

    def _close(self):
        """Destroy splash screen and accompanying shadow window."""
        try:
            self.shadow.destroy()
        except Exception:
            pass
        self.destroy()
