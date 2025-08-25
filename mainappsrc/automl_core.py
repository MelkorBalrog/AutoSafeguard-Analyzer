import importlib as _importlib
_impl = _importlib.import_module('mainappsrc.core.automl_core')
globals().update(_impl.__dict__)
