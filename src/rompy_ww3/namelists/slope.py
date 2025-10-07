"""SLOPE_NML namelist implementation for WW3."""

from typing import Optional
from pydantic import Field
from .basemodel import NamelistBaseModel


class Slope(NamelistBaseModel):
    """SLOPE_NML namelist for WW3.

    Defines the reflexion slope map.
    """

    sf: Optional[float] = Field(
        default=None, description="Scale factor to apply to slope values"
    )
    filename: Optional[str] = Field(
        default=None, description="Filename containing slope data"
    )
    idf: Optional[int] = Field(default=None, description="File unit number")
    idla: Optional[int] = Field(
        default=None, description="Layout indicator for slope data"
    )
    idfm: Optional[int] = Field(
        default=None, description="Format indicator for slope data"
    )
    format: Optional[str] = Field(
        default=None, description="Formatted read format for slope data"
    )
