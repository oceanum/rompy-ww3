"""OUTPUT_TYPE_NML namelist implementation for WW3."""

from typing import Optional, List
from pydantic import Field
from .basemodel import NamelistBaseModel


class OutputTypeField(NamelistBaseModel):
    """Field output parameters for WW3."""
    
    list: Optional[str] = Field(
        default=None,
        description="List of fields to output (space-separated)"
    )


class OutputTypePoint(NamelistBaseModel):
    """Point output parameters for WW3."""
    
    file: Optional[str] = Field(
        default=None,
        description="Point output file"
    )
    name: Optional[str] = Field(
        default=None,
        description="Point output name"
    )


class OutputTypeTrack(NamelistBaseModel):
    """Track output parameters for WW3."""
    
    format: Optional[bool] = Field(
        default=None,
        description="Track file format (T=formatted, F=unformatted)"
    )


class OutputTypePartition(NamelistBaseModel):
    """Partition output parameters for WW3."""
    
    x0: Optional[int] = Field(
        default=None,
        description="Partition start X index"
    )
    xn: Optional[int] = Field(
        default=None,
        description="Partition end X index"
    )
    nx: Optional[int] = Field(
        default=None,
        description="Partition X resolution"
    )
    y0: Optional[int] = Field(
        default=None,
        description="Partition start Y index"
    )
    yn: Optional[int] = Field(
        default=None,
        description="Partition end Y index"
    )
    ny: Optional[int] = Field(
        default=None,
        description="Partition Y resolution"
    )
    format: Optional[bool] = Field(
        default=None,
        description="Partition file format (T=formatted, F=unformatted)"
    )


class OutputTypeCoupling(NamelistBaseModel):
    """Coupling output parameters for WW3."""
    
    sent: Optional[str] = Field(
        default=None,
        description="Fields sent in coupling exchange"
    )
    received: Optional[str] = Field(
        default=None,
        description="Fields received in coupling exchange"
    )
    couplet0: Optional[bool] = Field(
        default=None,
        description="Coupling at T+0 flag"
    )


class OutputTypeRestart(NamelistBaseModel):
    """Restart output parameters for WW3."""
    
    extra: Optional[str] = Field(
        default=None,
        description="Extra fields to write to restart"
    )


class OutputType(NamelistBaseModel):
    """TYPE section of OUTPUT_TYPE_NML for WW3 (single-grid)."""
    
    field: Optional[OutputTypeField] = Field(
        default=None,
        description="Field output parameters"
    )
    point: Optional[OutputTypePoint] = Field(
        default=None,
        description="Point output parameters"
    )
    track: Optional[OutputTypeTrack] = Field(
        default=None,
        description="Track output parameters"
    )
    partition: Optional[OutputTypePartition] = Field(
        default=None,
        description="Partition output parameters"
    )
    coupling: Optional[OutputTypeCoupling] = Field(
        default=None,
        description="Coupling output parameters"
    )
    restart: Optional[OutputTypeRestart] = Field(
        default=None,
        description="Restart output parameters"
    )


class AllType(NamelistBaseModel):
    """ALLTYPE section of OUTPUT_TYPE_NML for WW3 (multi-grid)."""
    
    field: Optional[OutputTypeField] = Field(
        default=None,
        description="Field output parameters for all grids"
    )
    point: Optional[OutputTypePoint] = Field(
        default=None,
        description="Point output parameters for all grids"
    )
    track: Optional[OutputTypeTrack] = Field(
        default=None,
        description="Track output parameters for all grids"
    )
    partition: Optional[OutputTypePartition] = Field(
        default=None,
        description="Partition output parameters for all grids"
    )


class IType(NamelistBaseModel):
    """ITYPE(I) section of OUTPUT_TYPE_NML for WW3 (multi-grid)."""
    
    field: Optional[OutputTypeField] = Field(
        default=None,
        description="Field output parameters for grid I"
    )
    point: Optional[OutputTypePoint] = Field(
        default=None,
        description="Point output parameters for grid I"
    )
    track: Optional[OutputTypeTrack] = Field(
        default=None,
        description="Track output parameters for grid I"
    )
    partition: Optional[OutputTypePartition] = Field(
        default=None,
        description="Partition output parameters for grid I"
    )