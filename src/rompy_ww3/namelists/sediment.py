"""SED_NML namelist implementation for WW3."""

from typing import Optional
from pydantic import Field
from .basemodel import NamelistBaseModel


class Sediment(NamelistBaseModel):
    """SED_NML namelist for WW3.

    Defines the sedimentary bottom map.
    """

    sf: Optional[float] = Field(
        default=None, description="Scale factor to apply to sediment values"
    )
    filename: Optional[str] = Field(
        default=None, description="Filename containing sediment data"
    )
    idf: Optional[int] = Field(default=None, description="File unit number")
    idla: Optional[int] = Field(
        default=None, description="Layout indicator for sediment data"
    )
    idfm: Optional[int] = Field(
        default=None, description="Format indicator for sediment data"
    )
    format: Optional[str] = Field(
        default=None, description="Formatted read format for sediment data"
    )
