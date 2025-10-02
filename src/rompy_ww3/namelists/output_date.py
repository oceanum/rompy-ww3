"""OUTPUT_DATE_NML namelist implementation for WW3."""

from typing import Optional
from pydantic import Field
from .basemodel import NamelistBaseModel


class OutputDateField(NamelistBaseModel):
    """Field output date parameters for WW3."""

    start: Optional[str] = Field(
        default=None, description="Field output start time (yyyymmdd hhmmss)"
    )
    stride: Optional[str] = Field(
        default=None, description="Field output time stride (seconds)"
    )
    stop: Optional[str] = Field(
        default=None, description="Field output stop time (yyyymmdd hhmmss)"
    )


class OutputDatePoint(NamelistBaseModel):
    """Point output date parameters for WW3."""

    start: Optional[str] = Field(
        default=None, description="Point output start time (yyyymmdd hhmmss)"
    )
    stride: Optional[str] = Field(
        default=None, description="Point output time stride (seconds)"
    )
    stop: Optional[str] = Field(
        default=None, description="Point output stop time (yyyymmdd hhmmss)"
    )


class OutputDateTrack(NamelistBaseModel):
    """Track output date parameters for WW3."""

    start: Optional[str] = Field(
        default=None, description="Track output start time (yyyymmdd hhmmss)"
    )
    stride: Optional[str] = Field(
        default=None, description="Track output time stride (seconds)"
    )
    stop: Optional[str] = Field(
        default=None, description="Track output stop time (yyyymmdd hhmmss)"
    )


class OutputDateRestart(NamelistBaseModel):
    """Restart output date parameters for WW3."""

    start: Optional[str] = Field(
        default=None, description="Restart output start time (yyyymmdd hhmmss)"
    )
    stride: Optional[str] = Field(
        default=None, description="Restart output time stride (seconds)"
    )
    stop: Optional[str] = Field(
        default=None, description="Restart output stop time (yyyymmdd hhmmss)"
    )


class OutputDateBoundary(NamelistBaseModel):
    """Boundary output date parameters for WW3."""

    start: Optional[str] = Field(
        default=None, description="Boundary output start time (yyyymmdd hhmmss)"
    )
    stride: Optional[str] = Field(
        default=None, description="Boundary output time stride (seconds)"
    )
    stop: Optional[str] = Field(
        default=None, description="Boundary output stop time (yyyymmdd hhmmss)"
    )


class OutputDatePartition(NamelistBaseModel):
    """Partition output date parameters for WW3."""

    start: Optional[str] = Field(
        default=None, description="Partition output start time (yyyymmdd hhmmss)"
    )
    stride: Optional[str] = Field(
        default=None, description="Partition output time stride (seconds)"
    )
    stop: Optional[str] = Field(
        default=None, description="Partition output stop time (yyyymmdd hhmmss)"
    )


class OutputDateCoupling(NamelistBaseModel):
    """Coupling output date parameters for WW3."""

    start: Optional[str] = Field(
        default=None, description="Coupling output start time (yyyymmdd hhmmss)"
    )
    stride: Optional[str] = Field(
        default=None, description="Coupling output time stride (seconds)"
    )
    stop: Optional[str] = Field(
        default=None, description="Coupling output stop time (yyyymmdd hhmmss)"
    )


class OutputDate(NamelistBaseModel):
    """DATE section of OUTPUT_DATE_NML for WW3 (single-grid)."""

    field: Optional[OutputDateField] = Field(
        default=None, description="Field output date parameters"
    )
    point: Optional[OutputDatePoint] = Field(
        default=None, description="Point output date parameters"
    )
    track: Optional[OutputDateTrack] = Field(
        default=None, description="Track output date parameters"
    )
    restart: Optional[OutputDateRestart] = Field(
        default=None, description="Restart output date parameters"
    )
    boundary: Optional[OutputDateBoundary] = Field(
        default=None, description="Boundary output date parameters"
    )
    partition: Optional[OutputDatePartition] = Field(
        default=None, description="Partition output date parameters"
    )
    coupling: Optional[OutputDateCoupling] = Field(
        default=None, description="Coupling output date parameters"
    )


class AllDate(NamelistBaseModel):
    """ALLDATE section of OUTPUT_DATE_NML for WW3 (multi-grid)."""

    field: Optional[OutputDateField] = Field(
        default=None, description="Field output date parameters for all grids"
    )
    point: Optional[OutputDatePoint] = Field(
        default=None, description="Point output date parameters for all grids"
    )
    track: Optional[OutputDateTrack] = Field(
        default=None, description="Track output date parameters for all grids"
    )
    restart: Optional[OutputDateRestart] = Field(
        default=None, description="Restart output date parameters for all grids"
    )
    boundary: Optional[OutputDateBoundary] = Field(
        default=None, description="Boundary output date parameters for all grids"
    )
    partition: Optional[OutputDatePartition] = Field(
        default=None, description="Partition output date parameters for all grids"
    )
    coupling: Optional[OutputDateCoupling] = Field(
        default=None, description="Coupling output date parameters for all grids"
    )


class IDate(NamelistBaseModel):
    """IDATE(I) section of OUTPUT_DATE_NML for WW3 (multi-grid)."""

    field: Optional[OutputDateField] = Field(
        default=None, description="Field output date parameters for grid I"
    )
    point: Optional[OutputDatePoint] = Field(
        default=None, description="Point output date parameters for grid I"
    )
    track: Optional[OutputDateTrack] = Field(
        default=None, description="Track output date parameters for grid I"
    )
    restart: Optional[OutputDateRestart] = Field(
        default=None, description="Restart output date parameters for grid I"
    )
    boundary: Optional[OutputDateBoundary] = Field(
        default=None, description="Boundary output date parameters for grid I"
    )
    partition: Optional[OutputDatePartition] = Field(
        default=None, description="Partition output date parameters for grid I"
    )
    coupling: Optional[OutputDateCoupling] = Field(
        default=None, description="Coupling output date parameters for grid I"
    )
