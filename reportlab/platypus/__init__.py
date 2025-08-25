# Author: Miguel Marina <karel.capek.robotics@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later
#
# Copyright (C) 2025 Capek System Safety & Robotic Solutions
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

class Table:
    def __init__(self, *args, **kwargs):
        pass

    def setStyle(self, *args, **kwargs):
        pass


class TableStyle:
    def __init__(self, *args, **kwargs):
        pass


class SimpleDocTemplate:
    """Very small stand‑in for ReportLab's ``SimpleDocTemplate``.

    The real class exposes a number of attributes used during PDF generation
    such as ``pagesize`` and the document margins.  The application relies on
    these for layout calculations, so this stub stores them as plain attributes
    which can be queried by the calling code.
    """

    def __init__(self, filename, **kwargs):
        self.filename = filename

        # Basic document geometry
        self.pagesize = kwargs.get("pagesize", (612.0, 792.0))
        self.leftMargin = kwargs.get("leftMargin", 72.0)
        self.rightMargin = kwargs.get("rightMargin", 72.0)
        self.topMargin = kwargs.get("topMargin", 72.0)
        self.bottomMargin = kwargs.get("bottomMargin", 72.0)

    def build(self, flowables):
        """Create a minimal PDF so callers see an output file.

        The real ReportLab library converts the list of *flowables* into a
        fully formatted PDF. Re-implementing that logic would be excessive for
        the tests in this kata, but the application expects that invoking
        ``build`` results in a PDF file on disk. To satisfy that expectation we
        simply write a tiny, valid PDF header and trailer. The generated file
        contains no real content but is sufficient for checks that merely verify
        the file exists or can be opened as a PDF.
        """

        # Minimal PDF structure – essentially a blank document.
        header = b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n"
        body = (
            b"1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n"
            b"2 0 obj<</Type/Pages/Count 0>>endobj\n"
            b"trailer<</Root 1 0 R /Size 3>>\n"
            b"%%EOF"
        )

        with open(self.filename, "wb") as fh:
            fh.write(header)
            fh.write(body)


class Paragraph:
    def __init__(self, *args, **kwargs):
        pass


class Spacer:
    def __init__(self, *args, **kwargs):
        pass


class Image:
    def __init__(self, *args, **kwargs):
        pass


class PageBreak:
    def __init__(self, *args, **kwargs):
        pass


class LongTable(Table):
    pass
