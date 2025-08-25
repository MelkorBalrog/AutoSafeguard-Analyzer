import importlib as _importlib
_impl = _importlib.import_module('mainappsrc.subapps.reliability_subapp')
globals().update(_impl.__dict__)
