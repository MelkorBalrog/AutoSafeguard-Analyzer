def figure(*args, **kwargs):
    pass

def title(*args, **kwargs):
    pass

def savefig(*args, **kwargs):
    pass

def close(*args, **kwargs):
    pass

def text(*args, **kwargs):
    class DummyText:
        pass
    return DummyText()

def axis(*args, **kwargs):
    pass

def gca(*args, **kwargs):
    """Return a dummy ``Axes`` object.

    The real ``matplotlib.pyplot`` module exposes :func:`gca` (get current
    axes).  The lightweight testing stub previously omitted this helper,
    which caused attribute errors when code expected it to be present.  This
    minimal implementation returns an object with the limited methods used by
    the project.
    """

    class DummyAxes:
        def annotate(self, *args, **kwargs):
            pass

        def scatter(self, *args, **kwargs):
            pass

        def text(self, *args, **kwargs):
            return text(*args, **kwargs)

        def axis(self, *args, **kwargs):
            pass

    return DummyAxes()

def tight_layout(*args, **kwargs):
    pass
