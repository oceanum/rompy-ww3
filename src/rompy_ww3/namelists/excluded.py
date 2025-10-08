"""EXCL_COUNT_NML, EXCL_POINT_NML and EXCL_BODY_NML namelist implementations for WW3."""

from typing import List, Optional
from pydantic import Field, BaseModel
from .basemodel import NamelistBaseModel


class ExcludedPoint(BaseModel):
    """Represents a single excluded point configuration."""

    x_index: Optional[int] = Field(
        default=None, description="X index of the excluded point"
    )
    y_index: Optional[int] = Field(
        default=None, description="Y index of the excluded point"
    )
    connect: Optional[bool] = Field(
        default=None, description="Connect flag for the point"
    )


class ExcludedBody(BaseModel):
    """Represents a single excluded body configuration."""

    x_index: Optional[int] = Field(
        default=None, description="X index of the excluded body"
    )
    y_index: Optional[int] = Field(
        default=None, description="Y index of the excluded body"
    )


class ExcludedCount(NamelistBaseModel):
    """EXCL_COUNT_NML namelist for WW3.

    Defines the number of excluded points and bodies.
    """

    n_point: Optional[int] = Field(
        default=None, description="Number of excluded segments"
    )
    n_body: Optional[int] = Field(default=None, description="Number of excluded bodies")


class ExcludedPointList(NamelistBaseModel):
    """EXCL_POINT_NML namelist for WW3.

    Defines the excluded points.
    """

    points: List[ExcludedPoint] = Field(
        default_factory=list, description="List of excluded points"
    )

    def render(self) -> str:
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

    Defines the excluded bodies.
    """

    bodies: List[ExcludedBody] = Field(
        default_factory=list, description="List of excluded bodies"
    )

    def render(self) -> str:
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
