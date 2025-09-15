"""TIMESTEPS_NML namelist implementation for WW3."""

from typing import Optional, List
from pydantic import Field
from .basemodel import NamelistBaseModel


class Timesteps(NamelistBaseModel):
    """TIMESTEPS_NML namelist for WW3.
    
    Defines the timesteps parameterization.
    """
    
    dt: Optional[float] = Field(
        default=None,
        description="Main time step (seconds)"
    )
    dtfld: Optional[float] = Field(
        default=None,
        description="Field output time step (seconds)"
    )
    dtpnt: Optional[float] = Field(
        default=None,
        description="Point output time step (seconds)"
    )
    dttrk: Optional[float] = Field(
        default=None,
        description="Track output time step (seconds)"
    )
    dtres: Optional[float] = Field(
        default=None,
        description="Restart output time step (seconds)"
    )
    dtbnd: Optional[float] = Field(
        default=None,
        description="Boundary output time step (seconds)"
    )
    dtprt: Optional[float] = Field(
        default=None,
        description="Partition output time step (seconds)"
    )
    dtcpl: Optional[float] = Field(
        default=None,
        description="Coupling time step (seconds)"
    )