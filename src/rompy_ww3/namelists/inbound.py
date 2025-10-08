"""INBND_COUNT_NML and INBND_POINT_NML namelist implementations for WW3."""

from typing import List, Optional
from pydantic import Field, BaseModel
from .basemodel import NamelistBaseModel


class InboundPoint(BaseModel):
    """Represents a single inbound boundary point configuration."""

    x_index: Optional[int] = Field(
        default=None, description="X index of the included point"
    )
    y_index: Optional[int] = Field(
        default=None, description="Y index of the included point"
    )
    connect: Optional[bool] = Field(
        default=None, description="Connect flag for the point"
    )


class InboundCount(NamelistBaseModel):
    """INBND_COUNT_NML namelist for WW3.

    Defines the number of input boundary points.
    """

    n_point: Optional[int] = Field(
        default=None, description="Number of boundary points"
    )


class InboundPointList(NamelistBaseModel):
    """INBND_POINT_NML namelist for WW3.

    Defines the input boundary points.
    """

    points: List[InboundPoint] = Field(
        default_factory=list, description="List of inbound boundary points"
    )

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
