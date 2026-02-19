"""Grid component for WW3 configuration."""

from typing import Optional
from pydantic import Field as PydanticField, model_validator
from ..namelists.spectrum import Spectrum
from ..namelists.run import Run
from ..namelists.timesteps import Timesteps
from ..namelists.depth import Depth
from ..namelists.mask import Mask
from ..namelists.obstacle import Obstacle
from ..namelists.slope import Slope
from ..namelists.sediment import Sediment
from ..namelists.inbound import InboundCount, InboundPointList
from ..namelists.excluded import ExcludedCount, ExcludedPointList, ExcludedBodyList
from ..namelists.outbound import OutboundCount, OutboundLineList
from ..namelists.curv import Curv
from ..namelists.unst import Unst
from ..namelists.smc import Smc
from ..namelists.grid import Grid as GridNML, Rect
from .basemodel import WW3ComponentBaseModel

from rompy.core.grid import BaseGrid
import numpy as np
from rompy.logging import get_logger

logger = get_logger(__name__)


class Grid(WW3ComponentBaseModel, BaseGrid):
    """Component for ww3_grid.nml containing grid configuration.

    The Grid component represents the grid preprocessing configuration for WW3.
    It contains all the namelist objects needed for configuring the WW3 grid preprocessing
    program (ww3_grid.nml).

    This component manages:
    - SPECTRUM_NML: Spectral parameterization including frequency and direction discretization
    - RUN_NML: Run parameterization including propagation and source term flags
    - TIMESTEPS_NML: Time step configuration including CFL constraints
    - GRID_NML & RECT_NML/CURV_NML/UNST_NML/SMC_NML: Grid definition and parameters
    - DEPTH_NML: Bathymetry depth data configuration
    - MASK_NML: Point status map configuration
    - OBSTACLE_NML: Obstruction map configuration
    - SLOPE_NML: Reflection slope map configuration
    - SEDIMENT_NML: Sedimentary bottom map configuration
    - INBOUND_NML: Input boundary point configuration
    - EXCLUDED_NML: Excluded point and body configuration
    - OUTBOUND_NML: Output boundary line configuration

    The Grid component is used for grid preprocessing runs and provides a clean interface
    for configuring all aspects of the WW3 grid preprocessing program.

    Key Features:
    - **Spectral Configuration**: Frequency and direction discretization
    - **Run Parameters**: Propagation and source term control
    - **Time Stepping**: CFL-constrained time step configuration
    - **Grid Definition**: Support for all WW3 grid types (RECT, CURV, UNST, SMC)
    - **Bathymetry**: Depth data configuration and processing
    - **Masking**: Point status and exclusion configuration
    - **Boundary Conditions**: Input and output boundary configuration
    """

    spectrum: Optional[Spectrum] = PydanticField(
        default=None,
        description=(
            "SPECTRUM_NML configuration defining spectral parameterization. "
            "Includes frequency increment, first frequency, number of frequencies and directions, "
            "and direction offset for wave spectrum discretization."
        ),
    )
    run: Optional[Run] = PydanticField(
        default=None,
        description=(
            "RUN_NML configuration defining run parameterization. "
            "Includes flags for propagation components (X, Y, theta, k) and source terms."
        ),
    )
    timesteps: Optional[Timesteps] = PydanticField(
        default=None,
        description=(
            "TIMESTEPS_NML configuration defining time step parameters. "
            "Includes CFL-constrained time steps for propagation and source terms."
        ),
    )
    depth: Optional[Depth] = PydanticField(
        default=None,
        description=(
            "DEPTH_NML configuration defining bathymetry depth data. "
            "Includes scale factor and filename for depth data input."
        ),
    )
    mask: Optional[Mask] = PydanticField(
        default=None,
        description=(
            "MASK_NML configuration defining point status map. "
            "Includes filename for point status map data input."
        ),
    )
    obstacle: Optional[Obstacle] = PydanticField(
        default=None,
        description=(
            "OBSTACLE_NML configuration defining obstruction map. "
            "Includes scale factor and filename for obstruction data input."
        ),
    )
    slope: Optional[Slope] = PydanticField(
        default=None,
        description=(
            "SLOPE_NML configuration defining reflection slope map. "
            "Includes scale factor and filename for reflection slope data input."
        ),
    )
    sediment: Optional[Sediment] = PydanticField(
        default=None,
        description=(
            "SEDIMENT_NML configuration defining sedimentary bottom map. "
            "Includes scale factor and filename for sediment data input."
        ),
    )
    inbound_count: Optional[InboundCount] = PydanticField(
        default=None,
        description=(
            "INBOUND_COUNT_NML configuration defining number of input boundary points. "
            "Specifies how many input boundary segments and bodies are defined."
        ),
    )
    inbound_points: Optional[InboundPointList] = PydanticField(
        default=None,
        description=(
            "INBOUND_POINT_NML configuration defining input boundary points. "
            "Specifies the list of input boundary points and connection flags."
        ),
    )
    excluded_count: Optional[ExcludedCount] = PydanticField(
        default=None,
        description=(
            "EXCLUDED_COUNT_NML configuration defining number of excluded points and bodies. "
            "Specifies how many excluded segments and bodies are defined."
        ),
    )
    excluded_points: Optional[ExcludedPointList] = PydanticField(
        default=None,
        description=(
            "EXCLUDED_POINT_NML configuration defining excluded points. "
            "Specifies the list of excluded points and connection flags."
        ),
    )
    excluded_bodies: Optional[ExcludedBodyList] = PydanticField(
        default=None,
        description=(
            "EXCLUDED_BODY_NML configuration defining excluded bodies. "
            "Specifies the list of excluded bodies (closed sea point regions)."
        ),
    )
    outbound_count: Optional[OutboundCount] = PydanticField(
        default=None,
        description=(
            "OUTBOUND_COUNT_NML configuration defining number of output boundary lines. "
            "Specifies how many output boundary lines are defined."
        ),
    )
    outbound_lines: Optional[OutboundLineList] = PydanticField(
        default=None,
        description=(
            "OUTBOUND_LINE_NML configuration defining output boundary lines. "
            "Specifies the list of output boundary lines with start points, increments, and counts."
        ),
    )
    curv: Optional[Curv] = PydanticField(
        default=None,
        description=(
            "CURV_NML configuration defining curvilinear grid parameters. "
            "Includes coordinate data specifications for curvilinear grids."
        ),
    )
    unst: Optional[Unst] = PydanticField(
        default=None,
        description=(
            "UNST_NML configuration defining unstructured grid parameters. "
            "Includes filename and format specifications for unstructured grids."
        ),
    )
    smc: Optional[Smc] = PydanticField(
        default=None,
        description=(
            "SMC_NML configuration defining spherical multiple-cell grid parameters. "
            "Includes file specifications for SMC grid components."
        ),
    )
    grid: Optional[GridNML] = PydanticField(
        default=None,
        description=(
            "GRID_NML configuration defining general grid parameters. "
            "Includes grid name, type, coordinate system, closure, and depth limits."
        ),
    )
    rect: Optional[Rect] = PydanticField(
        default=None,
        description=(
            "RECT_NML configuration defining rectilinear grid parameters. "
            "Includes grid dimensions, increments, and corner coordinates."
        ),
    )

    @model_validator(mode="after")
    def validate_grid_closure(self) -> "Grid":
        """Validate grid closure consistency.

        This validator checks for grid closure consistency:
        - If grid.rect is not None and grid.rect.nx * grid.rect.sx = 360,
          then grid.grid.clos (GRID_NML%clos) should be set to 'SMPL'.

        Returns:
            Grid: The validated Grid component instance

        Raises:
            ValueError: If grid closure inconsistency is detected
        """
        if self.rect is not None:
            # Check if the grid spans 360 degrees in longitude (x-direction)
            # which indicates a closed/periodic grid in longitude
            longitude_extent = self.rect.nx * self.rect.sx
            if (
                abs(longitude_extent - 360.0) < 1e-6
            ):  # Account for floating point precision
                # If grid closure is needed, ensure clos parameter is set to 'SMPL'
                if self.grid is not None:
                    if self.grid.clos != "SMPL":
                        logger.warning(
                            f"Grid spans 360 degrees longitude ({self.rect.nx} * {self.rect.sx} = {longitude_extent}), "
                            f"but clos is set to '{self.grid.clos}'. Setting to 'SMPL' for proper closure."
                        )
                        self.grid.clos = "SMPL"
                else:
                    # If grid namelist doesn't exist, create it with clos = 'SMPL'
                    logger.warning(
                        f"Grid spans 360 degrees longitude ({self.rect.nx} * {self.rect.sx} = {longitude_extent}), "
                        f"but no GRID_NML component exists. Creating GRID_NML with clos='SMPL' for proper closure."
                    )
                    from ..namelists.grid import Grid as GridNML

                    self.grid = GridNML(clos="SMPL")

        return self

    @property
    def x(self) -> np.ndarray:
        """Get the x-coordinate array for the grid.

        Returns:
            np.ndarray: The x-coordinate array for the grid points
        """
        x, y = self.meshgrid
        return x

    @property
    def y(self) -> np.ndarray:
        """Get the y-coordinate array for the grid.

        Returns:
            np.ndarray: The y-coordinate array for the grid points
        """
        x, y = self.meshgrid
        return y

    @property
    def meshgrid(self) -> np.ndarray:
        """Get the meshgrid for the grid.

        Returns:
            np.ndarray: The meshgrid (x, y) arrays for the grid points
        """
        x = np.linspace(
            self.rect.x0, self.rect.x0 + self.rect.sx * (self.rect.nx - 1), self.rect.nx
        )
        y = np.linspace(
            self.rect.y0, self.rect.y0 + self.rect.sy * (self.rect.ny - 1), self.rect.ny
        )
        return np.meshgrid(x, y)
