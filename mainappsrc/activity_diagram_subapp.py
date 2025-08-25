import importlib as _importlib
_impl = _importlib.import_module('mainappsrc.subapps.activity_diagram_subapp')
globals().update(_impl.__dict__)
