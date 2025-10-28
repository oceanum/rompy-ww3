"""SPECTRA_NML namelist implementation for WW3."""

from typing import Optional
from pydantic import Field
from .basemodel import NamelistBaseModel


class Spectra(NamelistBaseModel):
    """SPECTRA_NML namelist for WW3.

    Defines type 1 (spectra) output configuration for point output.
    """

    output: Optional[int] = Field(
        default=None,
        description=(
            "Output type: "
            "1=Print plots, "
            "2=Table of 1-D spectra, "
            "3=Transfer file, "
            "4=Spectral partitioning"
        ),
    )
    scale_fac: Optional[int] = Field(
        default=None, description="Scale factor (-1=disabled)"
    )
    output_fac: Optional[int] = Field(
        default=None, description="Output factor (0=normalized)"
    )
