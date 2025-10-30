"""RUN_NML namelist implementation for WW3."""

from typing import Optional
from pydantic import Field, field_validator
from .basemodel import NamelistBaseModel


class Run(NamelistBaseModel):
    """RUN_NML namelist for WW3.

    The RUN_NML namelist defines the run parameterization for WAVEWATCH III.
    This namelist controls which physical processes are active during the simulation.
    Each flag enables or disables a specific component of the wave model physics.
    """

    fldry: Optional[bool] = Field(
        default=None,
        description=(
            "Dry run flag. If true, performs I/O operations only without calculations. "
            "This is useful for testing file operations and namelist parsing without "
            "executing the full model simulation. When enabled, the model will go through "
            "the motions of reading and writing files but will not perform wave calculations."
        )
    )
    flcx: Optional[bool] = Field(
        default=None,
        description=(
            "X-component of propagation flag. If true, enables propagation in the X direction. "
            "This controls the spatial advection of wave energy in the X (typically longitudinal) "
            "direction. Disabling this would prevent wave energy from moving in the X direction."
        )
    )
    flcy: Optional[bool] = Field(
        default=None,
        description=(
            "Y-component of propagation flag. If true, enables propagation in the Y direction. "
            "This controls the spatial advection of wave energy in the Y (typically latitudinal) "
            "direction. Disabling this would prevent wave energy from moving in the Y direction."
        )
    )
    flcth: Optional[bool] = Field(
        default=None,
        description=(
            "Direction shift flag. If true, enables directional shifting of the wave spectrum. "
            "This controls the propagation of wave energy in directional space (theta-advection). "
            "This process accounts for changes in wave direction due to refraction, current effects, etc."
        )
    )
    flck: Optional[bool] = Field(
        default=None,
        description=(
            "Wavenumber shift flag. If true, enables wavenumber shifting of the wave spectrum. "
            "This controls the propagation of wave energy in wavenumber space (k-advection). "
            "This process accounts for changes in wave frequency due to current and depth variations."
        )
    )
    flsou: Optional[bool] = Field(
        default=None,
        description=(
            "Source terms flag. If true, enables source terms (wind input, nonlinear wave-wave "
            "interactions, and dissipation). This controls the energy input and output processes "
            "that affect the wave spectrum. Disabling this would result in wave energy being "
            "only advected without any gain or loss of energy."
        )
    )

    @field_validator('fldry', 'flcx', 'flcy', 'flcth', 'flck', 'flsou')
    @classmethod
    def validate_boolean_flags(cls, v):
        """Validate that all flags are boolean values."""
        if v is not None and not isinstance(v, bool):
            raise ValueError(f"Flag must be a boolean value, got {type(v)}")
        return v
