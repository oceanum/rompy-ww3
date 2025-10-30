"""DOMAIN_NML namelist implementation for WW3."""

from typing import Optional
from pydantic import Field, field_validator
from .basemodel import NamelistBaseModel
from .validation import validate_date_format, validate_io_type


class Domain(NamelistBaseModel):
    """DOMAIN_NML namelist for WW3.

    The DOMAIN_NML namelist defines top-level model parameters for WAVEWATCH III.
    This namelist is used by both single-grid (ww3_shel) and multi-grid (ww3_multi) programs.

    For single-grid implementation:
    - IOSTYP defines the output server mode for parallel implementation
    - START and STOP define the simulation time period

    For multi-grid implementation:
    - NRINP defines the number of grids for input fields
    - NRGRD defines the number of wave model grids
    - Various flags control output behavior in multi-grid runs
    """

    # Single-grid parameters
    start: Optional[str] = Field(
        default=None,
        description=(
            "Start date for the entire model in format 'YYYYMMDD HHMMSS'. "
            "This sets the starting time for the wave model simulation. "
            "Example: '20100101 120000' for January 1, 2010 at 12:00:00 UTC."
        )
    )
    stop: Optional[str] = Field(
        default=None,
        description=(
            "Stop date for the entire model in format 'YYYYMMDD HHMMSS'. "
            "This sets the ending time for the wave model simulation. "
            "Example: '20101231 000000' for December 31, 2010 at 00:00:00 UTC."
        )
    )
    iostyp: Optional[int] = Field(
        default=None,
        description=(
            "Output server type defining how output is handled in parallel implementation:\n"
            "  0: No data server processes, direct access output from each process "
            "(requires true parallel file system)\n"
            "  1: No data server process. All output for each type performed by process "
            "that performs computations too\n"
            "  2: Last process is reserved for all output, and does no computing\n"
            "  3: Multiple dedicated output processes"
        ),
        ge=0,
        le=3
    )

    # Multi-grid parameters
    nrinp: Optional[int] = Field(
        default=None,
        description="Number of grids defining input fields (for multi-grid runs).",
        ge=1
    )
    nrgrd: Optional[int] = Field(
        default=None,
        description="Number of wave model grids (for multi-grid runs).",
        ge=1
    )
    unipts: Optional[bool] = Field(
        default=None,
        description="Flag for using unified point output file (for multi-grid runs)."
    )
    upproc: Optional[bool] = Field(
        default=None,
        description="Flag for dedicated process for unified point output (for multi-grid runs)."
    )
    pshare: Optional[bool] = Field(
        default=None,
        description="Flag for grids sharing dedicated output processes (for multi-grid runs)."
    )
    flghg1: Optional[bool] = Field(
        default=None,
        description="Flag for masking computation in two-way nesting (for multi-grid runs)."
    )
    flghg2: Optional[bool] = Field(
        default=None,
        description="Flag for masking at printout time (for multi-grid runs)."
    )

    @field_validator('start', 'stop')
    @classmethod
    def validate_date_fields(cls, v):
        """Validate date format for start and stop fields."""
        if v is not None:
            return validate_date_format(v)
        return v

    @field_validator('iostyp')
    @classmethod
    def validate_iostyp_field(cls, v):
        """Validate IOSTYP field value."""
        if v is not None:
            return validate_io_type(v)
        return v
