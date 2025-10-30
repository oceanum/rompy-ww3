"""CURV_NML namelist implementation for WW3."""

from typing import Optional, Union
from pydantic import Field, field_validator
from .basemodel import NamelistBaseModel
from ..core.data import WW3DataBlob


class CoordData(NamelistBaseModel):
    """Coordinate data structure for curvilinear grids in WW3.

    This structure defines how coordinate data is read from files for curvilinear grids.
    It includes scaling, offset, file specifications and format information.
    """

    sf: Optional[float] = Field(
        default=1.0,
        description=(
            "Scale factor for coordinate values. Used to convert from file values to model coordinates. "
            "The final coordinate value is calculated as: scale_factor * value_read + add_offset."
        ),
        gt=0  # Must be positive
    )
    off: Optional[float] = Field(
        default=0.0,
        description=(
            "Add offset for coordinate values. Used to convert from file values to model coordinates. "
            "The final coordinate value is calculated as: scale_factor * value_read + add_offset."
        )
    )
    filename: Optional[Union[str, WW3DataBlob]] = Field(
        default="unset",
        description=(
            "Filename or data blob containing the coordinate data. This file should contain "
            "the coordinate values for the curvilinear grid (either X or Y coordinates)."
        )
    )
    idf: Optional[int] = Field(
        default=21,
        description=(
            "File unit number for the coordinate file. Each file in WW3 is assigned a unique unit number "
            "to distinguish between different input files during processing."
        ),
        ge=1  # Must be positive file unit number
    )
    idla: Optional[int] = Field(
        default=1,
        description=(
            "Layout indicator for reading coordinate data:\n"
            "  1: Read line-by-line from bottom to top\n"
            "  2: Like 1, but with a single read statement\n"
            "  3: Read line-by-line from top to bottom\n"
            "  4: Like 3, but with a single read statement"
        ),
        ge=1,
        le=4
    )
    idfm: Optional[int] = Field(
        default=1,
        description=(
            "Format indicator for reading coordinate data:\n"
            "  1: Free format (default)\n"
            "  2: Fixed format\n"
            "  3: Unformatted"
        ),
        ge=1,
        le=3
    )
    format: Optional[str] = Field(
        default="(....)",
        description=(
            "Formatted read format specification, like '(f10.6)' for float type. "
            "Use '(....)' for auto detection of the format. This specifies how the "
            "coordinate values should be read from the file."
        )
    )

    @field_validator('idla')
    @classmethod
    def validate_idla(cls, v):
        """Validate layout indicator."""
        if v is not None and v not in [1, 2, 3, 4]:
            raise ValueError(f"Layout indicator (idla) must be between 1 and 4, got {v}")
        return v

    @field_validator('idfm')
    @classmethod
    def validate_idfm(cls, v):
        """Validate format indicator."""
        if v is not None and v not in [1, 2, 3]:
            raise ValueError(f"Format indicator (idfm) must be 1, 2, or 3, got {v}")
        return v


class Curv(NamelistBaseModel):
    """CURV_NML namelist for WW3.

    The CURV_NML namelist defines the parameters for curvilinear grids in WAVEWATCH III.
    Curvilinear grids have variable spacing and can adapt to complex coastlines and bathymetry.
    
    The minimum grid size is 3x3. The coordinate data (xcoord and ycoord) specify how
    coordinate values are read from input files for each grid point.
    Each coordinate dimension has its own CoordData specification.
    """

    nx: Optional[int] = Field(
        default=None,
        description="Number of points along the x-axis of the curvilinear grid. Minimum size is 3x3 grid.",
        ge=3  # Minimum grid size is 3x3
    )
    ny: Optional[int] = Field(
        default=None,
        description="Number of points along the y-axis of the curvilinear grid. Minimum size is 3x3 grid.",
        ge=3  # Minimum grid size is 3x3
    )
    xcoord: Optional[CoordData] = Field(
        default=None,
        description=(
            "X-coordinate data specification defining how longitude/x-coordinates "
            "are read from the input file for the curvilinear grid."
        )
    )
    ycoord: Optional[CoordData] = Field(
        default=None,
        description=(
            "Y-coordinate data specification defining how latitude/y-coordinates "
            "are read from the input file for the curvilinear grid."
        )
    )

    @field_validator('nx', 'ny')
    @classmethod
    def validate_grid_dimensions(cls, v):
        """Validate grid dimensions."""
        if v is not None:
            if v < 3:
                raise ValueError(f"Grid dimension must be at least 3, got {v}")
        return v
