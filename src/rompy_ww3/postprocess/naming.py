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


def _extract_restart_number(filename: str) -> int:
    """Extract the sequence number from a restart filename.

    Args:
        filename: Restart filename (e.g., "restart001.ww3")

    Returns:
        Sequence number (e.g., 1), or 1 if no number found
    """
    import re

    match = re.match(r"^restart(\d+)\.ww3$", filename, re.IGNORECASE)
    if match:
        return int(match.group(1))
    return 1


def _get_restart_basename(filename: str) -> str:
    """Extract the base restart filename without numbering.

    WW3 creates numbered restart files like restart001.ww3, restart002.ww3.
    This function strips the numbers to produce restart.ww3 for consistent
    target naming.

    Args:
        filename: Original filename (e.g., "restart001.ww3")

    Returns:
        Base filename without numbers (e.g., "restart.ww3")
    """
    import re

    # Match pattern: restart + optional digits + .ww3
    match = re.match(r"^(restart)(\d+)(\.ww3)$", filename, re.IGNORECASE)
    if match:
        return f"{match.group(1)}{match.group(3)}"
    return filename


def compute_restart_valid_date(
    restart_path: Path, start_date: str, output_stride: int
) -> str:
    """Compute the valid date for a numbered restart file.

    WW3 restart files are numbered sequentially starting from 1.
    The valid date is computed as:
      valid_date = start_date + (seq_num - 1) * output_stride

    For example, with start_date="20080522 000000" and output_stride=21600 (6 hours):
      - restart001.ww3 -> 20080522_000000
      - restart002.ww3 -> 20080522_060000
      - restart003.ww3 -> 20080522_120000
      - restart004.ww3 -> 20080522_180000

    Parameters:
    - restart_path: Path to the restart file (used to extract sequence number).
    - start_date: Date string in WW3 format ('YYYYMMDD HHMMSS').
    - output_stride: Output stride in seconds.

    Returns:
    - Date string in 'YYYYMMDD_HHMMSS' format.
    """
    if not isinstance(start_date, str) or not isinstance(output_stride, int):
        raise ValueError("start_date must be a string and output_stride must be an int")

    from datetime import datetime, timedelta

    seq_num = _extract_restart_number(restart_path.name)
    start_dt = datetime.strptime(start_date, "%Y%m%d %H%M%S")
    offset_seconds = (seq_num - 1) * output_stride
    valid_dt = start_dt + timedelta(seconds=offset_seconds)
    return valid_dt.strftime("%Y%m%d_%H%M%S")


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

    For restart files, the numbering (e.g., restart001.ww3) is stripped to
    produce a consistent restart.ww3 basename.

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
    # Strip numbering from restart filenames (restart001.ww3 -> restart.ww3)
    basename = _get_restart_basename(local_path.name)
    return f"{valid_date}_{basename}"
