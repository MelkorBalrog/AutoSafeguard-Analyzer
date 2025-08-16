# SPDX-License-Identifier: GPL-3.0-or-later
# Author: OpenAI Assistant
#
# A simple editor for building specification documents with basic
# formatting features. Users can add requirement sections, insert
# images, links and tables, export the document as a PDF and send it
# for review using the existing review toolbox.

from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from typing import List
import webbrowser

import tkinter as tk
from tkinter import ttk, filedialog, simpledialog

from gui import messagebox
from gui.review_toolbox import ParticipantDialog, ReviewData

try:  # Pillow is optional
    from PIL import Image, ImageTk
except Exception:  # pragma: no cover - pillow optional
    Image = ImageTk = None

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet


@dataclass
class RequirementSection:
    """A single section within the specification document."""

    title: str
    content: str = ""
    images: List[str] = field(default_factory=list)


class _SectionEditor(tk.Toplevel):
    """Dialog window used to edit a single requirement section."""

    def __init__(self, master: tk.Widget, section: RequirementSection):
        super().__init__(master)
        self.title("Edit Section")
        self.section = section
        self._images: List[tk.PhotoImage] = []

        top = ttk.Frame(self)
        top.pack(fill=tk.BOTH, expand=True)

        ttk.Label(top, text="Title:").pack(anchor="w")
        self.title_var = tk.StringVar(value=section.title)
        ttk.Entry(top, textvariable=self.title_var).pack(fill=tk.X)

        self.text = tk.Text(top, wrap="word")
        self.text.insert("1.0", section.content)
        self.text.pack(fill=tk.BOTH, expand=True, pady=5)

        btn_frame = ttk.Frame(top)
        btn_frame.pack(fill=tk.X)
        ttk.Button(btn_frame, text="Insert Image", command=self.insert_image).pack(
            side=tk.LEFT, padx=2
        )
        ttk.Button(btn_frame, text="Insert Link", command=self.insert_link).pack(
            side=tk.LEFT, padx=2
        )
        ttk.Button(btn_frame, text="Insert Table", command=self.insert_table).pack(
            side=tk.LEFT, padx=2
        )

        ttk.Button(self, text="Save", command=self._save).pack(pady=5)

    def insert_image(self) -> None:
        if Image is None:
            messagebox.showerror("Images", "Pillow is required to insert images")
            return
        path = filedialog.askopenfilename(parent=self, filetypes=[("Images", "*.png;*.jpg;*.jpeg;*.gif")])
        if not path:
            return
        img = Image.open(path)
        tk_img = ImageTk.PhotoImage(img)
        self.text.image_create(tk.INSERT, image=tk_img)
        self._images.append(tk_img)  # keep reference
        self.section.images.append(path)

    def insert_link(self) -> None:
        txt = simpledialog.askstring("Link Text", "Text:", parent=self)
        if not txt:
            return
        url = simpledialog.askstring("URL", "Link URL:", parent=self)
        if not url:
            return
        start = self.text.index(tk.INSERT)
        self.text.insert(tk.INSERT, txt)
        end = self.text.index(tk.INSERT)
        tag = f"link_{start.replace('.', '_')}"
        self.text.tag_add(tag, start, end)
        self.text.tag_config(tag, foreground="blue", underline=True)
        self.text.tag_bind(tag, "<Button-1>", lambda e, link=url: webbrowser.open(link))
        self.text.insert(tk.INSERT, " ")

    def insert_table(self) -> None:
        rows = simpledialog.askinteger("Rows", "Number of rows:", parent=self, minvalue=1, maxvalue=10)
        cols = simpledialog.askinteger("Columns", "Number of columns:", parent=self, minvalue=1, maxvalue=10)
        if not rows or not cols:
            return
        header = "| " + " | ".join([f"Col{i+1}" for i in range(cols)]) + " |\n"
        sep = "| " + " | ".join(["---" for _ in range(cols)]) + " |\n"
        body = "".join("| " + " | ".join(["" for _ in range(cols)]) + " |\n" for _ in range(rows))
        self.text.insert(tk.INSERT, header + sep + body + "\n")

    def _save(self) -> None:
        self.section.title = self.title_var.get().strip() or self.section.title
        self.section.content = self.text.get("1.0", "end").strip()
        self.destroy()


