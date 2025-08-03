"""Minimal page size definitions used by the simplified ReportLab stub.

The real ReportLab library defines page sizes in points (1 point = 1/72 inch).
For our purposes we only need support for the US Letter size and the ability
to swap dimensions for landscape orientation.  These helpers provide reasonable
defaults so that PDF generation code can calculate available drawing areas.
"""

# Width and height of a US Letter page in points (8.5" x 11")
letter = (612.0, 792.0)


def landscape(pagesize):
    """Return the dimensions for a landscape oriented page.

    The real ReportLab `landscape` function simply swaps the width and height of
    the supplied page size.  Doing the same here keeps our stub compatible with
    code that expects this behaviour.
    """

    width, height = pagesize
    return height, width

