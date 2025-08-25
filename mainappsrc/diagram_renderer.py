import importlib as _importlib
_impl = _importlib.import_module('mainappsrc.core.diagram_renderer')
globals().update(_impl.__dict__)
