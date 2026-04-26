"""Smoke tests for sillok.telemetry — placeholder until the module ships.

The telemetry module is scheduled for Phase 1 (see roadmap §1 / docs/modules/).
These smoke tests exist so the directory is not empty and the unit test
discovery does not silently miss a future module.
"""
from __future__ import annotations


def test_() -> None:
    """Importing the namespace must not raise even when stub-only."""
    import importlib

    mod = importlib.import_module("sillok.telemetry")
    # __all__ may be empty until the module is implemented;
    # we only assert that the namespace imports cleanly.
    assert hasattr(mod, "__all__") or hasattr(mod, "__doc__")
