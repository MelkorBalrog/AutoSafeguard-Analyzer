import importlib as _importlib
_impl = _importlib.import_module('mainappsrc.managers.cta_manager')
globals().update(_impl.__dict__)
