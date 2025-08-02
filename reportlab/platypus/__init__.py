"""Minimal stubs for the ReportLab library used during testing.

The real project depends on ReportLab for PDF generation, but the full
dependency is heavy and not required for the unit tests.  These lightweight
classes implement just enough of the public API for the application to run
without importing the external package.
"""

class _Stub:
    def __init__(self, *args, **kwargs):
        pass


class Table(_Stub):
    pass


class LongTable(Table):
    pass


class TableStyle(_Stub):
    pass


class SimpleDocTemplate(_Stub):
    def build(self, flowables, onFirstPage=None, onLaterPages=None):  # noqa: D401
        """Placeholder ``build`` method that simply ignores the flowables."""
        return


class Paragraph(_Stub):
    pass


class Spacer(_Stub):
    pass


class Image(_Stub):
    pass


class PageBreak(_Stub):
    pass
