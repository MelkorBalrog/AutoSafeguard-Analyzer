def figure(*args, **kwargs):
    pass

def title(*args, **kwargs):
    pass

def savefig(fname, *args, **kwargs):
    """Write a tiny placeholder PNG image.

    The real ``matplotlib`` library serializes the current figure to the
    provided file or file-like object.  The test environment only needs a
    valid image container, so this stub writes a 1x1 transparent PNG.  The
    function accepts both file paths and binary file objects to mirror the
    behaviour used in the project.
    """

    import base64

    # A base64 encoded 1x1 pixel transparent PNG.
    png_bytes = base64.b64decode(
        b"iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMBAF8+CJkAAAAASUVORK5CYII="
    )

    if hasattr(fname, "write"):
        fname.write(png_bytes)
    else:
        with open(fname, "wb") as f:
            f.write(png_bytes)

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
