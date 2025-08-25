import importlib as _importlib
_impl = _importlib.import_module('mainappsrc.core.event_dispatcher')
globals().update(_impl.__dict__)
