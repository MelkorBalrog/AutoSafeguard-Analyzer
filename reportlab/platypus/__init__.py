class Table:
    def __init__(self, *args, **kwargs):
        pass


class TableStyle:
    def __init__(self, *args, **kwargs):
        pass


class SimpleDocTemplate:
    def __init__(self, *args, pagesize=(0, 0), **kwargs):
        self.pagesize = pagesize
        self.width, self.height = pagesize

    def build(self, story):
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


class LongTable:
    def __init__(self, *args, **kwargs):
        pass
