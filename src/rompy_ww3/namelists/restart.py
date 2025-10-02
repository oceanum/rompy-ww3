"""RESTART_NML namelist implementation for WW3."""

from typing import Optional
from pydantic import Field
from .basemodel import NamelistBaseModel


class Restart(NamelistBaseModel):
    """RESTART_NML namelist for WW3.

    Defines the assimilation time for initialising the wave model.
    """

    restarttime: Optional[str] = Field(
        default=None, description="Assimilation time (yyyymmdd hhmmss)"
    )


class Update(NamelistBaseModel):
    """Update approach and associated variables for WW3."""

    prcntg: Optional[float] = Field(
        default=None,
        description="Correction factor applied to all gridpoints (e.g. 1.)",
    )
    prcntg_cap: Optional[float] = Field(
        default=None,
        description="Cap on maximum SWH correction factor (should not be less than 1.0)",
    )
