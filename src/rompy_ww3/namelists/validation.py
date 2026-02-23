"""Validation utilities for WW3 namelists."""

from datetime import datetime
from typing import Union
from enum import Enum
import re

# WW3-specific constants
WW3_BOOLEAN_VALUES = {"T", "F"}
IOSTYP_VALUES = {0, 1, 2, 3}
GRID_TYPE_VALUES = {"RECT", "CURV", "UNST", "SMC"}
COORD_TYPE_VALUES = {"SPHE", "CART"}
CLOS_TYPE_VALUES = {"NONE", "SMPL", "TRPL"}
FORCING_VALUES = {"F", "T", "H", "C"}  # No forcing, external file, homogeneous, coupled


def validate_date_format(date_str: str) -> str:
    """Validate and convert date string to WW3 format (YYYYMMDD HHMMSS)."""
    if not date_str:
        return date_str

    # Check if it's already in the right format
    if re.match(r"^\d{8}\s\d{6}$", date_str.strip()):
        return date_str

    # Try to parse the date string
    try:
        # Attempt to parse different date formats
        if len(date_str) == 15:  # 'YYYYMMDD HHMMSS' format
            datetime.strptime(date_str, "%Y%m%d %H%M%S")
            return date_str
        elif len(date_str) == 17:  # 'YYYYMMDD HHMMSSSSS' format (with extra chars)
            datetime.strptime(date_str[:15], "%Y%m%d %H%M%S")
            return date_str[:15]
        elif (
            "-" in date_str and ":" in date_str
        ):  # 'YYYY-MM-DD HHMMSS' or 'YYYY-MM-DDTHHMMSS' format
            for fmt in ["%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S"]:
                try:
                    date_obj = datetime.strptime(date_str, fmt)
                    return date_obj.strftime("%Y%m%d %H%M%S")
                except ValueError:
                    continue
        else:
            # Try parsing as basic date with time
            possible_formats = [
                "%Y/%m/%d %H:%M:%S",
                "%Y-%m-%d %H:%M",
                "%Y/%m/%d %H:%M",
                "%Y-%m-%d",
                "%Y/%m/%d",
            ]
            for fmt in possible_formats:
                try:
                    date_obj = datetime.strptime(date_str, fmt)
                    return date_obj.strftime("%Y%m%d %H%M%S")
                except ValueError:
                    continue
    except ValueError:
        pass

    raise ValueError(
        f"Invalid date format: '{date_str}'. Expected format: 'YYYYMMDD HHMMSS'"
    )


def validate_ww3_boolean(value: str) -> str:
    """Validate WW3 boolean value ('T' or 'F')."""
    # Accept Enum members by coercing to their underlying value
    if isinstance(value, Enum):
        value = value.value
    if not isinstance(value, str):
        raise ValueError(f"Expected string, got {type(value)}")

    upper_value = value.upper()
    if upper_value not in WW3_BOOLEAN_VALUES:
        raise ValueError(
            f"Invalid WW3 boolean value: '{value}'. Must be one of {WW3_BOOLEAN_VALUES}"
        )

    return upper_value


def validate_range(
    value: Union[int, float],
    min_val: Union[int, float],
    max_val: Union[int, float],
    field_name: str,
) -> Union[int, float]:
    """Validate that a value is within a specified range."""
    if value < min_val or value > max_val:
        raise ValueError(
            f"{field_name} value {value} is out of range [{min_val}, {max_val}]"
        )
    return value


def validate_io_type(value: int) -> int:
    """Validate IOSTYP value (0-3)."""
    # Allow Enum members by using their underlying value
    if isinstance(value, Enum):
        value = value.value
    if value not in IOSTYP_VALUES:
        raise ValueError(
            f"IOSTYP value {value} is invalid. Must be one of {sorted(list(IOSTYP_VALUES))}"
        )
    return value