class SpecificationEditor(tk.Toplevel):
    """Main window for arranging requirement sections and exporting."""

    def __init__(self, master: tk.Widget):
        super().__init__(master)
        self.title("Specification Document Editor")
        self.sections: List[RequirementSection] = []

        frame = ttk.Frame(self)
        frame.pack(fill=tk.BOTH, expand=True)

        self.listbox = tk.Listbox(frame)
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        controls = ttk.Frame(frame)
        controls.pack(side=tk.LEFT, fill=tk.Y, padx=5)
        ttk.Button(controls, text="Add", command=self.add_section).pack(fill=tk.X)
        ttk.Button(controls, text="Edit", command=self.edit_section).pack(fill=tk.X)
        ttk.Button(controls, text="Remove", command=self.remove_section).pack(fill=tk.X)
        ttk.Button(controls, text="Up", command=lambda: self.move_section(-1)).pack(fill=tk.X)
        ttk.Button(controls, text="Down", command=lambda: self.move_section(1)).pack(fill=tk.X)

        bottom = ttk.Frame(self)
        bottom.pack(fill=tk.X)
        ttk.Button(bottom, text="Send to Review", command=self.send_to_review).pack(
            side=tk.RIGHT, padx=5, pady=5
        )
        ttk.Button(bottom, text="Export PDF", command=self.export_pdf).pack(
            side=tk.RIGHT, padx=5, pady=5
        )

    # section management -------------------------------------------------
    def add_section(self) -> None:
        title = simpledialog.askstring("Title", "Section title:", parent=self)
        if not title:
            return
        self.sections.append(RequirementSection(title=title))
        self.listbox.insert(tk.END, title)

    def edit_section(self) -> None:
        sel = self.listbox.curselection()
        if not sel:
            return
        idx = sel[0]
        section = self.sections[idx]
        dlg = _SectionEditor(self, section)
        self.wait_window(dlg)
        self.listbox.delete(idx)
        self.listbox.insert(idx, section.title)

    def remove_section(self) -> None:
        sel = self.listbox.curselection()
        if not sel:
            return
        idx = sel[0]
        self.listbox.delete(idx)
        del self.sections[idx]

    def move_section(self, delta: int) -> None:
        sel = self.listbox.curselection()
        if not sel:
            return
        i = sel[0]
        j = i + delta
        if j < 0 or j >= len(self.sections):
            return
        self.sections[i], self.sections[j] = self.sections[j], self.sections[i]
        text = self.listbox.get(i)
        self.listbox.delete(i)
        self.listbox.insert(j, text)
        self.listbox.selection_set(j)

    # export/review ------------------------------------------------------
    def export_pdf(self) -> None:
        """Generate a PDF document from the current sections."""
        path = filedialog.asksaveasfilename(
            parent=self,
            defaultextension=".pdf",
            filetypes=[("PDF", "*.pdf")],
        )
        if not path:
            return
        doc = SimpleDocTemplate(path)
        story = []
        styles = getSampleStyleSheet()
        for section in self.sections:
            story.append(Paragraph(section.title, styles["Heading1"]))
            story.append(Paragraph(section.content.replace("\n", "<br/>"), styles["Normal"]))
            for img in section.images:
                try:
                    story.append(Image(img, width=200, height=150))
                except Exception:
                    continue
            story.append(Spacer(1, 12))
        doc.build(story)
        messagebox.showinfo("Export", f"Saved PDF to {path}")

    def send_to_review(self) -> None:
        """Collect participants and store review information."""
        dlg = ParticipantDialog(self, joint=False)
        if dlg.result is None:
            return
        moderators, participants = dlg.result
        review = ReviewData(
            name="Specification Review",
            description="Specification document",
            moderators=moderators,
            participants=participants,
        )
        path = filedialog.asksaveasfilename(
            parent=self,
            defaultextension=".json",
            filetypes=[("JSON", "*.json")],
        )
        if not path:
            return
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(asdict(review), fh, indent=2)
        messagebox.showinfo("Review", f"Review data saved to {path}")
