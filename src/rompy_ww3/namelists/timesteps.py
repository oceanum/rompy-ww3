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

    Defines timestep parameterization.
    """

    dtmax: Optional[float] = Field(..., description="Maximum CFL timestep (seconds)")
    dtxy: Optional[float] = Field(..., description="Propagation timestep (seconds)")
    dtkth: Optional[float] = Field(..., description="Refraction timestep (seconds)")
    dtmin: Optional[float] = Field(
        default=10, description="Minimum  time step (seconds)"
    )

    @model_validator(mode="after")
    def validate_timesteps(cls, model):
        """Validate timestep relationships and ranges."""
        # dtmax ≈ 3 × dtxy (±10%)
        if model.dtmax is not None and model.dtxy is not None:
            expected_dtmax = 3 * model.dtxy
            if not (0.9 * expected_dtmax <= model.dtmax <= 1.1 * expected_dtmax):
                raise ValueError(
                    f"dtmax ({model.dtmax}) should be about 3 × dtxy ({model.dtxy})"
                )

        # dtkth ≈ dtmax/2 or dtmax/10 (±10%)
        if model.dtkth is not None and model.dtmax is not None:
            dtkth_half = model.dtmax / 2
            dtkth_tenth = model.dtmax / 10
            if not (dtkth_tenth <= model.dtkth <= dtkth_half):
                raise ValueError(
                    f"dtkth ({model.dtkth}) should be between  dtmax/10 ({dtkth_tenth}) and dtmax/2 ({dtkth_half})"
                )

        # dtmin between 5 and 60
        if model.dtmin is not None:
            if not (5 <= model.dtmin <= 60):
                raise ValueError(
                    f"dtmin ({model.dtmin}) should be between 5 and 60 seconds"
                )

        return model
