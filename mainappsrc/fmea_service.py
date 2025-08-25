import importlib as _importlib
_impl = _importlib.import_module('mainappsrc.core.fmea_service')
globals().update(_impl.__dict__)
