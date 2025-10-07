"""SPECTRUM_NML namelist implementation for WW3."""

from typing import Optional
from pydantic import Field
from .basemodel import NamelistBaseModel


class Spectrum(NamelistBaseModel):
    """SPECTRUM_NML namelist for WW3.

    Defines the spectrum parameterization.
    """

    xfr: Optional[float] = Field(default=1.1, description="Frequency increment")
    freq1: Optional[float] = Field(default=0.035714, description="First frequency (Hz)")
    nk: Optional[int] = Field(
        default=25, description="Number of frequencies (wavenumbers)"
    )
    nth: Optional[int] = Field(default=25, description="Number of direction bins")
    thoff: Optional[float] = Field(
        default=None, description="Relative offset of first direction [-0.5,0.5]"
    )
