"""GRID_NML and RECT_NML namelist implementation for WW3."""

from typing import Optional
from pydantic import Field, field_validator
from .basemodel import NamelistBaseModel
from .validation import validate_grid_type, validate_coord_type, validate_clos_type


class Grid(NamelistBaseModel):
    """GRID_NML namelist for WW3.

    The GRID_NML namelist defines the grid to preprocess for WAVEWATCH III.
    This namelist sets up the basic characteristics of the computational grid.

    The WW3 model supports several grid types and coordinate systems, with options
    for grid closure to handle special cases like tripole grids.
    """

    name: Optional[str] = Field(
        default=None,
        description=(
            "Grid name for identification, used for naming and referencing this grid "
            "in model output and processing. Should be descriptive and unique."
        ),
    )
    nml: Optional[str] = Field(
        default=None,
        description=(
            "Namelist file name that contains additional grid-dependent parameters. "
            "This points to another namelist file that may contain grid-specific settings "
            "beyond those defined in this namelist."
        ),
    )
    type: Optional[str] = Field(
        default=None,
        description=(
            "Grid type defining the grid geometry:\n"
            "  'RECT': Rectilinear grid with constant x,y spacing\n"
            "  'CURV': Curvilinear grid with variable spacing\n"
            "  'UNST': Unstructured grid (triangle-based)\n"
            "  'SMC': Spherical Multiple-Cell grid"
        ),
    )
    coord: Optional[str] = Field(
        default=None,
        description=(
            "Coordinate system for the grid:\n"
            "  'SPHE': Spherical coordinates (degrees)\n"
            "  'CART': Cartesian coordinates (meters)\n"
            "Note: Grid closure can only be applied in spherical coordinates."
        ),
    )
    clos: Optional[str] = Field(
        default=None,
        description=(
            "Grid closure type for handling domain boundaries:\n"
            "  'NONE': No closure applied (standard boundaries)\n"
            "  'SMPL': Simple grid closure - grid is periodic in i-index and wraps at i=NX+1.\n"
            "          In other words, (NX+1,J) => (1,J). Works with RECT and CURV grids.\n"
            "  'TRPL': Tripole grid closure - grid is periodic in i-index and has closure at j=NY+1.\n"
            "          (NX+1,J<=NY) => (1,J) and (I,NY+1) => (NX-I+1,NY). Works with CURV grids only.\n"
            "          NX must be even for tripole closure."
        ),
    )
    zlim: Optional[float] = Field(
        default=-0.1,
        description=(
            "Coastline limit depth (meters) in negative values below mean sea level. "
            "This value distinguishes sea points from land points. All points with depth "
            "values (ZBIN) greater than this limit (ZLIM) will be considered as excluded "
            "points and will never be wet points, even if water level rises above. "
            "It can only overwrite the status of a sea point to a land point. "
            "The value must be negative (below mean sea level)."
        ),
        le=0,  # Must be less than or equal to 0 (below sea level)
    )
    dmin: Optional[float] = Field(
        default=2.5,
        description=(
            "Absolute minimum depth allowed for wave propagation (meters). "
            "This is the depth value used in the model if input depth is lower, "
            "to prevent model instability. Values below this will be set to DMIN "
            "to avoid model blow-up in very shallow areas."
        ),
        gt=0,  # Must be positive
    )

    @field_validator("type")
    @classmethod
    def validate_grid_type_field(cls, v):
        """Validate grid type field."""
        if v is not None:
            return validate_grid_type(v)
        return v

    @field_validator("coord")
    @classmethod
    def validate_coord_type_field(cls, v):
        """Validate coordinate type field."""
        if v is not None:
            return validate_coord_type(v)
        return v

    @field_validator("clos")
    @classmethod
    def validate_clos_type_field(cls, v):
        """Validate grid closure type field."""
        if v is not None:
            return validate_clos_type(v)
        return v

    @field_validator("zlim")
    @classmethod
    def validate_zlim(cls, v):
        """Validate coastline limit depth."""
        if v is not None:
            if v > 0:
                raise ValueError(
                    f"Coastline limit depth (zlim) must be <= 0 (below sea level), got {v}"
                )
        return v

    @field_validator("dmin")
    @classmethod
    def validate_dmin(cls, v):
        """Validate minimum depth for wave propagation."""
        if v is not None:
            if v <= 0:
                raise ValueError(f"Minimum depth (dmin) must be positive, got {v}")
        return v


