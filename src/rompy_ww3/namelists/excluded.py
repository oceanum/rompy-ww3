"""EXCL_COUNT_NML, EXCL_POINT_NML and EXCL_BODY_NML namelist implementations for WW3."""

from typing import List, Optional
from pydantic import Field, BaseModel, field_validator
from .basemodel import NamelistBaseModel


class ExcludedPoint(BaseModel):
    """Represents a single excluded point configuration.

    The excluded points define grid points that should be excluded from the simulation.
    Each point is specified by its grid indices and a connect flag that determines
    if intermediate points should be added to the exclusion list.
    """

    x_index: Optional[int] = Field(
        default=None,
        description="X grid index of the excluded point, defines the discrete x-coordinate counter",
        ge=1,  # Assuming grid indices start at 1
    )
    y_index: Optional[int] = Field(
        default=None,
        description="Y grid index of the excluded point, defines the discrete y-coordinate counter",
        ge=1,  # Assuming grid indices start at 1
    )
    connect: Optional[bool] = Field(
        default=None,
        description=(
            "Connect flag for the point. If true and the present and previous point are on a grid line "
            "or diagonal, all intermediate points are also defined as excluded points."
        ),
    )

    @field_validator("x_index", "y_index")
    @classmethod
    def validate_grid_index(cls, v):
        """Validate grid index is positive."""
        if v is not None:
            if v < 1:
                raise ValueError(f"Grid index must be positive, got {v}")
        return v

    @field_validator("connect")
    @classmethod
    def validate_connect_flag(cls, v):
        """Validate connect flag is a boolean."""
        if v is not None and not isinstance(v, bool):
            raise ValueError(f"Connect flag must be a boolean, got {type(v)}")
        return v


class ExcludedBody(BaseModel):
    """Represents a single excluded body configuration.

    The excluded bodies define closed bodies of sea points to be removed from the simulation.
    Each body is defined by a point inside the closed body, which results in
    the entire closed body of sea points being excluded.
    """

    x_index: Optional[int] = Field(
        default=None,
        description="X grid index of the excluded body, should be a point inside the closed body to be removed",
        ge=1,  # Assuming grid indices start at 1
    )
    y_index: Optional[int] = Field(
        default=None,
        description="Y grid index of the excluded body, should be a point inside the closed body to be removed",
        ge=1,  # Assuming grid indices start at 1
    )

    @field_validator("x_index", "y_index")
    @classmethod
    def validate_grid_index(cls, v):
        """Validate grid index is positive."""
        if v is not None:
            if v < 1:
                raise ValueError(f"Grid index must be positive, got {v}")
        return v


class ExcludedCount(NamelistBaseModel):
    """EXCL_COUNT_NML namelist for WW3.

    The EXCL_COUNT_NML namelist defines the number of excluded points and bodies
    for WAVEWATCH III grids. This namelist sets up how many excluded points and bodies
    will be specified in the corresponding EXCL_POINT_NML and EXCL_BODY_NML namelists.

    If no mask is defined, EXCL can be used to specify excluded areas.
    NOTE: If a mask is defined, EXCL cannot be used.
    """

    n_point: Optional[int] = Field(
        default=None,
        description="Number of excluded point segments, defines how many excluded points will be specified",
        ge=0,  # Can have 0 excluded points
    )
    n_body: Optional[int] = Field(
        default=None,
        description="Number of excluded bodies, defines how many closed bodies will be removed from the grid",
        ge=0,  # Can have 0 excluded bodies
    )

    @field_validator("n_point", "n_body")
    @classmethod
    def validate_counts(cls, v):
        """Validate counts are non-negative."""
        if v is not None:
            if v < 0:
                raise ValueError(f"Count must be non-negative, got {v}")
        return v


class ExcludedPointList(NamelistBaseModel):
    """EXCL_POINT_NML namelist for WW3.

    The EXCL_POINT_NML namelist defines the excluded points for WAVEWATCH III grids.
    Each point is specified by its grid indices (x_index, y_index) and a connect flag.

    If no mask is defined, EXCL can be used to specify excluded areas.
    NOTE: If a mask is defined, EXCL cannot be used.

    The excluded points are specified as segments of points that define areas to be
    excluded from the simulation. The connect flag determines if intermediate points
    between consecutive points are also excluded.
    """

    points: List[ExcludedPoint] = Field(
        default_factory=list,
        description="List of excluded points, each specifying x_index, y_index, and connect flag",
    )

    @field_validator("points")
    @classmethod
    def validate_points_list(cls, v):
        """Validate the points list."""
        if v is not None:
            for i, point in enumerate(v):
                if not isinstance(point, ExcludedPoint):
                    raise ValueError(
                        f"Point at index {i} must be of type ExcludedPoint, got {type(point)}"
                    )
        return v

    def render(self, *args, **kwargs) -> str:
        """Render the namelist content with unindexed parameters."""
        lines = ["&EXCL_POINT_NML"]

        for j, point in enumerate(self.points, 1):
            # Format as unindexed: EXCL_POINT(J) = x_index y_index connect
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
                lines.append(f"  EXCL_POINT({j})       = {spaced_values}")
            lines.append("")  # Add a blank line between points for readability

        lines.append("/")
        return "\n".join(lines)


class ExcludedBodyList(NamelistBaseModel):
    """EXCL_BODY_NML namelist for WW3.

    The EXCL_BODY_NML namelist defines the excluded bodies for WAVEWATCH III grids.
    Each body is specified by a point inside the closed body to be removed.

    If no mask is defined, EXCL can be used to specify excluded areas.
    NOTE: If a mask is defined, EXCL cannot be used.

    The excluded bodies are specified as points inside closed bodies of sea points.
    Each specified point will result in the entire closed body of sea points
    containing that point to be removed from the simulation.
    """

    bodies: List[ExcludedBody] = Field(
        default_factory=list,
        description="List of excluded bodies, each specified by a point inside the closed body to be removed",
    )

    @field_validator("bodies")
    @classmethod
    def validate_bodies_list(cls, v):
        """Validate the bodies list."""
        if v is not None:
            for i, body in enumerate(v):
                if not isinstance(body, ExcludedBody):
                    raise ValueError(
                        f"Body at index {i} must be of type ExcludedBody, got {type(body)}"
                    )
        return v

    def render(self, *args, **kwargs) -> str:
        """Render the namelist content with unindexed parameters."""
        lines = ["&EXCL_BODY_NML"]

        for k, body in enumerate(self.bodies, 1):
            # Format as unindexed: EXCL_BODY(K) = x_index y_index
            values = []
            if body.x_index is not None:
                values.append(str(body.x_index))
            if body.y_index is not None:
                values.append(str(body.y_index))

            if values:
                # Simple space-separated format - Fortran will read this correctly
                spaced_values = " ".join(values)
                lines.append(f"  EXCL_BODY({k})        = {spaced_values}")
            lines.append("")  # Add a blank line between bodies for readability

        lines.append("/")
        return "\n".join(lines)
