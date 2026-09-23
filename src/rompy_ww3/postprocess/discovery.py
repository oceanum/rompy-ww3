"""File discovery and pattern generation for WW3 output files.

This module provides functions to parse WW3 output configuration from namelists
and deterministically calculate which output files will be created based on
timing parameters (start, stop, stride).
"""

from calendar import monthrange
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from rompy.core.responses import Artifact, ArtifactType

from rompy_ww3.namelists.output_type import OutputType


def parse_output_type(output_type: OutputType) -> dict[str, Any]:
    """Parse OutputType namelist and extract configuration for all output types.

    This function extracts configuration from a WW3 OutputType namelist object,
    returning a dictionary containing the configuration for all 6 WW3 output types:
    field, point, track, partition, coupling, and restart.

    Args:
        output_type: WW3 OutputType namelist object containing output configuration

    Returns:
        Dictionary with keys for each output type. Each value is either:
        - None if the output type is not configured
        - A dict containing the configuration for that output type

    Example:
        >>> from rompy_ww3.namelists.output_type import OutputType, OutputTypeField
        >>> output_type = OutputType(field=OutputTypeField(list="HS DIR SPR"))
        >>> config = parse_output_type(output_type)
        >>> config["field"]
        {"list": "HS DIR SPR"}
        >>> config["point"]
        None
    """
    result: dict[str, dict[str, Any] | None] = {
        "field": None,
        "point": None,
        "track": None,
        "partition": None,
        "coupling": None,
        "restart": None,
    }

    # Parse field output configuration
    field = getattr(output_type, "field", None)
    if field is not None:
        result["field"] = {"list": field.list}

    # Parse point output configuration
    point = getattr(output_type, "point", None)
    if point is not None:
        result["point"] = {"file": point.file, "name": point.name}

    # Parse track output configuration
    track = getattr(output_type, "track", None)
    if track is not None:
        result["track"] = {"format": track.format}

    # Parse partition output configuration
    partition = getattr(output_type, "partition", None)
    if partition is not None:
        result["partition"] = {
            "x0": partition.x0,
            "xn": partition.xn,
            "nx": partition.nx,
            "y0": partition.y0,
            "yn": partition.yn,
            "ny": partition.ny,
            "format": partition.format,
        }

    # Parse coupling output configuration
    coupling = getattr(output_type, "coupling", None)
    if coupling is not None:
        result["coupling"] = {
            "sent": coupling.sent,
            "received": coupling.received,
            "couplet0": coupling.couplet0,
        }

    # Parse restart output configuration
    restart = getattr(output_type, "restart", None)
    if restart is not None:
        result["restart"] = {"extra": restart.extra}

    return result


def _advance_split_period(current: datetime, timesplit: int) -> datetime:
    """Advance one WW3 split period without calendar-day drift."""
    if timesplit == 4:
        year = current.year + 1
        day = min(current.day, monthrange(year, current.month)[1])
        return current.replace(year=year, day=day)
    if timesplit == 6:
        year = current.year + (current.month == 12)
        month = 1 if current.month == 12 else current.month + 1
        day = min(current.day, monthrange(year, month)[1])
        return current.replace(year=year, month=month, day=day)
    if timesplit == 8:
        return current + timedelta(days=1)
    if timesplit == 10:
        return current + timedelta(hours=1)
    raise ValueError(f"Unsupported WW3 time split: {timesplit}")


