"""Boundary update component for WW3 configuration."""

from typing import Optional
from pydantic import Field
from .basemodel import WW3ComponentBaseModel
from ..namelists.bound import Bound


class Bounc(WW3ComponentBaseModel):
    """Component for ww3_bounc.nml containing boundary update configuration."""

    bound_nml: Optional[Bound] = Field(
        default=None, description="BOUND_NML configuration for boundary preprocessing"
    )
