import importlib as _importlib
_impl = _importlib.import_module('mainappsrc.core.page_diagram')
globals().update(_impl.__dict__)
