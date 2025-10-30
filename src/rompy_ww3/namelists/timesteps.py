"""TIMESTEPS_NML namelist implementation for WW3."""

from typing import Optional
from pydantic import Field, model_validator
from .basemodel import NamelistBaseModel

#  -------------------------------------------------------------------- !
#  Define the timesteps parameterization via TIMESTEPS_NML namelist
#
#  * It is highly recommended to set up time steps which are multiple
#    between them.
#
#  * The first time step to calculate is the maximum CFL time step
#    which depend on the lowest frequency FREQ1 previously set up and the
#    lowest spatial grid resolution in meters DXY.
#    reminder : 1 degree=60minutes // 1minute=1mile // 1mile=1.852km
#    The formula for the CFL time is :
#    Tcfl = DXY / (G / (FREQ1*4*Pi) ) with the constants Pi=3,14 and G=9.8m/s²;
#    DTXY  ~= 90% Tcfl
#    DTMAX ~= 3 * DTXY   (maximum global time step limit)
#
#  * The refraction time step depends on how strong can be the current velocities
#    on your grid :
#    DTKTH ~= DTMAX / 2   ! in case of no or light current velocities
#    DTKTH ~= DTMAX / 10  ! in case of strong current velocities
#
#  * The source terms time step is usually defined between 5s and 60s.
#    A common value is 10s.
#    DTMIN ~= 10
#


class Timesteps(NamelistBaseModel):
    """TIMESTEPS_NML namelist for WW3.

    The TIMESTEPS_NML namelist defines the timestep parameterization for WAVEWATCH III.
    Proper timestep selection is critical for model stability and accuracy.
    
    The timesteps should be set up as multiples of each other for best results.
    The time step relationships recommended by WW3 documentation are:
    - DTXY is the maximum CFL time step for x-y propagation
    - DTMAX is the maximum global time step (typically ≈ 3 × DTXY)
    - DTKTH is the maximum CFL time step for k-theta propagation (typically DTMAX/2 to DTMAX/10)
    - DTMIN is the minimum source term time step (typically between 5-60 seconds)
    """

    dtmax: Optional[float] = Field(
        ...,
        description=(
            "Maximum global time step (seconds). This is the largest time step allowed "
            "in the model, typically about 3 times the DTXY step to satisfy CFL criteria. "
            "The formula for the CFL time step depends on the lowest frequency (FREQ1) "
            "and the lowest spatial grid resolution (DXY): Tcfl = DXY / (G / (FREQ1*4*Pi)) "
            "where G=9.8m/s². DTMAX is typically around 3 × DTXY."
        ),
        gt=0  # Must be positive
    )
    dtxy: Optional[float] = Field(
        ...,
        description=(
            "Maximum CFL time step for x-y propagation (seconds). This time step controls "
            "the spatial advection of wave energy in geographical space. It should be set "
            "based on the CFL condition and is typically about 90% of the theoretical CFL "
            "limit: DTXY ≈ 0.9 * DXY / (G / (FREQ1*4*Pi)) where G=9.8m/s²."
        ),
        gt=0  # Must be positive
    )
    dtkth: Optional[float] = Field(
        ...,
        description=(
            "Maximum CFL time step for k-theta propagation (seconds). This time step controls "
            "the propagation of wave energy in spectral space (wavenumber and direction). "
            "The value depends on current velocities: for no/light currents, DTKTH ≈ DTMAX/2, "
            "while for strong currents, DTKTH ≈ DTMAX/10."
        ),
        gt=0  # Must be positive
    )
    dtmin: Optional[float] = Field(
        default=10,
        description=(
            "Minimum source term time step (seconds). This controls the time step for "
            "source term calculations (wind input, nonlinear interactions, dissipation). "
            "Typical values range between 5 and 60 seconds, with 10 seconds being common."
        ),
        ge=0.1,  # Reasonable minimum
        le=3600  # Reasonable maximum (1 hour)
    )

    @model_validator(mode="after")
    def validate_timesteps(self) -> "Timesteps":
        """Validate timestep relationships and ranges."""
        # dtmax ≈ 3 × dtxy (±10%)
        if self.dtmax is not None and self.dtxy is not None:
            expected_dtmax = 3 * self.dtxy
            if not (0.9 * expected_dtmax <= self.dtmax <= 1.1 * expected_dtmax):
                raise ValueError(
                    f"dtmax ({self.dtmax}) should be about 3 × dtxy ({self.dtxy})"
                )

        # dtkth ≈ dtmax/2 or dtmax/10 (±10%)
        if self.dtkth is not None and self.dtmax is not None:
            dtkth_half = self.dtmax / 2
            dtkth_tenth = self.dtmax / 10
            if not (dtkth_tenth <= self.dtkth <= dtkth_half):
                raise ValueError(
                    f"dtkth ({self.dtkth}) should be between  dtmax/10 ({dtkth_tenth}) and dtmax/2 ({dtkth_half})"
                )

        # dtmin between 5 and 60
        if self.dtmin is not None:
            if not (5 <= self.dtmin <= 60):
                raise ValueError(
                    f"dtmin ({self.dtmin}) should be between 5 and 60 seconds"
                )

        return self
