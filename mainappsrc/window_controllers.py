import importlib as _importlib
_impl = _importlib.import_module('mainappsrc.core.window_controllers')
globals().update(_impl.__dict__)
