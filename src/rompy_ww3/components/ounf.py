"""Field output component for WW3 configuration."""

from typing import Optional
from ..namelists.field import Field
from ..namelists.output_file import File
from .basemodel import WW3ComponentBaseModel


class Ounf(WW3ComponentBaseModel):
    """Component for ww3_ounf.nml containing field (NetCDF) output configuration."""

    field: Optional[Field] = None
    file: Optional[File] = None
