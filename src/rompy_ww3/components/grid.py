"""Grid component for WW3 configuration."""

from typing import Optional
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


class GridComponent(WW3ComponentBaseModel):
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
    grid_nml: Optional[Grid] = None
    rect_nml: Optional[Rect] = None
