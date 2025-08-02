class Table:
    def __init__(self, *args, **kwargs):
        pass

    def setStyle(self, *args, **kwargs):
        pass


class TableStyle:
    def __init__(self, *args, **kwargs):
        pass


class SimpleDocTemplate:
    def __init__(self, filename, **kwargs):
        self.filename = filename
        self.kwargs = kwargs

    def build(self, flowables):
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
