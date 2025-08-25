import importlib as _importlib
_impl = _importlib.import_module('mainappsrc.core.app_lifecycle_ui')
globals().update(_impl.__dict__)
