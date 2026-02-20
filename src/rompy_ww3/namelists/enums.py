"""
Centralized WW3 fixed-vocabulary enums.
Each enum value is the canonical WW3 token/code.
Provide a strict parse_enum helper for robust, case-insensitive lookup.
"""

from __future__ import annotations

from enum import Enum, IntEnum
from typing import Type, Union


def parse_enum(enum_cls: Type[Enum], value: Union[str, int, Enum]) -> Enum:
    """
    Strictly parse a value into a member of the given Enum class.

    Precedence (highest to lowest):
    1) If value is already an instance of enum_cls, return it.
    2) If value is an Enum member of enum_cls, return the member.
    3) If value exactly equals a member.value (string/int) -> return that member.
    4) If value case-insensitive matches a member.value (for strings) -> return that member.
    5) If value case-insensitive matches a member.name -> return that member.
    6) If enum_cls is an IntEnum and value is a numeric string -> parse int and map to member.
    7) Otherwise, raise ValueError listing allowed canonical values.
    Whitespace around strings is trimmed.
    """
    # 1. Already an instance
    if isinstance(value, enum_cls):
        return value

    # 2. If value is an Enum member of the same class
    if isinstance(value, Enum) and value.__class__ is enum_cls:
        return value

    # 3. If enum_cls is IntEnum and numeric strings / ints
    if issubclass(enum_cls, IntEnum):
        if isinstance(value, int):
            try:
                return enum_cls(value)
            except ValueError:
                pass
        if isinstance(value, str):
            s = value.strip()
            if s.isdigit() or (s.startswith("-") and s[1:].isdigit()):
                try:
                    return enum_cls(int(s))
                except ValueError:
                    pass

    # 4. Strings: exact match and tolerant matches
    if isinstance(value, str):
        s = value.strip()
        for m in enum_cls:
            if str(m.value) == s:
                return m
        # 4b. Case-insensitive match on value (when value is string)
        for m in enum_cls:
            if isinstance(m.value, str) and m.value.lower() == s.lower():
                return m
        # 5. Case-insensitive name match
        low = s.lower()
        for m in enum_cls:
            if m.name.lower() == low:
                return m

    # 7. Unknown
    allowed = ", ".join(str(getattr(m, "value", m)) for m in enum_cls)
    raise ValueError(f"Invalid value: must be one of: {allowed}")


class GRID_TYPE(str, Enum):
    """Fixed vocabulary: WW3 grid types."""

    RECT = "RECT"
    CURV = "CURV"
    UNST = "UNST"
    SMC = "SMC"


class COORD_TYPE(str, Enum):
    """Coordinate system types for WW3 inputs."""

    SPHE = "SPHE"
    CART = "CART"


class CLOS_TYPE(str, Enum):
    """Grid closure types (NONE/SMPL/TRPL)."""

    NONE = "NONE"
    SMPL = "SMPL"
    TRPL = "TRPL"


class FORCING(str, Enum):
    """Forcing flag vocabulary (F/T/H/C)."""

    F = "F"
    T = "T"
    H = "H"
    C = "C"


class IOSTYP(IntEnum):
    """IO type vocabulary (0-3)."""

    TYPE0 = 0
    TYPE1 = 1
    TYPE2 = 2
    TYPE3 = 3


class LayoutIndicator(IntEnum):
    """Layout indicator for reading strategies (1-4)."""

    LAYOUT_1 = 1
    LAYOUT_2 = 2
    LAYOUT_3 = 3
    LAYOUT_4 = 4


class FormatIndicator(IntEnum):
    """Format indicator for input formats (1-3)."""

    FREE_FORMAT = 1
    FIXED_FORMAT = 2
    UNFORMATTED = 3


class HomogInputName(str, Enum):
    """Homogeneous input parameter names (15 values)."""

    IC1 = "IC1"
    IC2 = "IC2"
    IC3 = "IC3"
    IC4 = "IC4"
    IC5 = "IC5"
    MDN = "MDN"
    MTH = "MTH"
    MVS = "MVS"
    LEV = "LEV"
    CUR = "CUR"
    MOV = "MOV"
    WND = "WND"
    ICE = "ICE"
    TAU = "TAU"
    RHO = "RHO"


class UpdateMethod(str, Enum):
    """Update method options for homogeneous inputs."""

    REPLACE = "REPLACE"
    ADD = "ADD"
    MULTIPLY = "MULTIPLY"


# Backwards-compatible aliases for uppercase export names
LAYOUT_INDICATOR = LayoutIndicator
FORMAT_INDICATOR = FormatIndicator
HOMOG_INPUT_NAME = HomogInputName
UPDATE_METHOD = UpdateMethod
__all__ = [
    "GRID_TYPE",
    "COORD_TYPE",
    "CLOS_TYPE",
    "FORCING",
    "IOSTYP",
    "LAYOUT_INDICATOR",
    "FORMAT_INDICATOR",
    "HOMOG_INPUT_NAME",
    "UPDATE_METHOD",
    "parse_enum",
]