def validate_grid_type(value: str) -> str:
    """Validate grid type value."""
    # Accept Enum members by coercing to their underlying value
    if isinstance(value, Enum):
        value = value.value
    if not isinstance(value, str):
        raise ValueError(f"Expected string, got {type(value)}")

    upper_value = value.upper()
    if upper_value not in GRID_TYPE_VALUES:
        raise ValueError(
            f"Invalid grid type: '{value}'. Must be one of {sorted(list(GRID_TYPE_VALUES))}"
        )

    return upper_value


def validate_coord_type(value: str) -> str:
    """Validate coordinate type value."""
    # Accept Enum members by coercing to their underlying value
    if isinstance(value, Enum):
        value = value.value
    if not isinstance(value, str):
        raise ValueError(f"Expected string, got {type(value)}")

    upper_value = value.upper()
    if upper_value not in COORD_TYPE_VALUES:
        raise ValueError(
            f"Invalid coordinate type: '{value}'. Must be one of {sorted(list(COORD_TYPE_VALUES))}"
        )

    return upper_value


def validate_clos_type(value: str) -> str:
    """Validate grid closure type value."""
    # Accept Enum members by coercing to their underlying value
    if isinstance(value, Enum):
        value = value.value
    if not isinstance(value, str):
        raise ValueError(f"Expected string, got {type(value)}")

    upper_value = value.upper()
    if upper_value not in CLOS_TYPE_VALUES:
        raise ValueError(
            f"Invalid grid closure type: '{value}'. Must be one of {sorted(list(CLOS_TYPE_VALUES))}"
        )

    return upper_value


def validate_forcing_type(value: str) -> str:
    """Validate forcing type value."""
    # Accept Enum members by coercing to their underlying value
    if isinstance(value, Enum):
        value = value.value
    if not isinstance(value, str):
        raise ValueError(f"Expected string, got {type(value)}")

    upper_value = value.upper()
    if upper_value not in FORCING_VALUES:
        raise ValueError(
            f"Invalid forcing type: '{value}'. Must be one of {sorted(list(FORCING_VALUES))}"
        )

    return upper_value


def validate_positive_value(
    value: Union[int, float], field_name: str
) -> Union[int, float]:
    """Validate that a value is positive."""
    if value <= 0:
        raise ValueError(f"{field_name} value {value} must be positive")
    return value


def validate_non_negative_value(
    value: Union[int, float], field_name: str
) -> Union[int, float]:
    """Validate that a value is non-negative."""
    if value < 0:
        raise ValueError(f"{field_name} value {value} must be non-negative")
    return value


def validate_percentage(value: Union[int, float], field_name: str) -> Union[int, float]:
    """Validate that a value is a percentage (0-100)."""
    if value < 0 or value > 100:
        raise ValueError(f"{field_name} value {value} is out of range [0, 100]")
    return value


def validate_angle(value: Union[int, float], field_name: str) -> Union[int, float]:
    """Validate that an angle value is in the valid range [-360, 360]."""
    if value < -360 or value > 360:
        raise ValueError(f"{field_name} value {value} is out of range [-360, 360]")
    return value


def validate_direction_range(
    value: Union[int, float], field_name: str
) -> Union[int, float]:
    """Validate that a direction is in the valid range [0, 360]."""
    if value < 0 or value > 360:
        raise ValueError(f"{field_name} value {value} is out of range [0, 360]")
    return value


def validate_frequency_range(
    value: Union[int, float], field_name: str
) -> Union[int, float]:
    """Validate that a frequency value is in reasonable range for WW3."""
    if value <= 0 or value > 1.0:  # WW3 typically uses frequencies < 1 Hz
        raise ValueError(
            f"{field_name} value {value} is out of reasonable range (0, 1.0]"
        )
    return value


def validate_direction_bins(value: int, field_name: str) -> int:
    """Validate that number of direction bins is valid."""
    if value <= 0 or value > 720:  # Maximum practical direction bins
        raise ValueError(
            f"{field_name} value {value} is out of reasonable range (0, 720]"
        )
    return value


def validate_frequency_bins(value: int, field_name: str) -> int:
    """Validate that number of frequency bins is valid."""
    if value <= 0 or value > 100:  # Maximum reasonable frequency bins
        raise ValueError(
            f"{field_name} value {value} is out of reasonable range (0, 100]"
        )
    return value
