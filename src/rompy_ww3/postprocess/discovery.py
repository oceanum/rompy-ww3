"""File discovery and pattern generation for WW3 output files.

This module provides functions to parse WW3 output configuration from namelists
and deterministically calculate which output files will be created based on
timing parameters (start, stop, stride).
"""

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
    if output_type.field is not None:
        result["field"] = {
            "list": output_type.field.list,
        }

    # Parse point output configuration
    if output_type.point is not None:
        result["point"] = {
            "file": output_type.point.file,
            "name": output_type.point.name,
        }

    # Parse track output configuration
    if output_type.track is not None:
        result["track"] = {
            "format": output_type.track.format,
        }

    # Parse partition output configuration
    if output_type.partition is not None:
        result["partition"] = {
            "x0": output_type.partition.x0,
            "xn": output_type.partition.xn,
            "nx": output_type.partition.nx,
            "y0": output_type.partition.y0,
            "yn": output_type.partition.yn,
            "ny": output_type.partition.ny,
            "format": output_type.partition.format,
        }

    # Parse coupling output configuration
    if output_type.coupling is not None:
        result["coupling"] = {
            "sent": output_type.coupling.sent,
            "received": output_type.coupling.received,
            "couplet0": output_type.coupling.couplet0,
        }

    # Parse restart output configuration
    if output_type.restart is not None:
        result["restart"] = {
            "extra": output_type.restart.extra,
        }

    return result


def generate_manifest(
    output_dir: Path,
    output_type_config: dict,
    start_date: str | None = None,
    stop_date: str | None = None,
    output_stride: int | None = None,
    field_samefile: bool = True,
    field_prefix: str = "ww3.",
    field_timesplit: int | None = None,
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
                delta_map = {
                    4: timedelta(days=365),
                    6: timedelta(days=31),
                    8: timedelta(days=1),
                    10: timedelta(hours=1),
                }
                step = delta_map[field_timesplit]
                current = start_dt
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
                    current += step
        else:
            # No dates available, predict prefix only as a fallback
            filename = f"{field_prefix}*.nc"
            # Don't add wildcard patterns — skip

    # --- Always-present artifacts ---
    if include_always_present:
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


def infer_artifacts_from_files(
    files: list[Path], output_types: dict[str, Any], root: Path | str
) -> list[Artifact]:
    """Infer artifact types from files relative to an explicit workspace root.

    This function determines the artifact type for each file based on its filename
    and the configured output types. It follows WW3 naming conventions:
    - restart* files are classified as OTHER
    - ww3.*.nc files are NETCDF if 'field' is in output_types
    - points.*.nc files are NETCDF if 'point' is in output_types
    - track.*.nc files are NETCDF if 'track' is in output_types
    - All other files are classified as OTHER

    ``root`` is the canonical workspace/staging directory for the run. It must be
    supplied by the caller; deriving a root from the observed files can silently
    discard directory prefixes and turn colliding paths into the same artifact.
    Files which resolve outside that root are skipped.

    Args:
        files: List of Path objects representing files to analyze.
        output_types: Dict mapping output type names to their configurations.
        root: Canonical workspace/staging root for relative artifact paths.

    Returns:
        List[Artifact]: List of artifacts with inferred types and sizes.
    """
    artifacts: list[Artifact] = []
    resolved_root = Path(root).resolve()
    for file_path in files:
        file_path = Path(file_path)
        resolved_file = file_path.resolve()
        try:
            relative_path = resolved_file.relative_to(resolved_root).as_posix()
        except ValueError:
            # Local artifacts must remain bounded by the declared workspace.
            continue

        # Determine artifact type from filename and configured output types
        filename = file_path.name

        if filename.startswith("restart"):
            # Restart files
            artifact_type = ArtifactType.OTHER
        elif filename.startswith("ww3.") and filename.endswith(".nc"):
            # Field output: ww3.*.nc
            artifact_type = (
                ArtifactType.NETCDF if "field" in output_types else ArtifactType.OTHER
            )
        elif filename.startswith("points.") and filename.endswith(".nc"):
            # Point output: points.*.nc
            artifact_type = (
                ArtifactType.NETCDF if "point" in output_types else ArtifactType.OTHER
            )
        elif filename.startswith("track.") and filename.endswith(".nc"):
            # Track output: track.*.nc
            artifact_type = (
                ArtifactType.NETCDF if "track" in output_types else ArtifactType.OTHER
            )
        else:
            # Other files (e.g., spec.nc, arbitrary *.nc)
            artifact_type = ArtifactType.OTHER

        # Determine size if file exists; be resilient if it does not
        try:
            size_bytes = file_path.stat().st_size
        except (OSError, FileNotFoundError):
            size_bytes = None

        artifacts.append(
            Artifact(
                # Canonical local artifact paths are relative to the run output.
                # The inference API has no output-dir argument, so retain the
                # staging-relative filename rather than emitting an invalid absolute path.
                path=relative_path,
                artifact_type=artifact_type,
                size_bytes=size_bytes,
                description=None,
            )
        )

    return artifacts
