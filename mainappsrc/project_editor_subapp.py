import importlib as _importlib
_impl = _importlib.import_module('mainappsrc.subapps.project_editor_subapp')
globals().update(_impl.__dict__)
