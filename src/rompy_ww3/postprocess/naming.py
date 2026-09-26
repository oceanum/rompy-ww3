"""WW3 target naming strategy for the core transfer lifecycle.

The core transfer processor owns reconciliation, retries, transfer execution,
redacted evidence, and persistence.  This module owns only the WW3 naming
rules that are supplied to that processor as a callable strategy.
"""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from rompy.core.responses import LocalArtifact

from rompy_ww3.namelists.validation import validate_date_format


def normalize_datestamp(date_str: str) -> str:
    """Normalize an accepted WW3 date to ``YYYYMMDD_HHMMSS``."""
    return validate_date_format(date_str).replace(" ", "_")


def _extract_restart_number(filename: str) -> int:
    """Return the one-based sequence number in a WW3 restart filename."""
    import re

    match = re.match(r"^restart(\d+)\.ww3$", filename, re.IGNORECASE)
    return int(match.group(1)) if match else 1


def _get_restart_basename(filename: str) -> str:
    """Strip the sequence number from a numbered WW3 restart filename."""
    import re

    match = re.match(r"^(restart)(\d+)(\.ww3)$", filename, re.IGNORECASE)
    return f"{match.group(1)}{match.group(3)}" if match else filename


def compute_restart_valid_date(
    restart_path: Path, start_date: str, output_stride: int
) -> str:
    """Compute the WW3 valid date for one numbered restart file."""
    if not isinstance(start_date, str) or not isinstance(output_stride, int):
        raise TypeError("start_date must be a string and output_stride must be an int")
    start_dt = datetime.strptime(
        validate_date_format(start_date), "%Y%m%d %H%M%S"
    ).replace(tzinfo=timezone.utc)
    valid_dt = start_dt + timedelta(
        seconds=(_extract_restart_number(restart_path.name) - 1) * output_stride
    )
    return valid_dt.strftime("%Y%m%d_%H%M%S")


def compute_target_name(
    local_path: Path,
    date_str: str | None = None,
    is_restart: bool = False,
    start_date: str | None = None,
    output_stride: int | None = None,
    restart_path: Path | None = None,
) -> str:
    """Compute a WW3 target basename using the legacy public API."""
    if not is_restart:
        if not date_str:
            raise ValueError("date_str required when not computing a restart name")
        return f"{normalize_datestamp(date_str)}_{local_path.name}"
    if start_date is None or output_stride is None:
        raise ValueError(
            "start_date and output_stride required for restart target naming"
        )
    valid_date = compute_restart_valid_date(
        restart_path or local_path, start_date, output_stride
    )
    return f"{valid_date}_{_get_restart_basename(local_path.name)}"


def _coerce_date(value: Any) -> str | None:
    if isinstance(value, str):
        return value
    if value is None:
        return None
    try:
        return value.strftime("%Y%m%d %H%M%S")
    except (AttributeError, TypeError):
        return None


class WW3TargetNaming:
    """Callable WW3 naming capability consumed by core transfer.

    The strategy receives a typed core ``LocalArtifact`` and contains no
    transfer, retry, locking, persistence, or result construction behavior.
    ``start_date`` and ``output_stride`` are supplied by the WW3 adapter from
    typed run evidence rather than by the core transfer implementation.
    """

    def __init__(
        self,
        *,
        start_date: str | None,
        output_stride: int | None,
        naming_policy: str = "restart_only",
    ) -> None:
        if naming_policy not in {"restart_only", "datestamp_all"}:
            raise ValueError(f"Invalid naming_policy: {naming_policy}")
        self.start_date = start_date
        self.output_stride = output_stride
        self.naming_policy = naming_policy

    def __call__(self, artifact: LocalArtifact) -> str:
        """Return one safe destination basename for a typed local artifact."""
        path = Path(artifact.path)
        date = _coerce_date(artifact.date) or self.start_date
        is_restart = artifact.artifact_type is not None and (
            getattr(artifact.artifact_type, "value", artifact.artifact_type)
            == "restart"
        )
        is_restart = is_restart or (
            path.name.lower().startswith("restart")
            and path.name.lower().endswith(".ww3")
        )
        if is_restart and date is not None and self.output_stride is not None:
            return compute_target_name(
                path,
                is_restart=True,
                start_date=date,
                output_stride=self.output_stride,
                restart_path=path,
            )
        if (
            not is_restart
            and self.naming_policy == "datestamp_all"
            and date is not None
        ):
            return compute_target_name(path, date_str=date)
        return path.name


def target_naming_for_run(
    run_result: Any, naming_policy: str = "restart_only"
) -> Callable[[LocalArtifact], str]:
    """Build the WW3 strategy from canonical typed run evidence."""
    timing = getattr(run_result, "timing", None)
    metadata = getattr(run_result, "metadata", {}) or {}
    ww3_metadata = metadata.get("ww3", {}) if isinstance(metadata, dict) else {}
    stride = (
        ww3_metadata.get("restart_stride_seconds")
        if isinstance(ww3_metadata, dict)
        else None
    )
    if isinstance(stride, bool):
        stride = None
    try:
        output_stride = int(stride) if stride is not None else None
    except (TypeError, ValueError):
        output_stride = None
    return WW3TargetNaming(
        start_date=_coerce_date(getattr(timing, "start_time", None)),
        output_stride=output_stride,
        naming_policy=naming_policy,
    )


__all__ = [
    "WW3TargetNaming",
    "compute_restart_valid_date",
    "compute_target_name",
    "normalize_datestamp",
    "target_naming_for_run",
]
