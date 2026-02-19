"""RESTART_NML namelist implementation for WW3."""

from datetime import datetime
from typing import Optional
from pydantic import Field, field_validator
from .basemodel import NamelistBaseModel
from .validation import validate_date_format


class Restart(NamelistBaseModel):
    """RESTART_NML namelist for WW3.

    The RESTART_NML namelist defines the restart time for initializing the wave model in WAVEWATCH III.
    This namelist specifies the time at which the model should initialize from restart files,
    allowing continuation of simulations from a previous state.

    The restart time is used to select the appropriate restart file(s) for model initialization.
    This is essential for long-term simulations that need to be broken into segments or
    for initializing forecasts from analysis states.
    """

    restarttime: Optional[datetime] = Field(
        default=None,
        description=(
            "Restart time for model initialization. Accepts datetime objects or strings in format 'YYYYMMDD HHMMSS'. "
            "This specifies the time at which the model should initialize from restart files. "
            "The model will look for restart files corresponding to this time to initialize "
            "the wave spectra and other state variables. "
            "Example: datetime(2010, 1, 1, 0, 0, 0) or '20100101 000000' for January 1, 2010 at 00:00:00 UTC."
        ),
    )

    @field_validator("restarttime", mode="before")
    @classmethod
    def parse_restarttime(cls, v):
        """Parse date string to datetime object (backward-compatible)."""
        if v is None:
            return v
        if isinstance(v, str):
            # Validate format first (reuse existing validation)
            validate_date_format(v)
            # Parse WW3 format: YYYYMMDD HHMMSS
            try:
                parsed = datetime.strptime(v, "%Y%m%d %H%M%S")
                if parsed.tzinfo is not None:
                    raise ValueError(
                        "Timezone-aware datetimes not supported - use naive datetimes only"
                    )
                return parsed
            except ValueError as e:
                raise ValueError(
                    f"Invalid date format for 'restarttime': {v}. Expected 'YYYYMMDD HHMMSS'. Error: {e}"
                )
        if isinstance(v, datetime):
            if v.tzinfo is not None:
                raise ValueError(
                    "Timezone-aware datetimes not supported - use naive datetimes only"
                )
            return v
        return v


class Update(NamelistBaseModel):
    """Update approach and associated variables for WW3.

    The Update namelist defines parameters for adjusting or correcting model states during initialization.
    This is typically used for data assimilation or model state corrections to improve forecast accuracy.

    The update parameters control how observational data or analysis corrections are applied
    to the model state, including correction factors and caps on maximum adjustments.
    """

    prcntg: Optional[float] = Field(
        default=None,
        description=(
            "Percentage correction factor applied to all grid points during model update. "
            "This is a multiplicative factor applied to the wave spectra during initialization. "
            "A value of 1.0 means no change, values > 1.0 amplify the spectra, values < 1.0 dampen it. "
            "Example: 1.0 for no change, 1.1 for 10% amplification, 0.9 for 10% damping."
        ),
        gt=0,  # Must be positive
    )
    prcntg_cap: Optional[float] = Field(
        default=None,
        description=(
            "Cap on maximum significant wave height (SWH) correction factor. "
            "This limits how much the wave spectra can be amplified during the update process. "
            "The value should not be less than 1.0 to prevent damping of already corrected fields. "
            "Example: 1.5 to limit maximum amplification to 50% above original values."
        ),
        ge=1.0,  # Should not be less than 1.0
    )

    @field_validator("prcntg")
    @classmethod
    def validate_prcntg(cls, v):
        """Validate percentage correction factor."""
        if v is not None and v <= 0:
            raise ValueError(
                f"Percentage correction factor (prcntg) must be positive, got {v}"
            )
        return v

    @field_validator("prcntg_cap")
    @classmethod
    def validate_prcntg_cap(cls, v):
        """Validate percentage cap."""
        if v is not None and v < 1.0:
            raise ValueError(
                f"Percentage cap (prcntg_cap) should not be less than 1.0, got {v}"
            )
        return v
