"""Field output component for WW3 configuration."""

from typing import Optional
from ..namelists.unformatted import UnformattedOutput
from .basemodel import WW3ComponentBaseModel


class FieldOutputComponent(WW3ComponentBaseModel):
    """Component for ww3_ounf.nml containing field (NetCDF) output configuration."""

    unformatted: Optional[UnformattedOutput] = None
