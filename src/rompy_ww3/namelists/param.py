"""PARAM_NML namelist implementation for WW3."""

from typing import Optional
from pydantic import Field, field_validator
from .basemodel import NamelistBaseModel


class Param(NamelistBaseModel):
    """PARAM_NML namelist for WW3.

    The PARAM_NML namelist defines the type 2 (mean parameter) output configuration for point output in WAVEWATCH III.
    This namelist controls how mean wave parameters are output for specific points in the model domain.
    
    Type 2 output provides statistical wave parameters derived from the spectra, such as
    significant wave height (HS), mean periods (T01, T02, Tp), mean direction (DIR), 
    directional spread (SPR), and peak direction (DP). This is the most commonly used output type
    for operational wave forecasting and model verification.
    """

    output: Optional[int] = Field(
        default=None,
        description=(
            "Output type for mean parameter data:\n"
            "  1: Forcing parameters (wind, current, etc.)\n"
            "  2: Mean wave parameters (HS, Tp, DIR, etc.)\n"
            "  3: Nondimensional parameters (U*, friction velocity scaled)\n"
            "  4: Nondimensional parameters (U10, 10m wind scaled)\n"
            "  5: Validation table format\n"
            "  6: WMO standard output format\n"
            "This determines the format and content of the mean parameter output."
        ),
        ge=1,
        le=6
    )

    @field_validator('output')
    @classmethod
    def validate_output_type(cls, v):
        """Validate output type."""
        if v is not None and v not in [1, 2, 3, 4, 5, 6]:
            raise ValueError(f"Output type must be 1-6, got {v}")
        return v
