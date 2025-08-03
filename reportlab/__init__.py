"""Lightweight stand-in for the real :mod:`reportlab` package.

This module provides a very small subset of the real project's
functionality so the test suite can run in environments where the
dependency is not installed.  When a full installation of ReportLab is
available on ``sys.path`` *outside* of this repository we prefer to use
that implementation instead of the stub.  This mirrors the behaviour of
optional dependencies: local development gets the complete feature set
while the test environment continues to rely on the tiny fallback
defined in this repo.
"""

from __future__ import annotations

import importlib.machinery
import importlib.util
import os
import sys


# ---------------------------------------------------------------------------
# Attempt to locate a real ReportLab distribution somewhere else on the
# import path.  The repository itself contains this stub package which would
# normally shadow an external installation.  By searching ``sys.path`` for a
# different location we can dynamically load the genuine library when it is
# present (for example on a contributor's machine) while still falling back to
# the minimal test stub when running in the execution environment used for the
# kata tests where ReportLab is not installed.
_package_dir = os.path.abspath(os.path.dirname(__file__))
_repo_root = os.path.abspath(os.path.join(_package_dir, os.pardir))

_search_paths = [p for p in sys.path if os.path.abspath(p) != _repo_root]
_spec = importlib.machinery.PathFinder.find_spec(__name__, _search_paths)

if _spec is not None:
    # A real distribution was found.  Load it and replace the stub module's
    # globals with the actual implementation so downstream imports behave as
    # if ReportLab had been imported directly.
    _real_module = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(_real_module)  # type: ignore[union-attr]
    globals().update(_real_module.__dict__)
    sys.modules[__name__] = _real_module
else:
    # The real library is absent – the remainder of this package (e.g.
    # ``reportlab.lib.colors``) provides just enough surface area for our
    # tests.  No further work is required here.
    __all__: list[str] = []

