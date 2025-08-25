"""Compatibility wrapper for relocated architecture window module."""

from .windows import architecture as _architecture
from .windows.architecture import *  # noqa: F401,F403

# Re-export private helpers relied upon by tests
_get_next_id = _architecture._get_next_id
_ensure_ibd_boundary = _architecture._ensure_ibd_boundary
_all_connection_tools = _architecture._all_connection_tools
_sync_ibd_aggregation_parts = getattr(
    _architecture, "_sync_ibd_aggregation_parts", None
)
