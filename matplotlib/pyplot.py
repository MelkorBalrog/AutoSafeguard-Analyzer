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

def tight_layout(*args, **kwargs):
    pass


class _DummyAxes:
    """Minimal stand-in for :class:`matplotlib.axes.Axes` used in tests.

    The real project only relies on a very small subset of matplotlib's
    functionality.  The upstream library is fairly heavy and not available in
    the execution environment for the tests, so we provide a light‑weight
    shim that implements just the bits we need.  Currently the code exercises
    the ``annotate``, ``scatter`` and ``text`` methods on an axes instance.

    Each method simply accepts any arguments and performs no action.  This is
    sufficient for our non-graphical testing purposes while preserving the
    expected API surface.
    """

    def annotate(self, *args, **kwargs):
        pass

    def scatter(self, *args, **kwargs):
        pass

    def text(self, *args, **kwargs):
        class DummyText:
            pass

        return DummyText()

    def axis(self, *args, **kwargs):
        pass


def gca(*args, **kwargs):
    """Return a dummy axes object.

    In the real matplotlib this would return the current axes; here we return
    an instance of :class:`_DummyAxes` which exposes the minimal API required
    by the project.
    """

    return _DummyAxes()
