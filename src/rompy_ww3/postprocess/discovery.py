"""File discovery and pattern generation for WW3 output files.

This module provides functions to parse WW3 output configuration from namelists
and deterministically calculate which output files will be created based on
timing parameters (start, stop, stride).
"""

from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

from rompy_ww3.namelists.output_type import OutputType


def parse_output_type(output_type: OutputType) -> Dict[str, Any]:
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
    result: Dict[str, Optional[Dict[str, Any]]] = {
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
    start_date: Optional[str] = None,
    stop_date: Optional[str] = None,
    output_stride: Optional[int] = None,
) -> List[Path]:
    """Calculate manifest of WW3 output files based on timing configuration.

    Deterministically calculates which output files WW3 will create based on
    the configured output types and timing parameters. Does NOT scan filesystem.

    Args:
        output_dir: Directory where WW3 output files will be located
        output_type_config: Dictionary with output type configuration
        start_date: Simulation start date in 'YYYYMMDD HHMMSS' format
        stop_date: Simulation stop date in 'YYYYMMDD HHMMSS' format
        output_stride: Output stride in seconds

    Returns:
        List of Path objects for files that will be created

    Raises:
        ValueError: If required timing parameters are missing for restart output
    """
    manifest: List[Path] = []

    if output_type_config.get("restart") is not None:
        if start_date is None or stop_date is None or output_stride is None:
            raise ValueError(
                "start_date, stop_date, and output_stride are required "
                "to calculate restart file manifest"
            )

        start_dt = datetime.strptime(start_date, "%Y%m%d %H%M%S")
        stop_dt = datetime.strptime(stop_date, "%Y%m%d %H%M%S")
        stride_td = timedelta(seconds=output_stride)

        current_dt = start_dt + stride_td
        file_num = 1

        while current_dt <= stop_dt:
            restart_file = output_dir / f"restart{file_num:03d}.ww3"
            manifest.append(restart_file)
            current_dt += stride_td
            file_num += 1

    return manifest
