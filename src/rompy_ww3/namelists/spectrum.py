"""SPECTRUM_NML namelist implementation for WW3."""

from typing import Optional
from pydantic import Field, field_validator
from .basemodel import NamelistBaseModel
from .validation import validate_range, validate_direction_bins, validate_frequency_bins


class Spectrum(NamelistBaseModel):
    """SPECTRUM_NML namelist for WW3.

    The SPECTRUM_NML namelist defines the spectral parameterization for WAVEWATCH III.
    This namelist specifies the frequency and direction discretization of the wave spectrum.
    
    The wave spectrum is discretized in frequency and direction. The frequency space
    is typically logarithmically spaced, while the direction space is evenly spaced.
    """

    xfr: Optional[float] = Field(
        default=1.1,
        description=(
            "Frequency increment factor, defines the logarithmic spacing of frequency bins. "
            "The frequency spacing follows: f(i) = freq1 * xfr^(i-1) for i=1,...,nk. "
            "Typical values range from about 1.05 to 1.2, representing 5% to 20% frequency increments."
        ),
        gt=1.0  # Must be greater than 1 for logarithmic spacing
    )
    freq1: Optional[float] = Field(
        default=0.035714,
        description=(
            "First frequency in the spectrum (Hz). This is the lowest frequency in the wave spectrum. "
            "Typical values for ocean applications range from 0.03 Hz (about 33s period) to 0.5 Hz (2s period)."
        ),
        gt=0.0  # Must be positive
    )
    nk: Optional[int] = Field(
        default=25,
        description="Number of frequency bins in the spectrum. This defines spectral resolution in frequency space.",
        ge=2,  # Must have at least 2 frequencies for a spectrum
        le=100  # Reasonable upper limit
    )
    nth: Optional[int] = Field(
        default=25,
        description="Number of direction bins in the spectrum. This defines spectral resolution in direction space.",
        ge=2,  # Must have at least 2 directions for directional spectrum
        le=720  # Reasonable upper limit
    )
    thoff: Optional[float] = Field(
        default=None,
        description=(
            "Relative offset of first direction [-0.5, 0.5], as a fraction of the direction bin size. "
            "This parameter shifts the directional grid. A value of 0 means no offset. "
            "Values of -0.5 or 0.5 create a grid offset by half a bin width."
        ),
        ge=-0.5,  # Lower bound
        le=0.5  # Upper bound
    )

    @field_validator('xfr')
    @classmethod
    def validate_xfr(cls, v):
        """Validate frequency increment factor."""
        if v is not None:
            if v <= 1.0:
                raise ValueError(f"Frequency increment factor (xfr) must be > 1.0, got {v}")
            if v > 2.0:  # Reasonable upper limit
                raise ValueError(f"Frequency increment factor (xfr) seems too high: {v}")
        return v

    @field_validator('freq1')
    @classmethod
    def validate_freq1(cls, v):
        """Validate first frequency."""
        if v is not None:
            if v <= 0.0:
                raise ValueError(f"First frequency (freq1) must be positive, got {v}")
            if v > 1.0:  # Frequencies > 1 Hz are extremely high for ocean waves
                raise ValueError(f"First frequency (freq1) seems too high: {v}")
        return v

    @field_validator('nk')
    @classmethod
    def validate_nk(cls, v):
        """Validate number of frequency bins."""
        if v is not None:
            if v < 2:
                raise ValueError(f"Number of frequency bins (nk) must be at least 2, got {v}")
        return v

    @field_validator('nth')
    @classmethod
    def validate_nth(cls, v):
        """Validate number of direction bins."""
        if v is not None:
            if v < 2:
                raise ValueError(f"Number of direction bins (nth) must be at least 2, got {v}")
        return v

    @field_validator('thoff')
    @classmethod
    def validate_thoff(cls, v):
        """Validate direction offset."""
        if v is not None:
            if v < -0.5 or v > 0.5:
                raise ValueError(f"Direction offset (thoff) must be between -0.5 and 0.5, got {v}")
        return v
