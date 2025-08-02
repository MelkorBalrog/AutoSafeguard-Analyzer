class DummyStyles(dict):
    def add(self, style):
        pass

def getSampleStyleSheet():
    return DummyStyles()

class ParagraphStyle:
    def __init__(self, *args, **kwargs):
        pass
