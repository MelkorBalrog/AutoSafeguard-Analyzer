import importlib as _importlib
_impl = _importlib.import_module('mainappsrc.managers.repository_manager')
globals().update(_impl.__dict__)
