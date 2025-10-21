"""Boundary component for WW3 configuration."""

from typing import Optional
from ..namelists.bound import Bound
from .basemodel import WW3ComponentBaseModel


class BoundaryComponent(WW3ComponentBaseModel):
    """Component for ww3_bound.nml containing boundary configuration."""

    bound: Optional[Bound] = None
