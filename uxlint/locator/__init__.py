"""Locator backends turn (image + text query) into boxes.

This is the swappable model layer. `MockLocator` lets you run uxlint
end-to-end with no GPU; `LocateAnythingLocator` plugs in NVIDIA's
LocateAnything VLM for real results.
"""

from uxlint.locator.base import Locator
from uxlint.locator.mock import MockLocator

__all__ = ["Locator", "MockLocator", "get_locator"]


def get_locator(name: str = "mock", **kwargs) -> Locator:
    """Factory: `get_locator("mock")` or `get_locator("locate-anything")`."""
    name = name.lower()
    if name in ("mock", "demo"):
        return MockLocator(**kwargs)
    if name in ("locate-anything", "locateanything", "la"):
        # Imported lazily so the heavy torch/transformers deps are optional.
        from uxlint.locator.locate_anything import LocateAnythingLocator

        return LocateAnythingLocator(**kwargs)
    raise ValueError(f"Unknown locator backend: {name!r}")