class Rect(NamelistBaseModel):
    """RECT_NML namelist for WW3.

    The RECT_NML namelist defines the parameters for rectilinear grids in WAVEWATCH III.
    Rectilinear grids have constant spacing in each direction and form a regular grid.

    The minimum grid size is 3x3. The coordinate increments (SX, SY) define the spacing
    between grid points and depend on the coordinate system (spherical or cartesian).
    """

    nx: Optional[int] = Field(
        default=None,
        description="Number of points along the x-axis of the rectilinear grid. Minimum size is 3x3 grid.",
        ge=3,  # Minimum grid size is 3x3
    )
    ny: Optional[int] = Field(
        default=None,
        description="Number of points along the y-axis of the rectilinear grid. Minimum size is 3x3 grid.",
        ge=3,  # Minimum grid size is 3x3
    )
    sx: Optional[float] = Field(
        default=None,
        description=(
            "Grid increment along x-axis. In spherical coordinates (degrees), this is the "
            "longitude increment. In cartesian coordinates (meters), this is the x-direction spacing. "
            "If grid increments are given in minutes of arc, the scaling factor SF must be set to 60 "
            "to provide an increment factor in degrees."
        ),
        gt=0,  # Must be positive
    )
    sy: Optional[float] = Field(
        default=None,
        description=(
            "Grid increment along y-axis. In spherical coordinates (degrees), this is the "
            "latitude increment. In cartesian coordinates (meters), this is the y-direction spacing. "
            "If grid increments are given in minutes of arc, the scaling factor SF must be set to 60 "
            "to provide an increment factor in degrees."
        ),
        gt=0,  # Must be positive
    )
    sf: Optional[float] = Field(
        default=1.0,
        description=(
            "Scaling division factor for x-y axis. Used when grid increments are given in "
            "different units. For example, if SX and SY are in minutes of arc, set SF to 60 "
            "to convert to degrees. Value = value_read / scale_fac."
        ),
        gt=0,  # Must be positive
    )
    x0: Optional[float] = Field(
        default=None,
        description=(
            "X-coordinate of the lower-left corner of the grid. In spherical coordinates, "
            "this is the longitude of the SW corner. In cartesian coordinates, this is "
            "the x-coordinate of the SW corner. If CSTRG='SMPL', then SX is forced to 360/NX."
        ),
    )
    y0: Optional[float] = Field(
        default=None,
        description=(
            "Y-coordinate of the lower-left corner of the grid. In spherical coordinates, "
            "this is the latitude of the SW corner. In cartesian coordinates, this is "
            "the y-coordinate of the SW corner."
        ),
    )
    sf0: Optional[float] = Field(
        default=1.0,
        description=(
            "Scaling division factor for x0,y0 coordinates. Used when the corner coordinates "
            "are given in different units. Value = value_read / scale_fac."
        ),
        gt=0,  # Must be positive
    )

    @field_validator("nx", "ny")
    @classmethod
    def validate_grid_dimensions(cls, v):
        """Validate grid dimensions."""
        if v is not None:
            if v < 3:
                raise ValueError(f"Grid dimension must be at least 3, got {v}")
        return v

    @field_validator("sx", "sy", "sf", "sf0")
    @classmethod
    def validate_positive_values(cls, v):
        """Validate that spacing and scaling factors are positive."""
        if v is not None:
            if v <= 0:
                raise ValueError(
                    f"Spacing and scaling factors must be positive, got {v}"
                )
        return v
