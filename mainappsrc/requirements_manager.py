import importlib as _importlib
_impl = _importlib.import_module('mainappsrc.managers.requirements_manager')
globals().update(_impl.__dict__)
