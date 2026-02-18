"""File discovery and pattern generation for WW3 output files.

This module provides functions to parse WW3 output configuration from namelists
and discover output files based on the configured output types.
"""

from pathlib import Path
from typing import Any, Dict, Optional

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


def generate_manifest(output_dir: Path, output_type_config: dict) -> list[Path]:
    """Generate a manifest of expected WW3 output files (v1, restart-only).

    This minimal implementation is a proof-of-concept for Task 8. It only
    handles the restart output type. When restart is configured in the input
    dictionary, it returns a single Path for the restart file:
    output_dir / "restart.ww3". If restart is not configured, an empty list is
    returned.

    Notes for future outputs (not implemented in v1):
    - field, point, track, partition, coupling output types
    - Timestamped filenames and additional fields need to be computed
    - This function should leverage parse_output_type() once a proper OutputType
      object can be constructed from the dict (for now we keep v1 simple).
    """
    manifest: list[Path] = []

    # V1: only support restart output
    if output_type_config.get("restart") is not None:
        manifest.append(output_dir / "restart.ww3")

    return manifest
