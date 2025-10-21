"""WW3 Namelist package."""

from .basemodel import NamelistBaseModel
from .domain import Domain
from .input import (
    Input,
    InputGrid,
    ModelGrid,
    InputForcing,
    InputAssim,
    ModelGridForcing,
    ModelGridResource,
)
from .output_type import OutputType, AllType, IType
from .output_date import OutputDate, AllDate, IDate
from .homogeneous import HomogCount, HomogInput
from .spectrum import Spectrum
from .run import Run
from .timesteps import Timesteps
from .grid import Grid, Rect
from .bound import Bound
from .forcing import Forcing, ForcingField, ForcingGrid
from .track import Track, TrackFile
from .field import Field
from .point import Point, PointFile
from .restart import Restart, Update
from .unformatted import UnformattedOutput
from .pointoutput import PointOutput
from .restartupdate import RestartUpdate
from .parameters import ModelParameters
from .depth import Depth
from .mask import Mask
from .obstacle import Obstacle
from .slope import Slope
from .sediment import Sediment
from .inbound import InboundCount, InboundPointList, InboundPoint
from .excluded import (
    ExcludedCount,
    ExcludedPointList,
    ExcludedBodyList,
    ExcludedPoint,
    ExcludedBody,
)
from .outbound import OutboundCount, OutboundLineList, OutboundLine
from .curv import Curv, CoordData
from .unst import Unst
from .smc import Smc, SMCFile
from .file import File

__all__ = [
    "NamelistBaseModel",
    "Domain",
    "Input",
    "InputGrid",
    "ModelGrid",
    "InputForcing",
    "InputAssim",
    "ModelGridForcing",
    "ModelGridResource",
    "OutputType",
    "AllType",
    "IType",
    "OutputDate",
    "AllDate",
    "IDate",
    "HomogCount",
    "HomogInput",
    "Spectrum",
    "Run",
    "Timesteps",
    "Grid",
    "Rect",
    "Bound",
    "Forcing",
    "ForcingField",
    "ForcingGrid",
    "Track",
    "TrackFile",
    "Field",
    "Point",
    "PointFile",
    "Restart",
    "Update",
    "UnformattedOutput",
    "PointOutput",
    "RestartUpdate",
    "ModelParameters",
    "Depth",
    "Mask",
    "Obstacle",
    "Slope",
    "Sediment",
    "InboundCount",
    "InboundPointList",
    "InboundPoint",
    "ExcludedCount",
    "ExcludedPointList",
    "ExcludedBodyList",
    "ExcludedPoint",
    "ExcludedBody",
    "OutboundCount",
    "OutboundLineList",
    "OutboundLine",
    "Curv",
    "CoordData",
    "Unst",
    "Smc",
    "SMCFile",
    "File",
]
