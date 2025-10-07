"""CURV_NML namelist implementation for WW3."""

from typing import Optional
from pydantic import Field
from .basemodel import NamelistBaseModel


class CoordData(NamelistBaseModel):
    """Coordinate data structure for curvilinear grids."""

    sf: Optional[float] = Field(default=1.0, description="Scale factor")
    off: Optional[float] = Field(default=0.0, description="Add offset")
    filename: Optional[str] = Field(default="unset", description="Filename")
    idf: Optional[int] = Field(default=21, description="File unit number")
    idla: Optional[int] = Field(default=1, description="Layout indicator")
    idfm: Optional[int] = Field(default=1, description="Format indicator")
    format: Optional[str] = Field(default="(....)", description="Formatted read format")


class Curv(NamelistBaseModel):
    """CURV_NML namelist for WW3.

    Defines the curvilinear grid type.
    """

    nx: Optional[int] = Field(default=None, description="Number of points along x-axis")
    ny: Optional[int] = Field(default=None, description="Number of points along y-axis")
    xcoord: Optional[CoordData] = Field(default=None, description="X-coordinate data")
    ycoord: Optional[CoordData] = Field(default=None, description="Y-coordinate data")
