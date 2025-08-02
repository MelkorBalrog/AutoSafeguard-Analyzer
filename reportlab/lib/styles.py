"""Lightweight stand-ins for ReportLab style classes used in tests.

The real ``reportlab`` package ships with a fairly feature rich style system
that provides a number of default styles (e.g. ``Title`` or ``Heading1``).
This project only needs a minimal subset of that functionality in order to
exercise the PDF generation code.  The previous stub returned an empty
dictionary which caused lookups such as ``pdf_styles["Title"]`` to raise a
``KeyError`` during tests.  The PDF report generator expects a handful of
predefined styles to exist, so we provide simple implementations here that are
good enough for the unit tests.
"""


class DummyStyles(dict):
    """A very small style container mimicking ReportLab's behaviour.

    Styles are stored by name and can be retrieved using dictionary access.
    ``add`` mirrors the API of ``reportlab.lib.styles.StyleSheet1.add``.
    """

    def add(self, style):
        # Store the style by its name so it can be looked up later.
        if hasattr(style, "name"):
            self[style.name] = style


def getSampleStyleSheet():
    """Return a stylesheet populated with the default styles we rely on."""

    styles = DummyStyles()

    # Populate the styles with the names used throughout the code base.  The
    # actual formatting attributes are irrelevant for the tests so we simply
    # create ``ParagraphStyle`` instances with the appropriate ``name``.
    for default_name in ["Title", "Heading1", "Heading2", "Heading3", "Normal"]:
        styles[default_name] = ParagraphStyle(name=default_name)

    return styles


class ParagraphStyle:
    """Minimal placeholder for ReportLab's ``ParagraphStyle``.

    It stores any attributes passed to the constructor so that code accessing
    those attributes later on does not fail.
    """

    def __init__(self, name="", parent=None, **kwargs):
        self.name = name
        self.parent = parent
        for key, value in kwargs.items():
            setattr(self, key, value)

