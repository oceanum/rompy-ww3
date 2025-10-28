"""Grid component for WW3 configuration."""

from typing import Optional
from pydantic import model_validator
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
from ..namelists.grid import Grid, Rect
from .basemodel import WW3ComponentBaseModel


from rompy.core.grid import BaseGrid
import numpy as np
from rompy.logging import get_logger


logger = get_logger(__name__)


class Grid(WW3ComponentBaseModel, BaseGrid):
    """Component for ww3_grid.nml containing grid configuration."""

    spectrum: Optional[Spectrum] = None
    run: Optional[Run] = None
    timesteps: Optional[Timesteps] = None
    depth: Optional[Depth] = None
    mask: Optional[Mask] = None
    obstacle: Optional[Obstacle] = None
    slope: Optional[Slope] = None
    sediment: Optional[Sediment] = None
    inbound_count: Optional[InboundCount] = None
    inbound_points: Optional[InboundPointList] = None
    excluded_count: Optional[ExcludedCount] = None
    excluded_points: Optional[ExcludedPointList] = None
    excluded_bodies: Optional[ExcludedBodyList] = None
    outbound_count: Optional[OutboundCount] = None
    outbound_lines: Optional[OutboundLineList] = None
    curv: Optional[Curv] = None
    unst: Optional[Unst] = None
    smc: Optional[Smc] = None
    grid: Optional[Grid] = None
    rect: Optional[Rect] = None

    @model_validator(mode="after")
    def validate_grid_closure(self):
        """
        Validator to check for grid closure.
        If grid.rect is not None and grid.rect.nx * grid.rect.sx = 360,
        then grid.grid.clos (GRID_NML%clos) should be set to 'SMPL'.
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
        return np.linspace(
            self.rect.x0, self.rect.x0 + self.rect.sx * (self.rect.nx - 1), self.rect.nx
        )

    @property
    def y(self) -> np.ndarray:
        return np.linspace(
            self.rect.y0, self.rect.y0 + self.rect.sy * (self.rect.ny - 1), self.rect.ny
        )
