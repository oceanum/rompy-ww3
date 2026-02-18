"""Naming helpers for WW3 post-processing outputs.

This module provides utilities to normalize WW3 datestamps and to
derive target names for generated files (regular outputs and restarts).

The v1 implementation focuses on correct formatting and input validation
and intentionally defers the full restart-datetime computation to a later
phase. See compute_restart_valid_date() for details.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from rompy_ww3.namelists.validation import validate_date_format


def normalize_datestamp(date_str: str) -> str:
    """Convert a WW3 date string to a filesystem-friendly timestamp.

    This converts any accepted WW3 date format to the internal
    YYYYMMDD_HHMMSS representation. The function uses the existing
    validate_date_format() utility to coerce different input formats into
    a canonical 'YYYYMMDD HHMMSS' form, then replaces the space with an
    underscore to produce 'YYYYMMDD_HHMMSS'.

    Doctests (examples):
    >>> normalize_datestamp("20100101 000000")
    '20100101_000000'
    >>> normalize_datestamp("2010-01-01 00:00:00")
    '20100101_000000'
    """
    normalized = validate_date_format(date_str)
    # validate_date_format returns a string in 'YYYYMMDD HHMMSS' form
    datestamp_with_space = normalized
    return datestamp_with_space.replace(" ", "_")


def compute_restart_valid_date(
    restart_path: Path, start_date: str, output_stride: int
) -> str:
    """Compute a valid date string for a restart file.

    This is a placeholder implementation for the initial (v1) stage. The
    full implementation would parse restart metadata to determine the exact
    time at which the restart is valid. For now, we conservatively return the
    normalized start_date as the valid date.

    Parameters:
    - restart_path: Path to the restart file (not used in v1 but kept for API
      compatibility).
    - start_date: Date string describing the start time (in one of the supported
      WW3 formats).
    - output_stride: Timestep/stride of the output; kept for API compatibility.

    Returns:
    - A date string in the 'YYYYMMDD_HHMMSS' format representing the valid date.

    Note: This v1 implementation returns the normalized start_date. A full
    implementation should derive the actual valid restart date from WW3 restart
    metadata.

    Doctests (examples):
    >>> compute_restart_valid_date(Path("restart.ww3"), "20100101 000000", 3600)
    '20100101_000000'
    """
    if not isinstance(start_date, str) or not isinstance(output_stride, int):
        raise ValueError("start_date must be a string and output_stride must be an int")
    return normalize_datestamp(start_date)


def compute_target_name(
    local_path: Path,
    date_str: Optional[str] = None,
    is_restart: bool = False,
    start_date: Optional[str] = None,
    output_stride: Optional[int] = None,
    restart_path: Optional[Path] = None,
) -> str:
    """Compute a datestamped target filename for a given local path.

    The target filename format is:
      <datestamp>_<basename>
    where datestamp uses the YYYYMMDD_HHMMSS format.

    Parameters:
    - local_path: Path to the target file (e.g. Path("out_grd.ww3"))
    - date_str: Datestamp in a WW3-friendly format (e.g. "20100101 000000").
                Required if is_restart is False.
    - is_restart: If True, compute the restart valid date instead of using date_str.
    - start_date: Required when is_restart is True. The start date for the restart.
    - output_stride: Required when is_restart is True. The restart output stride.
    - restart_path: Optional path to a restart file (not used in v1 but kept for API).

    Returns:
    - A string in the format '<datestamp>_<basename>'.
    """
    if not is_restart:
        if not date_str:
            raise ValueError("date_str required when not computing a restart name")
        datestamp = normalize_datestamp(date_str)
        return f"{datestamp}_{local_path.name}"

    if start_date is None or output_stride is None:
        raise ValueError(
            "start_date and output_stride required for restart target naming"
        )
    valid_date = compute_restart_valid_date(
        restart_path or Path("."), start_date, output_stride
    )
    return f"{valid_date}_{local_path.name}"
