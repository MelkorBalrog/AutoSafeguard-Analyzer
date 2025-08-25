import importlib as _importlib
_impl = _importlib.import_module('mainappsrc.subapps.diagram_export_subapp')
globals().update(_impl.__dict__)
