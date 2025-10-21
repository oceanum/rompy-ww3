"""Boundary update component for WW3 configuration."""

from typing import Optional
from ..namelists.restart import Update
from .basemodel import WW3ComponentBaseModel


class Bounc(WW3ComponentBaseModel):
    """Component for ww3_bounc.nml containing boundary update configuration."""

    update: Optional[Update] = None
