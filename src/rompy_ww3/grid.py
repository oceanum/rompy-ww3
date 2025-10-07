"""WW3 Rompy grid."""

import logging
from pathlib import Path
from typing import Literal, Optional
from pydantic import Field, model_validator

from rompy.core.grid import RegularGrid


logger = logging.getLogger(__name__)

HERE = Path(__file__).parent


class Grid(RegularGrid):
    """Ww3 grid class with WW3-specific parameters.

    This class extends the RegularGrid with WW3-specific grid parameters
    needed for wave model configuration.
    """

    model_type: Literal["ww3"] = Field(
        default="ww3",
        description="Model type discriminator",
    )

    # WW3 grid parameters
    name: Optional[str] = Field(
        default=None, description="Grid name for identification"
    )
    grid_type: Optional[str] = Field(
        default="RECT",
        description="Grid type: 'RECT' (rectilinear), 'CURV' (curvilinear), 'UNST' (unstructured)",
    )
    coordinate_system: Optional[str] = Field(
        default="SPHE",
        description="Coordinate system: 'SPHE' (spherical), 'CART' (cartesian)",
    )
    grid_closure: Optional[str] = Field(
        default="NONE",
        description="Grid closure: 'NONE', 'SMPL' (simple), 'TRPL' (tripole)",
    )
    zlim: Optional[float] = Field(
        default=-0.10, description="Minimum depth limit (meters)"
    )
    dmin: Optional[float] = Field(
        default=2.5, description="Minimum depth for wave propagation (meters)"
    )

    # Rectilinear grid parameters
    nx: Optional[int] = Field(
        default=None, description="Number of points along x-axis (for RECT grids)"
    )
    ny: Optional[int] = Field(
        default=None, description="Number of points along y-axis (for RECT grids)"
    )
    sx: Optional[float] = Field(
        default=None, description="Grid increment along x-axis (for RECT grids)"
    )
    sy: Optional[float] = Field(
        default=None, description="Grid increment along y-axis (for RECT grids)"
    )
    sf: Optional[float] = Field(
        default=None, description="Scaling factor for grid increments (for RECT grids)"
    )
    sf0: Optional[float] = Field(
        default=None,
        description="Scaling factor for x0, y0 coordinates (for RECT grids)",
    )

    # Grid boundaries
    x0: Optional[float] = Field(
        default=None, description="Western boundary of the grid"
    )
    y0: Optional[float] = Field(
        default=None, description="Southern boundary of the grid"
    )
    x1: Optional[float] = Field(
        default=None, description="Eastern boundary of the grid"
    )
    y1: Optional[float] = Field(
        default=None, description="Northern boundary of the grid"
    )

    @model_validator(mode="after")
    def validate_grid_parameters(self) -> "Grid":
        """Validate grid parameters."""
        # Validate grid type
        if self.grid_type and self.grid_type not in ["RECT", "CURV", "UNST", "SMC"]:
            raise ValueError(
                "grid_type must be one of 'RECT', 'CURV', 'UNST', or 'SMC'"
            )

        # Validate coordinate system
        if self.coordinate_system and self.coordinate_system not in ["SPHE", "CART"]:
            raise ValueError("coordinate_system must be one of 'SPHE' or 'CART'")

        # Validate grid closure
        if self.grid_closure and self.grid_closure not in ["NONE", "SMPL", "TRPL"]:
            raise ValueError("grid_closure must be one of 'NONE', 'SMPL', or 'TRPL'")

        # Validate rectilinear grid parameters
        if self.grid_type == "RECT":
            if self.nx is not None and self.nx <= 0:
                raise ValueError("nx must be positive for RECT grids")
            if self.ny is not None and self.ny <= 0:
                raise ValueError("ny must be positive for RECT grids")
            if self.sx is not None and self.sx <= 0:
                raise ValueError("sx must be positive for RECT grids")
            if self.sy is not None and self.sy <= 0:
                raise ValueError("sy must be positive for RECT grids")

        # Validate boundaries
        if self.x0 is not None and self.x1 is not None and self.x0 >= self.x1:
            raise ValueError("x0 must be less than x1")
        if self.y0 is not None and self.y1 is not None and self.y0 >= self.y1:
            raise ValueError("y0 must be less than y1")

        return self

    @property
    def grid_dimensions(self) -> tuple[Optional[int], Optional[int]]:
        """Get grid dimensions (nx, ny)."""
        return (self.nx, self.ny)

    @property
    def grid_spacing(self) -> tuple[Optional[float], Optional[float]]:
        """Get grid spacing (sx, sy)."""
        return (self.sx, self.sy)

    @property
    def grid_boundaries(
        self,
    ) -> tuple[Optional[float], Optional[float], Optional[float], Optional[float]]:
        """Get grid boundaries (x0, y0, x1, y1)."""
        return (self.x0, self.y0, self.x1, self.y1)

    def calculate_grid_size(self) -> Optional[float]:
        """Calculate approximate grid area in square degrees or square meters.

        Returns:
            Approximate grid area or None if boundaries are not defined.
        """
        if self.x0 is None or self.x1 is None or self.y0 is None or self.y1 is None:
            return None

        if self.coordinate_system == "SPHE":
            # Approximate area calculation for spherical coordinates (in square degrees)
            return (self.x1 - self.x0) * (self.y1 - self.y0)
        else:
            # Cartesian coordinates (in square meters or whatever units are used)
            return (self.x1 - self.x0) * (self.y1 - self.y0)

    def generate_grid_nml(self) -> str:
        """Generate GRID_NML namelist content."""
        lines = []
        lines.append("! Generated by rompy-ww3")
        lines.append("&GRID_NML")

        if self.name:
            lines.append(f"  GRID%NAME              =  '{self.name}'")
        if self.grid_type:
            lines.append(f"  GRID%TYPE              =  '{self.grid_type}'")
        if self.coordinate_system:
            lines.append(f"  GRID%COORD             =  '{self.coordinate_system}'")
        if self.grid_closure:
            lines.append(f"  GRID%CLOS              =  '{self.grid_closure}'")
        if self.zlim is not None:
            lines.append(f"  GRID%ZLIM              =  {self.zlim}")
        if self.dmin is not None:
            lines.append(f"  GRID%DMIN              =  {self.dmin}")

        lines.append("/")
        return "\n".join(lines)

    def generate_rect_nml(self) -> str:
        """Generate RECT_NML namelist content."""
        lines = []
        lines.append("! Generated by rompy-ww3")
        lines.append("&RECT_NML")

        if self.nx is not None:
            lines.append(f"  RECT%NX                =  {self.nx}")
        if self.ny is not None:
            lines.append(f"  RECT%NY                =  {self.ny}")
        if self.sx is not None:
            lines.append(f"  RECT%SX                =  {self.sx}")
        elif self.dx is not None:  # Using dx from parent class as sx
            lines.append(f"  RECT%SX                =  {self.dx}")
        if self.sy is not None:
            lines.append(f"  RECT%SY                =  {self.sy}")
        elif self.dy is not None:  # Using dy from parent class as sy
            lines.append(f"  RECT%SY                =  {self.dy}")
        if self.sf is not None:
            lines.append(f"  RECT%SF                =  {self.sf}")
        if self.x0 is not None:
            lines.append(f"  RECT%X0                =  {self.x0}")
        if self.y0 is not None:
            lines.append(f"  RECT%Y0                =  {self.y0}")
        if hasattr(self, "sf0") and self.sf0 is not None:
            lines.append(f"  RECT%SF0               =  {self.sf0}")

        lines.append("/")
        return "\n".join(lines)

    def write_grid_files(self, workdir: Path) -> None:
        """Write grid namelist files."""
        workdir.mkdir(parents=True, exist_ok=True)

        # Write GRID_NML
        grid_nml_content = self.generate_grid_nml()
        with open(workdir / "grid.nml", "w") as f:
            f.write(grid_nml_content)

        # Write RECT_NML if it's a rectilinear grid
        if self.grid_type == "RECT":
            rect_nml_content = self.generate_rect_nml()
            with open(workdir / "rect.nml", "w") as f:
                f.write(rect_nml_content)

        logger.info(f"Wrote grid files to {workdir}")

    def get_template_context(self) -> dict:
        """Generate template context for Jinja2 templates.

        Returns:
            Dictionary containing grid parameters for templates.
        """
        return {
            "name": self.name,
            "grid_type": self.grid_type,
            "coordinate_system": self.coordinate_system,
            "grid_closure": self.grid_closure,
            "zlim": self.zlim,
            "dmin": self.dmin,
            "nx": self.nx,
            "ny": self.ny,
            "sx": self.sx,
            "sy": self.sy,
            "sf": self.sf,
            "x0": self.x0,
            "y0": self.y0,
            "x1": self.x1,
            "y1": self.y1,
            "grid_dimensions": self.grid_dimensions,
            "grid_spacing": self.grid_spacing,
            "grid_boundaries": self.grid_boundaries,
            "grid_area": self.calculate_grid_size(),
        }
