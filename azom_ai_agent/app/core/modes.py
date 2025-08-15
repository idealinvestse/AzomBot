from __future__ import annotations

from enum import Enum


class Mode(str, Enum):
    """Runtime mode for AZOM.

    LIGHT: simplified feature set and limits
    FULL: full-featured experience
    """

    LIGHT = "light"
    FULL = "full"

    @classmethod
    def from_str(cls, value: str | None, default: "Mode" = "Mode.FULL") -> "Mode":  # type: ignore[name-defined]
        if not value:
            return cls.FULL if default is None else default
        v = value.strip().lower()
        if v in (cls.LIGHT.value, "l"):
            return cls.LIGHT
        return cls.FULL
