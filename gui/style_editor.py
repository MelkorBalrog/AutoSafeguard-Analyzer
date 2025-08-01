import tkinter as tk
from tkinter import colorchooser, filedialog, messagebox
from .style_manager import StyleManager

class StyleEditor(tk.Toplevel):
    """Simple editor for diagram style colors."""

    def __init__(self, master=None):
        super().__init__(master)
        self.title("Style Editor")
        self.manager = StyleManager.get_instance()
        self.entries = {}
        row = 0
        for obj_type in sorted(self.manager.styles.keys()):
            tk.Label(self, text=obj_type).grid(row=row, column=0, sticky="w", padx=4, pady=2)
            ent = tk.Entry(self)
            ent.insert(0, self.manager.styles[obj_type])
            ent.grid(row=row, column=1, padx=4, pady=2)
            btn = tk.Button(self, text="...", command=lambda t=obj_type: self.choose_color(t))
            btn.grid(row=row, column=2, padx=2)
            self.entries[obj_type] = ent
            row += 1
        btn_frame = tk.Frame(self)
        btn_frame.grid(row=row, columnspan=3, pady=8)
        tk.Button(btn_frame, text="Save As...", command=self.save).pack(side=tk.LEFT, padx=4)
        tk.Button(btn_frame, text="Load", command=self.load).pack(side=tk.LEFT, padx=4)
        tk.Button(btn_frame, text="Apply", command=self.apply).pack(side=tk.LEFT, padx=4)
        tk.Button(btn_frame, text="Close", command=self.destroy).pack(side=tk.LEFT, padx=4)

    def choose_color(self, obj_type):
        cur = self.entries[obj_type].get()
        color = colorchooser.askcolor(color=cur, parent=self)[1]
        if color:
            self.entries[obj_type].delete(0, tk.END)
            self.entries[obj_type].insert(0, color)

    def apply(self):
        for t, ent in self.entries.items():
            self.manager.styles[t] = ent.get()
        if hasattr(self.master, 'redraw'):
            self.master.redraw()
        if self.master:
            self.master.event_generate('<<StyleChanged>>', when='tail')

    def save(self):
        self.apply()
        path = filedialog.asksaveasfilename(defaultextension='.xml', filetypes=[('Style XML', '*.xml')])
        if path:
            self.manager.save_style(path)
            messagebox.showinfo('Style Editor', 'Style saved to ' + path)

    def load(self):
        path = filedialog.askopenfilename(filetypes=[('Style XML', '*.xml')])
        if path:
            self.manager.load_style(path)
            for t, ent in self.entries.items():
                ent.delete(0, tk.END)
                ent.insert(0, self.manager.styles.get(t, ''))
            if hasattr(self.master, 'redraw'):
                self.master.redraw()
            if self.master:
                self.master.event_generate('<<StyleChanged>>', when='tail')
