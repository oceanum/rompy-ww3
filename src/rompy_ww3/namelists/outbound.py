"""OUTBND_COUNT_NML and OUTBND_LINE_NML namelist implementations for WW3."""

from typing import List, Optional
from pydantic import Field, BaseModel
from .basemodel import NamelistBaseModel


class OutboundLine(BaseModel):
    """Represents a single outbound boundary line configuration."""

    x0: Optional[float] = Field(default=None, description="X index of the start point")
    y0: Optional[float] = Field(default=None, description="Y index of the start point")
    dx: Optional[float] = Field(default=None, description="X-along increment")
    dy: Optional[float] = Field(default=None, description="Y-along increment")
    np: Optional[int] = Field(default=None, description="Number of points in the line")


class OutboundCount(NamelistBaseModel):
    """OUTBND_COUNT_NML namelist for WW3.

    Defines the number of output boundary lines.
    """

    n_line: Optional[int] = Field(
        default=None, description="Number of output boundary lines"
    )


class OutboundLineList(NamelistBaseModel):
    """OUTBND_LINE_NML namelist for WW3.

    Defines the output boundary lines.
    """

    lines: List[OutboundLine] = Field(
        default_factory=list, description="List of outbound boundary lines"
    )

    def render(self) -> str:
        """Render the namelist content with indexed parameters."""
        lines = ["&OUTBND_LINE_NML"]

        for i, line in enumerate(self.lines, 1):
            if line.x0 is not None:
                lines.append(f"  OUTBND_LINE({i})%X0 = {line.x0}")
            if line.y0 is not None:
                lines.append(f"  OUTBND_LINE({i})%Y0 = {line.y0}")
            if line.dx is not None:
                lines.append(f"  OUTBND_LINE({i})%DX = {line.dx}")
            if line.dy is not None:
                lines.append(f"  OUTBND_LINE({i})%DY = {line.dy}")
            if line.np is not None:
                lines.append(f"  OUTBND_LINE({i})%NP = {line.np}")
            lines.append("")  # Add a blank line between lines for readability

        lines.append("/")
        return "\n".join(lines)
