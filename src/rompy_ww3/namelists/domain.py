"""DOMAIN_NML namelist implementation for WW3."""

from typing import Optional
from pydantic import Field
from .basemodel import NamelistBaseModel


class Domain(NamelistBaseModel):
    """DOMAIN_NML namelist for WW3.

    Defines top-level model parameters.
    """

    # Single-grid parameters
    start: Optional[str] = Field(
        default=None, description="Start date for the entire model (yyyymmdd hhmmss)"
    )
    stop: Optional[str] = Field(
        default=None, description="Stop date for the entire model (yyyymmdd hhmmss)"
    )
    iostyp: Optional[int] = Field(default=None, description="Output server type (0-3)")

    # Multi-grid parameters
    nrinp: Optional[int] = Field(
        default=None, description="Number of grids defining input fields"
    )
    nrgrd: Optional[int] = Field(default=None, description="Number of wave model grids")
    unipts: Optional[bool] = Field(
        default=None, description="Flag for using unified point output file"
    )
    upproc: Optional[bool] = Field(
        default=None, description="Flag for dedicated process for unified point output"
    )
    pshare: Optional[bool] = Field(
        default=None, description="Flag for grids sharing dedicated output processes"
    )
    flghg1: Optional[bool] = Field(
        default=None, description="Flag for masking computation in two-way nesting"
    )
    flghg2: Optional[bool] = Field(
        default=None, description="Flag for masking at printout time"
    )
