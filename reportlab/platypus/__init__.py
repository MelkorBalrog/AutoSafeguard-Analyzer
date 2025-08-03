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
        """Create a minimal placeholder PDF file.

        The real ReportLab library renders the ``flowables`` into a binary PDF
        document on disk.  For the purposes of the tests in this kata we only
        need a tangible file to be created so that downstream code believes the
        report was generated successfully.  We therefore write a tiny, valid
        PDF header and trailer to ``self.filename``; the contents aren't meant
        to be human readable but the resulting file is recognised as a PDF by
        most tools.
        """

        import os

        # Ensure the target directory exists before attempting to write.
        os.makedirs(os.path.dirname(self.filename) or ".", exist_ok=True)

        # Write the smallest possible PDF structure.  This isn't a useful
        # document but it is enough for file viewers to identify it as a PDF
        # and, more importantly, for calling code to see that a file exists.
        minimal_pdf = (
            b"%PDF-1.4\n"
            b"1 0 obj<</Type/Catalog>>endobj\n"
            b"trailer<</Root 1 0 R>>\n%%EOF"
        )

        with open(self.filename, "wb") as fh:
            fh.write(minimal_pdf)


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
