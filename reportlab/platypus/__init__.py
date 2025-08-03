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
        """Placeholder build method – does nothing in this stub."""
        pass


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
