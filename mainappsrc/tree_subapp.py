import importlib as _importlib
_impl = _importlib.import_module('mainappsrc.subapps.tree_subapp')
globals().update(_impl.__dict__)
