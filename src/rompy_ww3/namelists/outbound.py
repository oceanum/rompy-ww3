"""OUTBND_COUNT_NML and OUTBND_LINE_NML namelist implementations for WW3."""

from typing import List, Optional
from pydantic import Field, BaseModel, field_validator
from .basemodel import NamelistBaseModel


class OutboundLine(BaseModel):
    """Represents a single outbound boundary line configuration.

    The outbound boundary lines define straight lines for output boundaries
    in the WW3 model. Each line is defined by its starting point (x0, y0),
    increments (dx, dy), and number of points. These are used to create
    nest files with output boundaries for inner grids.
    """

    x0: Optional[float] = Field(
        default=None,
        description="X coordinate of the start point of the boundary line",
    )
    y0: Optional[float] = Field(
        default=None,
        description="Y coordinate of the start point of the boundary line",
    )
    dx: Optional[float] = Field(
        default=None,
        description="X-along increment for the boundary line, defines the step in x-direction",
    )
    dy: Optional[float] = Field(
        default=None,
        description="Y-along increment for the boundary line, defines the step in y-direction",
    )
    np: Optional[int] = Field(
        default=None,
        description=(
            "Number of points in the boundary line. A negative number starts a new output file. "
            "This defines how many points will be included in the boundary line starting from (x0,y0) "
            "with increments (dx,dy)."
        ),
        ne=0  # Should not be zero
    )

    @field_validator('np')
    @classmethod
    def validate_number_of_points(cls, v):
        """Validate number of points is not zero."""
        if v is not None:
            if v == 0:
                raise ValueError(f"Number of points (np) must not be zero, got {v}")
        return v


class OutboundCount(NamelistBaseModel):
    """OUTBND_COUNT_NML namelist for WW3.

    The OUTBND_COUNT_NML namelist defines the number of output boundary lines
    for WAVEWATCH III grids. This namelist sets up how many boundary lines
    will be specified in the corresponding OUTBND_LINE_NML namelist.
    
    It creates a nest file with output boundaries for an inner grid.
    The prefered way to do it is to use ww3_bounc program.
    These do not need to be defined for data transfer between grids in the multi-grid driver.
    """

    n_line: Optional[int] = Field(
        default=None,
        description="Number of output boundary lines, defines how many boundary lines will be specified",
        ge=0  # Can have 0 boundary lines
    )

    @field_validator('n_line')
    @classmethod
    def validate_n_line(cls, v):
        """Validate number of lines is non-negative."""
        if v is not None:
            if v < 0:
                raise ValueError(f"Number of lines must be non-negative, got {v}")
        return v


class OutboundLineList(NamelistBaseModel):
    """OUTBND_LINE_NML namelist for WW3.

    The OUTBND_LINE_NML namelist defines the output boundary lines for WAVEWATCH III grids.
    Each line is specified by its starting point (x0, y0), increments (dx, dy), and number of points (np).
    
    Output boundary points are defined as a number of straight lines, defined by its starting point (X0,Y0),
    increments (DX,DY) and number of points. A negative number of points starts a new output file.
    
    For spherical grids in degrees, an example would be:
    '1.75  1.50  0.25 -0.10     3'
    '2.25  1.50 -0.10  0.00    -6'
    '0.10  0.10  0.10  0.00   -10'
    
    It creates a nest file with output boundaries for an inner grid.
    The prefered way to do it is to use ww3_bounc program.
    These do not need to be defined for data transfer between grids in the multi-grid driver.
    """

    lines: List[OutboundLine] = Field(
        default_factory=list,
        description="List of outbound boundary lines, each specifying x0, y0, dx, dy, and np"
    )

    @field_validator('lines')
    @classmethod
    def validate_lines_list(cls, v):
        """Validate the lines list."""
        if v is not None:
            for i, line in enumerate(v):
                if not isinstance(line, OutboundLine):
                    raise ValueError(f"Line at index {i} must be of type OutboundLine, got {type(line)}")
        return v

    def render(self) -> str:
        """Render the namelist content with unindexed parameters."""
        lines = ["&OUTBND_LINE_NML"]

        for i, line in enumerate(self.lines, 1):
            # Format as unindexed: OUTBND_LINE(I) = x0 y0 dx dy np
            values = []
            if line.x0 is not None:
                values.append(str(line.x0))
            if line.y0 is not None:
                values.append(str(line.y0))
            if line.dx is not None:
                values.append(str(line.dx))
            if line.dy is not None:
                values.append(str(line.dy))
            if line.np is not None:
                values.append(str(line.np))

            if values:
                # Simple space-separated format - Fortran will read this correctly
                spaced_values = " ".join(values)
                lines.append(f"  OUTBND_LINE({i})         = {spaced_values}")
            lines.append("")  # Add a blank line between lines for readability

        lines.append("/")
        return "\n".join(lines)