def generate_manifest(
    output_dir: Path,
    output_type_config: dict,
    start_date: str | None = None,
    stop_date: str | None = None,
    output_stride: int | None = None,
    field_samefile: bool = True,
    field_prefix: str = "ww3.",
    field_timesplit: int | None = None,
    point_prefix: str = "points.",
    track_prefix: str = "track.",
    point_samefile: bool = True,
    point_timesplit: int | None = None,
    point_start_date: str | None = None,
    point_stop_date: str | None = None,
    track_timesplit: int | None = None,
    track_start_date: str | None = None,
    track_stop_date: str | None = None,
    point_window_strict: bool = False,
    track_window_strict: bool = False,
    always_present: list[tuple[str, ArtifactType]] | None = None,
    include_always_present: bool = True,
) -> list[Artifact]:
    """Calculate manifest of WW3 output files based on timing configuration.

    Deterministically calculates which output files WW3 will create based on
    the configured output types and timing parameters. Does NOT scan filesystem.

    Args:
        output_dir: Directory where WW3 output files will be located.
        output_type_config: Dictionary with output type configuration
            (keys: field, point, track, restart, ...).
        start_date: Simulation start date in 'YYYYMMDD HHMMSS' format.
        stop_date: Simulation stop date in 'YYYYMMDD HHMMSS' format.
        output_stride: Restart output stride in seconds.
        field_samefile: Whether field output uses single-file mode (True) or
            split-file mode (False). Default True.
        field_prefix: Prefix for field output filenames (e.g. ``"ww3."``).
        field_timesplit: Time-splitting option for multi-file field output.
            Ignored when field_samefile=True.
        point_prefix: Prefix for deterministic point NetCDF output.
        track_prefix: Prefix for deterministic track NetCDF output.
        point_samefile: Whether point output uses one file.
        point_timesplit: Point split code (4/6/8/10) when split.
        point_start_date: Point output start date, falling back to ``start_date``.
        point_stop_date: Point output stop date, falling back to ``stop_date``.
        track_timesplit: Track split code (4/6/8/10) when split.
        track_start_date: Track output start date, falling back to ``start_date``.
        track_stop_date: Track output stop date, falling back to ``stop_date``.
        point_window_strict: Do not fall back to domain stop for configured point
            component windows.
        track_window_strict: Do not fall back to domain stop for configured track
            component windows.
        always_present: Explicit component-generated always-present artifacts.
        include_always_present: Whether to include always-present WW3 artifacts
            (mod_def.ww3, log.ww3, namelist files, shell scripts). Default True.

    Returns:
        List of Artifact objects with relative paths and correct ArtifactType.

    Raises:
        ValueError: If required timing parameters are missing for restart output.
    """
    manifest: list[Artifact] = []

    # --- Restart files ---
    if output_type_config.get("restart") is not None:
        if start_date is None or stop_date is None or output_stride is None:
            raise ValueError(
                "start_date, stop_date, and output_stride are required "
                "to calculate restart file manifest"
            )

        start_dt = datetime.strptime(start_date, "%Y%m%d %H%M%S").replace(
            tzinfo=timezone.utc
        )
        stop_dt = datetime.strptime(stop_date, "%Y%m%d %H%M%S").replace(
            tzinfo=timezone.utc
        )
        stride_td = timedelta(seconds=output_stride)

        current_dt = start_dt + stride_td
        file_num = 1

        while current_dt <= stop_dt:
            filename = f"restart{file_num:03d}.ww3"
            manifest.append(
                Artifact(
                    path=filename,
                    artifact_type=ArtifactType.RESTART,
                )
            )
            current_dt += stride_td
            file_num += 1

    # --- Field output files ---
    if output_type_config.get("field") is not None:
        if start_date is not None:
            # Derive YYYYMM suffix from start_date
            try:
                start_dt = datetime.strptime(start_date, "%Y%m%d %H%M%S").replace(
                    tzinfo=timezone.utc
                )
            except ValueError:
                start_dt = datetime.strptime(start_date, "%Y%m%d").replace(
                    tzinfo=timezone.utc
                )
            date_suffix = start_dt.strftime("%Y%m")
        else:
            date_suffix = "000000"

        if field_samefile:
            # Single file: {prefix}YYYYMM.nc
            filename = f"{field_prefix}{date_suffix}.nc"
            manifest.append(
                Artifact(
                    path=filename,
                    artifact_type=ArtifactType.NETCDF,
                )
            )
        elif (
            field_timesplit is not None
            and start_date is not None
            and stop_date is not None
        ):
            # Multi-file mode: split by timesplit interval
            timesplit_map = {
                4: ("yearly", "%Y"),
                6: ("monthly", "%Y%m"),
                8: ("daily", "%Y%m%d"),
                10: ("hourly", "%Y%m%d%H"),
            }
            if field_timesplit not in timesplit_map:
                # Fall back to single file
                filename = f"{field_prefix}{date_suffix}.nc"
                manifest.append(
                    Artifact(
                        path=filename,
                        artifact_type=ArtifactType.NETCDF,
                    )
                )
            else:
                _, fmt = timesplit_map[field_timesplit]
                start_dt = datetime.strptime(start_date, "%Y%m%d %H%M%S").replace(
                    tzinfo=timezone.utc
                )
                stop_dt = datetime.strptime(stop_date, "%Y%m%d %H%M%S").replace(
                    tzinfo=timezone.utc
                )
                current = start_dt
                if field_timesplit == 6:
                    current = current.replace(day=1)
                while current <= stop_dt:
                    date_suffix = current.strftime(fmt)
                    filename = f"{field_prefix}{date_suffix}.nc"
                    # Deduplicate
                    if not any(a.path == filename for a in manifest):
                        manifest.append(
                            Artifact(
                                path=filename,
                                artifact_type=ArtifactType.NETCDF,
                            )
                        )
                    current = _advance_split_period(current, field_timesplit)
        else:
            # No dates available, predict prefix only as a fallback
            filename = f"{field_prefix}*.nc"
            # Don't add wildcard patterns — skip

    def split_output_names(
        prefix: str,
        samefile: bool,
        timesplit: int | None,
        split_start: str | None,
        split_stop: str | None,
        fallback_start: str | None,
        fallback_stop: str | None,
    ) -> list[str]:
        """Return one or deterministic split-period output names."""
        effective_start = split_start or fallback_start
        effective_stop = split_stop or fallback_stop
        if samefile or timesplit is None or timesplit == 0 or not effective_start:
            if effective_start is None:
                suffix = "000000"
            else:
                try:
                    parsed_start = datetime.strptime(
                        effective_start, "%Y%m%d %H%M%S"
                    ).replace(tzinfo=timezone.utc)
                except ValueError:
                    parsed_start = datetime.strptime(
                        effective_start, "%Y%m%d"
                    ).replace(tzinfo=timezone.utc)
                suffix = parsed_start.strftime("%Y%m")
            return [f"{prefix}{suffix}.nc"]
        formats = {4: "%Y", 6: "%Y%m", 8: "%Y%m%d", 10: "%Y%m%d%H"}
        if timesplit not in formats or not effective_stop:
            return split_output_names(prefix, True, None, effective_start, effective_stop, None, None)
        current = datetime.strptime(effective_start, "%Y%m%d %H%M%S").replace(tzinfo=timezone.utc)
        stop = datetime.strptime(effective_stop, "%Y%m%d %H%M%S").replace(tzinfo=timezone.utc)
        if timesplit == 6:
            current = current.replace(day=1)
        names: list[str] = []
        while current <= stop:
            name = f"{prefix}{current.strftime(formats[timesplit])}.nc"
            if name not in names:
                names.append(name)
            current = _advance_split_period(current, timesplit)
        return names

    # --- Point and track NetCDF outputs ---
    if output_type_config.get("point") is not None:
        manifest.extend(
            Artifact(path=name, artifact_type=ArtifactType.NETCDF)
            for name in split_output_names(
                point_prefix,
                point_samefile,
                point_timesplit,
                point_start_date,
                point_stop_date,
                None if point_window_strict else start_date,
                None if point_window_strict else stop_date,
            )
        )
    if output_type_config.get("track") is not None:
        manifest.extend(
            Artifact(path=name, artifact_type=ArtifactType.NETCDF)
            for name in split_output_names(
                track_prefix,
                False,
                track_timesplit,
                track_start_date,
                track_stop_date,
                None if track_window_strict else start_date,
                None if track_window_strict else stop_date,
            )
        )

    # --- Always-present artifacts ---
    if include_always_present:
        if always_present is None:
            always_present = [
                ("mod_def.ww3", ArtifactType.OTHER),
                ("log.ww3", ArtifactType.TEXT),
                ("ww3_grid.nml", ArtifactType.TEXT),
                ("ww3_shel.nml", ArtifactType.TEXT),
                ("ww3_ounf.nml", ArtifactType.TEXT),
                ("namelists.nml", ArtifactType.TEXT),
                ("full_ww3.sh", ArtifactType.TEXT),
                ("preprocess_ww3.sh", ArtifactType.TEXT),
                ("postprocess_ww3.sh", ArtifactType.TEXT),
                ("run_ww3.sh", ArtifactType.TEXT),
                ("ST4TABUHF2.bin", ArtifactType.OTHER),
                ("mapsta.ww3", ArtifactType.OTHER),
                ("mask.ww3", ArtifactType.OTHER),
                ("out_grd.ww3", ArtifactType.OTHER),
            ]
        for filename, atype in always_present:
            manifest.append(
                Artifact(
                    path=filename,
                    artifact_type=atype,
                )
            )

    return manifest
