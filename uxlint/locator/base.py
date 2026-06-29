"""The Locator interface that every backend implements."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from uxlint.types import Box


@runtime_checkable
class Locator(Protocol):
    """Anything that can find UX elements in an image from text queries.

    A backend gets the screenshot path and a list of natural-language
    queries (e.g. "primary call-to-action button", "email input field")
    and returns, for each query, the boxes it found.
    """

    def locate(self, image_path: str, queries: list[str]) -> dict[str, list[Box]]:
        ...
