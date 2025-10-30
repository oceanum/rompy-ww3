"""SPECTRA_NML namelist implementation for WW3."""

from typing import Optional
from pydantic import Field, field_validator
from .basemodel import NamelistBaseModel


class Spectra(NamelistBaseModel):
    """SPECTRA_NML namelist for WW3.

    The SPECTRA_NML namelist defines the type 1 (spectra) output configuration for point output in WAVEWATCH III.
    This namelist controls how full wave spectra are output for specific points in the model domain.
    
    Type 1 output provides the complete 2D wave spectrum at specified points, which can be used for
    detailed spectral analysis, verification against observations, or as input to other spectral models.
    """

    output: Optional[int] = Field(
        default=None,
        description=(
            "Output type for spectra data:\n"
            "  1: Print plots (human-readable spectral plots)\n"
            "  2: Table of 1-D spectra (frequency-integrated spectra)\n"
            "  3: Transfer file (binary format for model-to-model transfer)\n"
            "  4: Spectral partitioning (separated swell partitions)\n"
            "This determines the format and content of the spectral output."
        ),
        ge=1,
        le=4
    )
    scale_fac: Optional[int] = Field(
        default=None,
        description=(
            "Scale factor for spectral output. This controls scaling of spectral values:\n"
            "  -1: Disabled (no scaling applied)\n"
            "  Other values: Scaling factor applied to spectra\n"
            "This is used to adjust units or magnitudes of spectral values in output."
        )
    )
    output_fac: Optional[int] = Field(
        default=None,
        description=(
            "Output factor for normalized spectra:\n"
            "  0: Normalized spectra (energy normalized to 1)\n"
            "  Other values: Non-normalized spectra with specified factor\n"
            "This controls whether spectra are normalized or output with original magnitudes."
        )
    )

    @field_validator('output')
    @classmethod
    def validate_output_type(cls, v):
        """Validate output type."""
        if v is not None and v not in [1, 2, 3, 4]:
            raise ValueError(f"Output type must be 1, 2, 3, or 4, got {v}")
        return v

    @field_validator('scale_fac')
    @classmethod
    def validate_scale_factor(cls, v):
        """Validate scale factor."""
        if v is not None and v == -1:
            # -1 is valid (disabled)
            pass
        elif v is not None and not isinstance(v, int):
            raise ValueError(f"Scale factor must be an integer, got {type(v)}")
        return v

    @field_validator('output_fac')
    @classmethod
    def validate_output_factor(cls, v):
        """Validate output factor."""
        if v is not None and not isinstance(v, int):
            raise ValueError(f"Output factor must be an integer, got {type(v)}")
        return v
