"""BOUND_NML namelist implementation for WW3."""

from typing import Optional
from pydantic import Field, field_validator
from .basemodel import NamelistBaseModel
from ..core.data import WW3DataBlob, WW3Boundary
from typing import Union


class Bound(NamelistBaseModel):
    """BOUND_NML namelist for WW3.

    The BOUND_NML namelist defines the input boundaries for preprocessing in WAVEWATCH III.
    This namelist is used by the ww3_bounc program to handle boundary data.

    This namelist controls how boundary conditions are read from or written to files,
    including interpolation methods and verbosity of output.
    """

    mode: Optional[str] = Field(
        default=None,
        description=(
            "Processing mode for boundary data:\n"
            "  'WRITE': Write boundary data to output files\n"
            "  'READ': Read boundary data from input files\n"
            "This determines the direction of data flow for boundary processing."
        ),
    )
    interp: Optional[int] = Field(
        default=2,
        description=(
            "Interpolation method for boundary data:\n"
            "  1: Nearest neighbor interpolation\n"
            "  2: Linear interpolation (default)\n"
            "This controls how boundary data is interpolated when necessary."
        ),
        ge=1,
        le=2,
    )
    verbose: Optional[int] = Field(
        default=1,
        description=(
            "Verbosity level for boundary processing output:\n"
            "  0: Minimal output\n"
            "  1: Standard output (default)\n"
            "  2: Detailed output\n"
            "This controls the level of detail in the processing logs."
        ),
        ge=0,
        le=2,
    )
    file: Optional[Union[str, WW3DataBlob, WW3Boundary]] = Field(
        default=None,
        description=(
            "Input/output file specification containing boundary data. "
            "This can be a string path, WW3DataBlob, or WW3Boundary object "
            "containing the boundary conditions in netCDF format (typically spec.nc)."
        ),
    )

    @field_validator("mode")
    @classmethod
    def validate_mode(cls, v):
        """Validate mode is either 'WRITE' or 'READ'."""
        if v is not None:
            valid_modes = {"WRITE", "READ", "write", "read"}
            if v.upper() not in valid_modes:
                raise ValueError(f"Mode must be 'WRITE' or 'READ', got {v}")
        return v.upper() if v is not None else v

    @field_validator("interp")
    @classmethod
    def validate_interp(cls, v):
        """Validate interpolation method."""
        if v is not None:
            if v not in [1, 2]:
                raise ValueError(
                    f"Interpolation method must be 1 (nearest) or 2 (linear), got {v}"
                )
        return v

    @field_validator("verbose")
    @classmethod
    def validate_verbose(cls, v):
        """Validate verbosity level."""
        if v is not None:
            if v not in [0, 1, 2]:
                raise ValueError(f"Verbosity level must be 0, 1, or 2, got {v}")
        return v
