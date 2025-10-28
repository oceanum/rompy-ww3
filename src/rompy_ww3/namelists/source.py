"""SOURCE_NML namelist implementation for WW3."""

from typing import Optional
from pydantic import Field
from .basemodel import NamelistBaseModel


class Source(NamelistBaseModel):
    """SOURCE_NML namelist for WW3.

    Defines type 3 (source terms) output configuration for point output.
    """

    output: Optional[int] = Field(
        default=None,
        description=(
            "Output type: "
            "1=Print plots, "
            "2=Table of 1-D S(f), "
            "3=Table of 1-D inverse time scales (1/T = S/F), "
            "4=Transfer file"
        ),
    )
    scale_fac: Optional[int] = Field(
        default=None, description="Scale factor (-1=disabled)"
    )
    output_fac: Optional[int] = Field(
        default=None, description="Output factor (0=normalized)"
    )
    table_fac: Optional[int] = Field(
        default=None,
        description=(
            "Table factor: "
            "0=Dimensional, "
            "1=Nondimensional in terms of U10, "
            "2=Nondimensional in terms of U*, "
            "3-5=like 0-2 with f normalized with fp"
        ),
    )
    spectrum: Optional[bool] = Field(
        default=None, description="Include spectrum in output (T/F)"
    )
    input: Optional[bool] = Field(
        default=None, description="Include input source term in output (T/F)"
    )
    interactions: Optional[bool] = Field(
        default=None, description="Include non linear interactions in output (T/F)"
    )
    dissipation: Optional[bool] = Field(
        default=None, description="Include dissipation source term in output (T/F)"
    )
    bottom: Optional[bool] = Field(
        default=None, description="Include bottom source term in output (T/F)"
    )
    ice: Optional[bool] = Field(
        default=None, description="Include ice source term in output (T/F)"
    )
    total: Optional[bool] = Field(
        default=None, description="Include total source term in output (T/F)"
    )
