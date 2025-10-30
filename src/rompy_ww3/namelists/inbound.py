"""INBND_COUNT_NML and INBND_POINT_NML namelist implementations for WW3."""

from typing import List, Optional
from pydantic import Field, BaseModel, field_validator
from .basemodel import NamelistBaseModel


class InboundPoint(BaseModel):
    """Represents a single inbound boundary point configuration.

    The inbound boundary points define locations where input boundary conditions
    are applied in the WW3 model. Each point is specified by its grid indices
    and a connect flag that determines if intermediate points should be added.
    """

    x_index: Optional[int] = Field(
        default=None,
        description="X grid index of the included point, defines the discrete x-coordinate counter",
        ge=1  # Assuming grid indices start at 1
    )
    y_index: Optional[int] = Field(
        default=None,
        description="Y grid index of the included point, defines the discrete y-coordinate counter",
        ge=1  # Assuming grid indices start at 1
    )
    connect: Optional[bool] = Field(
        default=None,
        description=(
            "Connect flag for the point. If true and the present and previous point are on a grid line "
            "or diagonal, all intermediate points are also defined as boundary points."
        )
    )

    @field_validator('x_index', 'y_index')
    @classmethod
    def validate_grid_index(cls, v):
        """Validate grid index is positive."""
        if v is not None:
            if v < 1:
                raise ValueError(f"Grid index must be positive, got {v}")
        return v

    @field_validator('connect')
    @classmethod
    def validate_connect_flag(cls, v):
        """Validate connect flag is a boolean."""
        if v is not None and not isinstance(v, bool):
            raise ValueError(f"Connect flag must be a boolean, got {type(v)}")
        return v


class InboundCount(NamelistBaseModel):
    """INBND_COUNT_NML namelist for WW3.

    The INBND_COUNT_NML namelist defines the number of input boundary points
    for WAVEWATCH III grids. This namelist sets up how many boundary points
    will be specified in the corresponding INBND_POINT_NML.
    
    If no mask is defined, INBOUND can be used to specify active boundaries.
    If the actual input data is not defined in the actual wave model run,
    the initial conditions will be applied as constant boundary conditions.
    
    The points must start from index 1 to N and define grid points from segment data
    identifying points at which input boundary conditions are to be defined.
    """

    n_point: Optional[int] = Field(
        default=None,
        description="Number of boundary points, defines how many boundary points will be specified",
        ge=0  # Can have 0 boundary points
    )

    @field_validator('n_point')
    @classmethod
    def validate_n_point(cls, v):
        """Validate number of points is non-negative."""
        if v is not None:
            if v < 0:
                raise ValueError(f"Number of points must be non-negative, got {v}")
        return v


class InboundPointList(NamelistBaseModel):
    """INBND_POINT_NML namelist for WW3.

    The INBND_POINT_NML namelist defines the input boundary points for WAVEWATCH III grids.
    Each point is specified by its grid indices (x_index, y_index) and a connect flag.
    
    If no mask is defined, INBOUND can be used to specify active boundaries.
    If the actual input data is not defined in the actual wave model run,
    the initial conditions will be applied as constant boundary conditions.
    
    The points must start from index 1 to N and define grid points from segment data
    identifying points at which input boundary conditions are to be defined.
    The connect flag determines if intermediate points between consecutive points
    are also included as boundary points.
    """

    points: List[InboundPoint] = Field(
        default_factory=list,
        description="List of inbound boundary points, each specifying x_index, y_index, and connect flag"
    )

    @field_validator('points')
    @classmethod
    def validate_points_list(cls, v):
        """Validate the points list."""
        if v is not None:
            for i, point in enumerate(v):
                if not isinstance(point, InboundPoint):
                    raise ValueError(f"Point at index {i} must be of type InboundPoint, got {type(point)}")
        return v

    def render(self) -> str:
        """Render the namelist content with unindexed parameters."""
        lines = ["&INBND_POINT_NML"]

        for i, point in enumerate(self.points, 1):
            # Format as unindexed: INBND_POINT(I) = x_index y_index connect
            values = []
            if point.x_index is not None:
                values.append(str(point.x_index))
            if point.y_index is not None:
                values.append(str(point.y_index))
            if point.connect is not None:
                values.append("T" if point.connect else "F")

            if values:
                # Simple space-separated format - Fortran will read this correctly
                spaced_values = " ".join(values)
                lines.append(f"  INBND_POINT({i})         = {spaced_values}")
            lines.append("")  # Add a blank line between points for readability

        lines.append("/")
        return "\n".join(lines)
