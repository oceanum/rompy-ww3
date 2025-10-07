"""GRID_NML and RECT_NML namelist implementation for WW3."""

from typing import Optional
from pydantic import Field
from .basemodel import NamelistBaseModel


class Grid(NamelistBaseModel):
    """GRID_NML namelist for WW3.

    Defines the grid to preprocess.
    """

    name: Optional[str] = Field(
        default=None, description="Grid name for identification"
    )
    nml: Optional[str] = Field(default=None, description="Namelist file name")
    type: Optional[str] = Field(
        default=None,
        description="Grid type: 'RECT' (rectilinear), 'CURV' (curvilinear), 'UNST' (unstructured)",
    )
    coord: Optional[str] = Field(
        default=None,
        description="Coordinate system: 'SPHE' (spherical), 'CART' (cartesian)",
    )
    clos: Optional[str] = Field(
        default=None,
        description="Grid closure: 'NONE', 'SMPL' (simple), 'TRPL' (tripole)",
    )
    zlim: Optional[float] = Field(
        default=-0.1, description="Minimum depth limit (meters)"
    )
    dmin: Optional[float] = Field(
        default=2.5, description="Minimum depth for wave propagation (meters)"
    )


class Rect(NamelistBaseModel):
    """RECT_NML namelist for WW3.

    Defines the rectilinear grid type.
    """

    nx: Optional[int] = Field(default=None, description="Number of points along x-axis")
    ny: Optional[int] = Field(default=None, description="Number of points along y-axis")
    sx: Optional[float] = Field(default=None, description="Grid increment along x-axis")
    sy: Optional[float] = Field(default=None, description="Grid increment along y-axis")
    sf: Optional[float] = Field(
        default=None, description="Scaling factor for grid increments"
    )
