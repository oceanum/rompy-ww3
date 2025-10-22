"""Parameters component for WW3 configuration."""

from typing import Optional
from ..namelists.parameters import ModelParameters
from .basemodel import WW3ComponentBaseModel


class Parameters(WW3ComponentBaseModel):
    """Component for namelists.nml containing model parameters configuration."""

    parameters: Optional[ModelParameters] = None
