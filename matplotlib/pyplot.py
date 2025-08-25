# Author: Miguel Marina <karel.capek.robotics@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later
#
# Copyright (C) 2025 Capek System Safety & Robotic Solutions
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

class Axes:
    """Minimal stand-in for :class:`matplotlib.axes.Axes`."""

    def clear(self):
        pass

    def plot(self, *args, **kwargs):
        pass

    def set_title(self, *args, **kwargs):
        pass

    def bar(self, *args, **kwargs):
        pass


class Figure:
    """Very small substitute for :class:`matplotlib.figure.Figure`.

    The real ``matplotlib`` library exposes a ``Figure`` class used to
    create and manage subplots.  The GUI's metrics tab imports this class via
    ``plt.Figure``.  The testing environment only requires enough behaviour
    to satisfy those imports, so this stub tracks created axes and exposes a
    ``tight_layout`` no-op.
    """

    def __init__(self, *args, **kwargs):
        self.axes = []

    def add_subplot(self, *args, **kwargs):  # pragma: no cover - trivial
        ax = Axes()
        self.axes.append(ax)
        return ax

    def tight_layout(self, *args, **kwargs):  # pragma: no cover - trivial
        pass


def figure(*args, **kwargs):
    return Figure(*args, **kwargs)

def title(*args, **kwargs):
    pass

def bar(*args, **kwargs):
    """Stub for bar chart drawing."""
    pass

def hist(*args, **kwargs):
    """Stub for histogram drawing."""
    pass

def xlabel(*args, **kwargs):
    pass

def ylabel(*args, **kwargs):
    pass

def xticks(*args, **kwargs):
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
